import cv2
import os
from ultralytics import YOLO

# ========== 核心：直接写文件名（模型/图片都在utills目录下） ==========
model_name = r"xxx.pt"       # 模型文件名（放utills下）
image_name = r"xxx.jpg"              # 图片文件名（放utills下）
output_name = "output.jpg"              # 结果保存到utills下

# 拼接当前目录路径（确保指向utills目录）
model_path = os.path.join(os.getcwd(), model_name)
image_path = os.path.join(os.getcwd(), image_name)
output_path = os.path.join(os.getcwd(), output_name)

# ========== 路径校验（帮你确认文件是否在utills下） ==========
# 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
print("📌 当前运行目录（utills）：", os.getcwd())
print("📌 模型文件路径：", model_path)
print("📌 图片文件路径：", image_path)

# 检查模型是否在utills下
if not os.path.exists(model_path):
    print(f"\n❌ 模型文件不存在！请把 {model_name} 复制到 utills 目录下")
    exit()
# 检查图片是否在utills下
if not os.path.exists(image_path):
    print(f"\n❌ 图片文件不存在！请把 {image_name} 复制到 utills 目录下")
    exit()

# ========== 加载模型 + 检测 ==========
# 加载模型（Windows用cpu，避免mps报错）
model = YOLO(model_path)

# 读取图片
image = cv2.imread(image_path)
if image is None:
    print("❌ 无法读取图片（可能图片损坏/格式不对）")
    exit()

# 推理（置信度0.3，IOU0.5，Windows用cpu）
results = model(image, conf=0.3, iou=0.5, device="cpu")[0]

# ========== 保存结果 ==========
# 个人矩阵

        #> - 抖音账号：从 0 至 1（日常分享实操、效率工具教程）
        #> - 微信公众号：从 0 至 1（可通过该渠道获取完整代码包及EXE程序）
        #> - 博客网站：[www.from0to1.cn](https://www.from0to1.cn)（持续更新实战教程、技术干货内容）
        #> - GitHub账号：[https://github.com/mtnljbydd](https://github.com/mtnljbydd)（开源更多实用工具脚本及项目工程）
annotated_image = results.plot()
cv2.imwrite(output_path, annotated_image)

print(f"\n✅ 检测完成！")
print(f"📤 结果图片已保存：{output_path}")