import hashlib
import string
import random

from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

from account.forms import RegisterForm, LoginForm, ResetPasswordForm
from common_service.fileService import FileManager
from common_service.redisService import GetDefaultRedis
from database.models import User
from common import constants
from common_service import redisService
from common.customResponse import NewSuccessResponse, NewErrorResponse

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
            redisService.SetEmailCaptcha(email, verification_code)
            # if not DEBUG:
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
        elif type == 'reset_password':
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
            'user_id': user.id,
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


class ResetPasswordView(APIView):
    def post(self, request):
        jsonDict = json.loads(request.body)
        result = ResetPasswordForm(jsonDict)
        if not result.is_valid():
            err = result.errors
            if 'captchaHashCode' in err:
                del err['captchaHashCode']
            if len(err) == 0:
                return NewErrorResponse(500, constants.INTERNAL_ERROR)
            else:
                key = list(err.keys())[0]
                return NewErrorResponse(400, f'{str(key)}: {err[key][0]}')
        email = result.cleaned_data.get('email')
        user = User.objects.filter(email=email).first()
        if user is None:
            return NewErrorResponse(442, "邮箱未注册")
        user.password = getPasswordHash(result.cleaned_data.get('password'))
        user.save()
        return NewSuccessResponse({"id": user.id, "email": user.email})


class GetSelfInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return NewSuccessResponse({
            "id": request.user.id,
            "avatar": request.user.avatar,
            "username": request.user.username,
            "email": request.user.email,
            "sex": request.user.sex,
            "loi": request.user.last_login,
        })

class AvatarUploadView(APIView):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'msg': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        file_url = FileManager().saveAvatar(file)
        return Response({'msg': '上传成功', 'url': f"account/{file_url}"}, status=status.HTTP_200_OK)


class UserInfo(APIView):
    def get(self, request, userID):
        try:
            user = User.objects.get(id=userID)
            user.password = None
            return NewSuccessResponse({
                "id": request.user.id,
                "avatar": request.user.avatar,
                "username": request.user.username,
                "email": request.user.email,
                "sex": request.user.sex,
                "loi": request.user.last_login,
            })
        except User.DoesNotExist:
            return NewErrorResponse(404, '用户不存在')

    def post(self, request, userID, *args, **kwargs):
        try:
            user = User.objects.get(id=userID)
        except User.DoesNotExist:
            return NewErrorResponse(404, '用户不存在')

        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.password = getPasswordHash(data.get('password', user.password))
        user.sex = data.get('sex', user.sex)
        user.avatar = data.get('avatar', user.avatar)
        user.save()

        return NewSuccessResponse({'msg': '个人信息保存成功'})