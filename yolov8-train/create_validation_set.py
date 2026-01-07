import os
import shutil
import random
import glob

# 分割数据集为训练集和验证集
print("正在分割数据集...")

# 设置随机种子
random.seed(42)

# 获取所有图像文件
train_images = glob.glob('dataset/train/images/*.jpg') + glob.glob('dataset/train/images/*.png')
print(f"总图像数量: {len(train_images)}")

# 随机打乱图像列表
random.shuffle(train_images)

# 计算验证集大小 (20%)
val_size = int(len(train_images) * 0.2)

# 分割数据集
train_set = train_images[val_size:]
val_set = train_images[:val_size]

print(f"训练集大小: {len(train_set)}")
print(f"验证集大小: {len(val_set)}")

# 确保验证集目录存在
os.makedirs('dataset/valid/images', exist_ok=True)
os.makedirs('dataset/valid/labels', exist_ok=True)

# 移动验证集文件
for img_path in val_set:
    # 移动图像文件
    img_basename = os.path.basename(img_path)
    val_img_path = os.path.join('dataset/valid/images', img_basename)
    shutil.move(img_path, val_img_path)
    
    # 移动TXT标签文件
    txt_basename = os.path.splitext(img_basename)[0] + '.txt'
    train_txt_path = os.path.join('dataset/train/labels', txt_basename)
    val_txt_path = os.path.join('dataset/valid/labels', txt_basename)
    if os.path.exists(train_txt_path):
        shutil.move(train_txt_path, val_txt_path)
    
    # 移动JSON标签文件（可选）
    json_basename = os.path.splitext(img_basename)[0] + '.json'
    train_json_path = os.path.join('dataset/train/labels', json_basename)
    val_json_path = os.path.join('dataset/valid/labels', json_basename)
    if os.path.exists(train_json_path):
        shutil.move(train_json_path, val_json_path)

print("数据集分割完成！")

# 检查数据集结构
print("\n数据集结构:")
print('├── dataset/')
print('│   ├── train/')
print(f'│   │   ├── images/ ({len(os.listdir("dataset/train/images"))} files)')
print(f'│   │   └── labels/ ({len(os.listdir("dataset/train/labels"))} files)')
print('│   └── valid/')
print(f'│       ├── images/ ({len(os.listdir("dataset/valid/images"))} files)')
print(f'│       └── labels/ ({len(os.listdir("dataset/valid/labels"))} files)')
