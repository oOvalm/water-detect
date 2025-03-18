import json

from django.core.cache import caches

from common import constants

def GetDefaultRedis():
    return caches['default'].client.get_client()

def SetEmailCaptcha(email, code):
    GetDefaultRedis().set(f"email-captcha:{email}", code, constants.MINUTE*60)

def GetEmailCaptcha(email):
    return GetDefaultRedis().get(f"email-captcha:{email}")

def UploadAnalyseProcess(fileUID, **kwargs):
    GetDefaultRedis().set(f"upload-analyse-process:{fileUID}", kwargs, constants.MINUTE*60)

def GetAnalyseProcess(fileUID):
    return GetDefaultRedis().get(f"upload-analyse-process:{fileUID}")
