import logging
import os
import subprocess
import time
from datetime import datetime
import cv2

from common.ProcessUtils import execute_command
from common.utils import get_video_duration
from common_service import redisService
from common_service.lock import RedisLock
from common_service.redisService import GetDefaultRedis
from online_stream.stream_m3u8 import stream_m3u8
from waterDetect import settings
from yolo.yolo_model.analyse import AnalyseImage, GetFromModel
from yolo.yolo_model.video_utils import merge_video_files, avi_to_ts

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


def capture_streamNanalyse(app, stream_key, event, que):
    process = None
    try:
        stream_name = f"{app}_{stream_key}"
        log.info(f"start capture {stream_name}")
        # 抢流的监听锁
        with RedisLock(GetDefaultRedis(), f"capture_ori_stream:{stream_name}", expire=5) as r:
            hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
            # 拿不到锁直接返回
            if not r.is_acquired:
                print('get lock fail')
                m3u8Path = GetStreamM3U8Path(app, stream_key, False)
                if m3u8Path is None:
                    que.put(f'm3u8 not found')
                else:
                    que.put(m3u8Path)
                event.set()
                return

            # 搞一下文件夹
            rtmp_url = f"rtmp://{rtmp_host}/{app}/{stream_key}"
            currentTimeStr = datetime.now().strftime("%Y%m%d%H%M%S")
            stream_base_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
            hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}"
            analyse_hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}_analyse"
            hls_path = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}\\{currentTimeStr}\\stream_{stream_key}.m3u8"
            if not os.path.exists(stream_base_folder):
                os.makedirs(stream_base_folder)
            if not os.path.exists(hls_folder):
                os.makedirs(hls_folder)
            if not os.path.exists(analyse_hls_folder):
                os.makedirs(analyse_hls_folder)

            # 开个子进程抓流，转为hls
            command = [
                settings.FFMPEG_PATH,
                '-i', rtmp_url,
                '-rw_timeout', '5000000',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:v', '500k',  # 设置视频比特率
                '-f', 'hls',
                '-hls_time', '10',
                '-hls_list_size', '6',
                hls_path
            ]
            print(' '.join(command))
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            # 返回
            if process.poll() is not None :
                print(f"ffmpeg error: {process.poll()}")
                que.put(f'capture stream failure')
                event.set()
                return
            if not os.path.exists(hls_path):
                que.put(f'capture not start')
            else:
                que.put(f'hls/{stream_name}/{currentTimeStr}/stream_{stream_key}.m3u8')
            event.set()

            # 当前线程扫ts文件，进行检测
            currentID, failTime = 0, 0

            analyse_m3u8_path = os.path.join(analyse_hls_folder, f"analysed_stream_{stream_key}.m3u8")
            analyse_m3u8 = stream_m3u8(analyse_m3u8_path, 6)

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
                    if failTime > 5*30:
                        print(f"cannot get new file for a long time: {hls_path}, maybe ffmpeg process failed, kill subprocess")
                        process.kill()
                        break
                    time.sleep(10)
                    continue
                # 更新m3u8文件
                analyseFilename = f"analysed_stream_{stream_key}{currentID}.ts"
                duration = AnalyseVideoForStreamTs(oriPath, stream_key, stream_name,
                                        currentID, currentTimeStr,
                                        os.path.join(analyse_hls_folder, analyseFilename))
                analyse_m3u8.push(analyseFilename, duration)
                analyse_m3u8.write()
                failTime = 0
                currentID += 1
            analyse_m3u8.done()
            analyse_m3u8.write()
    except Exception as e:
        print("capture_ori_stream error", e)
    finally:
        if process is not None and process.poll() is not None:
            process.kill()
        print('capture return')
        if not event.is_set():
            event.set()


def GetStreamM3U8Path(app, stream_key, isAnalyse=False):
    stream_name = f"{app}_{stream_key}"
    hls_folder = f"{settings.MEDIA_ROOT}\\hls\\{stream_name}"
    folders = os.listdir(hls_folder)
    if isAnalyse:
        folders = [f for f in folders if f.endswith('_analyse')]
    else:
        folders = [f for f in folders if not f.endswith('_analyse')]
    folders.sort()
    hls_path = f"hls/{stream_name}/{folders[-1]}/{'analysed_' if isAnalyse else ''}stream_{stream_key}.m3u8"
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, hls_path)):
        return hls_path
    else:
        return None

def AnalyseVideoForStreamTs(srcPath, stream_key, stream_name, currentID, streamTimeStr, destPath):
    videoPath = GetFromModel(srcPath, f"stream_{stream_key}{currentID}", f"{stream_name}_{streamTimeStr}")
    # 获取path的ts视频文件的时长
    avi_to_ts(videoPath, destPath)
    # 移除文件
    # os.remove(videoPath)
    return get_video_duration(destPath)
