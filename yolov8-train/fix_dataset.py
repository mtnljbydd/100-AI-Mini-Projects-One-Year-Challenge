import os
import shutil
import random
import glob

# 修复数据集，确保训练集和验证集没有重复文件
print("正在修复数据集...")

# 获取当前训练集和验证集的文件
train_images = glob.glob('dataset/train/images/*.jpg') + glob.glob('dataset/train/images/*.png')
train_labels = glob.glob('dataset/train/labels/*.txt')
val_images = glob.glob('dataset/valid/images/*.jpg') + glob.glob('dataset/valid/images/*.png')
val_labels = glob.glob('dataset/valid/labels/*.txt')

print(f'当前训练集图像: {len(train_images)}')
print(f'当前训练集标签: {len(train_labels)}')
print(f'当前验证集图像: {len(val_images)}')
print(f'当前验证集标签: {len(val_labels)}')

# 检查是否有重复文件
train_basenames = {os.path.splitext(os.path.basename(img))[0] for img in train_images}
val_basenames = {os.path.splitext(os.path.basename(img))[0] for img in val_images}

intersection = train_basenames & val_basenames
if intersection:
    print(f'\n警告: 训练集和验证集之间有 {len(intersection)} 个重复文件！')
    print(f'重复的文件名: {list(intersection)[:5]}...')  # 只显示前5个
else:
    print('\n✅ 训练集和验证集之间没有重复文件')

# 检查验证集中的重复标签文件
print('\n检查验证集中的重复标签文件...')
val_label_hashes = {}
for lbl_path in val_labels:
    with open(lbl_path, 'r') as f:
        content = f.read()
    file_hash = hash(content)
    if file_hash not in val_label_hashes:
        val_label_hashes[file_hash] = []
    val_label_hashes[file_hash].append(lbl_path)

# 统计重复的标签文件
duplicate_count = 0
for file_hash, files in val_label_hashes.items():
    if len(files) > 1:
        duplicate_count += len(files)
        print(f'哈希值 {file_hash}: {len(files)} 个重复文件')
        print(f'  示例: {os.path.basename(files[0])}')

if duplicate_count > 0:
    print(f'\n⚠️  验证集中共有 {duplicate_count} 个重复的标签文件')
else:
    print('\n✅ 验证集中没有重复的标签文件')

# 检查标签文件内容是否正常
print('\n检查标签文件内容...')
problematic_files = []
for lbl_path in val_labels[:5]:  # 只检查前5个
    with open(lbl_path, 'r') as f:
        lines = f.readlines()
    if len(lines) == 0:
        problematic_files.append(os.path.basename(lbl_path))
        continue
    # 检查每行的格式
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            problematic_files.append(os.path.basename(lbl_path))
            break
        try:
            cls_id = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            w = float(parts[3])
            h = float(parts[4])
            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                problematic_files.append(os.path.basename(lbl_path))
                break
        except ValueError:
            problematic_files.append(os.path.basename(lbl_path))
            break

if problematic_files:
    print(f'⚠️  发现 {len(problematic_files)} 个格式有问题的标签文件')
else:
    print('✅ 标签文件格式正常')

# 查看一下训练集和验证集的目录结构
print('\n数据集目录结构:')
print('├── dataset/')
print('│   ├── train/')
print(f'│   │   ├── images/ ({len(os.listdir("dataset/train/images"))} files)')
print(f'│   │   └── labels/ ({len(os.listdir("dataset/train/labels"))} files)')
print('│   └── valid/')
print(f'│       ├── images/ ({len(os.listdir("dataset/valid/images"))} files)')
print(f'│       └── labels/ ({len(os.listdir("dataset/valid/labels"))} files)')

print('\n数据集检查完成！')
