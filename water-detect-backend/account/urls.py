
from django.urls import path, include

from account import views


urlpatterns = [
    path('captcha', views.GenerateCaptchaView.as_view()),
    path('login', views.LoginView.as_view()),
    path('register', views.RegisterView.as_view()),
    path('selfInfo', views.GetSelfInfoView.as_view())

]
