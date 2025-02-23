import json

from captcha.models import CaptchaStore
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



# 验证验证码
def jarge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        try:
            # 获取根据hashkey获取数据库中的response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            if get_captcha.response == captchaStr.lower():  # 如果验证码匹配
                return True
        except:
            return False
    else:
        return False

