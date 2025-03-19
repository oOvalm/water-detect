import base64
import http
import logging
import queue
import subprocess
import threading
import uuid

import cv2
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination

from common_service import redisService
from common_service.lock import RedisLock
from common_service.redisService import GetDefaultRedis
from database.models import StreamKeyInfo
from database.serializers import StreamKeyInfoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


from online_stream.service import rtmp_host, capture_streamNanalyse, GetStreamM3U8Path
from waterDetect import settings

log = logging.getLogger(__name__)

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
def rtmpPublish(request):
    print(request.GET)
    username = request.GET.get('username')
    password = request.GET.get('password')
    app = request.GET.get('app')
    call = request.GET.get('call')
    stream_name = request.GET.get('name')
    # todo: 鉴权

    if RedisLock.is_locked(GetDefaultRedis(), f"capture_ori_stream:{app}_{stream_name}"):
        return HttpResponse('stream has been started', status=403)
    if app == 'live' and call == 'publish':
        # 异步开启监听
        thread = threading.Thread(target=capture_streamNanalyse,
                         args=(app, stream_name, threading.Event(), queue.Queue()))
        thread.start()
    return HttpResponse("ok", status=200)

def rtmpPublishDone(request):
    app = request.GET.get('app')
    stream_name = request.GET.get('name')
    redisService.SetStreamDone(f"{app}_{stream_name}")
    return HttpResponse("ok", status=200)




@csrf_exempt
@api_view(['GET'])
def stream_proxy(request, app, stream_key):
    try:
        if not RedisLock.is_locked(GetDefaultRedis(), f"capture_ori_stream:{app}_{stream_key}"):
            return HttpResponse('stream not start', status=404)
        isAnalyse = request.GET.get('analyse')
        m3u8Path = GetStreamM3U8Path(app, stream_key, isAnalyse == 'true')
        if m3u8Path is None:
            return HttpResponse("analyse not start", status=404)
        return HttpResponse(m3u8Path, content_type='text/plain')
    except Exception as e:
        log.error(e)
        return HttpResponse(f"Error: {str(e)}", status=500)



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class StreamKeyInfoViewSet(viewsets.ModelViewSet):
    queryset = StreamKeyInfo.objects.all()
    serializer_class = StreamKeyInfoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['stream_name']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 只返回 user_id 等于当前请求用户 id 的记录
        return self.queryset.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        # 生成一个随机的 UUID 并转换为字符串
        stream_key = base64.b64encode(str(uuid.uuid4()).encode('utf-8')[:9]).decode('utf-8').replace('=', '')
        serializer.save(user_id=self.request.user.id, stream_key=stream_key)

    def perform_update(self, serializer):
        # 更新时只传入 stream_name 和 stream_description
        serializer.save()