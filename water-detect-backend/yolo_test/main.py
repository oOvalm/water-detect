import time

from ultralytics import YOLO

model = YOLO("yolo11n.pt")

def InitYolo8():
    # Display model information (optional)
    # model.info()

    # Train the model on the COCO8 example dataset for 100 epochs
    # results = model.train(data="coco8.yaml", epochs=3)

    # if results is None:
    #     raise "train model failed"
    pass

def GetFromModel(path: str, resultName: str):
    results = model.predict(source=path)
    for result in results:
        result.save(filename=f"{path}/{resultName}.jpg")
        result.to()
    print('=====', results)

if __name__ == '__main__':
    InitYolo8()
    paths = [
        r'D:\coding\graduation-design\waterDetect\yolo_test\bus.jpg',
    ]
    for c in paths:
        GetFromModel(path=c, resultName='tmp')
    print('done')
    print('exit')