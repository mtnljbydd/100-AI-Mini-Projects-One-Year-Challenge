"""
COCO到YOLO注释格式转换脚本

该脚本用于将COCO格式的注释文件转换为YOLO格式。COCO格式是一种流行的基于JSON的目标检测格式，
包含图像注释、对象实例、对象分割和分类等信息。YOLO格式更简单，使用纯文本文件，
其中每行代表图像中的一个对象实例，对象类和边界框坐标归一化到[0, 1]范围。

使用方法：
1. 将此脚本放在与您的COCO注释文件相同的目录中，注释文件通常命名为'_annotations.coco.json'
2. 如果您的COCO文件具有不同的名称，请修改下面的'coco_json'变量
3. 运行脚本，它将读取COCO注释，将它们转换为YOLO格式，并将它们保存在指定的输出目录中

注意：以下代码也应该可以工作，这是在创建此脚本后发现的
from ultralytics.data.converter import convert_coco
convert_coco(labels_dir='path/to/coco/annotations/')
"""
# 导入所需库
import json
import os

# COCO JSON文件路径
# 确保此文件存在于与脚本相同的目录中
coco_json = '_annotations.coco.json'

# 存储YOLO格式注释文件的输出目录
# 转换后的注释文件将保存在此目录中
output_dir = 'yolo_annotations'

# 将COCO JSON格式注释转换为YOLO格式文本文件
def convert_coco_to_yolo(coco_json, output_dir):
    """
    将COCO JSON格式的注释转换为YOLO格式的文本文件
    
    参数:
        coco_json: COCO格式的JSON注释文件路径
        output_dir: 输出YOLO格式注释文件的目录路径
    """
    # 加载COCO JSON文件
    with open(coco_json) as file:
        data = json.load(file)

    # 如果输出目录不存在，则创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 提取图像尺寸信息
    # 创建一个字典，键为图像ID，值为(宽度, 高度)元组
    image_dimensions = {image['id']: (image['width'], image['height']) for image in data['images']}

    # 处理每个注释
    for annotation in data['annotations']:
        image_id = annotation['image_id']  # 获取注释对应的图像ID
        # COCO类ID从1开始，YOLO从0开始，所以减1
        category_id = annotation['category_id'] - 1
        bbox = annotation['bbox']  # 获取COCO格式的边界框 [x, y, width, height]

        # 计算归一化值
        # 找到对应的图像文件名
        file_name = next((img['file_name'] for img in data['images'] if img['id'] == image_id), None)
        if file_name is None:  # 如果找不到对应的图像，跳过
            continue

        base_file_name = os.path.splitext(file_name)[0]  # 获取不带扩展名的文件名
        width, height = image_dimensions[image_id]  # 获取图像尺寸
        
        # COCO边界框格式：[x, y, width, height]（左上角坐标和宽高）
        # YOLO边界框格式：[x_center, y_center, width, height]（归一化的中心点坐标和宽高）
        x_center = (bbox[0] + bbox[2] / 2) / width  # 计算归一化的中心X坐标
        y_center = (bbox[1] + bbox[3] / 2) / height  # 计算归一化的中心Y坐标
        norm_width = bbox[2] / width  # 计算归一化的宽度
        norm_height = bbox[3] / height  # 计算归一化的高度

        # 准备写入文件的行
        # YOLO格式：class_id x_center y_center width height
        line = f"{category_id} {x_center} {y_center} {norm_width} {norm_height}\n"

        # 写入对应的txt文件
        # 使用图像文件名作为注释文件名
        output_file = os.path.join(output_dir, f"{base_file_name}.txt")
        with open(output_file, 'a') as f:  # 使用追加模式，因为一个图像可能有多个注释
            f.write(line)

# 转换数据集
convert_coco_to_yolo(coco_json, output_dir)
