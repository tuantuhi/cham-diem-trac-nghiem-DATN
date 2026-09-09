import os
import cv2
import numpy as np
import json
import logging
import easyocr
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# --- Định nghĩa kiến trúc mạng CNN ---
class SimpleOCR_CNN(nn.Module):
    def __init__(self):
        super(SimpleOCR_CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3) 
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2, 2)              
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2, 2)              
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 4)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 8)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

class YOLOPipeline:
    def __init__(self, yolo_model_path: str = r"D:\Desktop\DATN\Ocr\models\best_v9.pt", ocr_model_path: str = r"D:\Desktop\DATN\Ocr\models\abcd_ocr.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 1. Tải mô hình YOLO
        self.model = YOLO(yolo_model_path)
        logger.info(f"Đã tải mô hình YOLO từ {yolo_model_path}")
        
        # 2. Tải mạng CNN OCR PyTorch tùy chỉnh
        self.ocr_model = SimpleOCR_CNN().to(self.device)
        self.ocr_model.load_state_dict(torch.load(ocr_model_path, map_location=self.device, weights_only=True))
        self.ocr_model.eval()
        self.ocr_transform = transforms.Compose([
            transforms.Resize((40, 40)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        self.classes = ['A', 'B', 'C', 'D']
        logger.info(f"Đã tải mô hình OCR CNN tùy chỉnh từ {ocr_model_path}")
        
        # 3. Tải EasyOCR
        self.reader = easyocr.Reader(['vi', 'en'], gpu=torch.cuda.is_available())
        logger.info("Đã tải EasyOCR")

    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Tự động phát hiện góc nghiêng và xoay phẳng hình ảnh."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=300, maxLineGap=50)
        
        angles = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if -15 <= angle <= 15 and abs(angle) > 0.1:
                    angles.append(angle)
                    
        if len(angles) > 0:
            median_angle = np.median(angles)
            logger.info(f"Đang xoay phẳng ảnh với góc {median_angle:.2f} độ")
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return image

    def _extract_boxes(self, img: np.ndarray):
        """Chạy YOLO để trích xuất các hộp giới hạn."""
        results = self.model(img, conf=0.2, iou=0.4, imgsz=640, verbose=False)
        boxes = results[0].boxes
        
        ques_boxes = []
        ans_boxes = []
        for box in boxes:
            cls_id = int(box.cls[0].item())
            name = self.model.names[cls_id]
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            conf = float(box.conf[0].item())
            
            if name == 'ques_id':
                ques_boxes.append((x1, y1, x2, y2, conf))
            elif name == 'selected_ans':
                ans_boxes.append((x1, y1, x2, y2, conf))
                
        return ques_boxes, ans_boxes

    def _read_question_ids(self, img: np.ndarray, ques_boxes: list) -> list:
        """Đọc ID câu hỏi và tính tọa độ TÂM (cy)."""
        img_h, img_w = img.shape[:2]
        
        ques_with_ids = []
        for box in ques_boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            pad = 2
            x1_c, y1_c = max(0, x1 - pad), max(0, y1 - pad)
            x2_c, y2_c = min(img_w, x2 + pad), min(img_h, y2 + pad)
            crop = img[y1_c:y2_c, x1_c:x2_c]
            
            parsed_id = None
            conf_val = 0.0
            ques_cy = (box[1] + box[3]) / 2  # Tính tâm Y
            
            if crop.size > 0:
                results = self.reader.readtext(crop)
                if results:
                    text, conf = results[0][1], results[0][2]
                    digits = ''.join(filter(str.isdigit, text))
                    if digits and conf >= 0.3:
                        parsed_id = int(digits)
                        conf_val = conf
                        
            ques_with_ids.append({"id": parsed_id, "box": box, "conf": conf_val, "cy": ques_cy})
                        
        # Sắp xếp theo TÂM Y 
        return sorted(ques_with_ids, key=lambda q: q["cy"])

    def _read_answers_only(self, img: np.ndarray, ans_boxes: list) -> list:
        img_h, img_w = img.shape[:2]
        ans_data = []  
        for ans_box in ans_boxes:
            ans_cy = (ans_box[1] + ans_box[3]) / 2  # Tính tâm Y
            
            x1, y1, x2, y2 = map(int, ans_box[:4])
            y1_c, y2_c = max(0, y1-2), min(img_h, y2+2)
            x1_c, x2_c = max(0, x1-2), min(img_w, x2+2)
            crop_img = img[y1_c:y2_c, x1_c:x2_c]
            
            if crop_img.size == 0:
                continue

            crop_rgb = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
            input_tensor = self.ocr_transform(Image.fromarray(crop_rgb)).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.ocr_model(input_tensor)
                _, predicted = torch.max(output.data, 1)
                choice = self.classes[predicted.item()]
            
            ans_data.append({
                "box": ans_box,
                "choice": choice,
                "cy": ans_cy   
            })
        return ans_data

    def _match_global(self, ans_data: list, ques_with_ids: list) -> list:
        if not ans_data or not ques_with_ids:
            return []

        # Sắp xếp đồng nhất toàn bộ bằng TÂM Y
        sorted_ques = sorted(ques_with_ids, key=lambda q: q["cy"])
        sorted_ans = sorted(ans_data, key=lambda a: a["cy"])

        final_results = []
        used_answers = set()

        for i, q in enumerate(sorted_ques):
            q_id = q["id"] if q["id"] is not None else (i + 1)
            
            q_height = q["box"][3] - q["box"][1]
            offset = q_height * 0.3
            
            # Khớp bằng vùng không gian giới hạn bởi các TÂM Y
            current_q_cy = q["cy"] - offset
            next_q_cy = (sorted_ques[i + 1]["cy"] - offset) if i + 1 < len(sorted_ques) else float('inf')

            for a_idx, a in enumerate(sorted_ans):
                if a_idx in used_answers:
                    continue
                
                if current_q_cy <= a["cy"] < next_q_cy:
                    final_results.append({
                        "question_index": q_id,
                        "choice": a["choice"],
                        "bbox": [round(v, 1) for v in a["box"][:4]],
                        "confidence": round(a["box"][4], 2) if len(a["box"]) > 4 else 1.0
                    })
                    used_answers.add(a_idx)

        return final_results

    def _match_and_read_answers(self, img: np.ndarray, ans_boxes: list, ques_with_ids: list) -> list:
        ans_data = self._read_answers_only(img, ans_boxes)
        return self._match_global(ans_data, ques_with_ids)

    def _draw_visualization(self, img: np.ndarray, ques_boxes: list, ans_results: list) -> np.ndarray:
        vis_img = img.copy()
        for box in ques_boxes:
            bx1, by1, bx2, by2 = map(int, box[:4])
            cv2.rectangle(vis_img, (bx1, by1), (bx2, by2), (255, 0, 0), 2)
            
        for ans in ans_results:
            if not ans["bbox"]:
                continue
            bx1, by1, bx2, by2 = map(int, ans["bbox"])
            cv2.rectangle(vis_img, (bx1, by1), (bx2, by2), (0, 255, 0), 3)
            
            text = f"Q{ans['question_index']}: {ans['choice']}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            cv2.rectangle(vis_img, (bx1, by1 - th - 10), (bx1 + tw, by1), (0, 255, 0), -1)
            cv2.putText(vis_img, text, (bx1, by1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        return vis_img

    def process_image(self, img: np.ndarray):
        if img is None:
            return [], None

        img = self.deskew_image(img)
        ques_boxes, ans_boxes = self._extract_boxes(img)
        ques_with_ids = self._read_question_ids(img, ques_boxes)
        ans_results = self._match_and_read_answers(img, ans_boxes, ques_with_ids)
        vis_img = self._draw_visualization(img, ques_boxes, ans_results)

        q_counts = {}
        for ans in ans_results:
            q_idx = ans["question_index"]
            q_counts[q_idx] = q_counts.get(q_idx, 0) + 1
            
        final_ans_results = []
        seen = set()
        for ans in ans_results:
            q_idx = ans["question_index"]
            if q_counts[q_idx] > 1:
                if q_idx not in seen:
                    ans_copy = ans.copy()
                    ans_copy["choice"] = None
                    final_ans_results.append(ans_copy)
                    seen.add(q_idx)
            else:
                final_ans_results.append(ans)

        return final_ans_results, vis_img

    def process(self, image_path: str, output_json: str, output_vis: str):
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Could not read image {image_path}")
            return
            
        ans_results, vis_img = self.process_image(img)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(ans_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Đã lưu {len(ans_results)} kết quả vào {output_json}")

        cv2.imwrite(output_vis, vis_img)
        logger.info(f"Đã lưu ảnh trực quan hóa vào {output_vis}")

    def process_api(self, image_path: str) -> dict[str, str]:
        img = cv2.imread(str(image_path))
        if img is None:
            return {}
        ans_results, _ = self.process_image(img)
        return {str(ans["question_index"]): ans["choice"] for ans in ans_results}

    def process_images_batch(self, images: list):
        all_ques_with_ids = []
        all_ans_data = []
        y_offset = 0

        for img in images:
            if img is None:
                continue
            
            img = self.deskew_image(img)
            ques_boxes, ans_boxes = self._extract_boxes(img)
            
            ques_with_ids = self._read_question_ids(img, ques_boxes)
            for q in ques_with_ids:
                box = list(q["box"])
                box[1] += y_offset
                box[3] += y_offset
                q["box"] = tuple(box)
                q["cy"] += y_offset  # Cộng offset ảo cho cy của câu hỏi
            all_ques_with_ids.extend(ques_with_ids)
            
            ans_data = self._read_answers_only(img, ans_boxes)
            for a in ans_data:
                box = list(a["box"])
                box[1] += y_offset
                box[3] += y_offset
                a["box"] = tuple(box)
                a["cy"] += y_offset  # Cộng offset ảo cho cy của đáp án
            all_ans_data.extend(ans_data)
            
            y_offset += img.shape[0]

        ans_results = self._match_global(all_ans_data, all_ques_with_ids)

        q_counts = {}
        for ans in ans_results:
            q_idx = ans["question_index"]
            q_counts[q_idx] = q_counts.get(q_idx, 0) + 1
            
        final_ans_results = []
        seen = set()
        for ans in ans_results:
            q_idx = ans["question_index"]
            if q_counts[q_idx] > 1:
                if q_idx not in seen:
                    ans_copy = ans.copy()
                    ans_copy["choice"] = None
                    final_ans_results.append(ans_copy)
                    seen.add(q_idx)
            else:
                final_ans_results.append(ans)

        return final_ans_results

    def process_api_batch(self, image_paths: list[str]) -> dict[str, str]:
        images = []
        for path in image_paths:
            img = cv2.imread(str(path))
            if img is not None:
                images.append(img)
                
        if not images:
            return {}
            
        ans_results = self.process_images_batch(images)
        return {str(ans["question_index"]): ans["choice"] for ans in ans_results}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys
    import glob
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pipeline = YOLOPipeline(os.path.join(base_dir, "models", "best_v9.pt"), os.path.join(base_dir, "models", "abcd_ocr.pth"))
    test_imgs = glob.glob(os.path.join(base_dir, "image_test_khoanh", "*.jpg"))
    print(f"Testing batch processing on {len(test_imgs)} images...")
    res = pipeline.process_api_batch(test_imgs)
    import json
    print(json.dumps(res, indent=2))