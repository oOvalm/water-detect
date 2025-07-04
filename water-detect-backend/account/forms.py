from django import forms

from database.models import User
from common_service import utils, redisService


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=128)
    password = forms.CharField(required=True)
    confirmPassword = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    emailCaptcha = forms.CharField(required=True)
    captcha = forms.CharField(required=True)
    captchaHashCode = forms.CharField(required=True)

    def clean(self):
        cleanedData = super().clean()
        password, confirmPassword, email = cleanedData.get('password'), cleanedData.get('confirmPassword'), cleanedData.get('email')
        emailCaptcha, captcha, captchaHashCode = cleanedData.get('emailCaptcha'), cleanedData.get('captcha'), cleanedData.get('captchaHashCode')
        if password != confirmPassword:
            self.add_error('confirmPassword', '密码不一致')
            return
        redisCaptcha = redisService.GetEmailCaptcha(email)
        if not redisCaptcha or redisCaptcha != emailCaptcha:
            self.add_error('emailCaptcha', '验证码错误')
            return
        if not utils.jarge_captcha(captcha, captchaHashCode):
            self.add_error('captcha', '图片验证码错误')
            return

    def ConvertToUser(self)-> User :
        user = User()
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        user.password = self.cleaned_data.get('password')
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)
    captcha = forms.CharField(required=True)
    captchaHashCode = forms.CharField(required=True)

    def clean(self):
        cleanedData = super().clean()
        # email, password = cleanedData.get('email'), cleanedData.get('password')
        captcha, captchaHashCode = cleanedData.get('captcha'), cleanedData.get('captchaHashCode')
        if not utils.jarge_captcha(captcha, captchaHashCode):
            self.add_error('captcha', '图片验证码错误')
            return

class ResetPasswordForm(forms.Form):
    email = forms.EmailField(required=True)
    emailCaptcha = forms.CharField(required=True)
    password = forms.CharField(required=True)
    confirmPassword = forms.CharField(required=True)
    captcha = forms.CharField(required=True)
    captchaHashCode = forms.CharField(required=True)
    def clean(self):
        cleanedData = super().clean()
        email, password, confirmPassword = cleanedData.get('email'), cleanedData.get('password'), cleanedData.get('confirmPassword')
        emailCaptcha, captcha, captchaHashCode = cleanedData.get('emailCaptcha'), cleanedData.get('captcha'), cleanedData.get('captchaHashCode')
        if password!= confirmPassword:
            self.add_error('confirmPassword', '密码不一致')
            return
        redisCaptcha = redisService.GetEmailCaptcha(email)
        if not redisCaptcha or redisCaptcha != emailCaptcha:
            self.add_error('emailCaptcha', '验证码错误')
            return
        if not utils.jarge_captcha(captcha, captchaHashCode):
            self.add_error('captcha', '图片验证码错误')
            return

