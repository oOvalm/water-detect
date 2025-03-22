import logging
import os

import numpy as np
import requests
from moviepy import VideoFileClip
from ultralytics import YOLO

from common.annotation import singleton
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

def GetYOLOOutPutPath(path: str, destFolderName: str, projFolderName: str):
    oriFilename = path.split('\\')[-1].split('.')[0]
    return os.path.join(BASE_TMP, projFolderName, destFolderName, f"{oriFilename}.avi")


def to_grayscale(frame):
    # 计算灰度值
    gray = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])
    # 复制灰度值到三个通道以保持 RGB 格式
    gray_frame = np.stack([gray] * 3, axis=-1).astype(np.uint8)
    return gray_frame


def convert_to_black_and_white(input_path, output_path):
    try:
        clip = VideoFileClip(input_path)
        # 应用灰度转换函数到每一帧
        bw_clip = clip.image_transform(to_grayscale)
        bw_clip.write_videofile(output_path, codec='h264_amf', preset="speed")
        clip.close()
        bw_clip.close()
        print(f"convert success: {output_path}")
    except Exception as e:
        print(f"convert fail: {e}")

def GetFromModel_Mock(path: str, destFolderName: str, projFolderName: str):
    oriFileName = path.split('\\')[-1].split('.')[0]
    tmp = os.path.join(BASE_TMP, projFolderName, destFolderName)
    os.makedirs(tmp)
    # ts_to_avi(path, os.path.join(tmp, f'{oriFileName}.avi'))
    convert_to_black_and_white(path, os.path.join(tmp, f'{oriFileName}.avi'))
    assert GetYOLOOutPutPath(path, destFolderName, projFolderName) == os.path.join(tmp, f'{oriFileName}.avi')
    return GetYOLOOutPutPath(path, destFolderName, projFolderName)

def GetFromModel(path: str, destFolderName: str, projFolderName: str):
    if USE_MOCK:
        return GetFromModel_Mock(path, destFolderName, projFolderName)
    # 使用模型对视频文件进行预测，并保存结果
    results = singleYOLO().predict(source=path, save=True,
                            project=os.path.join(BASE_TMP, projFolderName),
                            name=f"{destFolderName}", stream=True)
    for _ in results:
        pass
    return GetYOLOOutPutPath(path, destFolderName, projFolderName)

def AnalyseImage(image):
    if USE_MOCK:
        return to_grayscale(image)
    result = singleYOLO()(image, imgsz=320)
    return result[0].plot()



def GetFromRemote(file_path):
    url = 'http://127.0.0.1:8180/upload'
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                output_file_path = os.path.join(settings.MEDIA_ROOT, 'output_' + os.path.basename(file_path))
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(response.content)
                print(f'File uploaded and result saved to {output_file_path}')
            else:
                print(f'Upload failed: {response.text}')
    except FileNotFoundError:
        print('File not found')