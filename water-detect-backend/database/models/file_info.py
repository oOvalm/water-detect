import re
from enum import Enum

from django.db import models

from database.models.user import User


class FileInfoManager(models.Manager):
    def createVideo(self, file_pid: int, filename: str, fileSize: int, fileID: str, user: User):
        fileinfo = FileInfo(
            size = fileSize,
            file_pid = file_pid,
            folder_type=1,
            file_type=3,
            filename=filename,
            user_id=user.id,
            file_uid = fileID,
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
        prefix, suffix = parts[0], parts[1]
        while cnt > 0:
            # 按照最后一个点分割
            filename = f"{prefix}({id}).{suffix}"
            cnt = super().filter(file_pid=filePID, filename=filename, user_id=userID).count()
            id += 1
        return filename

    def ResolveFolderID(self, userID: int, folderID: int):
        if folderID == SystemFolder.AnalyseFolder.value:
            analyseFolder = super().filter(user_id=userID, folder_type=SystemFolder.AnalyseFolder.value)
            if analyseFolder.count() == 0:
                analyseFolder = self.createFolder(SystemFolder.Root.value, userID)
                analyseFolder.folder_type = SystemFolder.AnalyseFolder.value
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
    filename = models.CharField(max_length=4096, db_comment='用户上传时的文件名')
    folder_type = models.SmallIntegerField(default=0, db_comment='0:普通文件夹 1:根文件夹 2:分析文件夹')
    user_id = models.IntegerField(db_comment='userID')
    thumbnail = models.BinaryField(null=True, db_comment='thumbnail')
    extra = models.BinaryField(null=True, db_comment='extra')
    create_time = models.DateTimeField(auto_now_add=True,null=False)
    update_time = models.DateTimeField(auto_now=True,null=False)

    objects = FileInfoManager()

    class Meta:
        db_table = 'water_detect_file_info'

class FileExtra():
    pass

class VideoType(Enum):
    Raw = 1
    Analysed = 2


class FileType(Enum):
    Folder = 1
    Image = 2
    Video = 3

class SystemFolder(Enum):
    Root = -1
    AnalyseFolder = -2