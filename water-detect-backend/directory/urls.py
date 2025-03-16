from django.urls import path, include, re_path

from directory.views import FileListView, FolderListView, ThumbnailView, GetFileView, \
    DownloadFileView, FileInfoView, UploadView

urlpatterns = [
    # path('video', VideoView.as_view(), name='video'),
    path('fileList', FileListView.as_view(), name='FileList'),
    re_path(r'^FileInfo/(?P<pathType>uid|id)/(?P<fileID>\S+)$', FileInfoView.as_view(), name='FileInfo'),
    path('folderList', FolderListView.as_view(), name='FolderList'),
    path('upload', UploadView.as_view(), name='VideoV2'),
    path('thumbnail', ThumbnailView.as_view(), name='Thumbnail'),
    path('getFile/<str:fileID>', GetFileView.as_view(), name='getFile'),
    path('ts/getVideoInfo/<str:fileID>', GetFileView.as_view(), name='getVideoInfo'),
    path('createDownload/<str:fileID>', DownloadFileView.as_view(), name='downloadFile'),
    path('download/<str:fileID>', DownloadFileView.as_view(), name='downloadFile')
]