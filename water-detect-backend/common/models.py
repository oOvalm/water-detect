from enum import Enum


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