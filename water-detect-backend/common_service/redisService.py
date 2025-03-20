import json

from django.core.cache import caches

from common import constants

def GetDefaultRedis():
    return caches['default'].client.get_client()

def SetEmailCaptcha(email, code):
    GetDefaultRedis().set(f"email-captcha:{email}", code, constants.MINUTE*60)

def GetEmailCaptcha(email):
    return str(GetDefaultRedis().get(f"email-captcha:{email}").decode())

def UploadAnalyseProcess(fileUID, **kwargs):
    # 转成字符串
    parsed = json.dumps(kwargs)
    GetDefaultRedis().set(f"upload-analyse-process:{fileUID}", parsed, constants.MINUTE*60)

def GetAnalyseProcess(fileUID):
    return json.loads(GetDefaultRedis().get(f"upload-analyse-process:{fileUID}"))

def SetStreamDone(streamKey):
    GetDefaultRedis().set(f"stream-done:{streamKey}", "true", constants.DAY)
def GetStreamDone(streamKey):
    return GetDefaultRedis().get(f"stream-done:{streamKey}")
def DoneStreamDone(streamKey):
    GetDefaultRedis().delete(f"stream-done:{streamKey}")

