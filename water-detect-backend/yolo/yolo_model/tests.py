import subprocess
import sys
import time

import torch

from yolo.yolo_model.main import AnalyseVideo, merge_ts_files


def TestYoloAnalyse():
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

def TestMergeTs2Mp4():
    folder = r'D:\coding\graduation-design\water-detect\media\cuts\analysed_4c1c1295-03f8-4bdd-ae8a-67dce714a23c'
    target = r'D:\coding\graduation-design\water-detect\media\videos\analysed_xxx.mp4'
    merge_ts_files(folder, target)

def TestTs2Avi():
    pass

if __name__ == '__main__':
    print(sys.executable)
    result = subprocess.run(['which', 'pip'], capture_output=True, text=True)
    print(result.stdout.strip())
    print(torch.cuda.is_available())