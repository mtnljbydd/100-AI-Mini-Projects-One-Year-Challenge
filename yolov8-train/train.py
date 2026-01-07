# -*- coding: utf-8 -*-
"""
YOLOv8模型训练脚本

该脚本用于配置和启动YOLOv8模型的训练过程，支持不同大小的预训练模型选择和自定义训练参数。
训练完成后，模型会自动在验证集上进行评估，并将结果保存到指定目录。

新增功能：
- 自动检测并转换LabelMe格式(.json)的标注文件为YOLO格式(.txt)
- 支持批量转换train、valid、test目录下的标注文件
- 用户自定义训练任务名称
- 自动创建日志文件夹，按任务名称分类
- 训练完成后输出详细的结果信息

使用方法：
1. 确保已安装所需依赖包
2. 在dataset目录下准备好data.yaml配置文件和训练数据集
3. 数据集目录结构应该是：
   dataset/
   ├── train/
   │   ├── images/  # 训练图像
   │   └── labels/  # LabelMe格式的.json标注文件或YOLO格式的.txt文件
   ├── valid/
   │   ├── images/  # 验证图像
   │   └── labels/  # LabelMe格式的.json标注文件或YOLO格式的.txt文件
   └── data.yaml
4. 运行此脚本，按照提示选择模型大小和设置训练结果名称
"""
import os
import torch
5

import json
import glob
import logging
from datetime import datetime   
from ultralytics import YOLO

