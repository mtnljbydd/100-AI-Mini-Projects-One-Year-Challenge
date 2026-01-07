#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证集检查脚本

功能描述：
1. 检查验证集图像和标签文件的对应关系
2. 统计验证集图像和标签文件数量
3. 识别缺少标签的图像文件
4. 识别缺少图像的标签文件
5. 显示示例标签文件的内容

使用方法：
直接运行此脚本，无需参数
python check_valid_set.py

输出内容：
- 验证集图像和标签文件数量
- 缺少标签的图像文件列表（如果有）
- 缺少图像的标签文件列表（如果有）
- 前3个标签文件的内容示例（每个文件显示前5行）

检查逻辑：
1. 获取验证集所有图像和标签文件
2. 比较图像和标签的文件名（不含扩展名）
3. 找出不匹配的文件
4. 显示示例标签文件内容
"""
import os
import glob

# 检查验证集的图像和标签是否匹配
print("检查验证集图像和标签的对应关系...")

# 获取验证集的图像和标签文件
valid_img_files = glob.glob('dataset/valid/images/*.*')
valid_lbl_files = glob.glob('dataset/valid/labels/*.txt')

print(f'验证集图像文件数量: {len(valid_img_files)}')
print(f'验证集标签文件数量: {len(valid_lbl_files)}')

# 提取文件名（不含扩展名）
img_basenames = {os.path.splitext(os.path.basename(img))[0] for img in valid_img_files}
lbl_basenames = {os.path.splitext(os.path.basename(lbl))[0] for lbl in valid_lbl_files}

# 检查是否有图像缺少标签
missing_labels = img_basenames - lbl_basenames
if missing_labels:
    print(f'\n警告: 以下 {len(missing_labels)} 个图像缺少标签:')
    for basename in sorted(missing_labels):
        print(f'  - {basename}')
else:
    print('\n所有验证集图像都有对应的标签文件')

# 检查是否有标签缺少图像
missing_images = lbl_basenames - img_basenames
if missing_images:
    print(f'\n警告: 以下 {len(missing_images)} 个标签缺少图像:')
    for basename in sorted(missing_images):
        print(f'  - {basename}')
else:
    print('\n所有验证集标签都有对应的图像文件')

# 检查几个示例标签文件的内容
print('\n示例标签文件内容:')
sample_lbl_files = valid_lbl_files[:3]  # 只检查前3个标签文件
for lbl_path in sample_lbl_files:
    print(f'\n{os.path.basename(lbl_path)}:')
    with open(lbl_path, 'r') as f:
        lines = f.readlines()
    for line in lines[:5]:  # 只显示前5行
        print(f'  {line.strip()}')
    if len(lines) > 5:
        print(f'  ... 还有 {len(lines) - 5} 行')

print('\n检查完成')
