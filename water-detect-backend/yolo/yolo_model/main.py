import logging
import os
import threading
import time
from ultralytics import YOLO
from moviepy import VideoFileClip

from waterDetect import settings
BASE_TMP = os.path.join(settings.MEDIA_ROOT, 'analyse_tmp')
CUT_PATH = os.path.join(settings.MEDIA_ROOT, 'cuts')
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
    logger.info(f"start analyse video {fileUID}")
    destFolder = os.path.join(BASE_TMP, fileUID)
    files = os.listdir(path)
    for file in files:
        if file.endswith('.ts') or file.endswith('.mp4'):
            filename = f"analysed_{file.split('.')[0]}"
            print('aaa')
            GetFromModel(os.path.join(path, file), filename, fileUID)
            print('xxx')
            # 启动一个线程
            threading.Thread(
                target=resolveDoneVideo,
                args=(os.path.join(destFolder, filename, f"{file.split('.')[0]}.avi"), filename)).start()
            print('yyy')

    return destFolder

def resolveDoneVideo(videoPath, filename):
    avi_to_ts(videoPath, videoPath.replace('.avi', '.ts'))

def avi_to_ts(input_file, output_file):
    """
    将AVI文件转换为TS文件。

    :param input_file: 输入的AVI文件路径
    :param output_file: 输出的TS文件路径
    """
    print('start conver', input_file, output_file)
    # 加载AVI视频文件
    clip = VideoFileClip(input_file)
    # 将视频保存为TS格式
    clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
    # 关闭视频剪辑对象以释放资源
    clip.close()
    print('avi done')


if __name__ == '__main__':
    # 视频文件路径
    paths = [
        r'D:\coding\graduation-design\water-detect\media\cuts\2b2f2051-f52a-4dd7-b7a8-ba6cada07d4a',
        # r'D:\coding\graduation-design\water-detect\media\cuts\0da9640b-4f42-4717-b995-f8e089924e7e\0da9640b-4f42-4717-b995-f8e089924e7e_0000.ts'
    ]
    for c in paths:
        AnalyseVideo(c, '2b2f2051-f52a-4dd7-b7a8-ba6cada07d4a')
    print('done')
    time.sleep(5)
    print('exit')
