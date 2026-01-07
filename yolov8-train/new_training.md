# YOLOv8 训练与推理使用指南

## 项目概述

本项目提供了一套完整的YOLOv8目标检测和分割模型的训练与推理脚本，支持LabelMe标注文件的自动转换、数据集验证、模型训练和推理等功能。

## 最近的修改

### 1. 增强的数据集验证功能

在 `train.py` 中对数据集验证功能进行了增强，主要修改包括：

- **增加空数据集检查**：自动检测训练集和验证集是否为空
- **明确的错误提示**：当验证集为空时，显示清晰的警告信息
- **智能解决方案建议**：
  - 验证集为空时，建议运行 `python create_validation_set.py` 从训练集分割验证集
  - 标签文件格式错误时，建议使用 `python fix_dataset.py` 进行修复

## 核心脚本文件说明

### 1. 训练相关脚本

#### train.py
- **主要功能**：YOLOv8模型训练的主脚本
- **特性**：
  - 自动检测和转换LabelMe标注文件
  - 全面的数据集验证
  - 支持多种YOLOv8预训练模型选择
  - 灵活的训练参数配置
  - 训练过程可视化和日志记录
- **使用方法**：
  ```bash
  python train.py
  ```

#### create_validation_set.py
- **主要功能**：从训练集中随机分割一部分数据作为验证集
- **特性**：
  - 支持自定义验证集比例（默认为20%）
  - 保持图像和标签文件的对应关系
  - 支持同时移动.txt和.json格式的标签文件
- **使用方法**：
  ```bash
  python create_validation_set.py
  # 或自定义验证集比例
  python create_validation_set.py --val_ratio 0.3
  ```

### 2. 数据集处理脚本

#### convert_labelme_to_yolo.py
- **主要功能**：将LabelMe标注的JSON文件转换为YOLO格式的.txt标签文件
- **特性**：
  - 支持矩形和多边形标注转换
  - 自动读取data.yaml中的类别映射
  - 批量处理整个数据集目录
- **使用方法**：
  ```bash
  python convert_labelme_to_yolo.py
  ```

#### fix_dataset.py
- **主要功能**：检查并修复数据集中的标签文件问题
- **特性**：
  - 修复格式错误的标签行
  - 修正超出范围的坐标值
  - 检查缺失的标签文件
  - 检查训练集和验证集的重复文件
- **使用方法**：
  ```bash
  python fix_dataset.py
  ```

### 3. 数据集检查脚本

#### check_dataset.py
- **主要功能**：全面检查数据集的完整性和结构
- **特性**：
  - 显示数据集目录结构
  - 统计训练集和验证集的文件数量
  - 检查标签文件内容格式
  - 显示使用的类别ID
- **使用方法**：
  ```bash
  python check_dataset.py
  ```

#### check_labels.py
- **主要功能**：检查标签文件的格式和内容
- **特性**：
  - 验证标签行的格式正确性
  - 检查坐标值是否在有效范围内
  - 统计每个类别的样本数量
- **使用方法**：
  ```bash
  python check_labels.py
  ```

#### check_duplicate_images.py
- **主要功能**：检查数据集中的重复图像文件
- **特性**：
  - 通过文件哈希值检测重复图像
  - 支持批量处理目录
- **使用方法**：
  ```bash
  python check_duplicate_images.py
  ```

#### check_duplicate_labels.py
- **主要功能**：检查数据集中的重复标签文件
- **特性**：
  - 通过文件内容检测重复标签
  - 支持批量处理目录
- **使用方法**：
  ```bash
  python check_duplicate_labels.py
  ```

#### check_valid_set.py
- **主要功能**：专门检查验证集的完整性
- **特性**：
  - 验证验证集的图像和标签对应关系
  - 检查验证集的大小是否合适
- **使用方法**：
  ```bash
  python check_valid_set.py
  ```

### 4. 其他工具脚本

#### generate.py
- **主要功能**：生成合成数据集或辅助文件
- **使用方法**：
  ```bash
  python generate.py
  ```

#### yoloOutputCopyMatchingImages.py
- **主要功能**：根据YOLO输出结果复制匹配的图像文件
- **使用方法**：
  ```bash
  python yoloOutputCopyMatchingImages.py
  ```

#### yoloOutputToYoloAnnotations.py
- **主要功能**：将YOLO输出结果转换为YOLO标注格式
- **使用方法**：
  ```bash
  python yoloOutputToYoloAnnotations.py
  ```

