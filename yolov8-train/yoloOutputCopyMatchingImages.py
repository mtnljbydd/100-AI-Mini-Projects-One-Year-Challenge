"""
图像匹配复制脚本

该脚本用于根据图像文件在两个不同目录中的存在情况来筛选和复制选定的图像文件。
主要用例是识别在一个目录('curated_dir')中有对应注释文件且也存在于另一个目录('original_dir')中的图像文件。
一旦识别，这些选定的图像文件会从'original_dir'复制到第三个目录('matching_dir')，用于进一步处理或分析。

简单来说，该脚本用于根据精选的图像集合找到原始图像文件，这些精选图像可能已被修改（缩小、压缩、叠加预测图形等）。

脚本操作流程：
1. 从'curated_dir'读取图像文件名称，假设该目录中存在图像文件表示它有对应的注释文件
2. 检查这些图像文件是否也存在于'original_dir'目录中，确保只考虑同时存在于两个目录中的文件
3. 符合上述条件的文件被复制到'matching_dir'，如果该目录不存在则创建它
4. 在整个过程中，脚本记录其操作，提供有关正在处理的文件和遇到的任何差异的反馈，例如预期位置中缺少的文件

此工具在机器学习工作流中特别有用，其中需要根据特定标准（如注释的可用性）从较大的数据集中隔离图像子集。

使用方法：
1. 确保脚本从项目根目录运行
2. 配置目录路径参数
3. 运行脚本，将根据精选目录中的图像复制对应的原始图像
"""
import os
import shutil

# 目录路径配置
original_dir = 'input/original'  # 包含所有图像文件的目录，这是源图像文件夹，不需要有任何注释或说明。脚本将从此处复制匹配的图像
curated_dir = 'input/curated'    # 包含您选择保留的图像的目录，但这些图像已缩小或叠加了预测图形
matching_dir = 'input/matching'  # 选定图像文件的目标目录，将其视为输出目录

# 支持的图像扩展名
image_extensions = ['.jpg', '.jpeg', '.png']  # 可根据需要添加更多扩展名

# 脚本执行开始
print(f"精选目录: {curated_dir}")
print(f"原始目录: {original_dir}")
print(f"匹配输出目录: {matching_dir}")

# 如果匹配目录不存在，则创建它
if not os.path.exists(matching_dir):
    os.makedirs(matching_dir)
    print(f"已创建匹配目录: {matching_dir}")

# 检查文件扩展名是否匹配支持的图像类型的函数
def is_supported_image(file_name):
    """
    检查文件名是否具有支持的图像扩展名
    
    参数:
        file_name: 要检查的文件名
    
    返回:
        bool: 如果是支持的图像类型则返回True，否则返回False
    """
    return any(file_name.lower().endswith(ext) for ext in image_extensions)

# 列出精选目录中所有支持的图像文件
curated_files = [f for f in os.listdir(curated_dir) if is_supported_image(f)]
print(f"精选目录中的图像文件: {curated_files}")

# 遍历精选目录中的每个文件
for file_name in curated_files:
    # 构建原始目录和精选目录中的完整文件路径
    original_file_path = os.path.join(original_dir, file_name)
    curated_file_path = os.path.join(curated_dir, file_name)

    # 检查图像文件是否同时存在于原始目录和精选目录中
    if os.path.exists(original_file_path) and os.path.exists(curated_file_path):
        # 构建匹配目录中的目标路径
        matching_file_path = os.path.join(matching_dir, file_name)

        # 将文件从原始目录复制到匹配目录
        shutil.copy(original_file_path, matching_file_path)
        print(f"已复制: {original_file_path} -> {matching_file_path}")
    else:
        # 如果文件在任一目录中缺失，则打印错误消息
        if not os.path.exists(original_file_path):
            print(f"原始文件不存在: {original_file_path}")
        if not os.path.exists(curated_file_path):
            print(f"精选文件不存在: {curated_file_path}")

print("处理完成。")