from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from waterDetect import settings
from .views import rtmpPublish, rtmpPublishDone, startCaptureStream, StreamKeyInfoViewSet, stream_proxy

router = DefaultRouter()
router.register('', StreamKeyInfoViewSet)

urlpatterns = [
    path('rtmp_publish', rtmpPublish, name='rtmpAuth'),
    path('rtmp_publish_done', rtmpPublishDone, name='rtmpPublishDone'),
    path('publish_done', rtmpPublishDone, name='rtmpPublishDone'),
    path('start_capture_stream', startCaptureStream, name='startCaptureStream'),
    re_path('^proxy/(?P<app>live|analysed)/(?P<stream_key>\S+)', stream_proxy, name='stream_proxy'),
    path('streamkeyinfo/', include(router.urls))
] + static('hls/', document_root=f'{settings.MEDIA_ROOT}/hls/')


