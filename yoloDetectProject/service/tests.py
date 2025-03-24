import cv2
from ultralytics import YOLO

path = "./model/water_detect_model_45itr.pt"
model = YOLO(path)

if __name__ == '__main__':
    imgPath = "./test-data/images/img.png"
    videoPath = "./test-data/videos"
    result = model(videoPath, save=True, stream=True)