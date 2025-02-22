import os

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from common import constants
from common.utils import NewSuccessResponse, NewErrorResponse
from directory.models import VideoType, FileInfo
from directory.service import fileManager
from waterDetect import settings


# Create your views here.
class VideoView(APIView):
    def post(self, request):
        # 获取上传的文件
        video_file = request.FILES.get('directory')
        if video_file:
            try:
                fileID = fileManager.uploadVideo(video_file)
                opUser = request.user
                video = FileInfo.objects.createVideo(video_file, fileID, opUser)
                return NewSuccessResponse({"fileID": video.id})
            except Exception as e:
                print(e)
                return NewErrorResponse(500, constants.INTERNAL_ERROR)
        else:
            return NewErrorResponse(500, "file not found")

    def get(self, request):
        id = request.GET.get('id')
        video = FileInfo.objects.get(id=id)
        videoFile = fileManager.getVideo(video.fileUID)
        response = Response(videoFile, content_type='directory/mp4')
        response['Content-Disposition'] = f'attachment; filename={video.filename}'
        return response

class FolderView(APIView):
    def get(self, request):
        fileID = request.GET.get('fileID')
