
class AnalyseTask:
    def __init__(self, fileID, fileType, fileUID):
        self.fileID = fileID
        self.fileType = fileType
        self.fileUID = fileUID

    def toDict(self):
        return {
            'fileID': self.fileID,
            'fileType': self.fileType,
            'fileUID': self.fileUID
        }
    def __str__(self):
        return str(self.toDict())
