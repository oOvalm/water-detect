import json
import logging
from enum import Enum

from rest_framework.views import APIView

from common.constants import INTERNAL_ERROR
from common.customResponse import NewErrorResponse, NewSuccessResponse
from common.db_model import AnalyseFileType
from common_service import redisService
from database.models import FileInfo

log = logging.getLogger(__name__)
class AnalyseStatus(Enum):
    NotStart = 1
    Analysing = 2
    Done = 3
    Waiting = 4


class GetAnalyseProcess(APIView):
    def get(self, request, fileUID):
        try:
            userID = request.user.id
            analyseProcess = redisService.GetAnalyseProcess(fileUID)
            if analyseProcess is not None:
                analyseProcess['analyseStatus'] = AnalyseStatus.Analysing.value if analyseProcess['finished'] > 0 else AnalyseStatus.Waiting.value
                return NewSuccessResponse(analyseProcess)

            fileInfo = FileInfo.objects.filter(file_uid=fileUID, user_id=userID).first()
            if fileInfo is None:
                return NewErrorResponse(400, "origin file not found")
            extra = fileInfo.GetAnalyseInfo()
            if extra is None:
                return NewSuccessResponse({
                    "fileUID": fileUID,
                    "analyseStatus": AnalyseStatus.NotStart.value,
                })
            elif extra.is_analysed:
                return NewErrorResponse(400, "wrong file type")
            else:
                return NewSuccessResponse({
                    "fileUID": fileUID,
                    "analyseStatus":AnalyseStatus.Done.value,
                })
        except Exception as e:
            log.error(e)
            return NewErrorResponse(500, INTERNAL_ERROR)
