import logging
import os
import shutil
import threading
import time
from ultralytics import YOLO
from moviepy import VideoFileClip

from common_service import redis
from waterDetect import settings
BASE_TMP = os.path.join(settings.MEDIA_ROOT, 'analyse_tmp')
CUT_PATH = os.path.join(settings.MEDIA_ROOT, 'cuts')
VIDEO_PATH = os.path.join(settings.MEDIA_ROOT, 'videos')
YOLO_MODEL_PATH = r'D:\coding\graduation-design\water-detect\water-detect-backend\yolo\yolo_model\yolov8n.pt'

# 加载 YOLOv8n 模型
model = YOLO(YOLO_MODEL_PATH)
logger = logging.getLogger(__name__)

def GetFromModel(path: str, destFolderName: str, projFolderName: str):
    # 使用模型对视频文件进行预测，并保存结果
    results = model.predict(source=path, save=True,
                            project=os.path.join(BASE_TMP, projFolderName),
                            name=f"{destFolderName}", stream=True)
    for _ in results:
        pass


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
        shutil.copy2(originM3U8, destM3U8)  # 复制 index.m3u8 文件
    else:
        logger.warning(f"index.m3u8 not found {originM3U8}")

    for i, file in enumerate(files):
        if file.endswith('.ts') or file.endswith('.mp4'):
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
    videoFilePath = os.path.join(VIDEO_PATH, f"analysed_{fileUID}.mp4")
    merge_ts_files(destFolder, videoFilePath)
    FileManager().CreateThumbnail(videoFilePath, f"analysed_{fileUID}")
    return destFolder

def resolveDoneVideo(videoPath, destFolder, filename):
    avi_to_ts(videoPath, os.path.join(destFolder, f"{filename}.ts"))

def avi_to_ts(input_file, output_file):
    """
    将AVI文件转换为TS文件。

    :param input_file: 输入的AVI文件路径
    :param output_file: 输出的TS文件路径
    """
    print('start convert avi to ts', input_file, output_file)
    # 加载AVI视频文件
    clip = VideoFileClip(input_file)
    clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
    # 关闭视频剪辑对象以释放资源
    clip.close()
    print('avi done')

def merge_ts_files(input_folder, output_file):
    """
    将指定文件夹中的所有TS视频文件合并为一个视频文件

    :param input_folder: 包含TS视频文件的文件夹路径
    :param output_file: 合并后视频文件的输出路径
    """
    from moviepy import VideoFileClip, concatenate_videoclips
    logger.info(f"start merge ts to mp4, src_folder: {input_folder}, destFileName: {output_file}")
    # 获取文件夹中所有的TS文件
    ts_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.ts')]
    # 按文件名排序
    ts_files.sort()

    # 加载所有视频剪辑
    clips = [VideoFileClip(ts_file) for ts_file in ts_files]

    # 合并所有视频剪辑
    final_clip = concatenate_videoclips(clips, method="compose")

    # 保存合并后的视频
    final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

    # 关闭所有视频剪辑对象以释放资源
    for clip in clips:
        clip.close()
    final_clip.close()



