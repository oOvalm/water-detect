import os
import uuid
from abc import ABC, abstractmethod

from waterDetect import settings


class fileServiceABC(ABC):
    @abstractmethod
    def uploadVideo(self, file)->str:
        pass
    @abstractmethod
    def getVideo(self, fileID):
        pass

class LocalFileService(fileServiceABC):
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

    def getVideo(self, fileID):
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        file_path = os.path.join(upload_dir, fileID)
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