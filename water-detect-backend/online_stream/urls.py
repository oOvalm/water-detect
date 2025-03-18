from django.urls import path
from .views import rtmpAuth, rtmpPublishDone, startCaptureStream

urlpatterns = [
    path('rtmp_auth', rtmpAuth, name='rtmpAuth'),
    path('publish_done', rtmpPublishDone, name='rtmpPublishDone'),
    path('start_capture_stream', startCaptureStream, name='startCaptureStream')
]