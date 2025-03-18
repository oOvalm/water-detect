import subprocess
import threading

import cv2
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from online_stream.service import analyse_stream


def ResolveFrame(frame):
    print(type(frame))
    return frame
def start_resolve_stream(stream_name: str):
    try:
        # 输入流地址
        input_stream = f'rtmp://127.0.0.1:1935/live/{stream_name}'
        # 输出流地址，可根据实际情况修改
        output_stream = f'rtmp://127.0.0.1:1935/analysed/{stream_name}'

        # 打开 RTMP 流
        cap = cv2.VideoCapture(input_stream, cv2.CAP_FFMPEG)
        # 检查是否成功打开流
        if not cap.isOpened():
            print(f"cannot open rtmp stream: {input_stream}")
            return

        # 获取视频的帧率、宽度和高度
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

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

        while True:
            ret, frame = cap.read()
            if not ret:
                print("cannot read frame skip")
                break
            # 调试信息：打印帧的最小值和最大值
            print(f"min frame: {frame.min()}, max frame: {frame.max()}")
            # 处理每一帧
            processed_frame = ResolveFrame(frame)
            # 将处理后的帧写入 FFmpeg 进程的标准输入
            ffmpeg_process.stdin.write(processed_frame.tobytes())

        # 释放资源
        cap.release()
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
    except Exception as e:
        print(e)


@api_view(['GET'])
def startCaptureStream(request):
    stream_name = request.GET['stream_name']
    thread = threading.Thread(target=analyse_stream, args=(str(stream_name),))
    thread.start()
    return Response("ok!")

@api_view(['GET'])
def rtmpAuth(request):
    print(request.GET)
    username = request.GET.get('username')
    password = request.GET.get('password')
    app = request.GET.get('app')
    call = request.GET.get('call')
    stream_name = request.GET.get('name')
    # if username != password:
    #     return HttpResponse("no auth", status=403)
    # if app == 'live' and call == 'publish':
    #     thread = threading.Thread(target=start_resolve_stream, args=(str(stream_name),))
    #     thread.start()
    return HttpResponse("ok", status=200)

def rtmpPublishDone(request):
    app = request.GET['app']
    stream_name = request.GET.get('name')
    print(app, stream_name)
    return HttpResponse("ok", status=200)
