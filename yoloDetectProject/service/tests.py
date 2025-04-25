import cv2
from ultralytics import YOLO

from service import AnalyseVideo, AnalyseImage

path = "./model/water_detect_model_45itr.pt"
model = YOLO(path)

def TestModel():
    imgPath = "./test-data/images/img.png"
    videoPath = "./test-data/videos/青岛02.mp4"
    result = model(videoPath, save=True)
    videoPath = "./test-data/videos/青岛04.mp4"
    result_ = model(videoPath, save=True)

def TestAnalyseVideo():
    filePath = ".\\test-data\\videos\\青岛02.mp4"
    output_folder = r"D:\coding\graduation-design\water-detect\yoloDetectProject\service\dest"
    destName = "test"
    AnalyseVideo(filePath, output_folder, destName)

def TestAnalyseImage():
    p1 = r"D:\coding\graduation-design\water-detect\yoloDetectProject\detect-model\water-2\valid\images\150_2023-Flood-Time-Lapse-VNzrOBGzkA4-_jpg.rf.8e4472d128a5e32d77c87600df43c734.jpg"
    p2 = r"D:\coding\graduation-design\water-detect\yoloDetectProject\detect-model\water-2\valid\images\630_2023-Flood-Time-Lapse-VNzrOBGzkA4-_jpg.rf.4e38f4f27fe987cee2ff391de82ab899.jpg"
    # filePath = r"D:\coding\graduation-design\water-detect\yoloDetectProject\service\test-data\images\xx.png"
    output_folder = r"D:\coding\graduation-design\water-detect\yoloDetectProject\service\test-data\dest"
    destName = "test2"
    AnalyseImage(p2, output_folder, destName, destName)

if __name__ == '__main__':
    TestAnalyseImage()