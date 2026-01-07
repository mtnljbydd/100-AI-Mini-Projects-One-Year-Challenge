#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复标签检查脚本

功能描述：
1. 检查训练集和验证集的标签文件是否重复
2. 计算所有标签文件的MD5哈希值以识别重复内容
3. 统计验证集中相同内容的文件数量
4. 显示重复标签的哈希值和路径
5. 输出重复标签内容的示例

使用方法：
直接运行此脚本，无需参数
python check_duplicate_labels.py

输出内容：
- 训练集和验证集的标签文件数量
- 重复标签文件的哈希值和路径
- 验证集中相同内容的文件统计
- 重复标签内容的示例（前3行）

检查逻辑：
1. 首先计算所有训练集和验证集标签文件的MD5哈希值
2. 找到哈希值相同的重复标签文件
3. 统计验证集中每个哈希值对应的文件数量
4. 对重复的标签内容，显示示例内容
"""
import os
import hashlib
import glob

# 计算文件内容的哈希值
def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.md5(content).hexdigest()

# 检查训练集和验证集的标签是否重复
print("检查训练集和验证集的标签是否重复...")

# 获取所有标签文件
train_lbl_files = glob.glob('dataset/train/labels/*.txt')
valid_lbl_files = glob.glob('dataset/valid/labels/*.txt')

# 计算所有标签文件的哈希值
hash_dict = {}

# 检查训练集
print(f'\n检查训练集 ({len(train_lbl_files)} 个文件):')
for lbl_path in train_lbl_files:
    file_hash = get_file_hash(lbl_path)
    if file_hash in hash_dict:
        hash_dict[file_hash].append(lbl_path)
    else:
        hash_dict[file_hash] = [lbl_path]

# 检查验证集
print(f'\n检查验证集 ({len(valid_lbl_files)} 个文件):')
for lbl_path in valid_lbl_files:
    file_hash = get_file_hash(lbl_path)
    if file_hash in hash_dict:
        hash_dict[file_hash].append(lbl_path)
    else:
        hash_dict[file_hash] = [lbl_path]

# 查找重复的标签文件
print('\n重复的标签文件:')
has_duplicates = False
for file_hash, paths in hash_dict.items():
    if len(paths) > 1:
        has_duplicates = True
        print(f'\n哈希值: {file_hash}')
        for path in paths:
            print(f'  {path}')

if not has_duplicates:
    print('\n没有发现重复的标签文件')

# 检查验证集中相同内容的文件数量
print('\n验证集中相同内容的文件统计:')
valid_hashes = {get_file_hash(lbl_path): 0 for lbl_path in valid_lbl_files}
for lbl_path in valid_lbl_files:
    file_hash = get_file_hash(lbl_path)
    valid_hashes[file_hash] += 1

for file_hash, count in valid_hashes.items():
    print(f'哈希值 {file_hash}: {count} 个文件')
    # 显示该哈希值对应的文件内容示例
    if count > 1:
        sample_path = next(p for p in valid_lbl_files if get_file_hash(p) == file_hash)
        print(f'  示例内容 (来自 {os.path.basename(sample_path)}):')
        with open(sample_path, 'r') as f:
            lines = f.readlines()
        for line in lines[:3]:
            print(f'    {line.strip()}')
        if len(lines) > 3:
            print(f'    ... 还有 {len(lines) - 3} 行')

print('\n检查完成')
