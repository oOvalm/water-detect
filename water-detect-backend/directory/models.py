from enum import Enum

from django.db import models

class FileInfoManager(models.Manager):
    def createVideo(self, file, fileID, user):
        file = FileInfo(
            size=file
        )


# Create your models here.
class FileInfo(models.Model):
    file_pid = models.IntegerField(default=-1, db_comment='父目录id')
    size = models.BigIntegerField(default=0, db_comment='文件大小')
    file_path = models.CharField(default='', max_length=4096, db_comment='文件路径')
    folder_type = models.SmallIntegerField(default=0, db_comment='1:文件, 2:目录')
    file_type = models.SmallIntegerField(default=0, db_comment='1:图片, 2:视频')
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

