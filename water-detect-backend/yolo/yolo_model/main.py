import logging
import os
import shutil
import queue
import subprocess
import threading

import numpy as np
from PIL import Image
from ultralytics import YOLO

from common.annotation import singleton
from common.db_model import FileType
from common_service import redisService
from common.video_utils import InitStreamOutput, WriteFrameAsStream, merge_video_files
from waterDetect import settings
from yolo.yolo_model.analyse import GetFromModel, AnalyseImage

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
    # 只保留ts
    files = [f for f in os.listdir(path) if f.endswith('.ts')]
    threads = []

    redisService.UploadAnalyseProcess(fileUID, total=len(files), finished=0)
    if not os.path.exists(destFolder):
        os.makedirs(destFolder)

    q = queue.Queue()
    event_loop_thread = threading.Thread(
        target=process_video_queue,
        args=(q, destFolder, fileUID, len(files)),
        daemon=True
    )
    event_loop_thread.start()

    for i, file in enumerate(files):
        if file.endswith('.ts'):
            filename = f"analysed_{file.split('.')[0]}"
            videoPath = GetFromModel(os.path.join(path, file), filename, fileUID)
            q.put((videoPath, filename))


    for thread in threads:
        thread.join()
    if os.path.exists(tempAnalyseFolder):
        shutil.rmtree(tempAnalyseFolder)  # 删除临时文件夹
    else:
        logger.warning(f"temp folder not exist {tempAnalyseFolder}")
    q.put(None)
    event_loop_thread.join()

    videoFilePath = os.path.join(SOURCE_PATH, f"analysed_{fileUID}.mp4")
    merge_video_files(destFolder, videoFilePath, 'ts')
    FileManager().CreateThumbnail(videoFilePath, f"analysed_{fileUID}", FileType.Video.value)
    return f"analysed_{fileUID}", FileManager().GetFileSize(videoFilePath)


def AnalyseImageWithPath(path: str, fileUID: str):
    from common_service.fileService import FileManager
    logger.info(f"start analyse image {fileUID}")
    image = np.array(Image.open(path))
    analysedImage = AnalyseImage(image, filePath=path)
    targetPath = os.path.join(SOURCE_PATH, f"analysed_{fileUID}.jpg")
    Image.fromarray(analysedImage).save(targetPath)
    FileManager().CreateThumbnail(targetPath, f"analysed_{fileUID}", FileType.Image.value)
    return f"analysed_{fileUID}", FileManager().GetFileSize(targetPath)


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

def process_video_queue(queue, destFolder, fileUID, tot):
    output_process = None
    doneNum = 0
    while True:
        video_info = queue.get()
        if video_info is None:
            break
        videoPath, filename = video_info
        output_process = resolveDoneVideo(output_process, videoPath, destFolder, filename)
        doneNum += 1
        redisService.UploadAnalyseProcess(fileUID, total=tot, finished=doneNum)
        queue.task_done()
    if output_process:
        output_process.close()
        output_process.terminate()
        try:
            output_process.wait(timeout=10)  # 等待子进程退出
            logger.info("output_process teminated")
        except subprocess.TimeoutExpired:
            logger.info("output_process cannot exit in 10s, kill it!")
            output_process.kill()  # 强制终止子进程

    redisService.UploadAnalyseProcess(fileUID, total=tot, finished=tot)
