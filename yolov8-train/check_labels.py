#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签文件检查脚本

功能描述：
1. 加载数据集配置文件(data.yaml)获取类别信息
2. 检查训练集和验证集的标签文件
3. 验证图像和标签文件的对应关系
4. 检查标签格式是否正确（每行包含5个值）
5. 验证类别ID是否在有效范围内
6. 检查坐标是否在0-1范围内
7. 统计每个类别的样本数量
8. 识别无效标签和缺少样本的类别

使用方法：
直接运行此脚本，无需参数
python check_labels.py

输出内容：
- 数据集配置信息（类别数量和名称）
- 训练集和验证集的图像与标签数量
- 缺少标签的图像和缺少图像的标签警告
- 标签格式错误、类别ID无效、坐标超范围等错误信息
- 每个类别的样本数量分布
- 没有样本的类别警告
- 无效标签的总数量

检查逻辑：
1. 从data.yaml加载类别配置
2. 遍历train和valid集的标签文件
3. 检查每个标签文件的每一行
4. 验证格式、类别ID和坐标范围
5. 统计类别分布和错误数量
"""
import os
import glob
import yaml

# 加载数据集配置
with open('dataset/data.yaml', 'r', encoding='utf-8') as f:
    data_config = yaml.safe_load(f)

print(f"数据集配置:")
print(f"  类别数量: {data_config['nc']}")
print(f"  类别名称: {data_config['names']}")

# 检查训练集和验证集的标签文件
splits = ['train', 'valid']

for split in splits:
    print(f'\n=== 检查 {split} 集标签 ===')
    
    # 获取图像和标签文件
    image_files = glob.glob(f'dataset/{split}/images/*.*')
    label_files = glob.glob(f'dataset/{split}/labels/*.txt')
    
    print(f'  图像文件数量: {len(image_files)}')
    print(f'  标签文件数量: {len(label_files)}')
    
    # 检查图像和标签的对应关系
    img_basenames = {os.path.splitext(os.path.basename(img))[0] for img in image_files}
    lbl_basenames = {os.path.splitext(os.path.basename(lbl))[0] for lbl in label_files}
    
    missing_labels = img_basenames - lbl_basenames
    missing_images = lbl_basenames - img_basenames
    
    if missing_labels:
        print(f'  警告: 有 {len(missing_labels)} 个图像缺少标签')
    if missing_images:
        print(f'  警告: 有 {len(missing_images)} 个标签缺少图像')
    
    # 检查标签内容
    class_counts = {i: 0 for i in range(data_config['nc'])}
    invalid_labels = 0
    
    for lbl_path in label_files:
        with open(lbl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                print(f'  错误: {os.path.basename(lbl_path)} 中的行格式不正确: {line}')
                invalid_labels += 1
                continue
            
            try:
                class_id = int(parts[0])
                coords = list(map(float, parts[1:5]))
                
                # 检查类别ID是否有效
                if class_id < 0 or class_id >= data_config['nc']:
                    print(f'  错误: {os.path.basename(lbl_path)} 中的类别ID无效: {class_id}')
                    invalid_labels += 1
                    continue
                
                # 检查坐标是否在0-1范围内
                if any(c < 0 or c > 1 for c in coords):
                    print(f'  错误: {os.path.basename(lbl_path)} 中的坐标超出范围: {coords}')
                    invalid_labels += 1
                    continue
                
                # 更新类别计数
                class_counts[class_id] += 1
                
            except ValueError as e:
                print(f'  错误: {os.path.basename(lbl_path)} 中的值转换失败: {line}')
                invalid_labels += 1
                continue
    
    # 打印类别分布
    print(f"  类别分布:")
    for class_id in sorted(class_counts.keys()):
        print(f"    类别 {class_id} ({data_config['names'][class_id]}): {class_counts[class_id]} 个样本")
    
    # 检查是否有类别没有样本
    for class_id in range(data_config['nc']):
        if class_counts[class_id] == 0:
            print(f"  警告: 类别 {class_id} ({data_config['names'][class_id]}) 没有样本")
    
    print(f'  无效标签数量: {invalid_labels}')

print('\n=== 检查完成 ===')
