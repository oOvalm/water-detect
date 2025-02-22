import re
from enum import Enum

from django.core.files import File
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models

import account.models


class FileInfoManager(models.Manager):
    def createVideo(self, file:File, fileID: str, user: account.models.User):
        fileinfo = FileInfo(
            size = file.size,
            file_path='/',
            folder_type=1,
            file_type=2,
            filename=file.name,
            user_id=user.id,
            # thumbnail=// todo
        )
        fileinfo.save()
        return fileinfo
    def createFolder(self, pid: int, userID: int):
        files = super().filter(user_id=userID, file_pid=pid)
        parentPath = ""
        if pid != -1:
            parentPath = super().get(id=pid).file_path
        mp = {}
        for file in files:
            if re.match(r'^新建文件夹(\(\d+\)|)$', file.filename):
                mp[file.filename] = 1
        id = 1
        newFilename = f"新建文件夹"
        while newFilename in mp:
            newFilename = f"新建文件夹({id})"
            id += 1
        fileinfo = FileInfo(file_pid = pid, user_id=userID,
                            filename=newFilename, file_path=f"{parentPath}/{newFilename}",
                            file_type=1)
        fileinfo.save()
        return fileinfo



# Create your models here.
class FileInfo(models.Model):
    file_pid = models.IntegerField(default=-1, db_comment='父目录id')
    size = models.BigIntegerField(default=0, db_comment='文件大小')
    file_path = models.CharField(default='', max_length=4096, db_comment='文件路径')
    file_type = models.SmallIntegerField(default=0, db_comment='1:目录 2:图片 3:视频')
    filename = models.CharField(max_length=4096, db_comment='用户上传时的文件名')
    user_id = models.IntegerField(db_comment='userID')
    thumbnail = models.BinaryField(null=True, db_comment='thumbnail')
    extra = models.BinaryField(null=True, db_comment='extra')
    create_time = models.DateTimeField(auto_now_add=True,null=False)
    update_time = models.DateTimeField(auto_now=True,null=False)

    objects = FileInfoManager()

    # status
    # recovery_time
    # del_flag

class FileExtra():
    pass

class VideoType(Enum):
    Raw = 1
    Analysed = 2

