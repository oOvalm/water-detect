import json
from enum import Enum


class FileExtra:
    def __init__(self, **kwargs):
        self.analyseType = AnalyseFileType.Unknown
        self.oppositeID = 0
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __json__(self):
        return {
            "analyse_type": self.analyseType,
            "opposite_id": self.oppositeID,
        }

    @classmethod
    def from_json(cls, json_str):
        try:
            data = json.loads(json_str)
            return cls(**data)
        except json.JSONDecodeError:
            return cls()


class AnalyseFileType(Enum):
    Unknown = "unknown"
    Origin = "origin"
    Analysed = "analyse"

class VideoType(Enum):
    Raw = 1
    Analysed = 2


class FileType(Enum):
    Folder = 1
    Image = 2
    Video = 3

class SystemFolder(Enum):
    Root = -1
    OnlineAnalyseFolder = -2
    AnalysedFolder = -3

class FileStatus(Enum):
    Done = 0
    Converting = 1
    ConvertFailed = 2