from rest_framework.views import APIView

from common.customResponse import NewErrorResponse, NewSuccessResponse
from common.db_model import AnalyseFileType
from common_service import redis
from database.models import FileInfo


# Create your views here.
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
                "done": True,

            })
        analyseProcess = redis.GetAnalyseProcess(fileUID)
        analyseProcess['done'] = False
        return NewSuccessResponse(analyseProcess)
