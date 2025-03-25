
def download():
    from roboflow import Roboflow
    rf = Roboflow(api_key="BMY1Wp7jY7qJeUVOnk6T")
    project = rf.workspace("test-mvqra").project("water-uzqur")
    version = project.version(2)
    dataset = version.download("coco-segmentation")


def train():
    from ultralytics import YOLO
    model = YOLO("yolo11n-seg.pt")
    results = model.train(data="/data/coding/gao/water-2/water.yaml", epochs=100, imgsz=640)
    success = model.export()

def baseTrain():
    from ultralytics import YOLO
    model = YOLO("yolo11n-seg.pt")  # load a pretrained model (recommended for training)
    results = model.train(data="coco8-seg.yaml", epochs=100, imgsz=640)

if __name__ == '__main__':
    download()
    # baseTrain()
    # train()