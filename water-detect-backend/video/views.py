import os

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from common import constants
from common.utils import NewSuccessResponse, NewErrorResponse
from waterDetect import settings


# Create your views here.
class VideoView(APIView):
    def post(self, request):
        # 获取上传的文件
        video_file = request.FILES.get('video')
        if video_file:
            try:
                # 指定文件保存的目录
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
                # 确保目录存在
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                # 生成文件保存的完整路径
                file_path = os.path.join(upload_dir, video_file.name)
                # 保存文件
                with open(file_path, 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)
                return NewSuccessResponse()
            except Exception as e:
                print(e)
                return NewErrorResponse(500, constants.INTERNAL_ERROR)
        else:
            return NewErrorResponse(500, "file not found")
