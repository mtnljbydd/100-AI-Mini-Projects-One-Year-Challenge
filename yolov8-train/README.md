# YOLOv8 自定义目标检测与分割工具集

## 项目简介
这是我基于 YOLOv8 框架开发的一套完整的目标检测与分割解决方案。在实际项目开发过程中，我发现原始的 YOLOv8 虽然功能强大，但在数据处理、训练流程管理和结果分析方面还有很多可以优化的地方。因此，我整合并开发了这套工具集，旨在提供一个更加便捷、高效的模型开发流程。

该工具集特别优化了 Windows 环境下的使用体验，包含了从数据准备、模型训练、推理测试到结果分析的完整工作流，并添加了许多实用的辅助功能，如数据集自动检查与修复、标注格式转换等。

> [!IMPORTANT]
> 需要 **Python 3.11** 或更新版本，推荐使用 CUDA 加速以获得最佳性能。

## Windows 安装说明

### 方法一：使用 Python 虚拟环境 (venv)
1. **创建虚拟环境**
   
在项目根目录创建并激活 Python 虚拟环境：
```bash
python -m venv venv
venv\Scripts\activate
```

2. **安装支持 CUDA 的 PyTorch**
   
根据您系统的 CUDA 版本，从 [Pytorch.org](https://pytorch.org/) 安装 PyTorch。
如果不确定 CUDA 版本，可先安装 [Cuda Toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64) 11.8 或更高版本，然后执行：
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **安装 Ultralytics 和项目依赖**
在激活的虚拟环境中，安装 YOLOv8 核心库和项目所需的其他包：

```bash
pip install ultralytics
pip install -r requirements.txt
```

> [!TIP]
> 未来使用时，只需在项目根目录运行 `venv\Scripts\activate` 即可激活虚拟环境。

### 方法二：使用 Conda 创建环境
1. **创建 Conda 环境**

   在命令行中执行以下命令创建名为 `yolov8_env` 的环境（推荐 Python 3.10 或 3.11）：
   ```bash
   conda create -n yolov8_env python=3.10 -y
   ```

2. **激活 Conda 环境**
   ```bash
   conda activate yolov8_env
   ```

3. **安装支持 CUDA 的 PyTorch**
   
   使用 Conda 安装 PyTorch（CUDA 11.8 版本）：
   ```bash
   conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
   ```
   
   或者使用 pip 安装（如果 Conda 安装遇到问题）：
   ```bash
   pip install torch==2.3.1+cu118 torchvision==0.18.1+cu118 --index-url https://download.pytorch.org/whl/cu118
   ```

4. **安装项目依赖**
   
   安装 Ultralytics 和其他项目依赖：
   ```bash
   pip install ultralytics==8.1.25
   pip install -r requirements.txt
   ```

> [!TIP]
> 未来使用时，只需运行 `conda activate yolov8_env` 即可激活环境。

## 环境版本要求

### 核心依赖版本
| 依赖包 | 版本要求 | 说明 |
|-------|---------|------|
| Python | 3.10+ | 推荐使用 Python 3.10 或 3.11 |
| PyTorch | 2.3.1+cu118 | 带 CUDA 11.8 支持的版本 |
| torchvision | 0.18.1+cu118 | 与 PyTorch 版本匹配 |
| Ultralytics | 8.1.25 | YOLOv8 核心库 |
| numpy | 1.26.4+ | 数值计算库 |
| opencv-python | 4.10.0+ | 计算机视觉库 |

### CUDA 版本要求
- 推荐 CUDA 11.8 或更高版本
- 若使用 CPU 训练，可安装不带 CUDA 的 PyTorch 版本

## 项目结构

- **dataset/**: 存放数据集图片和标注文件
  - **train/**: 训练集数据（images/labels）
  - **valid/**: 验证集数据（images/labels）
- **input/matching/**: 用于检测测试的输入图片目录
- **models/**: 存储预训练模型和训练后的模型权重
- **training_output/**: 保存训练结果、模型权重、评估曲线和测试数据
- **log/**: 训练日志文件
- **核心脚本**: train.py（训练）、generate.py（推理）
- **辅助工具**: 数据集检查、修复和格式转换脚本
	
## Scripts Overview

> **Important:** 运行任何脚本前，请确保已激活虚拟环境。

### 核心功能脚本
- **train.py**: 我的核心训练脚本，在原始 YOLOv8 训练功能基础上，添加了自动标签转换、数据集验证和智能错误处理功能
- **generate.py**: 推理脚本，支持检测和分割两种模式，可自定义置信度阈值和类别过滤

### 个人优化亮点
在使用过程中，我发现数据集问题是最常见的训练障碍，因此特别开发和优化了以下功能：
- **自动数据集验证**：训练前自动检查数据完整性和格式正确性
- **智能错误提示**：提供详细的错误信息和解决方案，减少调试时间
- **一键数据修复**：通过 fix_dataset.py 自动修复常见的标签格式问题
- **可视化训练日志**：训练过程中实时显示关键指标，便于监控训练效果

### 辅助脚本
- **yoloOutputCopyMatchingImages.py**: 帮助根据匹配名称从一个文件夹选择和复制图像用于进一步处理
- **yoloOutputToYoloAnnotations.py**: 将检测输出转换为YOLO训练注释格式
- **CocoGetClasses.py**: 从COCO数据集中提取类别名称用于YOLO训练
- **cocoToYoloAnnotations.py**: 将COCO注释转换为YOLO格式

### 检查脚本
- **check_dataset.py**: 检查数据集目录结构和文件数量
- **check_duplicate_images.py**: 检查重复图像和标签文件
- **check_duplicate_labels.py**: 检查重复标签文件
- **check_labels.py**: 验证标签格式和类别分布
- **check_valid_set.py**: 检查验证集图像和标签的对应关系

### 修复与维护脚本
- **create_validation_set.py**: 从训练集自动分割数据创建验证集
- **fix_dataset.py**: 自动修复数据集标签文件中的格式错误和坐标问题

## Scripts In Detail

### 数据处理工具
- **yoloOutputCopyMatchingImages.py**: 从原始图像文件夹中复制与检测结果匹配的图像，用于筛选有效检测样本
- **yoloOutputToYoloAnnotations.py**: 将检测输出转换为YOLO训练标注格式，便于从检测结果中生成新的训练数据
- **dataset/CocoGetClasses.py**: 从COCO格式数据集中提取类别名称，用于配置YOLO训练
- **dataset/cocoToYoloAnnotations.py**: 将COCO格式标注转换为YOLO训练格式，支持跨格式数据迁移

### 检查脚本详细说明

> **check_dataset.py**:
> 检查数据集的目录结构和文件数量，帮助您确认数据集是否符合YOLOv8的要求。
> - 输出数据集目录结构
> - 统计训练集和验证集的图像与标签文件数量
> - 显示第一个标签文件的内容作为示例
> - 列出所有唯一的类别ID
> 
> 用法: `python check_dataset.py`

> **check_duplicate_images.py**:
> 检查数据集中的重复图像和标签文件，避免因重复数据导致的训练偏差。
> - 通过MD5哈希值检查标签文件的重复性
> - 验证对应图像文件是否重复
> - 支持.jpg和.png图像格式检测
> - 输出重复文件组的详细信息
> 
> 用法: `python check_duplicate_images.py`

> **check_duplicate_labels.py**:
> 专注于检查重复的标签文件，确保训练数据的多样性。
> - 计算所有标签文件的MD5哈希值
> - 识别重复内容的标签文件
> - 统计验证集中相同内容的文件数量
> - 显示重复标签内容的示例
> 
> 用法: `python check_duplicate_labels.py`

> **check_labels.py**:
> 验证标签文件的格式和内容是否符合YOLOv8标准。
> - 加载数据集配置文件获取类别信息
> - 检查图像和标签文件的对应关系
> - 验证标签格式、类别ID范围和坐标范围
> - 统计每个类别的样本数量
> - 识别无效标签和缺少样本的类别
> 
> 用法: `python check_labels.py`

> **check_valid_set.py**:
> 专门检查验证集的图像和标签对应关系，确保验证过程的准确性。
> - 统计验证集图像和标签文件数量
> - 识别缺少标签的图像和缺少图像的标签
> - 显示示例标签文件的内容
> 
> 用法: `python check_valid_set.py`

> **create_validation_set.py**:
> 从训练集自动分割一定比例的数据创建验证集，解决验证集为空的问题。
> - 默认从训练集中分割20%的数据到验证集
> - 支持随机种子设置，确保分割结果可重现
> - 自动创建必要的目录结构
> - 同时移动图像文件和对应的标签文件（包括TXT和JSON格式）
> - 显示分割前后的文件数量统计
> 
> 用法: `python create_validation_set.py`

> **fix_dataset.py**:
> 自动检测和修复数据集标签文件中的常见问题。
> - 检查并修复标签格式错误（如分隔符问题）
> - 验证并修正数值类型错误
> - 确保类别ID在有效范围内
> - 修正超出0-1范围的坐标值
> - 检查图像和标签文件的对应关系
> - 支持训练集和验证集的批量修复
> 
> 用法: `python fix_dataset.py`


# 训练自定义检测模型

本节是关于准备和训练自定义检测模型的简要指南。

### 1. 数据集准备

您可以使用以下几种方式准备数据集：
- **直接使用 YOLOv8 格式**：将图像放在 `dataset/train/images`，标注放在 `dataset/train/labels`
- **COCO 格式转换**：使用 `dataset/CocoGetClasses.py` 和 `dataset/cocoToYoloAnnotations.py` 转换COCO数据集
- **LabelMe 标注**：train.py 支持自动检测并转换 LabelMe JSON 标注文件

我在实际项目中使用过 Roboflow 上的水印数据集进行测试，效果良好。您可以根据自己的需求选择合适的数据集。

### 2. 数据集准备

将图像放在 `/train/images` 中，注释放在 `/train/labels` 中。对于 COCO 数据集，使用 `CocoGetClasses.py` 和 `cocoToYoloAnnotations.py` 进行转换。

### 3. 配置 data.yaml

编辑 `data.yaml` 以匹配您的数据集的类别数量和类别名称。


对于我们的水印数据集，它应该是：
```
nc: 1 # 类别数量
names: ['watermark'] # 类别名称
```


> 如果没有列出，您可以尝试下载数据集的 COCO.JSON 版本，然后运行此仓库中的 CocoGetClasses.py 脚本来提取您需要的 dataset.yaml 值。


### 4. 设置 train.py
在 `train.py` 中自定义训练参数，如文件夹名称、起始模型、epoch 数量。

```
"folder_name" 是 `training_output` 目录内的输出文件夹名称。
"starting_model" 是用于训练的模型。您可以从上面的列表中复制标准的 yolov8 模型。Nano 模型是最小的，训练速度更快，但通常性能较差。而 Xtra Large 则相反。如果您有分割数据集，请使用 -seg 模型。
"epoch_count" 您希望训练多少个版本。50 可能是一个很好的起点。对于小型模型或数据集非常小的模型，您可以将其设置为 500。如果 50 个 epoch 内没有任何改进，训练将自动停止。
```

### train.py 新增功能说明

**1. 自动 LabelMe 标注转换**
- 支持自动检测 dataset/train/images 和 dataset/valid/images 目录中的 LabelMe JSON 标注文件
- 自动将其转换为 YOLOv8 格式的标签文件（保存在对应的 labels 目录中）
- 转换前会自动加载 data.yaml 配置文件获取类别信息
- 显示转换进度和结果统计

**2. 增强的错误处理和解决方案**
- 数据集目录不存在时提供创建和准备指南
- data.yaml 配置文件缺失或格式错误时的修复建议
- 标签文件格式错误（如类别ID超范围、坐标超出0-1范围）的具体错误位置和修复方法
- 图像与标签文件不匹配时的排查步骤
- 数据集为空检查（训练集为空报错，验证集为空提供自动分割解决方案）
- CUDA内存不足错误的解决方案
- 训练中断或失败时的错误日志位置提示
- 提供 `create_validation_set.py` 和 `fix_dataset.py` 脚本自动修复常见数据集问题

**3. 智能训练流程**
- 自动检查数据集完整性
- 验证标签格式和内容
- 检测重复文件和无效数据
- 提供详细的错误诊断和修复建议
- 训练过程中自动保存最佳模型

**4. 用户友好的界面**
- 模型选择菜单
- 训练参数配置引导
- 清晰的进度显示
- 训练结果汇总

**注意：** train.py 现在会在训练前自动检查和转换标签文件，如果转换或验证失败，会提供详细的错误信息和解决方案，帮助您快速定位和修复问题。

### 5. 运行 train.py
执行 `train.py` 开始训练过程。模型和结果将保存在 `training_output` 目录中。

训练过程中会显示实时的损失值、精度等指标，您可以直观地了解模型训练进度。如果需要取消训练，可直接关闭窗口或按 `CTRL + C` 中断。

您可以在 `training_output` 目录中找到测试结果和模型。

脚本将始终在 /training_output/project_name/weights/ 目录中保存您的最新模型 (last.pt) 和当前表现最佳的模型 (best.pt)。

### 6. 测试您的模型
训练完成后，使用 `generate.py` 和您的模型在新图像上检测类别。将测试图像放在 `/generate_input` 中，运行脚本以在 `/generate_output` 中生成输出。
将您的输出模型复制到 `models` 目录中。现在是将其重命名为合适名称的好时机，例如 `watermarks_s_yolov8_v1.pt`。
> [!TIP]
> 您可能想要分别尝试 `last.pt` 和 `best.pt`，看看哪个模型对您来说表现最好。

打开 `generate.py` 编辑一些参数。
```
"model_path" 是您的模型路径。
"mode" 应根据您想要输出的内容设置为 detection（检测）或 segmentation（分割）
"selected_classes" 是您希望在运行脚本时识别和检测的类别的列表。
"class_overrides" 是覆盖列表。如果您希望用一个类替换另一个类，可以使用此选项。如果模型在错误的顺序上训练了类，或者您只是希望更改叠加图像中标签的名称，这可能会很有用。
"confidence_threshold" 是检测置信度阈值，高于此阈值才会被视为正检测。
```

现在将所有您想要测试模型的图像放在 `/generate_input` 文件夹中。

在环境中运行 `python generate.py` 启动生成过程。

带注释叠加层的输出图像以及检测文本文件将在 `/generate_output` 文件夹中找到。

推理结果将以图像叠加和文本标注的形式保存，便于直观查看检测效果和进一步分析。


# 个人使用经验与常见问题

在多次使用这套工具集进行实际项目开发后，我总结了一些经验和常见问题的解决方案，希望能帮助你更快上手：

## 数据准备建议
1. **数据质量优先**：确保数据集标注准确，避免模糊或错误标注
2. **类别平衡**：尽量保持各类别样本数量均衡，避免训练偏差
3. **数据增强**：适当使用数据增强技术，但不要过度增强导致数据失真
4. **验证集选择**：验证集应具有代表性，包含各种场景和难度的样本

## 训练技巧
1. **模型选择**：根据硬件条件和精度需求选择合适的模型大小（n/s/m/l/x）
2. **学习率调整**：初始学习率建议设置为 0.01，根据训练曲线调整
3. **训练时长**：监控验证集指标，避免过拟合
4. **权重保存**：定期保存模型权重，以便在训练中断时恢复

## 常见问题解决方案

### 1. 数据集相关错误

#### 训练集为空
```
错误: 训练集为空！请确保在 dataset/train/images 目录中添加图像文件。
```
> [!ERROR]
> 训练集必须包含至少一个图像文件。
> - 检查 dataset/train/images 目录是否存在图像文件
> - 确保图像文件格式被支持（.jpg, .png等）
> - 检查文件夹结构是否正确

#### 验证集为空
```
警告: 验证集为空！这可能会影响模型评估。
建议: 运行 python create_validation_set.py 从训练集自动分割数据。
```
> [!WARNING]
> 虽然验证集为空时训练仍可进行，但会影响模型评估的准确性。
> - 运行 `python create_validation_set.py` 从训练集自动分割20%的数据到验证集
> - 或手动准备验证集数据并放在 dataset/valid 目录中

#### No images found in {img_path}
```
Traceback (most recent call last):
  File "[YOUR INSTALL PATH HERE]\ultralytics\ultralytics-venv\Lib\site-packages\ultralytics\data\base.py", line 119, in get_img_files
    assert im_files, f"{self.prefix}No images found in {img_path}"
AssertionError: train: No images found in D:\AI\Projects\Yolov8Tutorial\dataset\train
```
> [!WARNING]
> 确保您的数据在指定路径中可用。
> - 检查文件夹结构是否正确
> - 确保图像文件格式被支持（.jpg, .png等）
> - 检查data.yaml配置文件中的路径是否正确

#### 标签文件格式错误
```
错误: image1.txt 中的类别ID无效: 10
错误: image2.txt 中的坐标超出范围: [1.2, 0.5, 0.8, 0.6]
```
> [!SOLUTION]
> - 检查data.yaml中的类别数量(nc)是否正确
> - 确保类别ID不超过nc-1
> - 验证坐标值是否在0-1范围内
> - 使用check_labels.py脚本进行批量检查
> - 运行 `python fix_dataset.py` 自动修复标签文件中的格式错误

#### 图像与标签不匹配
```
警告: 有 5 个图像缺少标签
警告: 有 2 个标签缺少图像
```
> [!SOLUTION]
> - 确保每个图像文件都有对应的标签文件（文件名相同，扩展名不同）
> - 删除多余的标签文件
> - 为缺少标签的图像添加标签或移除这些图像
> - 使用check_valid_set.py脚本检查验证集的匹配情况

### 2. 安装与环境错误

#### NotImplementedError: Could not run 'torchvision::nms'
```
NotImplementedError: Could not run 'torchvision::nms' with arguments from the 'CUDA' backend.
```
> [!CAUTION]
> 这可能是 PyTorch 安装问题。
> 
> 激活虚拟环境并运行此命令 `pip list`。
> 
> 查找 torch、torchaudio 和 torchvision 行。它们应该显示类似：
> 
> 	- torch              2.2.0+cu118
> 	- torchaudio         2.2.0+cu118
> 	- torchvision        0.17.0+cu118
> 	  
> 如果它们没有 +cu118，说明您的 CUDA 安装在环境中不起作用。
> 
> 请确保您按照确切的顺序执行安装步骤。如果顺序错误，您可能无法获得一个可用的环境。
> 
> 您可以尝试这个命令看看是否有帮助：`pip install torchvision --upgrade --force-reinstall`.

#### CUDA内存不足错误
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 8.00 GiB total capacity; 6.00 GiB already allocated; 0 bytes free; 6.00 GiB reserved in total by PyTorch)
```
> [!SOLUTION]
> - 减少batch_size参数（在train.py中）
> - 降低图像尺寸（imgsz参数）
> - 使用更小的模型（如yolov8n instead of yolov8l）
> - 关闭其他占用GPU内存的程序
> - 启用梯度累积（如果可用）

### 3. 训练相关错误

#### 训练过程中损失值异常
```
Epoch   1/50:  10%|█         | 1/10 [00:01<00:09,  1.00s/it]  
ERROR: Loss is nan or inf
```
> [!SOLUTION]
> - 检查标签文件是否有异常值（如NaN或无穷大）
> - 确保所有图像都有对应的标签
> - 降低学习率
> - 检查数据集是否包含损坏的图像

#### 训练中断或崩溃
```
KeyboardInterrupt
或
RuntimeError: Unexpected error from cudaGetDeviceCount()
```
> [!SOLUTION]
> - 训练中断后可以从last.pt继续训练
> - 检查GPU驱动是否正常
> - 确保电源供应稳定
> - 考虑降低训练强度（减小batch_size或模型大小）

### 4. 转换相关错误

#### LabelMe转换失败
```
转换失败: dataset/train/images/image1.json - 类别名称 'person' 未在data.yaml中找到
```
> [!SOLUTION]
> - 检查data.yaml中的类别名称是否与LabelMe标注中的名称一致
> - 确保data.yaml文件格式正确
> - 验证LabelMe JSON文件是否完整

### 5. 检查脚本相关问题

#### 重复文件警告
```
找到重复标签组 (哈希: abc123):
  - dataset/train/labels/image1.txt
  - dataset/train/labels/image2.txt
```
> [!SOLUTION]
> - 检查这些文件是否真的是重复的
> - 如果是重复数据，可以考虑删除其中一个
> - 如果是不同图像的相同标签，可以保留

### 6. 其他问题

#### 模型下载失败
```
错误: 无法下载模型 'yolov8n.pt'。请检查网络连接或手动下载。
```
> [!SOLUTION]
> - 检查网络连接
> - 手动下载模型文件到models目录
> - 确保models目录有写入权限

### 7. 数据集自动修复流程

如果您的数据集存在问题，可以使用以下自动修复流程：

1. **检查数据集完整性**：
   ```
   python check_dataset.py
   ```

2. **如果验证集为空**：
   ```
   python create_validation_set.py
   ```

3. **修复标签文件错误**：
   ```
   python fix_dataset.py
   ```

4. **再次验证数据集**：
   ```
   python check_labels.py
   ```

5. **开始训练**：
   ```
   python train.py
   ```

如果您遇到其他问题，可以查看训练日志文件（位于training_output/项目名称/logs目录）获取更详细的错误信息。
