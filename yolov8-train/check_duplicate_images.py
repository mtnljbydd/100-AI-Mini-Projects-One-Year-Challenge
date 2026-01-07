#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复图像检查脚本

功能描述：
1. 计算所有标签文件的MD5哈希值，识别重复标签
2. 检查重复标签对应的图像文件是否也是重复的
3. 输出重复标签和对应图像的详细信息

使用方法：
直接运行此脚本，无需参数
python check_duplicate_images.py

输出内容：
- 重复标签文件的哈希值和路径
- 重复标签对应的图像是否也是重复的
- 不重复图像的分组信息
- 标签内容示例

检查逻辑：
1. 首先计算所有标签文件的MD5哈希值
2. 找到哈希值相同的重复标签文件
3. 对每个重复标签组，找到对应的图像文件
4. 计算这些图像文件的MD5哈希值
5. 判断图像是否也是重复的并输出结果
"""
import os
import hashlib
import glob

# 计算文件的MD5哈希值
def calculate_hash(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"计算文件哈希值时出错 {file_path}: {e}")
        return None
    return hash_md5.hexdigest()

# 检查重复标签对应的图像是否也是重复的
print("检查重复标签对应的图像...")

# 获取所有标签文件
train_labels = glob.glob('dataset/train/labels/*.txt')
val_labels = glob.glob('dataset/valid/labels/*.txt')
all_labels = train_labels + val_labels

# 计算所有标签文件的哈希值
label_hashes = {}
for lbl_path in all_labels:
    file_hash = calculate_hash(lbl_path)
    if file_hash not in label_hashes:
        label_hashes[file_hash] = []
    label_hashes[file_hash].append(lbl_path)

# 检查每个哈希值对应的所有标签文件
for file_hash, lbl_paths in label_hashes.items():
    if len(lbl_paths) > 1:
        print(f"\n哈希值 {file_hash} 有 {len(lbl_paths)} 个重复标签:")
        
        # 获取对应的图像文件路径
        img_paths = []
        for lbl_path in lbl_paths:
            # 将 labels 替换为 images，将 .txt 替换为 .jpg
            img_path = lbl_path.replace('labels', 'images').replace('.txt', '.jpg')
            if os.path.exists(img_path):
                img_paths.append(img_path)
            else:
                # 尝试 .png 格式
                img_path_png = img_path.replace('.jpg', '.png')
                if os.path.exists(img_path_png):
                    img_paths.append(img_path_png)
                else:
                    print(f"  警告: 图像文件不存在 {img_path}")
        
        # 计算图像文件的哈希值
        img_hashes = {}
        for img_path in img_paths:
            img_hash = calculate_hash(img_path)
            if img_hash not in img_hashes:
                img_hashes[img_hash] = []
            img_hashes[img_hash].append(img_path)
        
        # 输出结果
        if len(img_hashes) == 1:
            print("  ✅ 这些标签对应的图像也是重复的")
            print(f"  图像路径: {img_paths[0]}")
        else:
            print(f"  ❌ 这些标签对应的图像不重复 ({len(img_hashes)} 种不同图像)")
            for i, (img_hash, img_paths_same_hash) in enumerate(img_hashes.items(), 1):
                print(f"  图像组 {i} ({len(img_paths_same_hash)} 个文件):")
                for img_path in img_paths_same_hash:
                    print(f"    {img_path}")
                    
            # 显示其中一个标签文件的内容
            with open(lbl_paths[0], 'r') as f:
                content = f.read()
            print(f"\n  标签内容示例 (来自 {os.path.basename(lbl_paths[0])}):")
            print(content[:200] + "..." if len(content) > 200 else content)

print("\n检查完成！")
