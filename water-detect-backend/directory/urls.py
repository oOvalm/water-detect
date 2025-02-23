from django.urls import path, include

from directory.views import VideoView, FileListView, FolderListView

urlpatterns = [
    path('video', VideoView.as_view(), name='video'),
    path('fileList', FileListView.as_view(), name='FileList'),
    path('folderList', FolderListView.as_view(), name='FolderList'),
]