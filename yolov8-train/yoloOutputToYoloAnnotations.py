"""
YOLO检测输出转训练注释脚本

该脚本用于将YOLO检测输出的文本格式重新映射为YOLO训练格式。它处理包含图像文件及其对应检测注释文件的给定文件夹。
对于每个图像及其关联的检测文件，脚本读取检测结果，将其边界框坐标从绝对像素值转换为相对于图像尺寸的归一化值，
然后将这些归一化值写入YOLO格式的新输出文件。

在运行脚本之前，请确保将'folder_path'变量设置为包含图像和检测文件的目录。检测文件应采用'<image_name>.txt'格式，
每行代表一个检测到的对象，格式为'class_name confidence x_start y_start x_end y_end'。

使用方法：
1. 从项目根目录运行此脚本
2. 确保images_folder和texts_folder变量指向正确的目录
3. 配置class_ids字典以匹配您的类名和ID映射
"""

from PIL import Image
import os

# 默认文件夹路径 - 如果图像和文本文件在同一个文件夹中，这些可以相同
images_folder = 'output/overlays'  # 图像文件夹路径
texts_folder = 'output/detections'  # 包含检测文本文件的文件夹路径

# 类名到类ID的映射
# 在此处添加或修改类名和对应的ID
class_ids = {
    'watermark': 0,  # 水印类，ID为0
    'rabbits': 1     # 兔子类，ID为1
    # 根据需要添加更多类名和ID
}

# 将检测格式从一种类型转换为YOLO格式并保存到输出文件
def convert_detections(input_file, image_file, output_file):
    """
    将单个图像的检测结果转换为YOLO训练格式
    
    参数:
        input_file: 输入检测文本文件路径
        image_file: 对应的图像文件路径
        output_file: 输出YOLO格式文件路径
    """
    # 打开图像文件获取尺寸
    with Image.open(image_file) as img:
        image_width, image_height = img.size
        print(f"图像尺寸 {image_file}: 宽度={image_width}, 高度={image_height}")

    # 从输入文件读取检测结果，并将归一化值写入输出文件
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            detections = line.strip().split(', ')
            for detection in detections:
                parts = detection.split()
                # 验证检测格式
                if len(parts) != 6:
                    print(f"跳过无效检测: {detection}")
                    continue

                # 提取检测详情
                class_name, confidence, x_start, y_start, x_end, y_end = parts
                # 获取类ID，如果类名未知则使用-1
                class_id = class_ids.get(class_name, -1)

                if class_id == -1:
                    print(f"未知类 '{class_name}', 跳过。")
                    continue

                # 将绝对坐标转换为归一化值
                # YOLO格式使用相对于图像尺寸的归一化坐标
                x_start, y_start, x_end, y_end = map(float, [x_start, y_start, x_end, y_end])
                x_center_ratio = ((x_start + x_end) / 2) / image_width  # 中心点X坐标归一化
                y_center_ratio = ((y_start + y_end) / 2) / image_height  # 中心点Y坐标归一化
                width_ratio = (x_end - x_start) / image_width  # 宽度归一化
                height_ratio = (y_end - y_start) / image_height  # 高度归一化

                # 将转换后的检测结果写入输出文件
                # YOLO格式: class_id x_center y_center width height
                outfile.write(f"{class_id} {x_center_ratio} {y_center_ratio} {width_ratio} {height_ratio}\n")

# 处理文件夹中的所有图像并将其检测结果转换为所需格式
def process_folders(images_folder, texts_folder):
    """
    处理整个文件夹中的图像和检测结果文件
    
    参数:
        images_folder: 包含图像文件的文件夹路径
        texts_folder: 包含检测文本文件的文件夹路径
    """
    # 遍历文本文件夹中的所有文件
    for text_file in os.listdir(texts_folder):
        base, ext = os.path.splitext(text_file)  # 分离文件名和扩展名
        if ext.lower() == '.txt':  # 只处理.txt文件
            # 构建对应的图像和输出文件路径
            corresponding_image_file = base + '.jpg'  # 假设图像扩展名为.jpg，可根据需要更改
            image_file_path = os.path.join(images_folder, corresponding_image_file)
            text_file_path = os.path.join(texts_folder, text_file)
            output_file_path = os.path.join(texts_folder, base + '_converted.txt')  # 输出文件添加_converted后缀

            # 如果对应的图像存在，则处理文件
            if os.path.exists(image_file_path):
                print(f"正在处理 {base}...")
                convert_detections(text_file_path, image_file_path, output_file_path)
            else:
                print(f"没有对应的图像文件: {text_file_path}")

# 在指定的文件夹上运行处理流程
process_folders(images_folder, texts_folder)