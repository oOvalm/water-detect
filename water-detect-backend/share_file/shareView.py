from django.utils import timezone
from rest_framework.views import APIView

from common.customResponse import NewSuccessResponse, NewErrorResponse
from common.db_model import ShareValidTypeEnums
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
        if file_pid and file_pid != "0":
            query['file_pid'] = file_pid
        else:
            query['id'] = session_share_dto['file_id']
        files = FileInfo.objects.filter(**query).order_by('update_time')
        # 这里可以添加分页逻辑
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
