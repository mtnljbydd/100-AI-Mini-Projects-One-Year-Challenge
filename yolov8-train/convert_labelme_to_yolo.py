import json
import os
import glob
from PIL import Image

# 类别映射，需要根据您的实际类别进行调整
# 从 data.yaml 中获取类别列表
import yaml
with open('dataset/data.yaml', 'r', encoding='utf-8') as f:
    data_config = yaml.safe_load(f)
    class_names = data_config['names']
    class_mapping = {name: idx for idx, name in enumerate(class_names)}

# 转换Labelme JSON到YOLO TXT

def convert_labelme_to_yolo(json_path, output_dir):
    # 加载JSON文件
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取图像尺寸
    # 如果JSON中没有图像尺寸信息，尝试从图像文件获取
    if 'imageWidth' in data and 'imageHeight' in data:
        img_width = data['imageWidth']
        img_height = data['imageHeight']
    else:
        # 从图像文件获取尺寸
        img_path = json_path.replace('labels', 'images').replace('.json', '.jpg')
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                img_width, img_height = img.size
        else:
            print(f"警告: 图像文件 {img_path} 不存在，跳过转换")
            return
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成YOLO格式的标签文件
    txt_filename = os.path.basename(json_path).replace('.json', '.txt')
    txt_path = os.path.join(output_dir, txt_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        for shape in data['shapes']:
            label = shape['label'].lower()  # 转换为小写
            # 检查类别是否在映射中
            if label not in class_mapping:
                print(f"警告: 类别 '{label}' 不在类别映射中，跳过")
                continue
            
            class_id = class_mapping[label]
            
            # 获取边界框坐标
            points = shape['points']
            # 无论形状类型，都计算所有点的最小和最大坐标
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            x1, x2 = min(x_coords), max(x_coords)
            y1, y2 = min(y_coords), max(y_coords)
            
            # 转换为YOLO格式：中心坐标和宽高，归一化到[0, 1]
            center_x = (x1 + x2) / 2 / img_width
            center_y = (y1 + y2) / 2 / img_height
            width = (x2 - x1) / img_width
            height = (y2 - y1) / img_height
            
            # 写入文件
            f.write(f"{class_id} {center_x} {center_y} {width} {height}\n")

# 处理所有JSON文件
print("开始转换Labelme JSON到YOLO TXT格式...")

# 转换训练集标签
print("处理训练集标签...")
train_json_files = glob.glob('dataset/train/labels/*.json')
for json_file in train_json_files:
    convert_labelme_to_yolo(json_file, 'dataset/train/labels')

# 转换验证集标签（如果有的话）
print("处理验证集标签...")
val_json_files = glob.glob('dataset/valid/labels/*.json')
for json_file in val_json_files:
    convert_labelme_to_yolo(json_file, 'dataset/valid/labels')

print("转换完成！")
