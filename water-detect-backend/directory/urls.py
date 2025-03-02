from django.urls import path, include

from directory.views import VideoView, FileListView, FolderListView, VideoV2View, ThumbnailView, GetFileView, \
    DownloadFileView

urlpatterns = [
    path('video', VideoView.as_view(), name='video'),
    path('fileList', FileListView.as_view(), name='FileList'),
    path('folderList', FolderListView.as_view(), name='FolderList'),
    path('video/v2', VideoV2View.as_view(), name='VideoV2'),
    path('thumbnail', ThumbnailView.as_view(), name='Thumbnail'),
    path('getFile/<str:fileID>', GetFileView.as_view(), name='getFile'),
    path('ts/getVideoInfo/<str:fileID>', GetFileView.as_view(), name='getVideoInfo'),
    path('createDownload/<str:fileID>', DownloadFileView.as_view(), name='downloadFile'),
    path('download/<str:fileID>', DownloadFileView.as_view(), name='downloadFile')
]