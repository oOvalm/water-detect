
from ultralytics import YOLO
model = YOLO("yolo11n-seg.pt")
def prodict(path):
    global model
    results = model.predict(source=path, save=True)
    # 可视化结果
    for r in results:
        im_array = r.plot()  # 绘制检测框和分割掩码
        # 这里可以保存或显示图像
        from PIL import Image
        img = Image.fromarray(im_array[..., ::-1])
        img.save('outpu.jpg')

if __name__ == '__main__':
    prodict('/data/coding/tt')