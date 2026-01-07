import os
import json
import sys
import tkinter as tk
from tkinter import filedialog

# ========== 强制设置编码，解决打包后中文乱码 ==========
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe运行环境
    import _locale
    _locale._getdefaultlocale = (lambda *args: ['zh_CN', 'utf8'])
else:
    # 如果是普通Python运行环境
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def select_folder():
    """弹出文件夹选择窗口，返回用户选择的文件夹路径"""
    # 隐藏 tkinter 主窗口（只保留文件夹选择弹窗）
    root = tk.Tk()
    root.withdraw()
    # 打开文件夹选择对话框
    folder_path = filedialog.askdirectory(title="请选择包含JSON文件的文件夹（会递归处理子文件夹）")
    return folder_path

def modify_json_label(folder_path, prefix):
    """递归遍历文件夹（含子文件夹）下所有.json文件，修改label字段（排除指定值）"""
    # 定义不需要修改的label值名单
    EXCLUDE_LABELS = {"hand2", "左手", "右手", "手"}
    
    # 检查文件夹路径是否有效
    if not os.path.isdir(folder_path):
        print(f"错误：选择的路径 {folder_path} 不是有效文件夹！")
        return False  # 返回False表示本次处理失败
    
    # 统计修改的文件和字段数量
    modified_files = 0
    modified_labels = 0
    skipped_labels = 0
    
    # 用os.walk递归遍历所有子文件夹
    for root_dir, sub_dirs, files in os.walk(folder_path):
        for filename in files:
            # 只处理.json文件
            if filename.lower().endswith(".json"):
                # 拼接完整的文件路径（包含子文件夹）
                file_path = os.path.join(root_dir, filename)
                try:
                    # 读取JSON文件（强制指定utf-8编码）
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 递归遍历JSON所有层级，找到所有label字段并修改（排除指定值）
                    def update_label(obj):
                        nonlocal modified_labels, skipped_labels
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if key == "label" and isinstance(value, str):
                                    # 判断是否在排除名单中
                                    if value in EXCLUDE_LABELS:
                                        skipped_labels += 1
                                        print(f"跳过 {file_path} 中的label：{value}（属于排除名单）")
                                    else:
                                        # 在label值开头添加前缀
                                        obj[key] = f"{prefix}{value}"
                                        modified_labels += 1
                                else:
                                    update_label(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                update_label(item)
                    
                    # 执行label修改
                    update_label(data)
                    
                    # 写回修改后的内容（强制指定utf-8编码）
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    modified_files += 1
                    print(f"完成处理文件：{file_path}")
                
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错：{str(e)}")
    
    # 输出最终统计结果
    print("\n===== 本轮处理完成 =====")
    print(f"共处理 {modified_files} 个JSON文件（含子文件夹）")
    print(f"共修改 {modified_labels} 个label字段")
    print(f"共跳过 {skipped_labels} 个排除名单内的label字段")
    return True  # 返回True表示本次处理完成

def ask_continue():
    """询问用户是否继续处理，返回True=继续，False=退出"""
    print("\n" + "="*50)
    while True:
        user_choice = input("请选择后续操作：\n输入 'y' 或 '继续' 表示继续处理其他文件夹\n输入 'n' 或 '退出' 表示退出程序\n你的输入：").strip().lower()
        if user_choice in ['y', '继续']:
            return True
        elif user_choice in ['n', '退出']:
            return False
        else:
            print(f"输入错误！你输入的是「{user_choice}」，请重新输入（仅支持 y/继续 或 n/退出）")

if __name__ == "__main__":
    print("===== JSON文件label批量修改工具 =====")
    print("使用说明：\n1. 选择目标文件夹（会递归处理所有子文件夹）\n2. 输入需要添加的前缀字段\n3. 处理完成后可选择继续或退出\n")
    
    # 循环执行，直到用户选择退出
    while True:
        # 1. 选择文件夹
        target_folder = select_folder()
        if not target_folder:
            print("未选择任何文件夹！")
            # 询问是否重新选择
            if not ask_continue():
                break
            continue
        
        print(f"\n已选择文件夹：{target_folder}（将递归处理所有子文件夹）")
        
        # 2. 接收用户输入的前缀
        prefix = input("请输入需要添加的字段：").strip()
        if not prefix:
            print("未输入任何字符！")
            # 询问是否重新操作
            if not ask_continue():
                break
            continue
        
        # 3. 执行修改操作
        print("\n开始批量修改JSON文件中的label字段（跳过hand2/左手/右手/手）...")
        modify_json_label(target_folder, prefix)
        
        # 4. 询问是否继续
        if not ask_continue():
            print("\n程序已退出，感谢使用！")
            break