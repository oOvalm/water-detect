import uuid

from django.utils import timezone
from rest_framework.views import APIView

from common.customResponse import NewSuccessResponse, NewErrorResponse
from common.db_model import ShareValidTypeEnums, FileType
from common_service.fileInfoService import GetAllFileInfoInFolders
from common_service.fileService import FileManager
from database.models import FileInfo, User
from database.serializers import FileInfoSerializer
from directory.views import FilePagination
from share_file.models import FileShare
from share_file.serializers import FileShareSerializer

SESSION_SHARE_KEY = "session_share_key_"
def get_session_share_from_session(session, share_id):
    return session.get(SESSION_SHARE_KEY + share_id)

def set_session_share_from_session(session, share_id, value):
    session[SESSION_SHARE_KEY + share_id] = value

def get_share_info_common(share_code):
    try:
        share = FileShare.objects.get(share_code=share_code)
        if share.valid_type != ShareValidTypeEnums.FOREVER.type and share.expire_time and timezone.now() > share.expire_time:
            raise ValueError("expired")
        share_info_vo = {
            "file_id": share.file_id,
            "user_id": share.user_id,
            "share_code": share.share_code,
            "valid_type": share.valid_type,
            "expire_time": share.expire_time,
            "share_time": share.share_time,
            "show_count": share.show_count
        }
        file_info = FileInfo.objects.get(id=share.file_id, user_id=share.user_id)
        share_info_vo['filename'] = file_info.filename
        user = User.objects.get(id=share.user_id)
        share_info_vo['username'] = user.username
        share_info_vo['avatar'] = user.avatar
        share_info_vo['user_id'] = user.id
        return share_info_vo
    except (FileShare.DoesNotExist, FileInfo.DoesNotExist, User.DoesNotExist):
        raise ValueError("record not found")




class GetShareLoginInfoView(APIView):
    def get(self, request):
        share_code = request.GET.get('shareId')
        if not share_code:
            raise ValueError('shareId is required')
        session_share_dto = get_session_share_from_session(request.session, share_code)
        if not session_share_dto:
            return NewSuccessResponse(None).to_response()
        fileShare = FileShare.objects.get(share_code=share_code)
        return NewSuccessResponse(FileShareSerializer(fileShare).data)


class GetShareInfoView(APIView):
    def get(self, request):
        share_code = request.query_params.get('shareId')
        if not share_code:
            raise ValueError('shareId is required')
        return NewSuccessResponse(get_share_info_common(share_code))


class CheckShareCodeView(APIView):
    def get(self, request):
        share_code = request.query_params.get('shareId')
        code = request.query_params.get('code')
        if not share_code or not code:
            return NewErrorResponse(400, 'shareId and code are required')
        try:
            share = FileShare.objects.get(share_code=share_code)
            if share.valid_type != ShareValidTypeEnums.FOREVER.type and share.expire_time and timezone.now() > share.expire_time:
                return NewErrorResponse(900, 'share has been expired')
            if share.code != code:
                return NewErrorResponse(400, 'code error')
            share.show_count += 1
            share.save()
            share_dto = {
                'id': share.id,
                'share_user_id': share.user_id,
                'file_id': share.file_id,
                'expire_time': share.expire_time
            }
            set_session_share_from_session(request.session, share_code, share_dto)
            return NewSuccessResponse()
        except FileShare.DoesNotExist:
            return NewErrorResponse(400, 'share does not exist')


class LoadFileListView(APIView):
    pagination_class = FilePagination
    def get(self, request):
        share_code = request.query_params.get('shareId')
        file_pid = request.query_params.get('filePid')
        if not share_code:
            raise ValueError('shareId is required')
        session_share_dto = get_session_share_from_session(request.session, share_code)
        query = {
            'user_id': session_share_dto['share_user_id'],
        }
        if file_pid and file_pid != "0" and file_pid!= "-1":
            query['file_pid'] = file_pid
        else:
            query['id'] = session_share_dto['file_id']
        files = FileInfo.objects.filter(**query).order_by('update_time')
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


class SaveShareView(APIView):
    def post(self, request):
        share_code = request.data.get('shareId')
        file_ids = request.data.get('shareFileIds')
        file_pid = request.data.get('filePid')
        
        if not all([share_code, file_ids, file_pid]):
            return NewErrorResponse(400, '参数不完整')
        file_pid = int(file_pid)
        try:
            share = FileShare.objects.get(share_code=share_code)
            if share.valid_type != ShareValidTypeEnums.FOREVER.type and share.expire_time and timezone.now() > share.expire_time:
                return NewErrorResponse(900, '分享已过期')

            files = FileInfo.objects.filter(id__in=file_ids, user_id=share.user_id)
            if file_pid != -1:
                _ = FileInfo.objects.get(id=file_pid, user_id=request.user.id)

            folder_files = []
            non_folder_files = []
            for file in files:
                if file.file_type == FileType.Folder.value:
                    folder_files.append(file)
                else:
                    non_folder_files.append(file)
            allFilesNeedCopy = non_folder_files + GetAllFileInfoInFolders([file.id for file in folder_files])

            folderMapping = {}

            # 按照BFS序转存
            for file in allFilesNeedCopy:
                new_file_uid = None
                if file.file_type != FileType.Folder.value:
                    new_file_uid = FileManager().copyFile(file)
                new_file_pid = file_pid if file.id not in folderMapping else folderMapping[file.id]
                target_folder_path = FileInfo.objects.getFilePath(new_file_pid)
                new_file = FileInfo.objects.create(
                    file_pid=new_file_pid,
                    file_uid=new_file_uid,
                    user_id=request.user.id,
                    size=file.size,
                    file_path=target_folder_path + '/' + file.filename,
                    file_type=file.file_type,
                    file_status=file.file_status,
                    filename=file.filename,
                    folder_type=file.folder_type,
                )
                if file.file_type == FileType.Folder.value:
                    folderMapping[file.id] = new_file.id

            return NewSuccessResponse()
            
        except FileShare.DoesNotExist:
            return NewErrorResponse(400, '分享不存在')
        except FileInfo.DoesNotExist:
            return NewErrorResponse(400, '文件或目标文件夹不存在')
        except Exception as e:
            return NewErrorResponse(500, str(e))

