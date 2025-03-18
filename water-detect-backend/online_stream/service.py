import logging
import os
import subprocess
from datetime import datetime

import cv2

from waterDetect import settings
from yolo.yolo_model.analyse import AnalyseImage
from yolo.yolo_model.video_utils import merge_video_files

rtmp_host = f"{settings.NGINX_CONFIG['host']}:{settings.NGINX_CONFIG['rtmp_port']}"

TempVideoFolder = os.path.join(settings.MEDIA_ROOT, 'tmp')
log = logging.getLogger(__name__)
def AnalyseFrame(frame):
    # 处理成黑白
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray
    # return AnalyseImage(frame)

def analyse_stream(stream_name):
    try:
        log.info(f"start capture {stream_name}")
        # 输入流地址
        input_stream = f'rtmp://{rtmp_host}/live/{stream_name}'
        output_stream = f'rtmp://{rtmp_host}/analysed/{stream_name}'

        currentTimeStr = datetime.now().strftime("%Y%m%d%H%M%S")
        streamFolder = os.path.join(TempVideoFolder, stream_name, currentTimeStr)
        baseFolder = os.path.join(TempVideoFolder, stream_name)
        if not os.path.exists(baseFolder):
            os.makedirs(baseFolder)
        if not os.path.exists(streamFolder):
            os.makedirs(streamFolder)

        # 打开 RTMP 流
        cap = cv2.VideoCapture(input_stream)
        # 检查是否成功打开流
        if not cap.isOpened():
            log.info(f"cannot open rtmp stream: {input_stream}")
            return
        log.info("conn input success")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames_per_minute = int(fps * 60)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 连接输出流
        # FFmpeg 命令，用于将处理后的帧推送到新的 RTMP 流
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{width}x{height}',
            '-r', str(fps),
            '-i', '-',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-f', 'flv',
            output_stream
        ]

        # 启动 FFmpeg 进程
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

        frame_count = 0
        frame_list = []
        while True:
            ret, frame = cap.read()
            if not ret:
                log.info(f"read to eof, save files: {stream_name}-{currentTimeStr}.mp4")
                # 先保存剩下的
                output_filename = f"output_{int(datetime.now().timestamp())}.mp4"
                save_frameList(frame_list, os.path.join(streamFolder, output_filename), fps)
                # 合并
                merge_video_files(streamFolder, os.path.join(settings.MEDIA_ROOT, 'files', f'{stream_name}-{currentTimeStr}.mp4'), 'mp4')
                break
            # 调试信息：打印帧的最小值和最大值
            analysedFrame = AnalyseFrame(frame)
            # 将当前帧添加到帧列表中
            frame_list.append(analysedFrame)
            ffmpeg_process.stdin.write(analysedFrame.tobytes())
            frame_count += 1

            if frame_count == frames_per_minute:
                output_filename = f"output_{int(datetime.now().timestamp())}.mp4"
                save_frameList(frame_list, os.path.join(streamFolder, output_filename), fps)
                print(f"Video saved: {output_filename}")
                # 清空帧列表和帧计数器
                frame_list = []
                frame_count = 0

        # 释放资源
        cap.release()
    except Exception as e:
        print(e)

def save_frameList(frames, outputPath, fps):
    if len(frames) == 0:
        return
    height, width, _ = frames[0].shape
    # 定义视频编码器和输出文件名
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # 创建视频写入对象
    out = cv2.VideoWriter(outputPath, fourcc, fps, (width, height))

    # 将帧列表中的帧写入视频文件
    for f in frames:
        out.write(f)

    # 释放视频写入对象
    out.release()