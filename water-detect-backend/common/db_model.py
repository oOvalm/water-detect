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
