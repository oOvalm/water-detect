from django.urls import path

from share_file.shareView import GetShareLoginInfoView, GetShareInfoView, CheckShareCodeView, LoadFileListView, \
    SaveShareView
from share_file.views import ShareFile, LoadShareListView, CancelShareView

urlpatterns = [
    path('shareFile', ShareFile.as_view()),
    path('loadShareList', LoadShareListView.as_view(), name='load-share-list'),
    path('cancelShare', CancelShareView.as_view(), name='cancel-share'),

    path('web/getShareLoginInfo', GetShareLoginInfoView.as_view(), name='get_share_login_info'),
    path('web/getShareInfo', GetShareInfoView.as_view(), name='get_share_info'),
    path('web/checkShareCode', CheckShareCodeView.as_view(), name='check_share_code'),
    path('web/loadFileList', LoadFileListView.as_view(), name='load_file_list'),
    path('web/saveShare', SaveShareView.as_view(), name='save_share'),

]
