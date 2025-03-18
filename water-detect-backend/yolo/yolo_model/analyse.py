import logging
import os

from ultralytics import YOLO

from common.annotation import singleton
from waterDetect import settings
from yolo.yolo_model.video_utils import ts_to_avi



USE_MOCK = False
BASE_TMP = os.path.join(settings.MEDIA_ROOT, 'analyse_tmp')
CUT_PATH = os.path.join(settings.MEDIA_ROOT, 'cuts')
SOURCE_PATH = os.path.join(settings.MEDIA_ROOT, 'files')
YOLO_MODEL_PATH = r'D:\coding\graduation-design\water-detect\water-detect-backend\yolo\yolo_model\yolov8n.pt'
# 加载 YOLOv8n 模型
@singleton
class singleYOLO(YOLO):
    def __init__(self):
        super().__init__(YOLO_MODEL_PATH)


logger = logging.getLogger(__name__)

def GetFromModel_Mock(path: str, destFolderName: str, projFolderName: str):
    oriFileName = path.split('\\')[-1].split('.')[0]
    tmp = os.path.join(BASE_TMP, projFolderName, destFolderName)
    os.makedirs(tmp)
    ts_to_avi(path, os.path.join(tmp, f'{oriFileName}.avi'))

def GetFromModel(path: str, destFolderName: str, projFolderName: str):
    if USE_MOCK:
        GetFromModel_Mock(path, destFolderName, projFolderName)
        return
    # 使用模型对视频文件进行预测，并保存结果
    results = singleYOLO().predict(source=path, save=True,
                            project=os.path.join(BASE_TMP, projFolderName),
                            name=f"{destFolderName}", stream=True)
    for _ in results:
        pass

def AnalyseImage(image):
    result = singleYOLO()(image, imgsz=320)
    return result[0].plot()
