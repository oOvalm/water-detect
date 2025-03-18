import logging
import os
import shutil
import threading
import time
from ultralytics import YOLO
from moviepy import VideoFileClip

from common.annotation import singleton
from common.db_model import FileType
from common_service import redis
from waterDetect import settings
from yolo.yolo_model.analyse import GetFromModel
from yolo.yolo_model.video_utils import avi_to_ts, merge_video_files

USE_MOCK = False


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


def AnalyseVideo(path: str, fileUID: str):
    from common_service.fileService import FileManager
    logger.info(f"start analyse video {fileUID}")
    tempAnalyseFolder = os.path.join(BASE_TMP, fileUID)
    destFolder = os.path.join(CUT_PATH, f"analysed_{fileUID}")
    files = os.listdir(path)
    threads = []

    redis.UploadAnalyseProcess(fileUID, total=len(files), finished=0)
    if not os.path.exists(destFolder):
        os.makedirs(destFolder)
    originM3U8 = os.path.join(path, 'index.m3u8')
    destM3U8 = os.path.join(destFolder, 'index.m3u8')
    if os.path.exists(originM3U8):
        # 写一份解析后的m3u8文件
        RewriteM3U8(originM3U8, destM3U8)
    else:
        logger.warning(f"index.m3u8 not found {originM3U8}")

    for i, file in enumerate(files):
        if file.endswith('.ts'):
            filename = f"analysed_{file.split('.')[0]}"
            GetFromModel(os.path.join(path, file), filename, fileUID)
            # 启动一个线程
            thread = threading.Thread(
                target=resolveDoneVideo,
                args=(
                    os.path.join(tempAnalyseFolder, filename, f"{file.split('.')[0]}.avi"),
                    destFolder,
                    filename))
            thread.start()
            threads.append(thread)
        redis.UploadAnalyseProcess(fileUID, total=len(files), finished=i+1)

    # 等待所有线程完成
    for thread in threads:
        thread.join()
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

def resolveDoneVideo(videoPath, destFolder, filename):
    avi_to_ts(videoPath, os.path.join(destFolder, f"{filename}.ts"))

