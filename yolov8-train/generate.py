"""
YOLOv8推理生成脚本

该脚本用于使用训练好的YOLOv8模型对图像进行推理，支持两种模式：
1. detection: 边界框检测模式，检测并标注图像中的物体边界
2. segmentation: 像素分割模式，对物体进行像素级分割

输出包括：
- 带标注的图像(overlays)
- 检测结果文本文件(detections)
- 检测掩码图像(masks)

使用方法：
1. 将待检测图像放入generate_input目录
2. 配置脚本中的参数（模型路径、模式、置信度阈值等）
3. 运行脚本，结果将保存在generate_output目录
"""
# 导入所需库
from ultralytics import YOLO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm  # 用于显示进度条
import cv2
import numpy as np

# 目录配置
input_dir = Path('./generate_input')      # 输入图像目录
input_dir.mkdir(parents=True, exist_ok=True)  # 如果目录不存在则创建

output_dir = Path('./generate_output')    # 输出目录
output_dir.mkdir(parents=True, exist_ok=True)  # 如果目录不存在则创建

overlay_dir = output_dir / 'overlays'     # 带标注的图像输出目录
overlay_dir.mkdir(parents=True, exist_ok=True)
overlay_prefix = ""  # 输出图像前缀，可留空
overlay_suffix = ""  # 输出图像后缀，可留空

detection_dir = output_dir / 'detections' # 检测结果文本文件输出目录
detection_dir.mkdir(parents=True, exist_ok=True)
detection_prefix = ""  # 检测结果文本前缀，可留空
detection_suffix = ""  # 检测结果文本后缀，可留空

mask_dir = output_dir / 'masks'           # 掩码图像输出目录
mask_dir.mkdir(parents=True, exist_ok=True)
mask_prefix = ""  # 掩码图像前缀，可留空
mask_suffix = ""  # 掩码图像后缀，可留空

# 加载训练好的模型
model_path = './models/best.pt'  # 模型文件路径
model = YOLO(model_path)

# 模式选择：detection（检测）或segmentation（分割）
mode = "detection"

# 是否检测所有类或仅检测选定的类
detect_all_classes = True  # 设置为True检测所有类，False仅检测下面指定的类

# 要检测的类列表
# 示例: ['SpeechBalloons', 'General_speech', 'hit_sound', 'blast_sound', 'narration speech', 'thought_speech', 'roar']
selected_classes = ['socks']

# 类覆盖映射，将左侧的类视为右侧的类
# 示例: 将thought_speech注释视为SpeechBalloons注释
class_overrides = {
    'thought_speech': 'SpeechBalloons',
}

# 置信度阈值，高于此值的检测结果才会被保留
confidence_threshold = 0.15

# 标签设置
label_boxes = True  # 是否绘制类名，False仅绘制边界框
font_size = 30      # 类标签的字体大小

# 尝试加载自定义字体，失败则使用默认字体
try:
    font = ImageFont.truetype("arial.ttf", 30)  # 可根据需要更新字体大小
except IOError:
    font = ImageFont.load_default()
    print("Default font will be used, as custom font not found.")

# 预定义的标签颜色和文本颜色配对列表
predefined_colors_with_text = [
    ((204, 0, 0),     'white'),  # 深红色，白色文本
    ((0, 204, 0),     'black'),  # 深绿色，黑色文本
    ((0, 0, 204),     'white'),  # 深蓝色，白色文本
    ((204, 204, 0),   'black'),  # 深黄色，黑色文本
    ((204, 0, 204),   'white'),  # 深洋红色，白色文本
    ((0, 204, 204),   'black'),  # 深青色，黑色文本
    ((153, 0, 0),     'white'),  # 深棕色，白色文本
    ((0, 153, 0),     'white'),  # 深绿色，白色文本
    ((0, 0, 153),     'white'),  # 深蓝色，白色文本
    ((153, 153, 0),   'black'),  # 深橄榄色，黑色文本
    # 可根据需要添加更多颜色对
]

# 为每个类分配颜色，如果类的数量超过颜色数量，则循环使用颜色
class_colors = {class_name: predefined_colors_with_text[i % len(predefined_colors_with_text)][0] for i, class_name in enumerate(selected_classes)}
text_colors = {class_name: predefined_colors_with_text[i % len(predefined_colors_with_text)][1] for i, class_name in enumerate(selected_classes)}


