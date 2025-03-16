from common.db_model import FileType
from database.models import FileInfo
from database.serializers import FileInfoSerializer


def DeleteFolders(folderIDs: list):
    q = []
    for fileID in folderIDs:
        fileInfos = FileInfo.objects.filter(file_pid=fileID)
        q.extend([fileInfo.id for fileInfo in fileInfos])
    deleted_files = []
    while len(q) > 0:
        fileID = q.pop(0)
        file = FileInfo.objects.get(id=fileID)
        if file.file_type == FileType.Folder.value:
            children = FileInfo.objects.filter(file_pid=fileID)
            for child in children:
                q.append(child.id)
        deleted_files.append(file)
        file.delete()
    return deleted_files
