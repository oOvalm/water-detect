import json

from rest_framework import serializers
from rest_framework.response import Response


class BaseResponse(object):
    def __init__(self):
        self.code = 0
        self.data = None
        self.msg = None

    @property
    def dict(self):
        return self.__dict__

    def dump(self):
        return json.dumps(self.dict)
class BaseResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    msg = serializers.CharField()
    data = serializers.JSONField()

def NewSuccessResponse(data=None):
    resp = BaseResponse()
    resp.data = data
    resp.msg = "ok"
    return Response(BaseResponseSerializer(resp).data)


def NewErrorResponse(code: int, msg: str):
    resp = BaseResponse()
    resp.code = code
    resp.msg = msg
    return Response(BaseResponseSerializer(resp).data)


