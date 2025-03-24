import json
import os

def convert_coco_to_yolo(coco_file_path, output_dir):
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取 COCO JSON 文件
    with open(coco_file_path, 'r') as f:
        coco_data = json.load(f)

    # 建立类别 ID 到索引的映射
    category_id_to_index = {category['id']: i for i, category in enumerate(coco_data['categories'])}

    # 处理每张图像
    for image in coco_data['images']:
        image_id = image['id']
        image_width = image['width']
        image_height = image['height']
        image_file_name = os.path.splitext(image['file_name'])[0]
        txt_file_path = os.path.join(output_dir, f"{image_file_name}.txt")

        # 找到该图像的所有标注
        image_annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]

        # 打开对应的 TXT 文件以写入标注信息
        with open(txt_file_path, 'w') as txt_file:
            for annotation in image_annotations:
                category_id = annotation['category_id']
                category_index = category_id_to_index[category_id]
                segs = annotation['segmentation']
                for seg in segs:
                    afSeg = []
                    for (i, s) in enumerate(seg):
                        if i%2==0:
                            afSeg.append(str(s/image_width))
                        else:
                            afSeg.append(str(s/image_height))
                    # 将标注信息写入 TXT 文件
                    if len(afSeg) > 0:
                        assert len(afSeg)%2==0 and len(afSeg) > 6
                        txt_file.write(f"{category_index} {' '.join(afSeg)}\n")

base = "water-2"
# 使用示例
path = [
    f'{base}/train',
    f'{base}/validate'
    f'{base}/test',
]
for p in path:
    convert_coco_to_yolo(f"/data/coding/water_detect/{p}/_annotations.coco.json", f"{p}/labels")    