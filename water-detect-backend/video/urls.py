from django.urls import path, include

from video.views import VideoView

urlpatterns = [
    path('', VideoView.as_view(), name='video'),
]