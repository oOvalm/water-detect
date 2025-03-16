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

USE_MOCK = True


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

def GetFromModel_Mock(path: str, destFolderName: str, projFolderName: str):
    oriFileName = path.split('\\')[-1].split('.')[0]
    tmp = os.path.join(BASE_TMP, projFolderName, destFolderName)
    os.makedirs(tmp)
    ts_to_avi(path, os.path.join(tmp, f'{oriFileName}.avi'))

def GetFromModel(path: str, destFolderName: str, projFolderName: str):
    if USE_MOCK:
        GetFromModel_Mock(path, destFolderName, projFolderName)
        return
    # 使用模型对视频文件进行预测，并保存结果
    results = singleYOLO().predict(source=path, save=True,
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
    merge_ts_files(destFolder, videoFilePath)
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

def ts_to_avi(input_file, output_file):
    try:
        # 加载 .ts 视频文件
        clip = VideoFileClip(input_file)
        # 将视频保存为 .avi 格式
        clip.write_videofile(output_file, codec='mpeg4')
        # 关闭视频剪辑对象
        clip.close()
        print(f"成功将 {input_file} 转换为 {output_file}")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")

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



