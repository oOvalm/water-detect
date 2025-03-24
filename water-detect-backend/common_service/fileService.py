import os
import shutil
import threading
import uuid
from abc import ABC, abstractmethod

from common import ScaleFilter, constants
from common.customError import ParamError
from common.db_model import FileType
from database.models import FileInfo
from waterDetect import settings


fileTypeSuffixMap = {
    FileType.Video.value: ["mp4","avi","rmvb","mkv","mov"],
    FileType.Image.value: ["jpeg","jpg","png","gif","bmp","dds","psd","pdt","webp","xmp","svg","tiff"]
}

def GetFileSuffix(filename):
    return filename.split('.')[-1]


def GetFileTypeBySuffix(filename):
    suffix = GetFileSuffix(filename)
    for fileType, suffixList in fileTypeSuffixMap.items():
        if suffix in suffixList:
            return fileType



class LocalFileService():
    folders = [
        'files',
        'thumbnail',
        'tmp',
        'cuts',
        'avatar',
    ]
    def __init__(self):
        for folder in LocalFileService.folders:
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, folder))

    # def uploadVideo(self, video_file):
    #     upload_dir = os.path.join(settings.MEDIA_ROOT, 'files')
    #     if not os.path.exists(upload_dir):
    #         os.makedirs(upload_dir)
    #     fileID = uuid.uuid4().__str__()
    #     file_path = os.path.join(upload_dir, fileID)
    #     with open(file_path, 'wb+') as destination:
    #         for chunk in video_file.chunks():
    #             destination.write(chunk)
    #     return fileID

    def uploadVideoChunk(self, *args, **kwargs):
        fileID = kwargs['file_id']
        index = kwargs['chunk_index']
        chunks = kwargs['chunks']
        file = kwargs['file']
        filename = kwargs['filename']
        if fileID == 'undefined':
            fileID = uuid.uuid4().__str__()
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        if not os.path.exists(os.path.join(upload_dir, fileID)):
            os.makedirs(os.path.join(upload_dir, fileID))
        with open(os.path.join(upload_dir, fileID, f'{index}'), 'wb+') as destination:
            destination.write(file.read())
        done, totSize, fileType = False, 0, None
        if index+1 == chunks:
            fileSuffix = GetFileSuffix(filename)
            fileType = GetFileTypeBySuffix(filename)
            file_path = os.path.join(upload_dir, fileID)
            target_path = os.path.join(settings.MEDIA_ROOT, 'files', f"{fileID}.{fileSuffix}")
            with open(target_path, 'wb+') as destination:
                for i in range(chunks):
                    with open(os.path.join(file_path, f'{i}'), 'rb') as source:
                        destination.write(source.read())
            totSize = os.path.getsize(target_path)
            #  删除文件夹
            for i in range(chunks):
                os.remove(os.path.join(file_path, f'{i}'))
            os.rmdir(file_path)
            done = True
        return fileID, totSize, fileType, done

    def CreateThumbnail(self, filePath, fileUID, fileType):
        thumbnailPath = ""
        if fileType == FileType.Video.value:
            thumbnailPath = f'{settings.MEDIA_ROOT}/thumbnail/{fileUID}.{constants.THUMBNAIL_FILE_TYPE}'
            ScaleFilter.create_cover4video(
                filePath,
                constants.COVER_WIDTH,
                thumbnailPath,
            )
        elif fileType == FileType.Image.value:
            thumbnailPath = f'{settings.MEDIA_ROOT}/thumbnail/{fileUID}.{constants.THUMBNAIL_FILE_TYPE}'
            ScaleFilter.compress_image(
                filePath,
                constants.COVER_WIDTH,
                thumbnailPath,
                False
            )
        return thumbnailPath

    # def getVideo(self, fileID):
    #     upload_dir = os.path.join(settings.MEDIA_ROOT, 'files')
    #     file_path = os.path.join(upload_dir, f"{fileID}.mp4")
    #     if os.path.exists(file_path):
    #         try:
    #             with open(file_path, 'rb') as file:
    #                 video_content = file.read()
    #             return video_content
    #         except Exception as e:
    #             print(f"Error reading the video file: {e}")
    #     else:
    #         print(f"Video file with ID {fileID} not found.")
    #     return None


    def DeleteFile(self, fileInfo):
        fileUID = fileInfo.file_uid
        removeFiles = [
            os.path.join(settings.MEDIA_ROOT, 'files', f"{fileInfo.UIDFilename()}"),
            os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"{fileUID}.{constants.THUMBNAIL_FILE_TYPE}"),
            # os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"analysed_{fileUID}.{constants.THUMBNAIL_FILE_TYPE}"),
        ]
        removeFolders = [
            os.path.join(settings.MEDIA_ROOT, 'cuts', f"{fileUID}"),
            # os.path.join(settings.MEDIA_ROOT, 'cuts', f"analysed_{fileUID}")
        ]
        for path in removeFiles:
            if os.path.exists(path):
                os.remove(path)
        for folder in removeFolders:
            if os.path.exists(folder):
                shutil.rmtree(folder)



    def cutFile4Video(self, fileInfo: FileInfo):
        fileUID = fileInfo.file_uid
        file_path = os.path.join(settings.MEDIA_ROOT, 'files', f"{fileInfo.UIDFilename()}")
        # 创建同名切片目录
        tsFolder = os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID)
        if not os.path.exists(tsFolder):
            os.makedirs(tsFolder)
        ScaleFilter.cut_files(file_path, tsFolder, fileUID)

    def GetTSFolder(self, fileUID):
        return os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID)
    def GetM3U8Path(self, fileUID):
        return self._getFilePath(fileUID, "m3u8")
    def GetTSPath(self, fileUID, tsName):
        return self._getFilePath(fileUID, "ts", tsName=tsName)
    def getThumbnailPath(self, fileUID):
        return self._getFilePath(fileUID, "thumbnail")
    def GetFilePath(self, fileInfo):
        fileUID, fileType = fileInfo.file_uid, fileInfo.file_type
        fileSuffix = GetFileSuffix(fileInfo.filename)
        if fileType == FileType.Video.value:
            return self._getFilePath(fileUID, "video", suffix=fileSuffix)
        elif fileType == FileType.Image.value:
            return self._getFilePath(fileUID, "image", suffix=fileSuffix)
        else:
            raise ValueError(f"Invalid file type: {fileType}")
    def _getFilePath(self, fileUID: str, fileType: str, *args, **kwargs):
        tsName = kwargs.get('tsName')
        suffix = kwargs.get('suffix')
        if fileType == "video" or fileType == "image":
            return os.path.join(settings.MEDIA_ROOT, 'files', f"{fileUID}.{suffix}")
        elif fileType == "ts":
            return os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID, tsName)
        elif fileType == "m3u8":
            return os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID, 'index.m3u8')
        elif fileType == "thumbnail":
            return os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"{fileUID}.{constants.THUMBNAIL_FILE_TYPE}")
        else:
            raise ParamError("todo!!")

    def GetFileSize(self, filePath):
        # 获取路径下文件大小
        return os.path.getsize(filePath)

    def saveAvatar(self, file):
        avatarRoot = os.path.join(settings.MEDIA_ROOT, 'avatar')
        if not os.path.exists(avatarRoot):
            os.makedirs(avatarRoot)
        fileID = uuid.uuid4().__str__()
        file_path = os.path.join(avatarRoot, f"user_avatar_{fileID}.{GetFileSuffix(file.name)}")
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return f'avatar/user_avatar_{fileID}.{GetFileSuffix(file.name)}'

    def copyFile(self, fileInfo):
        oriUID, newUID = fileInfo.file_uid, uuid.uuid4().__str__()
        # 按照DELETE处理的逻辑，进行复制
        # 复制文件
        copyFiles = [
            os.path.join(settings.MEDIA_ROOT, 'files', f"{fileInfo.UIDFilename()}"),
            os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"{oriUID}.{constants.THUMBNAIL_FILE_TYPE}"),
        ]
        destFiles = [
            os.path.join(settings.MEDIA_ROOT, 'files', f"{newUID}.{GetFileSuffix(fileInfo.filename)}"),
            os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"{newUID}.{constants.THUMBNAIL_FILE_TYPE}"),
        ]
        for srcPath, destPath in zip(copyFiles, destFiles):
            if os.path.exists(srcPath):
                shutil.copy(srcPath, destPath)

        if fileInfo.file_type == FileType.Video.value:
            copyFolders = [
                os.path.join(settings.MEDIA_ROOT, 'cuts', f"{oriUID}"),
            ]
            for folder in copyFolders:
                if os.path.exists(folder):
                    destFolder = os.path.join(settings.MEDIA_ROOT, 'cuts', f"{newUID}")
                    shutil.copytree(folder, os.path.join(settings.MEDIA_ROOT, 'cuts', f"{newUID}"))
                    # 将destFolder下所有文件名包含oriUID部分替换为newUID
                    for root, dirs, files in os.walk(destFolder):
                        for file in files:
                            if oriUID in file:
                                os.rename(os.path.join(root, file), os.path.join(root, file.replace(oriUID, newUID)))
            # 单独处理m3u8
            m3u8Path = os.path.join(settings.MEDIA_ROOT, 'cuts', f"{newUID}", 'index.m3u8')
            if os.path.exists(m3u8Path):
                with open(m3u8Path, 'r') as f:
                    lines = f.readlines()
                with open(m3u8Path, 'w') as f:
                    for line in lines:
                        f.write(line.replace(oriUID, newUID))
        return newUID


_fileManager = None
once = threading.Lock()
def FileManager() -> LocalFileService:
    global _fileManager
    with once:
        if _fileManager is None:
            _fileManager = LocalFileService()
        return _fileManager


