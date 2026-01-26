import torch
import argparse
import os
from typing import Dict, List, Any, Union

def load_pt_file(pt_path: str) -> Dict[str, Any]:
    """
    加载.pt文件并返回其内容（适配PyTorch 2.6+，支持Ultralytics YOLO模型）
    
    Args:
        pt_path: .pt文件的路径
    
    Returns:
        加载后的字典内容
    
    Raises:
        FileNotFoundError: 文件不存在
        RuntimeError: 文件损坏或不是合法的PyTorch文件
    """
    if not os.path.exists(pt_path):
        raise FileNotFoundError(f"文件不存在: {pt_path}")
    
    try:
        # 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
        # 关键修改：设置weights_only=False以支持加载包含自定义类的YOLO模型
        # 注意：仅在你信任该.pt文件来源时使用此设置！
        pt_content = torch.load(
            pt_path, 
            map_location=torch.device('cpu'),
            weights_only=False  # 关闭仅加载权重的限制，适配YOLO模型
        )
        return pt_content
    except RuntimeError as e:
        raise RuntimeError(f"加载文件失败，可能是文件损坏或非合法的PyTorch文件: {e}")

def extract_labels(pt_content: Dict[str, Any]) -> Union[List[str], None]:
    """
    从.pt文件内容中提取标签信息（适配YOLO模型的标签存储格式）
    
    Args:
        pt_content: 加载后的.pt文件内容
    
    Returns:
        找到的标签列表，如果未找到返回None
    """
    # 扩展YOLO模型常见的标签键名
    label_keys = [
        'labels', 'classes', 'category_names', 'class_names',
        'label_list', 'class_list', 'categories', 'names'  # YOLO模型常用'names'存储标签
    ]
    
    # 情况1：标签直接作为顶级键存在（YOLO模型通常用'names'）
    for key in label_keys:
        if key in pt_content:
            labels = pt_content[key]
            # YOLO的names可能是字典（{0: 'person', 1: 'car'}），需转换为列表
            if isinstance(labels, dict):
                # 按key排序后提取值
                sorted_labels = [str(v) for k, v in sorted(labels.items())]
                return sorted_labels
            elif isinstance(labels, (list, tuple)):
                return [str(label) for label in labels]
            elif isinstance(labels, torch.Tensor):
                return [str(label.item()) for label in labels]
    # 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
    # 情况2：标签在model/state_dict中
    if 'model' in pt_content and hasattr(pt_content['model'], 'names'):
        # YOLO模型的标签可能存在于model.names属性中
        labels = pt_content['model'].names
        if isinstance(labels, dict):
            return [str(v) for k, v in sorted(labels.items())]
    
    # 未找到标签
    return None

def detect_pt_labels(pt_path: str) -> None:
    """
    检测.pt文件的标签并打印结果
    
    Args:
        pt_path: .pt文件的路径
    """
    print(f"=== 开始检测 {pt_path} 的标签信息 ===")
    
    try:
        # 加载.pt文件
        pt_content = load_pt_file(pt_path)
        
        # 提取标签
        labels = extract_labels(pt_content)
        
        if labels:
            print(f"✅ 找到标签信息，共 {len(labels)} 个标签:")
            for idx, label in enumerate(labels, 1):
                print(f"  {idx}. {label}")
        else:
            print("❌ 未在文件中找到标签信息")
            print("\n可能的原因：")
            print("  1. 模型文件的标签存储在自定义嵌套层级中")
            print("  2. 标签键名未包含在label_keys列表中（可自行添加）")
    
    except Exception as e:
        print(f"❌ 检测失败: {str(e)[:500]}")  # 截断过长的错误信息，提升可读性

if __name__ == "__main__":
    # 设置命令行参数
    # 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
    parser = argparse.ArgumentParser(description='检测PyTorch .pt文件中的标签信息（适配YOLO模型）')
    parser.add_argument('pt_path', type=str, help='.pt文件的路径')
    args = parser.parse_args()
    
    # 执行检测
    detect_pt_labels(args.pt_path)