def detailed_dataset_check(dataset_dir):
    """
    详细检查数据集，验证图像与标签的对应关系和标签内容
    
    参数:
        dataset_dir: 数据集根目录
    """
    import yaml
    
    print('\n=== 详细数据集检查 ===')
    
    # 加载data.yaml中的类别信息
    yaml_path = os.path.join(dataset_dir, 'data.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    expected_classes = data.get('names', [])
    expected_nc = data.get('nc', 0)
    
    print(f'\n期望的类别数量: {expected_nc}')
    print(f'期望的类别列表: {expected_classes}')
    
    # 检查train和valid集
    for split in ['train', 'valid']:
        print(f'\n--- {split} 集详细检查 ---')
        
        # 定义路径
        img_dir = os.path.join(dataset_dir, split, 'images')
        lbl_dir = os.path.join(dataset_dir, split, 'labels')
        
        # 获取所有图像文件
        image_files = glob.glob(os.path.join(img_dir, '*.*'))
        image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        print(f'图像文件数量: {len(image_files)}')
        
        # 获取所有标签文件
        label_files = glob.glob(os.path.join(lbl_dir, '*.txt'))
        print(f'标签文件数量: {len(label_files)}')
        
        # 获取所有JSON文件
        json_files = glob.glob(os.path.join(lbl_dir, '*.json'))
        print(f'JSON标注文件数量: {len(json_files)}')
        
        # 统计每个类别的样本数量
        class_counts = {i: 0 for i in range(expected_nc)}
        
        # 检查每个标签文件
        for lbl_path in label_files[:10]:  # 只检查前10个文件
            try:
                with open(lbl_path, 'r') as f:
                    lines = f.readlines()
                
                base_name = os.path.splitext(os.path.basename(lbl_path))[0]
                img_path = None
                
                # 查找对应的图像文件
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    potential_img = os.path.join(img_dir, f'{base_name}{ext}')
                    if os.path.exists(potential_img):
                        img_path = potential_img
                        break
                
                if img_path:
                    print(f'\n文件 {base_name}:')
                    print(f'  ✅ 图像文件存在')
                    print(f'  标签行数: {len(lines)}')
                    
                    # 检查标签内容
                    for line_num, line in enumerate(lines[:5], 1):  # 只显示前5行
                        line = line.strip()
                        if not line:
                            continue
                        
                        parts = line.split()
                        if len(parts) != 5:
                            print(f'    ❌ 第{line_num}行格式错误: {line}')
                            continue
                        
                        cls_id = int(parts[0])
                        x, y, w, h = map(float, parts[1:5])
                        
                        # 检查类别ID是否在范围内
                        if 0 <= cls_id < expected_nc:
                            print(f'    ✅ 第{line_num}行: 类别 {cls_id} ({expected_classes[cls_id]}), 坐标 {x:.2f},{y:.2f},{w:.2f},{h:.2f}')
                            class_counts[cls_id] += 1
                        else:
                            print(f'    ❌ 第{line_num}行: 类别ID {cls_id} 超出范围 (0-{expected_nc-1})')
                else:
                    print(f'\n❌ 文件 {base_name}: 缺少对应的图像文件')
                    
            except Exception as e:
                print(f'\n❌ 文件 {os.path.basename(lbl_path)}: 读取错误 - {str(e)}')
        
        # 输出类别统计
        print(f'\n类别统计 (仅前10个文件):')
        for cls_id, count in class_counts.items():
            if count > 0:
                print(f'  类别 {cls_id} ({expected_classes[cls_id]}): {count} 个样本')
    
    print('\n=== 详细检查完成 ===')

def validate_dataset(dataset_dir):
    """
    验证数据集的完整性，检查图像与标签文件是否匹配、标签内容是否正确
    
    参数:
        dataset_dir: 数据集根目录
    
    返回:
        bool: 如果数据集验证通过返回True，否则返回False
    """
    import glob
    import yaml
    
    print('\n=== 数据集验证 ===')
    has_error = False
    
    # 检查data.yaml文件
    yaml_path = os.path.join(dataset_dir, 'data.yaml')
    if not os.path.exists(yaml_path):
        print(f'❌ 错误: 找不到data.yaml文件')
        print(f'   解决方案: 在dataset目录下创建data.yaml文件，包含以下内容:')
        print(f'   train: ../train/images')
        print(f'   val: ../valid/images')
        print(f'   nc: 类别数量')
        print(f'   names: ["类别1", "类别2", ...]')
        return False
    
    # 读取data.yaml文件
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    expected_nc = data.get('nc', 0)
    
    # 检查train和valid集
    for split in ['train', 'valid']:
        print(f'\n--- {split} 集 ---')
        
        # 定义路径
        img_dir = os.path.join(dataset_dir, split, 'images')
        lbl_dir = os.path.join(dataset_dir, split, 'labels')
        
        # 检查目录是否存在
        if not os.path.exists(img_dir):
            print(f'❌ 错误: 找不到{split}/images目录')
            print(f'   解决方案: 创建{dataset_dir}/{split}/images目录并放入图像文件')
            has_error = True
            continue
        
        if not os.path.exists(lbl_dir):
            print(f'❌ 错误: 找不到{split}/labels目录')
            print(f'   解决方案: 创建{dataset_dir}/{split}/labels目录并放入标签文件')
            has_error = True
            continue
        
        # 获取所有图像文件
        image_files = glob.glob(os.path.join(img_dir, '*.*'))
        image_files = [f for f in image_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        print(f'图像文件数量: {len(image_files)}')
        
        # 获取所有标签文件
        label_files = glob.glob(os.path.join(lbl_dir, '*.txt'))
        print(f'标签文件数量: {len(label_files)}')
        
        # 获取所有JSON文件
        json_files = glob.glob(os.path.join(lbl_dir, '*.json'))
        if json_files:
            print(f'发现{len(json_files)}个LabelMe JSON文件，将在训练前自动转换')
        
        # 检查数据集是否为空
        total_files = len(image_files) + len(label_files) + len(json_files)
        if split == 'train' and not image_files:
            print(f'❌ 错误: 训练集为空，没有找到任何图像文件')
            print(f'   解决方案: 将图像文件放入{dataset_dir}/{split}/images目录')
            has_error = True
        elif split == 'valid' and not image_files:
            print(f'⚠️  警告: 验证集为空，没有找到任何图像文件')
            print(f'   解决方案: 运行 python create_validation_set.py 从训练集分割一部分作为验证集')
            has_error = True
        
        # 检查每个图像是否有对应的标签文件
        missing_labels = []
        invalid_labels = []
        
        for img_path in image_files:
            # 获取图像文件名（不含扩展名）
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            # 对应的标签文件路径
            lbl_path = os.path.join(lbl_dir, f'{base_name}.txt')
            json_path = os.path.join(lbl_dir, f'{base_name}.json')
            
            if not os.path.exists(lbl_path) and not os.path.exists(json_path):
                missing_labels.append(base_name)
                continue
            
            # 如果存在JSON文件但不存在TXT文件，会在训练前自动转换
            if not os.path.exists(lbl_path) and os.path.exists(json_path):
                continue
            
            # 检查标签文件内容
            try:
                with open(lbl_path, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    invalid_labels.append((base_name, '标签文件为空'))
                    continue
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检查标签格式
                    parts = line.split()
                    if len(parts) != 5:
                        invalid_labels.append((base_name, f'第{line_num}行格式错误: {line}'))
                        continue
                    
                    # 检查类别ID和坐标
                    try:
                        cls_id = int(parts[0])
                        x, y, w, h = map(float, parts[1:5])
                    except ValueError:
                        invalid_labels.append((base_name, f'第{line_num}行数值格式错误: {line}'))
                        continue
                    
                    if cls_id < 0 or (expected_nc > 0 and cls_id >= expected_nc):
                        invalid_labels.append((base_name, f'第{line_num}行类别ID超出范围: {cls_id}'))
                        
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                        invalid_labels.append((base_name, f'第{line_num}行坐标超出范围: {x:.2f},{y:.2f},{w:.2f},{h:.2f}'))
                        
            except Exception as e:
                invalid_labels.append((base_name, f'读取错误: {str(e)}'))
        
        # 输出结果
        if missing_labels:
            print(f'❌ 缺失标签文件: {len(missing_labels)}')
            for name in missing_labels[:5]:
                print(f'  - {name}.jpg')
            print(f'   解决方案: 为上述图像创建对应的标签文件，或者使用python convert_labelme_to_yolo.py转换JSON标注')
            has_error = True
        
        if invalid_labels:
            print(f'❌ 无效标签文件: {len(invalid_labels)}')
            for name, err in invalid_labels[:5]:
                print(f'  - {name}.txt: {err}')
            print(f'   解决方案: 检查并修复上述标签文件的格式和内容，或使用 python fix_dataset.py 尝试自动修复')
            has_error = True
    
    if has_error:
        print('\n=== 验证失败，请根据上述错误信息进行修复 ===')
        return False
    else:
        print('\n=== 验证成功，数据集完整性良好 ===')
        return True

def convert_labelme_to_yolo(json_file, class_mapping=None):
    """
    将单个LabelMe JSON格式的注释转换为YOLO格式的文本文件
    
    参数:
        json_file: LabelMe格式的JSON注释文件路径
        class_mapping: 类别名称到ID的映射字典
    """
    # 加载LabelMe JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取图像信息
    image_width = data.get('imageWidth')
    image_height = data.get('imageHeight')
    
    if not image_width or not image_height:
        print(f"警告: {json_file} 中缺少图像尺寸信息，跳过转换")
        return False, {}
    
    # 构建输出文件路径（与JSON文件同名，扩展名为.txt）
    base_name = os.path.splitext(json_file)[0]
    output_file = f"{base_name}.txt"
    
    # 如果没有提供类别映射，自动从数据中提取
    if class_mapping is None:
        class_mapping = {}
        for shape in data.get('shapes', []):
            label = shape['label']
            if label not in class_mapping:
                class_mapping[label] = len(class_mapping)
    
    # 处理每个标注形状
    with open(output_file, 'w') as f:
        for shape in data.get('shapes', []):
            label = shape['label']
            points = shape['points']
            shape_type = shape.get('shape_type', 'rectangle')
            
            # 将标签名称转换为小写进行匹配
            label_lower = label.lower()
            
            # 获取类别ID
            if label_lower not in class_mapping:
                # 如果类别不在映射中，跳过该标注
                print(f"警告: {json_file} 中包含未在data.yaml中定义的类别 {label}，跳过此标注")
                continue
            else:
                class_id = class_mapping[label_lower]
            
            # 根据形状类型计算边界框
            if shape_type == 'rectangle':
                # 矩形：LabelMe存储四个角点，我们需要提取所有点的坐标范围
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
            elif shape_type == 'polygon':
                # 多边形：转换为边界框
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
            else:
                print(f"警告: {json_file} 中包含不支持的形状类型 {shape_type}，跳过此标注")
                continue
            
            # 计算YOLO格式的归一化坐标
            # YOLO格式：[x_center, y_center, width, height]
            x_center = (x1 + x2) / 2 / image_width
            y_center = (y1 + y2) / 2 / image_height
            norm_width = abs(x2 - x1) / image_width
            norm_height = abs(y2 - y1) / image_height
            
            # 写入YOLO格式的行
            line = f"{class_id} {x_center} {y_center} {norm_width} {norm_height}\n"
            f.write(line)
    
    return True, class_mapping

def load_class_mapping_from_yaml(yaml_path):
    """
    从data.yaml文件加载类别映射
    
    参数:
        yaml_path: data.yaml文件路径
    
    返回:
        class_mapping: 类别名称到ID的映射字典（小写键）
    """
    import yaml
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    class_mapping = {}
    if 'names' in data:
        for idx, name in enumerate(data['names']):
            # 将所有类别名称转换为小写，确保大小写不敏感匹配
            class_mapping[name.lower()] = idx
    
    return class_mapping

def batch_convert_labelme_to_yolo(dataset_dir):
    """
    批量转换数据集目录下的所有LabelMe JSON文件为YOLO格式
    
    参数:
        dataset_dir: 数据集根目录
    """
    # 需要检查的子目录
    subdirs = ['train/labels', 'valid/labels', 'test/labels']
    
    # 从data.yaml加载类别映射
    yaml_path = os.path.join(dataset_dir, 'data.yaml')
    class_mapping = load_class_mapping_from_yaml(yaml_path)
    
    print("开始检查并转换LabelMe格式标注文件...")
    print(f"使用data.yaml中的类别映射: {class_mapping}")
    
    for subdir in subdirs:
        # 构建完整路径
        labels_dir = os.path.join(dataset_dir, subdir)
        
        if not os.path.exists(labels_dir):
            print(f"目录 {labels_dir} 不存在，跳过")
            continue
        
        # 查找所有JSON文件
        json_files = glob.glob(os.path.join(labels_dir, '*.json'))
        
        if not json_files:
            print(f"在 {labels_dir} 中未找到LabelMe JSON文件")
            continue
        
        print(f"在 {labels_dir} 中找到 {len(json_files)} 个LabelMe JSON文件，开始转换...")
        
        success_count = 0
        for json_file in json_files:
            # 使用data.yaml中的类别映射，而不是自动生成的
            result, _ = convert_labelme_to_yolo(json_file, class_mapping)
            if result:
                success_count += 1
        
        print(f"  转换完成！成功转换 {success_count} 个文件，失败 {len(json_files) - success_count} 个文件")
    
    # 打印使用的类别映射
    if class_mapping:
        print("\n使用的类别映射:")
        for label, idx in sorted(class_mapping.items(), key=lambda x: x[1]):
            print(f"  {label}: {idx}")
    
    return class_mapping

def setup_logging(log_dir):
    """
    设置日志记录器
    
    参数:
        log_dir: 日志保存目录
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件路径
    log_file = os.path.join(log_dir, f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # 明确指定UTF-8编码
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """
    主函数，负责YOLOv8模型训练的整个流程
    
    流程包括：
    1. 检查并选择训练设备（GPU或CPU）
    2. 自动检测并转换LabelMe格式标注文件
    3. 验证数据集完整性
    4. 详细检查数据集
    5. 让用户选择预训练模型大小
    6. 设置训练结果名称
    7. 创建日志文件夹
    8. 配置训练参数
    9. 运行模型训练
    10. 评估训练后的模型
    11. 输出训练结果信息
    """
    # 检查CUDA（GPU支持）是否可用
    training_device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print("Using device:", training_device)

    # 获取数据集根目录
    dataset_dir = os.path.abspath('dataset')
    
    # 检查数据集目录是否存在
    if not os.path.exists(dataset_dir):
        print(f'❌ 错误: 找不到数据集目录 {dataset_dir}')
        print(f'   解决方案: 创建dataset目录并按照以下结构组织数据:')
        print(f'   dataset/')
        print(f'   ├── data.yaml')
        print(f'   ├── train/')
        print(f'   │   ├── images/')
        print(f'   │   └── labels/')
        print(f'   └── valid/')
        print(f'       ├── images/')
        print(f'       └── labels/')
        input("\nPress Enter to exit...")
        return
    
    # 自动转换LabelMe格式标注文件
    print("\n=== 开始自动转换LabelMe标注文件 ===")
    class_mapping = batch_convert_labelme_to_yolo(dataset_dir)
    if not class_mapping:
        print(f'❌ 警告: 未找到有效的类别映射')
        print(f'   解决方案: 检查dataset目录下的data.yaml文件是否包含正确的类别信息')
    
    # 验证数据集完整性
    print("\n=== 开始验证数据集完整性 ===")
    if not validate_dataset(dataset_dir):
        print(f'\n❌ 训练无法继续，数据集验证失败')
        print(f'   请根据上述错误信息修复数据集问题后重新运行')
        input("\nPress Enter to exit...")
        return
    
    # 详细检查数据集
    print("\n=== 开始详细检查数据集 ===")
    detailed_dataset_check(dataset_dir)

    # 模型选项字典，包含不同大小的YOLOv8预训练模型
    # 从大到小排列：Extra Large -> Nano
    model_options = {
        "1": "yolov8x.pt",  # Extra Large，最大的模型，性能最好但训练和推理速度最慢
        "2": "yolov8l.pt",  # Large
        "3": "yolov8m.pt",  # Medium
        "4": "yolov8s.pt",  # Small
        "5": "yolov8n.pt"   # Nano，最小的模型，训练和推理速度最快但性能可能较低
    }

    # 显示模型选择菜单
    print("\n=== 选择YOLOv8模型 ===")
    for key, value in model_options.items():
        # 获取模型描述注释
        comment_start = model_options[key].find("#")
        if comment_start != -1:
            model_desc = model_options[key][comment_start + 2:]
        else:
            model_desc = ""
        print(f"   {key}. {value.split()[0]} - {model_desc}")
    
    # 获取用户选择
    while True:
        choice = input("\n请输入模型编号 (1-5): ").strip()
        if choice in model_options:
            break
        print(f"❌ 输入无效，请输入1-5之间的数字")
    
    selected_model_name = model_options[choice]
    
    # 检查本地是否已存在该模型文件
    local_model_path = os.path.abspath(selected_model_name)
    if os.path.exists(local_model_path):
        starting_model = local_model_path
        print(f"使用本地已存在的模型: {starting_model}")
    else:
        # 自动下载模型，不询问用户
        print(f"未找到本地模型文件 {selected_model_name}，将自动从Ultralytics服务器下载...")
        starting_model = selected_model_name
        print(f"模型将自动下载并使用: {starting_model}")

    # 获取用户输入的训练任务名称
    import datetime
    default_name = f"watermark_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    custom_name = input(f"\n请输入训练任务名称 (默认: {default_name}): ").strip()
    if not custom_name:
        custom_name = default_name
    
    print(f"\n训练结果将保存到: training_output/{custom_name}")
    print(f"日志文件将保存到: log/{custom_name}")

    # 训练参数设置
    output_dir = 'training_output'      # 训练结果输出目录
    log_base_dir = 'log'                # 日志根目录
    log_dir = os.path.join(log_base_dir, custom_name)  # 任务日志目录
    batch_size = 8                      # 批处理大小，与之前成功训练一致
    epoch_count = 50                   # 训练轮数，恢复到之前的150轮
    img_size = 640                      # 输入图像大小
    lr0 = 0.0001                        # 初始学习率，使用更小的值以提高稳定性
    weight_decay = 0.0005               # 权重衰减
    momentum = 0.937                    # 动量
    cos_lr = True                       # 使用余弦退火学习率调度

    # 创建必要的目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 设置日志记录
    logger = setup_logging(log_dir)
    logger.info("YOLOv8训练任务开始")
    logger.info(f"训练任务名称: {custom_name}")
    logger.info(f"使用设备: {training_device}")
    logger.info(f"选择模型: {starting_model}")

    # 获取数据集配置文件的绝对路径
    dataset_path = os.path.abspath('dataset/data.yaml')
    
    # 删除旧的标签缓存文件，强制YOLO重新解析标签
    cache_files = [
        os.path.join(os.path.dirname(dataset_path), 'train', 'labels.cache'),
        os.path.join(os.path.dirname(dataset_path), 'valid', 'labels.cache'),
        os.path.join(os.path.dirname(dataset_path), 'test', 'labels.cache')
    ]
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logger.info(f"已删除旧的标签缓存文件: {cache_file}")
    
    # 检查并删除training_output目录下的所有.cache文件
    training_output_dir = os.path.join(os.getcwd(), 'training_output')
    if os.path.exists(training_output_dir):
        for root, dirs, files in os.walk(training_output_dir):
            for file in files:
                if file.endswith('.cache'):
                    cache_file = os.path.join(root, file)
                    try:
                        os.remove(cache_file)
                        logger.info(f"已删除训练输出目录下的缓存文件: {cache_file}")
                    except Exception as e:
                        logger.error(f"删除缓存文件失败 {cache_file}: {str(e)}")
    
    # 验证缓存是否已删除
    logger.info("验证缓存文件删除情况:")
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            logger.warning(f"警告: 缓存文件仍存在 {cache_file}")
        else:
            logger.info(f"确认: 缓存文件已删除 {cache_file}")
    
    # 加载YOLO模型
    print(f"正在加载YOLO模型: {starting_model}")
    logger.info(f"正在加载YOLO模型: {starting_model}")
    
    try:
        modelYolo = YOLO(starting_model)
        print("YOLO模型加载完成")
        logger.info("YOLO模型加载完成")
        
        # 调试输出：打印模型配置和参数
        logger.info(f"模型类型: {type(modelYolo.model)}")
        logger.info(f"模型设备: {next(modelYolo.model.parameters()).device}")
        logger.info(f"模型类别数: {modelYolo.model.model[-1].nc}")
        
        # 打印前几层的参数信息
        for name, param in list(modelYolo.model.named_parameters())[:5]:
            logger.info(f"参数 {name}: 形状={param.shape}, 均值={param.mean().item():.4f}, 标准差={param.std().item():.4f}")
    except Exception as e:
        print(f"模型加载失败: {e}")
        logger.error(f"模型加载失败: {e}")
        input("\nPress Enter to exit...")
        return
    
    try:
        # 检查数据集配置文件是否存在
        if not os.path.exists(dataset_path):
            print(f'❌ 错误: 找不到数据集配置文件 {dataset_path}')
            print(f'   解决方案: 确保data.yaml文件存在于dataset目录中')
            input("\nPress Enter to exit...")
            return
        
        # 添加更多调试信息
        logger.info(f"数据集路径: {dataset_path}")
        logger.info(f"类别映射: {class_mapping}")
        logger.info(f"训练参数: epochs={epoch_count}, batch={batch_size}, imgsz={img_size}, lr0={lr0}")
        
        # 开始训练模型
        logger.info("开始模型训练...")
        try:
            modelYolo.train(
                data=dataset_path,              # 数据集配置文件路径
                epochs=epoch_count,             # 训练轮数
                batch=batch_size,               # 批处理大小
                imgsz=img_size,                 # 输入图像大小
                device=training_device,         # 训练设备
                project=output_dir,             # 输出项目目录
                name=custom_name,               # 训练结果名称
                workers=2,                      # 工作线程数，为Windows稳定性降低此值
                lr0=lr0,                        # 初始学习率
                weight_decay=weight_decay,      # 权重衰减
                momentum=momentum,              # 动量
                cos_lr=cos_lr,                  # 使用余弦退火学习率调度
                cache=False,                    # 禁用缓存，强制重新解析标签
                augment=True,                   # 启用数据增强，与之前成功训练一致
                mosaic=1.0,                     # 启用马赛克数据增强
                fliplr=0.5,                     # 启用水平翻转
                flipud=0.0,                     # 禁用垂直翻转
                mixup=0.0,                      # 禁用混合
                amp=False                       # 禁用自动混合精度，提高数值稳定性
            )
        except Exception as train_error:
            logger.error(f"训练过程中发生错误: {str(train_error)}")
            print("\n" + "="*60)
            print("模型训练失败！")
            print("="*60)
            print(f"错误信息: {str(train_error)}")
            
            # 提供常见错误的解决方案
            if "CUDA out of memory" in str(train_error):
                print(f"\n🔍 问题分析: GPU内存不足")
                print(f"   解决方案: 减小batch_size（当前为{batch_size}）或imgsz（当前为{img_size}）")
                print(f"   例如: 将batch_size改为4，imgsz改为480")
            elif "No labels found" in str(train_error):
                print(f"\n🔍 问题分析: 未找到标签文件")
                print(f"   解决方案: 检查labels目录中的标签文件是否存在且格式正确")
                print(f"   标签文件应为.txt格式，每行包含：类别ID 中心点x 中心点y 宽度 高度")
            elif "AssertionError" in str(train_error) and "dataset" in str(train_error):
                print(f"\n🔍 问题分析: 数据集配置错误")
                print(f"   解决方案: 检查data.yaml文件中的路径和类别配置是否正确")
            else:
                print(f"\n🔍 建议: 查看完整日志文件以获取更多详细信息")
            
            print(f"日志目录: {os.path.abspath(log_dir)}")
            print("="*60)
            input("\nPress Enter to exit...")
            return
        
        logger.info("模型训练完成")
        
        # 在验证集上评估模型性能
        logger.info("开始模型评估...")
        try:
            metrics = modelYolo.val()
        except Exception as val_error:
            logger.error(f"模型评估过程中发生错误: {str(val_error)}")
            print("\n⚠️  警告: 模型评估失败，但训练已完成")
            print(f"错误信息: {str(val_error)}")
        
        logger.info("模型评估完成")
        
        # 训练成功信息
        training_success = True
        
        # 将默认的best.pt重命名为用户输入的名称
        default_model_path = os.path.join(output_dir, custom_name, 'weights', 'best.pt')
        custom_model_path = os.path.join(output_dir, custom_name, 'weights', f'{custom_name}.pt')
        
        if os.path.exists(default_model_path):
            os.rename(default_model_path, custom_model_path)
            logger.info(f"模型文件已从best.pt重命名为{custom_name}.pt")
        
        # 将模型文件复制到models文件夹，方便用户查找
        models_folder = os.path.join(os.getcwd(), 'models')
        os.makedirs(models_folder, exist_ok=True)  # 确保models文件夹存在
        
        models_model_path = os.path.join(models_folder, f'{custom_name}.pt')
        
        # 使用shutil.copy2保留文件元数据
        import shutil
        shutil.copy2(custom_model_path, models_model_path)
        logger.info(f"模型文件已复制到models文件夹: {models_model_path}")
        
        model_path = models_model_path
        
        # 输出训练结果信息
        print("\n" + "="*60)
        print("模型训练完成！")
        print("="*60)
        print(f"训练状态: {'成功' if training_success else '失败'}")
        print(f"训练任务名称: {custom_name}")
        print(f"模型路径: {os.path.abspath(model_path)}")
        print(f"日志目录: {os.path.abspath(log_dir)}")
        print(f"训练输出目录: {os.path.abspath(os.path.join(output_dir, custom_name))}")
        print("="*60)
        
        # 记录到日志
        logger.info(f"训练结果: {'成功' if training_success else '失败'}")
        logger.info(f"最佳模型路径: {os.path.abspath(model_path)}")
        if logger.handlers:
            logger.info(f"日志文件路径: {logger.handlers[0].baseFilename}")
    except Exception as e:
        training_success = False
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        print("\n" + "="*60)
        print("程序执行失败！")
        print("="*60)
        print(f"错误信息: {str(e)}")
        print(f"日志目录: {os.path.abspath(log_dir)}")
        print(f"\n🔍 建议: 查看完整日志文件以获取更多详细信息")
        print("="*60)

    # 等待用户输入后退出
    input("\nPress Enter to exit...")

# 确保脚本在直接运行时执行main函数
if __name__ == '__main__':
    main()
