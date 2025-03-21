from django.conf.urls.static import static
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from online_stream.views import StreamKeyInfoViewSet, rtmpPublish, rtmpPublishDone, stream_proxy
from waterDetect import settings

router = DefaultRouter()
router.register('', StreamKeyInfoViewSet)

urlpatterns = [
    path('rtmp_publish', rtmpPublish, name='rtmpAuth'),
    path('rtmp_publish_done', rtmpPublishDone, name='rtmpPublishDone'),
    re_path('proxy/(?P<app>live|analysed)/(?P<stream_id>\d+)', stream_proxy, name='stream_proxy'),
    path('streamkeyinfo/', include(router.urls))
] + static('hls/', document_root=f'{settings.MEDIA_ROOT}/hls/')