# 存储输入图像的路径
image_paths = []
for extension in ['*.jpg', '*.jpeg', '*.png']:  # 支持的图像扩展名
    image_paths.extend(input_dir.glob(extension))  # 收集所有匹配的图像文件

# 分割类，用于处理像素分割任务
class YOLOSEG:
    """
    YOLO分割类，用于处理像素级分割任务
    """
    def __init__(self, model_path):
        """
        初始化YOLO分割模型
        
        参数:
            model_path: 模型文件路径
        """
        self.model = YOLO(model_path)

    def detect(self, img):
        """
        对输入图像进行分割检测
        
        参数:
            img: 输入图像
        
        返回:
            bboxes: 边界框坐标
            class_ids: 类ID
            segmentation_contours_idx: 分割轮廓索引
            scores: 置信度分数
        """
        height, width, _ = img.shape  # 获取图像尺寸
        results = self.model.predict(source=img.copy(), save=False, save_txt=False)
        result = results[0]

        segmentation_contours_idx = []
        if len(result) > 0:
            for seg in result.masks.xy:
                segment = np.array(seg, dtype=np.float32)
                segmentation_contours_idx.append(segment)

        # 获取边界框、类ID和置信度分数
        bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
        class_ids = np.array(result.boxes.cls.cpu(), dtype="int")
        scores = np.array(result.boxes.conf.cpu(), dtype="float").round(2)
        return bboxes, class_ids, segmentation_contours_idx, scores

# 创建YOLO分割实例
ys = YOLOSEG(model_path)

# 估算文本大小的函数
def estimate_text_size(label, font_size):
    """
    估算文本在图像上占据的尺寸
    
    参数:
        label: 要绘制的文本
        font_size: 字体大小
    
    返回:
        text_width: 文本宽度
        text_height: 文本高度
    """
    approx_char_width = font_size * 0.6  # 近似字符宽度
    text_width = len(label) * approx_char_width  # 计算文本总宽度
    text_height = font_size  # 文本高度等于字体大小
    return text_width, text_height

# 将检测结果写入文件的函数
def write_detections_to_file(image_path, detections):
    """
    将检测结果写入文本文件
    
    参数:
        image_path: 图像文件路径
        detections: 检测结果列表
    """
    # 创建与图像同名的文本文件
    text_file_path = detection_dir / f"{detection_prefix}{image_path.stem}{detection_suffix}.txt"

    with open(text_file_path, 'w') as file:
        for detection in detections:
            file.write(f"{detection}\n")

