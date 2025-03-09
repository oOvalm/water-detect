import email
import hashlib
import logging
import string
from logging import Logger
import random

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import View
from rest_framework import permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

from account.forms import RegisterForm, LoginForm
from account.models import User
from account.serializers import UserSerializer
from common import constants, redis
from common.customResponse import BaseResponse, NewSuccessResponse, NewErrorResponse

import json

from waterDetect.settings import EMAIL_HOST_USER, DEBUG

PASSWORD_SALT = "salt==w=e"


def getPasswordHash(password):
    return hashlib.sha256((PASSWORD_SALT + password).encode('utf-8')).hexdigest()


class GenerateCaptchaView(APIView):
    """
    获取验证码相关
    """

    def get(self, request):
        hashkey = CaptchaStore.generate_key()  # 验证码答案
        image_url = captcha_image_url(hashkey)  # 验证码地址
        captcha = {'hashkey': hashkey, 'image_url': image_url}
        return NewSuccessResponse(captcha)

    """
    发送邮箱验证码
    """
    def post(self, request):
        try:
            # 解析请求中的 JSON 数据
            data = json.loads(request.body)
            email = data.get('email')
            type = data.get('type')
            if not email:
                return NewErrorResponse(400, '地址不能为空')
            valid, reason = self.is_valid_email(email, type)
            if not valid:
                return NewErrorResponse(400, reason)

            # 生成 6 位验证码
            verification_code = ''.join(random.choices(string.digits, k=6))

            # 邮件主题和内容
            subject = '验证码邮件'
            message = f'你的验证码是：{verification_code}'
            from_email = EMAIL_HOST_USER
            recipient_list = [email]
            # 发送邮件
            print(f"send email to {email}, {verification_code}")
            redis.SetEmailCaptcha(email, verification_code)
            if not DEBUG:
                send_mail(subject, message, from_email, recipient_list)
            return NewSuccessResponse()
        except json.JSONDecodeError:
            return NewErrorResponse(400, '无效json')

    def is_valid_email(self, email, type):
        if type == 'register':
            if User.objects.filter(email=email).first() is not None:
                return False, "该邮箱已注册"
            else:
                return True, ""
        else:
            return False, constants.INTERNAL_ERROR

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        result = LoginForm(json.loads(request.body))
        if not result.is_valid():
            err = result.errors
            if 'captchaHashCode' in err:
                del err['captchaHashCode']
            if len(err) == 0:
                return NewErrorResponse(500, constants.INTERNAL_ERROR)
            else:
                key = list(err.keys())[0]
                return NewErrorResponse(400, f'{str(key)}: {err[key][0]}')
        email, password = result.cleaned_data.get('email'), result.cleaned_data.get('password')
        user = User.objects.filter(email=email).first()
        if not user:
            return NewErrorResponse(400, "用户不存在")
        hashPsw = getPasswordHash(password)
        if hashPsw != user.password:
            return NewErrorResponse(400, "密码错误")

        refresh = RefreshToken.for_user(user)
        return NewSuccessResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class RegisterView(APIView):
    def post(self, request):
        jsonDict = json.loads(request.body)
        result = RegisterForm(jsonDict)
        if not result.is_valid():
            err = result.errors
            if 'captchaHashCode' in err:
                del err['captchaHashCode']
            if len(err) == 0:
                return NewErrorResponse(500, constants.INTERNAL_ERROR)
            else:
                key = list(err.keys())[0]
                return NewErrorResponse(400, f'{str(key)}: {err[key][0]}')
        newUser = result.ConvertToUser()
        user = User.objects.filter(email=newUser.email).first()
        if user is not None:
            return NewErrorResponse(441, "该邮箱已经注册")
        else:
            newUser.password = getPasswordHash(newUser.password)
            newUser.save()
            print(newUser.__dict__)
            return NewSuccessResponse({"id": newUser.id, "email": newUser.email})


class GetSelfInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return NewSuccessResponse({
            "username": request.user.username,
            "email": request.user.email,
            "password": request.user.password,
            "loi": request.user.last_login,
        })
