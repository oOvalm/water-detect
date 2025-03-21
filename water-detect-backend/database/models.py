from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

import json
import re
from enum import Enum

from django.db import models

from common.db_model import FileExtra, SystemFolder, AnalyseFileType, FileType


# Create your models here.

class UserManager(BaseUserManager):
    """
    user 额外的crud操作
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True,null=False)
    email = models.EmailField(null=False,default="",unique=True)
    password = models.CharField(null=False,default="",max_length=1024)
    username = models.CharField(max_length=100,null=False)
    sex = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1,null=False)
    avatar = models.CharField(max_length=1024,null=True)
    create_time = models.DateTimeField(auto_now_add=True,null=False)
    update_time = models.DateTimeField(auto_now=True,null=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'water_detect_user'

class FileInfoManager(models.Manager):
    def createVideo(self, file_pid: int, filename: str, fileSize: int, fileID: str, user: User):
        fileinfo = FileInfo(
            size = fileSize,
            file_pid = file_pid,
            folder_type=1,
            file_type=FileType.Video.value,
            filename=filename,
            user_id=user.id,
            file_uid = fileID,
            # thumbnail=// todo
        )
        fileinfo.save()
        return fileinfo
    def createAnalysedFile(self, oriFileID, analysedUID, fileSize=0):
        oriFile = super().get(id=oriFileID)
        newFilename = oriFile.filename.rsplit('.', 1)[0] + '.jpg'
        analysedFileInfo = FileInfo(
            file_status=0,
            file_pid=oriFile.file_pid,
            user_id = oriFile.user_id,
            is_analysed=True,
            size = fileSize,
            file_type = oriFile.file_type,
            filename = f"analysed_{newFilename}",
            file_uid = analysedUID,
            extra = json.dumps(FileExtra(analyseType=AnalyseFileType.Analysed.value, oppositeID=oriFileID).__json__()).encode('utf-8'),
        )
        analysedFileInfo.save()
        oriFile.extra = json.dumps(FileExtra(analyseType=AnalyseFileType.Origin.value, oppositeID=analysedFileInfo.id).__json__()).encode('utf-8')
        oriFile.save()

    def createStreamFile(self, filename: str,  fileUID: str, userID,fileSize=0, isAnalysed=False):
        """
        创建流回放的fileInfo，需要自己回填extra
        """
        streamFolder = super().filter(user_id=userID, file_pid=-1, folder_type=SystemFolder.StreamReplayFolder.value).first()
        if not streamFolder:
            streamFolder = self.createFolder(SystemFolder.Root.value, userID, "直播回放")
            streamFolder.folder_type = SystemFolder.StreamReplayFolder.value
            streamFolder.save()
        fileinfo = FileInfo(
            size = fileSize,
            file_pid = streamFolder.id,
            file_type=FileType.Video.value,
            filename=filename,
            user_id=userID,
            file_uid = fileUID,
            is_analysed=isAnalysed,
        )
        fileinfo.save()
        return fileinfo

    def createFolder(self, pid: int, userID: int, folderName="新建文件夹"):
        files = super().filter(user_id=userID, file_pid=pid)
        parentPath = ""
        if pid != -1:
            parentPath = super().get(id=pid).file_path
        newFilename = self.autoRename(pid, folderName, userID)
        fileinfo = FileInfo(file_pid = pid, user_id=userID,
                            filename=newFilename, file_path=f"{parentPath}/{newFilename}",
                            file_type=1)
        fileinfo.save()
        return fileinfo
    def getFilePath(self, fileID: int):
        if fileID == -1:
            return ""
        file = super().get(id=fileID)
        return file.file_path

    def autoRename(self, filePID: int, filename: str, userID: int):
        cnt = super().filter(file_pid=filePID, filename=filename, user_id=userID).count()
        if cnt == 0:
            return filename
        id = 1
        parts = filename.rsplit('.', 1)
        if len(parts) > 1:
            prefix, suffix = parts[0], parts[1]
            while cnt > 0:
                # 按照最后一个点分割
                filename = f"{prefix}({id}).{suffix}"
                cnt = super().filter(file_pid=filePID, filename=filename, user_id=userID).count()
                id += 1
        else:
            while cnt > 0:
                filename = f"{filename}({id})"
                cnt = super().filter(file_pid=filePID, filename=filename, user_id=userID).count()
                id += 1
        return filename

    def ResolveFolderID(self, userID: int, folderID: int):
        if folderID == SystemFolder.OnlineAnalyseFolder.value:
            analyseFolder = super().filter(user_id=userID, folder_type=SystemFolder.OnlineAnalyseFolder.value)
            if analyseFolder.count() == 0:
                analyseFolder = self.createFolder(SystemFolder.Root.value, userID)
                analyseFolder.folder_type = SystemFolder.OnlineAnalyseFolder.value
                analyseFolder.filename = self.autoRename(SystemFolder.Root.value, "在线分析文件夹", userID)
                analyseFolder.save()
            else:
                analyseFolder = analyseFolder[0]
            return analyseFolder.id
        return folderID



# Create your models here.



class FileInfo(models.Model):
    file_pid = models.IntegerField(default=-1, db_comment='父目录id')
    file_uid = models.CharField(null=True, max_length=4096, db_comment='文件唯一标识')
    size = models.BigIntegerField(default=0, db_comment='文件大小')
    file_path = models.CharField(default='', max_length=4096, db_comment='文件路径')
    file_type = models.SmallIntegerField(default=0, db_comment='1:目录 2:图片 3:视频')
    is_analysed = models.BooleanField(default=False, db_comment='是否分析过')
    file_status = models.SmallIntegerField(default=1, db_comment='0:正常 1:解析中 2:解析失败')
    filename = models.CharField(max_length=4096, db_comment='用户上传时的文件名')
    folder_type = models.SmallIntegerField(default=0, db_comment='0:普通文件夹 1:根文件夹 2:分析文件夹')
    user_id = models.IntegerField(db_comment='userID')
    extra = models.BinaryField(null=True, db_comment='extra')
    create_time = models.DateTimeField(auto_now_add=True,null=False)
    update_time = models.DateTimeField(auto_now=True,null=False)

    objects = FileInfoManager()

    class Meta:
        db_table = 'water_detect_file_info'

    def UIDFilename(self):
        return f"{self.file_uid}.{self.filename.split('.')[-1]}"




class StreamKeyInfo(models.Model):
    stream_name = models.CharField(max_length=1024, db_comment='流名称')
    stream_description = models.CharField(null=True, max_length=4096, db_comment='流描述')
    stream_key = models.CharField(null=True, max_length=1024, db_comment='流唯一标识')
    user_id = models.IntegerField(db_comment='userID')
    create_time = models.DateTimeField(auto_now_add=True, null=False)
    update_time = models.DateTimeField(auto_now=True, null=False)
    auth_type = models.SmallIntegerField(default=0, null=False, db_comment='1:公开 2:指定范围 3:仅自己')
    auth_user_emails = models.CharField(max_length=4096, null=True, db_comment='允许获取流的ID列表')
    class Meta:
        db_table = 'water_detect_stream_info'

    def getAuthUserEmails(self):
        if self.auth_user_emails is None:
            return []
        return self.auth_user_emails.split(',')
    def setAuthUserEmails(self, auth_user_emails):
        self.auth_user_emails = ','.join(auth_user_emails)