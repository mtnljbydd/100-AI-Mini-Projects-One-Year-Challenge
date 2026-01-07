"""
COCO类名提取脚本

该脚本从COCO格式的JSON注释文件中提取类名，并将它们保存为适合在机器学习框架中使用的文本文件，
特别是为YAML配置文件格式化。COCO（Common Objects in Context）格式是目标检测数据集的标准格式，
其中'categories'表示数据集中注释的不同对象类。

使用方法：
1. 将此脚本放在与您的COCO注释文件相同的目录中，注释文件通常命名为'_annotations.coco.json'
2. 如果您的注释文件与'_annotations.coco.json'名称不同，请更新下面的'coco_json'变量
3. 运行脚本，它将提取类名，格式化它们，并将它们保存到指定的输出文件

输出格式：
nc: 类的数量 # number of classes
names: ['类名1', '类名2', ...] # 类名列表
"""
# 导入所需库
import json

# COCO JSON文件路径
# 确保此文件存在于与脚本相同的目录中
coco_json = '_annotations.coco.json'

# 输出文件路径
# 提取的类名将保存到此文件
output_file = 'classes.yaml'

# 从COCO JSON文件中提取类名并以YAML友好格式保存
def extract_classes_and_save(coco_json, output_file):
    """
    从COCO JSON文件中提取类名并保存为YAML格式
    
    参数:
        coco_json: COCO格式的JSON注释文件路径
        output_file: 输出YAML文件路径
    """
    # 加载COCO JSON文件
    with open(coco_json) as file:
        data = json.load(file)

    # 从'categories'部分提取类名
    # 每个category包含'name'字段，代表类名
    classes = [category['name'] for category in data['categories']]
    num_classes = len(classes)  # 计算类的数量

    # 格式化为YAML格式
    # 将类名列表转换为带引号的字符串，并用逗号分隔
    formatted_classes = ", ".join([f"'{cls}'" for cls in classes])
    # 构建完整的YAML内容
    yaml_content = f"nc: {num_classes} # 类的数量\nnames: [{formatted_classes}]"

    # 保存到文件
    with open(output_file, 'w') as f:
        f.write(yaml_content)
    print(f"类名已保存到 {output_file}")

# 执行提取类名并保存的函数
extract_classes_and_save(coco_json, output_file)