import json
import logging
import os
import threading
import uuid

from django.core.cache import cache
from django.http import FileResponse, StreamingHttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from common import constants
from common.constants import UploadFileStatus
from common.customError import InternalServerError, ParamError
from common.db_model import FileType, FileStatus
from common.mqModels import AnalyseTask
from common.customResponse import NewSuccessResponse, NewErrorResponse
from common_service.fileService import FileManager
from database.models import FileInfo
from directory import utils
from directory.forms import GetFileListForm
from directory.serializers import FileInfoSerializer
from directory.service import mq
from waterDetect import settings

logger = logging.getLogger(__name__)
# Create your views here.
# class VideoView(APIView):
#     def post(self, request):
#         # 获取上传的文件
#         video_file = request.FILES.get('video')
#         if video_file:
#             fileID = FileManager().uploadVideo(video_file)
#             opUser = request.user
#             video = FileInfo.objects.createVideo(video_file, fileID, opUser)
#             return NewSuccessResponse({"fileID": video.id})
#         else:
#             return NewErrorResponse(400, "not file uploaded")
#
#     def get(self, request):
#         uid = request.GET.get('uid')
#         video = FileInfo.objects.get(file_uid=uid, user_id=request.user.id)
#         videoFile = FileManager().getVideo(video.file_uid)
#         response = Response(videoFile, content_type='directory/mp4')
#         response['Content-Disposition'] = f'attachment; filename={video.filename}'
#         return response


class UploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        file_name = request.data.get('fileName')
        file_md5 = request.data.get('fileMd5')
        chunk_index = request.data.get('chunkIndex')
        chunks = request.data.get('chunks')
        file_id = request.data.get('fileId')
        file_pid = request.data.get('filePid')

        if not all([file, file_name, file_md5, chunk_index, chunks, file_pid]):
            return NewErrorResponse(400, "Missing required fields")

        try:
            chunk_index = int(chunk_index)
            chunks = int(chunks)
            file_pid = int(file_pid)
        except ValueError:
            return NewErrorResponse(400, "chunkIndex and chunks must be integers")

        file_pid = FileInfo.objects.ResolveFolderID(request.user.id, file_pid)

        file_id, fileSize, fileType, done = FileManager().uploadVideoChunk(
            file=file,
            chunk_index=chunk_index,
            chunks=chunks,
            file_id=file_id,
            filename=file_name
        )
        status = UploadFileStatus.uploading.value
        if done:
            parentFile_path = FileInfo.objects.getFilePath(file_pid)
            file_name = FileInfo.objects.autoRename(file_pid, file_name, request.user.id)
            fileInfo = FileInfo.objects.create(
                file_pid=file_pid,
                file_uid=file_id,
                size=fileSize,
                file_path=parentFile_path + '/' + file_name,
                file_type=fileType,
                filename=file_name,
                user_id=request.user.id,
                file_status=FileStatus.Converting.value,
            )
            fileInfo.save()
            FileManager().CreateThumbnail(f'{settings.MEDIA_ROOT}/files/{fileInfo.UIDFilename()}', fileInfo.file_uid, fileInfo.file_type)
            threading.Thread(target=self.AsyncResolveFile, args=(fileInfo, request.user.id)).start()
            status = UploadFileStatus.upload_finish.value

        return NewSuccessResponse({
            "fileId": file_id,
            "status": status,
        })
    def AsyncResolveFile(self, fileInfo, userID):
        try:
            if fileInfo.file_type == FileType.Video.value:
                FileManager().cutFile4Video(fileInfo)
            fileInfo.file_status = FileStatus.Done.value
            fileInfo.save()
        except Exception as e:
            logger.error("AsyncResolveVideo", e)
            fileInfo.file_status = FileStatus.ConvertFailed.value
            fileInfo.save()
        mq.sendAnalyseTask(AnalyseTask(fileInfo.id, fileInfo.file_type, fileInfo.file_uid))


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
        FileInfo.objects.createFolder(int(pid), request.user.id)
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
        files = FileInfo.objects.filter(id__in=file_ids, user_id=request.user.id)
        for file in files:
            FileManager().DeleteFile(file)
        deleted_count, _ = files.delete()
        return NewSuccessResponse({"count": deleted_count})


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

class ThumbnailView(APIView):
    def get(self, request):
        fileID = request.GET.get('fileID')
        if fileID is None:
            raise ParamError("Missing fileID parameter")
        file = FileInfo.objects.get(id=fileID)
        file_path = FileManager().getThumbnailPath(file.file_uid)
        if not os.path.exists(file_path):
            raise InternalServerError
        thumbnail = open(file_path, 'rb')
        return FileResponse(thumbnail, content_type='image/jpeg')



class GetFileView(APIView):
    def get(self, request, fileID):
        needAnalysed = request.GET.get('analysed')
        path = ""
        if fileID[-3:] == ".ts":
            # 根据最右边的下划线分隔
            fileUID = fileID.rsplit('_', 1)[0]
            path = FileManager().GetTSPath(fileUID, fileID)
            file = open(path, 'rb')
            return FileResponse(file, content_type="video/MP2T")
        else:
            fileInfo = FileInfo.objects.get(id=fileID)
            fileUID = fileInfo.file_uid
            if needAnalysed is not None and needAnalysed == "true":
                fileUID = f"analysed_{fileInfo.file_uid}"
            if fileInfo.file_type == FileType.Video.value:
                path = FileManager().GetM3U8Path(fileUID)
                file = open(path, 'rb')
                return FileResponse(file)
            else:
                return NewErrorResponse(400, "todo file type")

class DownloadFileView(APIView):
    def get(self, request, fileID):
        if request.path.split('/')[-2] == "createDownload":
            fileInfo = FileInfo.objects.get(id=fileID)
            if fileInfo.file_type == FileType.Folder.value:
                return NewErrorResponse(400, "invalid file id")
            code = "download_" + uuid.uuid4().__str__()
            cache.set(code, fileID, constants.HOUR)
            return NewSuccessResponse({"code": code})
        elif request.path.split('/')[-2] == "download":
            fileID = cache.get(fileID)
            if fileID is None:
                return NewErrorResponse(400, "invalid code")
            fileInfo = FileInfo.objects.get(id=fileID)
            path = FileManager().GetFilePath(fileInfo.file_uid, fileInfo.file_type)
            file = open(path, 'rb')
            response = StreamingHttpResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename={fileInfo.filename}'
            return response


class FileInfoView(APIView):
    def get(self, request, fileID, pathType):
        userID, fileInfo = request.user.id, None
        if pathType == "id":
            fileInfo = FileInfo.objects.get(id=fileID, user_id=userID)
        elif pathType == "uid":
            fileInfo = FileInfo.objects.get(file_uid=fileID, user_id=userID)
        return NewSuccessResponse(FileInfoSerializer(fileInfo).data)
