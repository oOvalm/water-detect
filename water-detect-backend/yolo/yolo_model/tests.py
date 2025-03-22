import os
import subprocess
import sys
import time

import requests
import torch

from yolo.yolo_model.analyse import GetFromRemote
from yolo.yolo_model.main import AnalyseTsVideoFolder, merge_video_files


def TestYoloAnalyse():
    # 视频文件路径
    paths = [
        r'D:\coding\graduation-design\water-detect\media\cuts\2b2f2051-f52a-4dd7-b7a8-ba6cada07d4a',
        # r'D:\coding\graduation-design\water-detect\media\cuts\0da9640b-4f42-4717-b995-f8e089924e7e\0da9640b-4f42-4717-b995-f8e089924e7e_0000.ts'
    ]
    for c in paths:
        AnalyseTsVideoFolder(c, '2b2f2051-f52a-4dd7-b7a8-ba6cada07d4a')
    print('done')
    time.sleep(5)
    print('exit')

def TestMergeTs2Mp4():
    folder = r'D:\coding\graduation-design\water-detect\media\cuts\analysed_4c1c1295-03f8-4bdd-ae8a-67dce714a23c'
    target = r'D:\coding\graduation-design\water-detect\media\videos\analysed_xxx.mp4'
    merge_video_files(folder, target, 'ts')

def TestTs2Avi():
    pass

import subprocess


def check_rtmp_stream(url):
    try:
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            url
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        if output and float(output) > 0:
            return True
        else:
            return False
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
        return False


def TestUpload():
    url = 'http://127.0.0.1:8180/upload'
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                print('File uploaded successfully')
            else:
                print(f'Upload failed: {response.text}')
    except FileNotFoundError:
        print('File not found')

# 示例用法
if __name__ == '__main__':
    file_path = r'D:\coding\graduation-design\water-detect\media\files\1e1e8ee3-0c63-44f2-9776-d37bbf7f2d5c.mp4'
    GetFromRemote(file_path)
    # rtmp_url = 'rtmp://8.148.229.47:1935/live/ZGVmNjMzY2Et'
    # if check_rtmp_stream(rtmp_url):
    #     print("该 RTMP 地址有输入流。")
    # else:
    #     print("该 RTMP 地址无输入流。")
