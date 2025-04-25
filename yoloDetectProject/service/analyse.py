import logging
import os
import subprocess
import uuid

import cv2
import numpy as np
import requests
from moviepy import VideoFileClip
from ultralytics import YOLO

USE_MOCK = False # 测试时使用灰度图代替YOLO检测
logger = logging.getLogger(__name__)

YOLO_MODEL_PATH = r'D:\coding\graduation-design\water-detect\yoloDetectProject\service\model\best.pt'
model = YOLO(YOLO_MODEL_PATH)

BASE_FOLDER = r'D:\coding\graduation-design\water-detect\yoloDetectProject\service\tmp'

if not os.path.isdir(BASE_FOLDER):
    os.mkdir(BASE_FOLDER)


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

# def GetFromModel_Mock(path: str, destFolderName: str, projFolderName: str):
#     oriFileName = path.split('\\')[-1].split('.')[0]
#     tmp = os.path.join(BASE_TMP, projFolderName, destFolderName)
#     os.makedirs(tmp)
#     # ts_to_avi(path, os.path.join(tmp, f'{oriFileName}.avi'))
#     convert_to_black_and_white(path, os.path.join(tmp, f'{oriFileName}.avi'))
#     return GetYOLOOutPutPath(path, destFolderName, projFolderName)

def CompressVideo(input_path, output_path):
    # 打开输入视频文件
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-c:v', 'h264_amf','-profile:v', 'main',
        '-c:a', 'copy',
        output_path
    ], check=True)

def AnalyseVideo(filePath, outputFolder, destName):
    # if USE_MOCK:
    #     return GetFromModel_Mock(path, destFolderName, projFolderName)
    uid = str(uuid.uuid4())
    model(filePath, save=True, project=outputFolder, name=uid)
    srcFilename = filePath.split('\\')[-1].split('.')[0]
    srcPath = f"{outputFolder}/{uid}/{srcFilename}.avi"
    DestPath = f"{outputFolder}/{uid}/{destName}"
    CompressVideo(srcPath, DestPath)
    return DestPath


def AnalyseImage(filePath, outputFolder, suffix,uid):
    # if USE_MOCK:
    #     return GetFromModel_Mock(path, destFolderName, projFolderName)
    model(filePath, save=True, project=outputFolder, name=uid)
    DestPath = f"{outputFolder}/{uid}/{uid}.{suffix}"
    return DestPath