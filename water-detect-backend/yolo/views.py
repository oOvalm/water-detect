from enum import Enum

from rest_framework.views import APIView

from common.customResponse import NewErrorResponse, NewSuccessResponse
from common.db_model import AnalyseFileType
from common_service import redis
from database.models import FileInfo


# Create your views here.
class AnalyseStatus(Enum):
    NotStart = 1
    Analysing = 2
    Done = 3


class GetAnalyseProcess(APIView):
    def get(self, request, fileUID):
        userID = request.user.id
        fileInfo = FileInfo.objects.filter(file_uid=fileUID, user_id=userID).first()
        if fileInfo is None:
            return NewErrorResponse(400, "origin file not found")
        extra = fileInfo.fileExtra
        if extra.analyseType == AnalyseFileType.Analysed:
            return NewErrorResponse(400, "wrong file type")
        if extra.oppositeID != 0:
            return NewSuccessResponse({
                "fileUID": fileUID,
                "analyseStatus":AnalyseStatus.Done.value,
            })
        analyseProcess = redis.GetAnalyseProcess(fileUID)
        if analyseProcess is None:
            return NewSuccessResponse({
                "fileUID": fileUID,
                "analyseStatus":AnalyseStatus.NotStart.value,
            })
        analyseProcess['analyseStatus'] = AnalyseStatus.Analysing.value
        return NewSuccessResponse(analyseProcess)
