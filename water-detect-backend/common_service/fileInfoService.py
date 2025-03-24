from common.db_model import FileType
from database.models import FileInfo
from database.serializers import FileInfoSerializer


def GetAllFileInfoInFolders(folderIDs: list):
    """
    通过bfs的方式获取文件夹下所有文件，包含文件夹本身(BFS序)
    """
    q = []
    bfsFileInfos = []
    for fileID in folderIDs:
        fileInfos = FileInfo.objects.filter(file_pid=fileID)
        q.extend([fileInfo.id for fileInfo in fileInfos])
        bfsFileInfos.append(FileInfo.objects.get(id=fileID))
    while len(q) > 0:
        fileID = q.pop(0)
        file = FileInfo.objects.get(id=fileID)
        if file.file_type == FileType.Folder.value:
            children = FileInfo.objects.filter(file_pid=fileID)
            for child in children:
                q.append(child.id)
        bfsFileInfos.append(file)
    return bfsFileInfos