# 处理图像，显示进度条
print(f"Generating outputs in {mode} mode.")
for image_path in tqdm(image_paths, desc='Processing Images'):
    # 检测模式
    if mode == "detection":
        # 使用OpenCV加载图像用于掩码生成
        img_cv = cv2.imread(str(image_path))
        # 初始化一个空白掩码用于所有检测
        mask_img = np.zeros(img_cv.shape[:2], dtype=np.uint8)

        # 使用PIL加载图像用于生成带标注的图像
        img_pil = Image.open(image_path)
        results = model.predict(img_pil)  # 进行推理
        draw = ImageDraw.Draw(img_pil)  # 创建绘图对象
        detections = []  # 存储检测结果

        # 如果有检测结果且包含边界框
        if len(results) > 0 and results[0].boxes.xyxy is not None:
            # 遍历每个检测结果
            for idx, box in enumerate(results[0].boxes.xyxy):
                x1, y1, x2, y2 = box[:4].tolist()  # 获取边界框坐标
                cls_id = int(results[0].boxes.cls[idx].item())  # 获取类ID
                conf = results[0].boxes.conf[idx].item()  # 获取置信度
                # 获取类名，如果ID无效则使用"Unknown"
                cls_name = results[0].names[cls_id] if 0 <= cls_id < len(results[0].names) else "Unknown"
                cls_name = class_overrides.get(cls_name, cls_name)  # 应用类覆盖映射

                # 检查是否满足检测条件（类在选定列表中或检测所有类，且置信度高于阈值）
                if (cls_name in selected_classes or detect_all_classes) and conf >= confidence_threshold:
                    box_color = class_colors.get(cls_name, (255, 0, 0))  # 获取边界框颜色
                    text_color = text_colors.get(cls_name, 'black')  # 获取文本颜色
                    draw.rectangle([x1, y1, x2, y2], outline=box_color, width=7)  # 绘制边界框

                    # 填充掩码图像
                    cv2.rectangle(mask_img, (int(x1), int(y1)), (int(x2), int(y2)), 255, thickness=-1)  # -1表示填充矩形

                    # 如果需要绘制标签
                    if label_boxes:
                        label = f"{cls_name}: {conf:.2f}"  # 标签文本
                        text_size = estimate_text_size(label, font_size)  # 估算文本大小
                        # 绘制标签背景
                        draw.rectangle([x1, y1 - text_size[1] - 5, x1 + text_size[0], y1], fill=box_color)
                        # 绘制标签文本
                        draw.text((x1, y1 - text_size[1] - 5), label, fill=text_color, font=font)

                    # 将检测结果添加到列表
                    detections.append(f"{cls_name} {conf:.2f} {x1} {y1} {x2} {y2}")

        # 保存带标注的图像
        img_pil.save(overlay_dir / f"{overlay_prefix}{image_path.stem}{overlay_suffix}{image_path.suffix}")

        # 将检测结果写入文本文件
        write_detections_to_file(image_path, detections)

        # 保存掩码图像
        mask_output_path = mask_dir / f"{mask_prefix}{image_path.stem}{mask_suffix}.png"
        cv2.imwrite(str(mask_output_path), mask_img)
    
    # 分割模式
    elif mode == "segmentation":
        # 使用OpenCV加载图像用于分割和掩码生成
        img_cv = cv2.imread(str(image_path))
        height, width, _ = img_cv.shape  # 获取图像尺寸

        # 使用YOLOSEG进行分割检测
        bboxes, classes, segmentations, scores = ys.detect(img_cv)

        # 初始化一个空白掩码用于所有分割
        mask_img = np.zeros(img_cv.shape[:2], dtype=np.uint8)

        # 使用原始YOLO模型进行初始标注
        img_pil = Image.open(image_path)
        results = model.predict(img_pil)
        # 获取带标注的图像
        if hasattr(results[0], 'render'):
            annotated_img = results[0].render()[0]  # 使用'render'（如果可用）
        else:
            annotated_img = results[0].plot()  # 使用'plot'作为回退
        annotated_img = np.array(annotated_img)  # 转换为NumPy数组以便CV2处理

        # 保存分割数据的文本文件
        txt_output_path = detection_dir / f"{detection_prefix}{image_path.stem}{detection_suffix}.txt"
        with open(txt_output_path, 'w') as f:
            # 遍历每个分割结果
            for bbox, class_id, seg in zip(bboxes, classes, segmentations):
                # 归一化分割数据
                seg_normalized = seg / [width, height]
                # 将归一化数据写入文本文件
                seg_data = ' '.join([f'{x:.6f},{y:.6f}' for x, y in seg_normalized])
                f.write(f'{class_id} {seg_data}\n')

                # 在掩码图像上绘制分割区域
                cv2.fillPoly(mask_img, [np.array(seg, dtype=np.int32)], 255)

                # 在标注图像上绘制边界框和分割掩码
                x, y, x2, y2 = bbox
                cv2.rectangle(annotated_img, (x, y), (x2, y2), (0, 0, 255), 2)
                cv2.polylines(annotated_img, [np.array(seg, dtype=np.int32)], isClosed=True, color=(0, 0, 255), thickness=2)

        # 保存带标注的图像
        overlay_output_path = overlay_dir / f"{overlay_prefix}{image_path.stem}{overlay_suffix}{image_path.suffix}"
        cv2.imwrite(str(overlay_output_path), annotated_img)

        # 保存掩码图像
        mask_output_path = mask_dir / f"{mask_prefix}{image_path.stem}{mask_suffix}.png"
        cv2.imwrite(str(mask_output_path), mask_img)

# 处理完成，显示结果统计
print(f"Processed {len(image_paths)} images. Overlays saved to '{overlay_dir}', Detections saved to '{detection_dir}', and Masks saved to '{mask_dir}'.")
