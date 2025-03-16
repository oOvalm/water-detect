import json

from django.core.cache import cache

from common import constants


def SetEmailCaptcha(email, code):
    cache.set(f"email-captcha:{email}", code, constants.MINUTE*60)

def GetEmailCaptcha(email):
    return cache.get(f"email-captcha:{email}")

def UploadAnalyseProcess(fileUID, **kwargs):
    cache.set(f"upload-analyse-process:{fileUID}", kwargs, constants.MINUTE*60)

def GetAnalyseProcess(fileUID):
    return cache.get(f"upload-analyse-process:{fileUID}")
