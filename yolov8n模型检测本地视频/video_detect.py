import cv2
import os
import hashlib
from ultralytics import YOLO

# ========== 核心配置：务必确认模型文件名是你自己训练的！ ==========
# 【重点】修改为你自己训练的模型文件名（比如：my_train_model.pt）
model_name = "xxx.pt"  
video_name = "xxx.mp4"        
output_name = "output_detected.mp4"  

# ========== 脚本所在目录（utills） ==========
utills_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(utills_dir, model_name)
video_path = os.path.join(utills_dir, video_name)
output_path = os.path.join(utills_dir, output_name)

# ========== 路径/文件校验 ==========
print("📌 脚本所在目录（utills）：", utills_dir)
print("📌 模型文件路径：", model_path)
print("📌 输入视频路径：", video_path)

# 检查模型是否存在
if not os.path.exists(model_path):
    print(f"\n❌ 模型文件不存在！请确认 {model_name} 在 utills 目录下")
    exit()

# 【新增】验证模型文件（避免加载错误文件）
# 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
def get_file_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()

model_md5 = get_file_md5(model_path)
print(f"📌 模型文件MD5：{model_md5}（可用于验证文件是否正确）")

# 检查视频是否存在
if not os.path.exists(video_path):
    print(f"\n❌ 视频文件不存在！请确认 {video_name} 在 utills 目录下")
    exit()

# ========== 加载模型 ==========
try:
    model = YOLO(model_path)
    model_classes = model.names
    print(f"✅ 模型加载成功！模型包含 {len(model_classes)} 个类别：{list(model_classes.values())}")
    # 【重点提醒】如果这里显示的还是person/car等，说明模型文件不对！
    if 'person' in model_classes.values() and len(model_classes) <= 20:
        print("⚠️ 警告：当前加载的模型是通用预训练模型，不是你自己训练的！")
except Exception as e:
    print(f"❌ 模型加载失败：{e}")
    exit()

# ========== 打开视频文件 ==========
# 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("❌ 无法打开视频文件（可能格式不支持/文件损坏）")
    exit()

# ========== 获取视频参数 + 修复编码问题 ==========
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = cap.get(cv2.CAP_PROP_FPS) or 30

# 【修复编码问题】放弃openh264，使用mp4v/XVID编码（兼容性最好）
# 优先用mp4v，若失败则用XVID
fourcc_options = [cv2.VideoWriter_fourcc(*'mp4v'), cv2.VideoWriter_fourcc(*'XVID')]
out = None
for fourcc in fourcc_options:
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if out.isOpened():
        print(f"✅ 视频写入器初始化成功（编码：{chr(fourcc&0xFF)}{chr((fourcc>>8)&0xFF)}{chr((fourcc>>16)&0xFF)}{chr((fourcc>>24)&0xFF)}）")
        break

if not out or not out.isOpened():
    print("❌ 所有编码格式都无法创建输出视频！")
    cap.release()
    exit()

print(f"🚀 开始检测... | 视频尺寸：{width}x{height} | 帧率：{fps}")

# ========== 逐帧检测 ==========
# 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
frame_count = 0
detected_object_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        results = model(
            frame, 
            conf=0.3, 
            iou=0.5, 
            device="GPU",
            verbose=False
        )[0]

        current_detected = len(results.boxes) if results.boxes is not None else 0
        detected_object_count += current_detected
        annotated_frame = results.plot()
        out.write(annotated_frame)

    except Exception as e:
        print(f"\n⚠️ 第 {frame_count+1} 帧推理出错：{e}")
        out.write(frame)

    frame_count += 1
    if frame_count % 30 == 0:
        print(f"🔄 已处理 {frame_count} 帧 | 累计检测到 {detected_object_count} 个目标")

# ========== 释放资源 ==========
cap.release()
out.release()
cv2.destroyAllWindows()

# ========== 最终统计 ==========
print(f"\n✅ 检测完成！")
print(f"📤 输出视频保存到：{output_path}")
print(f"📊 共处理 {frame_count} 帧 | 累计检测到 {detected_object_count} 个目标")

# 【再次提醒】
if 'person' in model_classes.values():
    print("\n❌ 关键问题：你加载的模型是通用预训练模型，不是自定义训练的！")
    print("请检查：")
    print("  1. 模型文件名是否正确（是否是训练完成后生成的best.pt/last.pt）")
    print("  2. 是否将训练好的模型文件复制到了utills目录下")
    print("  3. 模型文件是否被覆盖（比如误放了官方预训练模型）")