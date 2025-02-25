import json
import logging
import os

from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from common import constants
from common.customError import InternalServerError, ParamError
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
            raise ParamError()
        parentID = form.cleaned_data.get('filePid')
        searchFilename = form.cleaned_data.get('searchFilename')
        files = FileInfo.objects.filter(file_pid=parentID, user_id=request.user.id)
        if searchFilename is not None and searchFilename.strip() != '':
            files = files.filter(filename__contains=searchFilename)
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
    def post(self, request):
        body = json.loads(request.body)
        pid = body['filePid']
        FileInfo.objects.createFolder(pid, request.user.id)
        return NewSuccessResponse()

    def put(self, request):
        body = json.loads(request.body)
        action_type = body.get('type')
        file_id = body.get('id')
        file_pid = body.get('filePid')
        new_file_name = body.get('newFileName')

        if not action_type or not file_id:
            raise ParamError(msg="Missing required parameters: type or id")

        file = FileInfo.objects.get(id=file_id)
        if action_type == "rename":
            if not new_file_name:
                raise ParamError(msg="Missing newFileName for rename action")
            file.filename = new_file_name
            file.save()
        elif action_type == "move":
            if file_pid is None:
                raise ParamError(msg="Missing filePid for move action")
            file.file_pid = file_pid
            file.save()
        else:
            raise InternalServerError
        return NewSuccessResponse(FileInfoSerializer(file).data)


    def delete(self, request):
        file_ids_str = request.query_params.get('fileIDs')
        if not file_ids_str:
            raise ParamError("Missing fileIDs parameter")

        file_ids = [int(id) for id in file_ids_str.split(',') if id.strip().isdigit()]
        if not file_ids:
            raise ParamError("No valid file IDs provided")

        deleted_count, _ = FileInfo.objects.filter(id__in=file_ids, user_id=request.user.id).delete()
        return NewSuccessResponse({"count", deleted_count})


class FolderListView(APIView):
    def get(self, request):
        filePid = request.GET.get('filePid')
        excludeFileIDs = request.GET.get('excludeFileIDs')
        excludeFileIDs = excludeFileIDs.split(',') if excludeFileIDs else None
        if filePid is None:
            raise ParamError("Missing filePid parameter")
        folders = FileInfo.objects.filter(file_pid=filePid, user_id=request.user.id)
        if excludeFileIDs is not None:
            folders = folders.exclude(id__in=excludeFileIDs)
        return NewSuccessResponse(FileInfoSerializer(folders, many=True).data)

    def post(self, request):
        # 传入 newFolderPid和moveFileIDs, 将FileIDs移动到newFolderPid下
        body = json.loads(request.body)
        newFolderPid = body.get('newFolderPid')
        moveFileIDs = body.get('moveFileIDs')
        if not newFolderPid or not moveFileIDs:
            raise ParamError("Missing newFolderPid or moveFileIDs parameter")
        rows = FileInfo.objects.filter(id__in=moveFileIDs, user_id=request.user.id).update(file_pid=newFolderPid)
        return NewSuccessResponse({"count": rows})