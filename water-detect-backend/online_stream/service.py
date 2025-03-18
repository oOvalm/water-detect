import logging
import os
import subprocess
import time
from datetime import datetime
import cv2

from common.ProcessUtils import execute_command
from common_service import redisService
from common_service.lock import RedisLock
from common_service.redisService import GetDefaultRedis
from waterDetect import settings
from yolo.yolo_model.analyse import AnalyseImage, GetFromModel
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


def capture_ori_stream(app, stream_key, event, que):
    try:
        stream_name = f"{app}_{stream_key}"
        with RedisLock(GetDefaultRedis(), f"capture_ori_stream:{stream_name}", expire=5) as r:
            hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
            if not r.is_acquired:
                print('get lock fail')
                folders = os.listdir(hls_folder)
                folders.sort()
                hls_path = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{folders[-1]}\\stream_{stream_key}.m3u8"
                if not os.path.exists(hls_path):
                    que.put(f'error bizError')
                else:
                    que.put(f'hls\\{stream_name}\\{folders[-1]}\\stream_{stream_key}.m3u8')
                event.set()
                return
            rtmp_url = f"rtmp://{rtmp_host}/{app}/{stream_key}"
            currentTimeStr = datetime.now().strftime("%Y%m%d%H%M%S")
            hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}"
            hls_path = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}\\stream_{stream_key}.m3u8"
            if not os.path.exists(f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"):
                os.makedirs(f"{settings.MEDIA_ROOT}\\hls\\{stream_name}")
            if not os.path.exists(hls_folder):
                os.makedirs(hls_folder)
            command = [
                settings.FFMPEG_PATH,
                '-loglevel', 'debug',  # 添加详细日志级别
                '-i', rtmp_url,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-f', 'hls',
                '-hls_time', '10',
                '-hls_list_size', '6',
                hls_path
            ]
            print(' '.join(command))
            # execute_command(command, outprint_log=True)
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            time.sleep(4)
            if process.poll() is not None :
                print(f"ffmpeg error: {process.poll()}")
                que.put(f'error bizError')
                event.set()
                return
            if not os.path.exists(hls_path):
                que.put(f'error bizError')
            else:
                que.put(f'hls\\{stream_name}\\{currentTimeStr}\\stream_{stream_key}.m3u8')
            event.set()
            currentID = 0
            failTime = 0
            while True:
                oriPath = os.path.join(hls_folder, f"stream_{stream_key}{currentID}.ts")
                if not os.path.exists(oriPath):
                    failTime += 1
                    process_return_code = process.poll()
                    print(f'not found new ts file {failTime}')
                    if process_return_code is not None:
                        # 子进程运行完成了 && 没有未解析的文件, 退出
                        print(f"ffmpeg process exited with return code {process_return_code}")
                        break
                    if not os.path.exists(hls_path) and failTime > 5*30:
                        print(f"hls file not exist: {hls_path}, maybe ffmpeg process failed, kill subprocess")
                        process.kill()
                        break
                    time.sleep(10)
                    continue
                GetFromModel(oriPath, f"stream_{stream_key}{currentID}", stream_name)
                currentID += 1
    except Exception as e:
        print("capture_ori_stream error", e)
    finally:
        if process.poll() is not None:
            process.kill()
        print('capture return')
        if not event.is_set():
            event.set()