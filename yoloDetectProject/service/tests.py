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
    filePath = r"D:\coding\graduation-design\water-detect\yoloDetectProject\service\test-data\images\img.png"
    output_folder = r"D:\coding\graduation-design\water-detect\yoloDetectProject\service\dest"
    destName = "test"
    AnalyseImage(filePath, output_folder, destName)

if __name__ == '__main__':
    TestAnalyseImage()