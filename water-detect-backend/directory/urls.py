from django.urls import path, include

from directory.views import VideoView, FileListView, FolderListView, VideoV2View, ThumbnailView

urlpatterns = [
    path('video', VideoView.as_view(), name='video'),
    path('fileList', FileListView.as_view(), name='FileList'),
    path('folderList', FolderListView.as_view(), name='FolderList'),
    path('video/v2', VideoV2View.as_view(), name='VideoV2'),
    path('thumbnail', ThumbnailView.as_view(), name='Thumbnail')
]