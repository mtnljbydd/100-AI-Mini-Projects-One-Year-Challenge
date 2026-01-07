#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据集完整性检查脚本

功能描述：
1. 检查当前工作目录和数据集目录结构
2. 统计训练集和验证集的图像与标签文件数量
3. 显示第一个训练集标签文件的内容
4. 检查并显示训练集中使用的所有类别ID

使用方法：
直接运行此脚本，无需参数
python check_dataset.py

输出内容：
- 当前工作目录路径
- 数据集目录结构（前5个文件）
- 训练集和验证集的文件数量统计
- 第一个标签文件的具体内容
- 训练集中使用的类别ID列表和数量
"""
import os
import glob

# 检查当前目录
print('当前工作目录:', os.getcwd())

# 检查数据集目录结构
dataset_dir = 'dataset'
print('\n数据集目录结构:')
if os.path.exists(dataset_dir):
    for root, dirs, files in os.walk(dataset_dir):
        level = root.replace(dataset_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # 只显示前5个文件
            print(f'{subindent}{file}')
        if len(files) > 5:
            print(f'{subindent}... 还有 {len(files) - 5} 个文件')
else:
    print('数据集目录不存在')

# 统计文件数量
train_images = glob.glob('dataset/train/images/*.*')
train_labels = glob.glob('dataset/train/labels/*.txt')
valid_images = glob.glob('dataset/valid/images/*.*')
valid_labels = glob.glob('dataset/valid/labels/*.txt')

print(f'\n训练集图像: {len(train_images)}')
print(f'训练集标签: {len(train_labels)}')
print(f'验证集图像: {len(valid_images)}')
print(f'验证集标签: {len(valid_labels)}')

# 检查标签文件内容
train_label_files = glob.glob('dataset/train/labels/*.txt')
if train_label_files:
    print(f'\n第一个训练集标签文件内容:')
    with open(train_label_files[0], 'r') as f:
        content = f.read()
    print(content)
    
    # 检查所有标签文件中的类别ID
    print('\n检查标签文件中的类别ID:')
    all_class_ids = set()
    for lbl_path in train_label_files:
        with open(lbl_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split()
            if parts:
                class_id = int(parts[0])
                all_class_ids.add(class_id)
    print(f'训练集中使用的类别ID: {sorted(all_class_ids)}')
    print(f'类别ID数量: {len(all_class_ids)}')
