from enum import Enum

MINUTE = 60

INTERNAL_ERROR = "internal server error"

VIDEO_COVER_WIDTH = 150
THUMBNAIL_FILE_TYPE = "png"

class UploadFileStatus(Enum):
    emptyFile = "emptyfile"
    fail="fail"
    init="init"
    uploading="uploading"
    upload_finish="upload_finish"
    upload_seconds="upload_seconds"


