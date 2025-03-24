import logging
import random
import string

from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework.views import APIView

from common.constants import INTERNAL_ERROR
from common.customResponse import NewErrorResponse, NewSuccessResponse
from common.db_model import ShareValidTypeEnums
from share_file.models import FileShare
from share_file.serializers import FileShareSerializer

log = logging.getLogger(__name__)

class ShareFile(APIView):
    def post(self, request):
        body = request.data
        fileID = body.get('id')
        valid_type = body.get('valid_type')
        code = body.get('code')
        type_enums = ShareValidTypeEnums.get_by_type(valid_type)
        if type_enums is None:
            return NewErrorResponse(400, "not support valid type")
        expire_time = timezone.now()
        if type_enums != ShareValidTypeEnums.FOREVER:
            expire_time = timezone.now() + timezone.timedelta(days=type_enums.days)

        cur_date = timezone.now()
        share_time = cur_date
        if not code:
            code = ''.join(random.choices(string.digits, k=5))
        share_code = ''.join(random.choices(string.ascii_letters, k=20))
        fileShare = FileShare(file_id=fileID,
                             user_id=request.user.id,
                             valid_type=valid_type,
                             expire_time=expire_time,
                             share_time=share_time,
                             code=code,
                             share_code=share_code)
        fileShare.save()
        return NewSuccessResponse(FileShareSerializer(fileShare).data)


class LoadShareListView(APIView):
    def get(self, request):
        page_no = int(request.query_params.get('pageNo', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        file_shares = FileShare.objects.filter(user_id=request.user.id).order_by('-share_time')
        paginator = Paginator(file_shares, page_size)
        page_obj = paginator.get_page(page_no)
        serializer = FileShareSerializer(page_obj, many=True)
        data = {
            'list': serializer.data,
            'pageNo': page_no,
            'pageSize': page_size,
            'totalCount': paginator.count
        }
        return NewSuccessResponse(data)


class CancelShareView(APIView):
    def post(self, request):
        try:
            share_ids = request.data.get('shareIds', '').split(',')
            FileShare.objects.filter(share_code__in=share_ids).delete()
            return NewSuccessResponse()
        except Exception as e:
            log.error(e)
            return NewErrorResponse(500, INTERNAL_ERROR)


