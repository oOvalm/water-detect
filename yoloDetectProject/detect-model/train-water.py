
def download():
    from roboflow import Roboflow
    rf = Roboflow(api_key="BMY1Wp7jY7qJeUVOnk6T")
    project = rf.workspace("test-mvqra").project("water-uzqur")
    version = project.version(2)
    dataset = version.download("coco-segmentation")


def train():
    from ultralytics import YOLO
    model = YOLO("yolo11-seg.yaml")
    results = model.train(data="coco8.yaml", epochs=3, imgsz=640)
    success = model.export()

if __name__ == '__main__':
    train();