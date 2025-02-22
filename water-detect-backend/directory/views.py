import json
import logging
import os

from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from common import constants
from common.customError import ParamError
from common.utils import NewSuccessResponse, NewErrorResponse
from directory.forms import GetFileListForm
from directory.models import VideoType, FileInfo
from directory.serializers import FileInfoSerializer
from directory.service import fileManager
from waterDetect import settings

logger = logging.getLogger(__name__)
# Create your views here.
class VideoView(APIView):
    def post(self, request):
        # 获取上传的文件
        video_file = request.FILES.get('video')
        if video_file:
            fileID = fileManager.uploadVideo(video_file)
            opUser = request.user
            video = FileInfo.objects.createVideo(video_file, fileID, opUser)
            return NewSuccessResponse({"fileID": video.id})
        else:
            return NewErrorResponse(400, "not file uploaded")

    def get(self, request):
        id = request.GET.get('id')
        video = FileInfo.objects.get(id=id)
        videoFile = fileManager.getVideo(video.fileUID)
        response = Response(videoFile, content_type='directory/mp4')
        response['Content-Disposition'] = f'attachment; filename={video.filename}'
        return response


class FilePagination(PageNumberPagination):
    page_size_query_param = 'pageSize'
    page_query_param = 'pageNo'

    def get_paginated_response(self, data):
        return NewSuccessResponse({
            'totalCount': self.page.paginator.count,
            'pageSize': self.get_page_size(self.request),
            'pageNo': self.page.number,
            'pageTotal': self.page.paginator.num_pages,
            'list': data
        })

class FileListView(APIView):
    pagination_class = FilePagination
    def get(self, request):
        form = GetFileListForm(request.GET)
        if not form.is_valid():
            logger.error(form.errors)
            raise ParamError
        parentID = form.cleaned_data.get('filePid')
        files = FileInfo.objects.filter(file_pid=parentID)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(files, request)
        if page is not None:
            serializer = FileInfoSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        return NewSuccessResponse({
            'totalCount': 0,
            'pageSize': 0,
            'pageNo': 1,
            'pageTotal': 0,
            'list': []
        })
    def put(self, request):
        body = json.loads(request.body)
        pid = body['filePid']
        FileInfo.objects.createFolder(pid, request.user.id)
        return NewSuccessResponse()