import logging
import os
import shutil
from ultralytics import YOLO

from common.annotation import singleton
from common.db_model import FileType
from common_service import redisService
from common.video_utils import InitStreamOutput, WriteFrameAsStream, merge_video_files
from waterDetect import settings
from yolo.yolo_model.analyse import GetFromModel

BASE_TMP = os.path.join(settings.MEDIA_ROOT, 'analyse_tmp')
CUT_PATH = os.path.join(settings.MEDIA_ROOT, 'cuts')
SOURCE_PATH = os.path.join(settings.MEDIA_ROOT, 'files')
YOLO_MODEL_PATH = r'D:\coding\graduation-design\water-detect\water-detect-backend\yolo\yolo_model\yolov8n.pt'

# 加载 YOLOv8n 模型
@singleton
class singleYOLO(YOLO):
    def __init__(self):
        super().__init__(YOLO_MODEL_PATH)


logger = logging.getLogger(__name__)


def AnalyseTsVideoFolder(path: str, fileUID: str):
    from common_service.fileService import FileManager
    logger.info(f"start analyse video {fileUID}")
    tempAnalyseFolder = os.path.join(BASE_TMP, fileUID)
    destFolder = os.path.join(CUT_PATH, f"analysed_{fileUID}")
    files = os.listdir(path)
    threads = []

    redisService.UploadAnalyseProcess(fileUID, total=len(files), finished=0)
    if not os.path.exists(destFolder):
        os.makedirs(destFolder)

    output_process = None

    for i, file in enumerate(files):
        if file.endswith('.ts'):
            filename = f"analysed_{file.split('.')[0]}"
            GetFromModel(os.path.join(path, file), filename, fileUID)
            # todo: 模型用gpu计算后, 这可以用线程处理
            output_process = resolveDoneVideo(output_process, os.path.join(tempAnalyseFolder, filename, f"{file.split('.')[0]}.avi"),
                             destFolder, filename)
        redisService.UploadAnalyseProcess(fileUID, total=len(files), finished=i+1)

    if os.path.exists(tempAnalyseFolder):
        shutil.rmtree(tempAnalyseFolder)  # 删除临时文件夹
    else:
        logger.warning(f"temp folder not exist {tempAnalyseFolder}")
    videoFilePath = os.path.join(SOURCE_PATH, f"analysed_{fileUID}.mp4")
    merge_video_files(destFolder, videoFilePath, 'ts')
    FileManager().CreateThumbnail(videoFilePath, f"analysed_{fileUID}", FileType.Video.value)
    return f"analysed_{fileUID}", FileManager().GetFileSize(videoFilePath)

def RewriteM3U8(src: str, dest: str):
    with open(src, 'r') as f:
        lines = f.readlines()
    with open(dest, 'w') as f:
        for line in lines:
            newLine = line
            if line.endswith('.ts') or line.endswith('.ts\n'):
                newLine = f"analysed_{line.split('.')[0]}.ts\n"
            f.write(newLine)

def resolveDoneVideo(output_process, videoPath, destFolder, filename):
    if output_process is None:
        ffname = filename.rsplit("_", 1)[0]
        output_process = InitStreamOutput(videoPath, destFolder, 'index.m3u8', tsPrefix=ffname)
    WriteFrameAsStream(output_process, videoPath)
    return output_process
