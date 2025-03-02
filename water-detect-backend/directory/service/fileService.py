import os
import uuid
from abc import ABC, abstractmethod

from common import ScaleFilter, constants
from common.customError import ParamError, InternalServerError
from directory.models import FileType
from waterDetect import settings


class fileServiceABC(ABC):
    @abstractmethod
    def uploadVideo(self, file)->str:
        pass
    @abstractmethod
    def getVideo(self, fileID):
        pass
    @abstractmethod
    def uploadVideoChunk(self, fileID, chunkIndex, chunk):
        pass
    @abstractmethod
    def getThumbnailPath(self, fileUID):
        pass
    @abstractmethod
    def DeleteFile(self, fileUID):
        pass

class LocalFileService(fileServiceABC):
    folders = [
        'videos',
        'thumbnail',
        'tmp',
        'cuts',
    ]
    def __init__(self):
        for folder in LocalFileService.folders:
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, folder)):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, folder))

    def uploadVideo(self, video_file):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        fileID = uuid.uuid4().__str__()
        file_path = os.path.join(upload_dir, fileID)
        with open(file_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        return fileID

    def uploadVideoChunk(self, *args, **kwargs):
        fileID = kwargs['file_id']
        index = kwargs['chunk_index']
        chunks = kwargs['chunks']
        file = kwargs['file']
        if fileID == 'undefined':
            fileID = uuid.uuid4().__str__()
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        if not os.path.exists(os.path.join(upload_dir, fileID)):
            os.makedirs(os.path.join(upload_dir, fileID))
        with open(os.path.join(upload_dir, fileID, f'{index}'), 'wb+') as destination:
            destination.write(file.read())
        done = False
        totSize = 0
        if index+1 == chunks:
            file_path = os.path.join(upload_dir, fileID)
            target_path = os.path.join(settings.MEDIA_ROOT, 'videos', f"{fileID}.mp4")
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
        if done:
            ScaleFilter.create_cover4video(
                f'{settings.MEDIA_ROOT}/videos/{fileID}.mp4',
                constants.VIDEO_COVER_WIDTH,
                f'{settings.MEDIA_ROOT}/thumbnail/{fileID}.{constants.THUMBNAIL_FILE_TYPE}',
            )
            self._cutFile4Video(fileID)
            # 视频切片
        return fileID, totSize, done

    def getVideo(self, fileID):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        file_path = os.path.join(upload_dir, f"{fileID}.mp4")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as file:
                    video_content = file.read()
                return video_content
            except Exception as e:
                print(f"Error reading the video file: {e}")
        else:
            print(f"Video file with ID {fileID} not found.")
        return None


    def DeleteFile(self, fileUID):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        file_path = os.path.join(upload_dir, f"{fileUID}.mp4")
        if os.path.exists(file_path):
            os.remove(file_path)
        thumbnail_path = os.path.join(upload_dir, f"{fileUID}.{constants.THUMBNAIL_FILE_TYPE}")
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)


    def _cutFile4Video(self, fileUID: str):
        file_path = os.path.join(settings.MEDIA_ROOT, 'videos', f"{fileUID}.mp4")
        # 创建同名切片目录
        tsFolder = os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID)
        if not os.path.exists(tsFolder):
            os.makedirs(tsFolder)
        ScaleFilter.cut_files(file_path, tsFolder, fileUID)

    def GetM3U8Path(self, fileUID):
        return self._getFilePath(fileUID, "m3u8")
    def GetTSPath(self, fileUID, tsName):
        return self._getFilePath(fileUID, "ts", tsName=tsName)
    def getThumbnailPath(self, fileUID):
        return self._getFilePath(fileUID, "thumbnail")
    def GetFilePath(self, fileUID, fileType: FileType):
        if fileType == FileType.Video.value:
            return self._getFilePath(fileUID, "video")
        elif fileType == FileType.Image.value:
            return self._getFilePath(fileUID, "image")
        else:
            raise ValueError(f"Invalid file type: {fileType}")
    def _getFilePath(self, fileUID: str, fileType: str, *args, **kwargs):
        tsName = kwargs.get('tsName')
        if fileType == "video":
            return os.path.join(settings.MEDIA_ROOT, 'videos', f"{fileUID}.mp4")
        elif fileType == "ts":
            return os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID, tsName)
        elif fileType == "m3u8":
            return os.path.join(settings.MEDIA_ROOT, 'cuts', fileUID, 'index.m3u8')
        elif fileType == "thumbnail":
            return os.path.join(settings.MEDIA_ROOT, 'thumbnail', f"{fileUID}.{constants.THUMBNAIL_FILE_TYPE}")
        elif fileType == "image":
            raise ParamError("todo!!")
        else:
            raise ParamError("todo!!")