## 完整使用流程

### 1. 准备数据集

1. **创建数据集目录结构**：
   ```
   dataset/
   ├── train/
   │   ├── images/      # 训练集图像文件
   │   └── labels/      # 训练集标签文件
   ├── valid/
   │   ├── images/      # 验证集图像文件
   │   └── labels/      # 验证集标签文件
   └── data.yaml        # 数据集配置文件
   ```

2. **配置data.yaml文件**：
   ```yaml
   train: ../train/images
   val: ../valid/images
   nc: 11  # 类别数量
   names: ['windows', 'bolibei', 'bottle', 'cloth', 'computer', 'cpu', 'cup', 'dianxian', 'milk', 'mouse', 'pen']  # 类别名称
   ```

### 2. 数据标注与转换

1. **使用LabelMe标注图像**：
   - 将标注的JSON文件保存在 `dataset/train/labels/` 目录
   - 确保JSON文件名与对应的图像文件名一致

2. **自动转换标注文件**：
   ```bash
   python convert_labelme_to_yolo.py
   ```
   - 或直接运行 `train.py`，它会自动检测并转换LabelMe JSON文件

### 3. 数据集验证与修复

1. **检查数据集完整性**：
   ```bash
   python check_dataset.py
   ```

2. **创建验证集（如果为空）**：
   ```bash
   python create_validation_set.py
   ```

3. **修复数据集问题**：
   ```bash
   python fix_dataset.py
   ```

### 4. 模型训练

1. **运行训练脚本**：
   ```bash
   python train.py
   ```

2. **训练过程**：
   - 自动检测和转换LabelMe标注文件
   - 验证数据集完整性
   - 选择YOLOv8预训练模型
   - 配置训练参数
   - 开始训练
   - 自动保存最佳模型

### 5. 模型使用

- **训练好的模型位置**：`models/` 目录
- **训练日志**：`log/` 目录
- **训练输出**：`training_output/` 目录（包含训练曲线、混淆矩阵等）

## 常见问题与解决方案

### 1. 验证集为空
**问题**：运行 `train.py` 时提示 "验证集为空"
**解决方案**：运行 `python create_validation_set.py` 从训练集分割一部分作为验证集

### 2. 标签文件格式错误
**问题**：运行 `train.py` 时提示 "无效标签文件"
**解决方案**：运行 `python fix_dataset.py` 尝试自动修复，或手动检查并修复标签文件

### 3. 类别ID超出范围
**问题**：标签文件中的类别ID大于data.yaml中定义的类别数量
**解决方案**：检查data.yaml中的nc（类别数量）是否正确，或修复标签文件中的类别ID

### 4. 图像和标签不匹配
**问题**：训练时提示 "缺失标签文件"
**解决方案**：确保每个图像文件都有对应的标签文件（.txt或.json格式）

## 项目结构

```
├── LICENSE
├── README.md
├── new_training.md      # 本使用指南
├── check_dataset.py     # 数据集完整性检查
├── check_duplicate_images.py  # 重复图像检查
├── check_duplicate_labels.py  # 重复标签检查
├── check_labels.py      # 标签格式检查
├── check_valid_set.py   # 验证集检查
├── convert_labelme_to_yolo.py  # LabelMe转YOLO格式
├── create_validation_set.py    # 创建验证集
├── dataset/             # 数据集目录
│   ├── data.yaml        # 数据集配置
│   ├── train/           # 训练集
│   └── valid/           # 验证集
├── fix_dataset.py       # 数据集修复
├── generate.py          # 数据生成工具
├── log/                 # 训练日志
├── models/              # 训练好的模型
├── requirements.txt     # 依赖包
├── setup.bat            # 安装脚本
├── train.py             # 训练主脚本
├── training_output/     # 训练输出结果
├── yoloOutputCopyMatchingImages.py  # 结果处理工具
└── yoloOutputToYoloAnnotations.py   # 结果转换工具
```

## 依赖安装

运行以下命令安装项目依赖：

```bash
pip install -r requirements.txt
```

或使用setup.bat（Windows）：

```bash
setup.bat
```

## 注意事项

1. 确保所有图像文件格式一致（建议使用.jpg或.png）
2. 标签文件的类别ID必须与data.yaml中的定义一致
3. 坐标值必须在0-1之间（YOLO格式要求）
4. 训练前建议先运行数据集检查脚本确保数据完整性
5. 首次训练时会自动下载YOLOv8预训练模型，请确保网络连接正常
