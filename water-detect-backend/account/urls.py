from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account import views
from account.views import AvatarUploadView, UserInfo
from waterDetect import settings

urlpatterns = [
    path('captcha', views.GenerateCaptchaView.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view()),
    path('resetPwd', views.ResetPasswordView.as_view()),
    path('selfInfo', views.GetSelfInfoView.as_view()),
    path('avatar', AvatarUploadView.as_view(), name='avatar-upload'),
    path('<int:userID>', UserInfo.as_view(), name='user-info'),


] + static('avatar/', document_root=f'{settings.MEDIA_ROOT}/avatar/')

