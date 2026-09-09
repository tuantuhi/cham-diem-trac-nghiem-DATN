# KHUNG BÁO CÁO ĐỒ ÁN TỐT NGHIỆP
## Đề tài: Nghiên cứu và Phát triển Hệ thống Chấm điểm Trắc nghiệm Tự động dựa trên Trí tuệ Nhân tạo và Thị giác Máy tính

---



---

## TRANG BÌA & MỤC LỤC

- Trang bìa (Trường, Khoa, Tên đề tài, GVHD, SVTH, Năm)
- Lời cam đoan
- Lời cảm ơn
- Tóm tắt đồ án (Tiếng Việt & Tiếng Anh - Abstract)
- Mục lục
- Danh mục hình ảnh
- Danh mục bảng biểu
- Danh mục từ viết tắt

---

## CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

### 1.1. Giới thiệu về hình thức thi trắc nghiệm tại Việt Nam

#### 1.1.1. Lịch sử và xu hướng áp dụng thi trắc nghiệm
- Từ kỳ thi THPT Quốc gia 2017: Bộ GD&ĐT chính thức chuyển sang hình thức trắc nghiệm khách quan cho hầu hết các môn thi
- Phạm vi ứng dụng: Thi THPT QG, thi đại học, kiểm tra định kỳ trong trường học, thi năng lực, chứng chỉ...
- Quy mô: Hàng triệu bài thi được xử lý mỗi năm trên cả nước

#### 1.1.2. Thực trạng chấm điểm trắc nghiệm hiện nay — Kết quả khảo sát

> [!IMPORTANT]
> **Đây là điểm nhấn quan trọng nhất của Chương 1.** Cần thực hiện khảo sát thực tế (Google Form, phỏng vấn) và đưa số liệu cụ thể vào đây.

**Đối tượng khảo sát đề xuất:**
- Giáo viên trung học phổ thông / đại học (30–50 người)
- Học sinh / sinh viên (50–100 người)
- Cán bộ quản lý giáo dục (5–10 người)

**Nội dung khảo sát đề xuất (kèm kết quả mẫu):**

| Câu hỏi khảo sát | Kết quả tiêu biểu (điền số liệu thực) |
|---|---|
| Trường/cơ sở bạn hiện dùng phương pháp chấm nào? | ~X% chấm tay, ~Y% máy quét OMR, ~Z% phần mềm |
| Trung bình mất bao lâu để chấm 1 lớp 40 bài? | 45–90 phút (chấm tay) |
| Bạn có gặp sai sót khi chấm tay không? | ~X% thường xuyên, ~Y% thỉnh thoảng |
| Chi phí máy chấm OMR chuyên dụng có phù hợp không? | ~X% cho là quá đắt |
| Bạn có muốn dùng điện thoại chụp ảnh để chấm không? | ~X% rất muốn |
| Khó khăn lớn nhất khi chấm bằng tay? | Tốn thời gian, dễ nhầm lẫn, khó thống kê |

**Biểu đồ khảo sát:** *(Vẽ biểu đồ tròn / cột từ số liệu thực)*

#### 1.1.3. Các phương pháp chấm điểm trắc nghiệm hiện có — Phân tích ưu nhược điểm

| Phương pháp | Mô tả | Ưu điểm | Hạn chế |
|---|---|---|---|
| **Chấm tay** | GV đối chiếu từng bài với đáp án | Không cần thiết bị | Chậm, dễ sai sót, khó thống kê |
| **Máy chấm OMR chuyên dụng** | Máy quét phiếu trả lời (Scantron, iMark...) | Nhanh, chính xác cao | Chi phí cao (50–200 triệu), cần phiếu in đặc biệt |
| **Phần mềm kết hợp máy quét** | Scan → phần mềm nhận diện | Khá chính xác | Vẫn cần máy quét, phức tạp khi triển khai |
| **Ứng dụng chụp ảnh hiện có** | GradeCam, Zipgrade... | Tiện, nhanh | Bản quyền, không tùy biến, phụ thuộc internet |
| **Hệ thống đề xuất (AI + thị giác máy tính)** | Dùng camera điện thoại + mô hình AI | Chi phí thấp, linh hoạt, tùy biến | Độ chính xác phụ thuộc chất lượng ảnh |

### 1.2. Lý do chọn đề tài và vấn đề cần giải quyết

**Các hạn chế còn tồn tại (rút ra từ khảo sát):**
1. **Chi phí cao:** Máy OMR chuyên dụng ngoài tầm với của trường nhỏ, tư nhân
2. **Thiếu linh hoạt:** Phiếu trả lời phải in đặc biệt, không dùng giấy thi thông thường
3. **Không hỗ trợ dạng khoanh vòng:** Các giải pháp OMR truyền thống chỉ hỗ trợ phiếu tô bong bóng, không xử lý được bài thi dạng khoanh tròn đáp án — rất phổ biến ở cấp THCS, tiểu học và đề thi tự ra
4. **Tốn thời gian:** Chấm tay 1 lớp mất 45–90 phút
5. **Khó thống kê:** Không có công cụ phân tích kết quả tập trung

**Giải pháp đề xuất:** Xây dựng hệ thống chấm điểm trắc nghiệm tự động sử dụng:
- Thị giác máy tính (Computer Vision) để xử lý ảnh phiếu trả lời
- Deep Learning (YOLOv8, CNN) để nhận diện đáp án dạng khoanh vòng
- Web application để quản lý và thao tác dễ dàng

### 1.3. Mục tiêu đề tài
- Xây dựng thuật toán chấm điểm OMR truyền thống (phiếu tô bong bóng) dựa trên OpenCV
- Xây dựng pipeline YOLOv8 + CNN nhận diện đáp án dạng khoanh vòng
- Phát triển REST API bằng FastAPI tích hợp cả hai phương pháp
- Xây dựng ứng dụng web đầy đủ (frontend React + backend Spring Boot) phục vụ người dùng cuối

### 1.4. Phạm vi và giới hạn đề tài
- Đầu vào: Ảnh chụp bằng điện thoại (JPG/PNG)
- Hỗ trợ phiếu tô bong bóng 20 câu và 50 câu
- Hỗ trợ bài thi dạng khoanh tròn (không form chuẩn)
- Mỗi câu có 4 lựa chọn A, B, C, D
- Giới hạn: Chưa hỗ trợ nhận diện thông tin thí sinh (mã số, tên)

### 1.5. Phương pháp nghiên cứu
- Nghiên cứu lý thuyết: Thị giác máy tính, Deep Learning, OMR
- Khảo sát thực tế: Bảng hỏi giáo viên & học sinh
- Thực nghiệm: Xây dựng và đánh giá trên bộ dữ liệu thực tế

### 1.6. Cấu trúc báo cáo
*(Mô tả ngắn gọn nội dung từng chương)*

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

### 2.1. Thị giác máy tính (Computer Vision) và Xử lý ảnh số

#### 2.1.1. Các khái niệm cơ bản
- Ảnh số, không gian màu (BGR, Grayscale, HSV)
- Biến đổi hình học: phép chiếu phối cảnh (Perspective Transform), `cv2.warpPerspective`

#### 2.1.2. Tiền xử lý ảnh — Các kỹ thuật sử dụng trong hệ thống
- **CLAHE (Contrast Limited Adaptive Histogram Equalization):** Cân bằng histogram cục bộ, giải quyết ánh sáng không đều khi chụp bằng điện thoại (`clipLimit=3.0, tileGridSize=(16,16)`)
- **Gaussian Blur:** Khử nhiễu pixel trước ngưỡng hóa (`kernel 5×5`)
- **Adaptive Thresholding:** Nhị phân hóa thích nghi (`blockSize=51, C=8`), khắc phục gradient ánh sáng toàn trang
- **Morphological Operations:** MORPH\_OPEN (loại đường in mỏng), MORPH\_CLOSE (lấp khoảng trống trong vùng tô)
- **Canny Edge Detection + HoughLinesP:** Phát hiện đường thẳng để deskew (nắn thẳng ảnh bị nghiêng)

#### 2.1.3. Phát hiện điểm chuẩn (Fiducial Markers)
- Vai trò: Xác định 4 góc phiếu trả lời để hiệu chỉnh phối cảnh
- Phương pháp: Tìm contour, so khớp tỷ lệ Aspect Ratio
- `cv2.getPerspectiveTransform` + `cv2.warpPerspective`

### 2.2. Optical Mark Recognition (OMR)

#### 2.2.1. Nguyên lý OMR truyền thống
- Xây dựng lưới tọa độ bong bóng (BubbleROI): tọa độ tâm `(cx, cy)`, bán kính, câu hỏi, lựa chọn
- Đo tỷ lệ tô đen (`fill_ratio`): pixel trắng / tổng pixel trong mặt nạ tròn
- Ngưỡng hóa thích nghi per-image dựa trên phân tích histogram

#### 2.2.2. Thuật toán xác định ngưỡng tô thích nghi (Adaptive Fill Threshold)
- Thu thập toàn bộ `fill_ratio` (~200 giá trị cho 50 câu × 4 lựa chọn)
- Vẽ histogram 50 bins, làm mịn bằng `scipy.ndimage.uniform_filter1d`
- Dùng `scipy.signal.find_peaks` tìm 2 đỉnh: đỉnh "trống" (~5–15%) và đỉnh "đã tô" (~45–85%)
- Tìm điểm trũng (valley) giữa 2 đỉnh → ngưỡng cut-off (giới hạn trong `[0.12, 0.28]`)
- Fallback: phân tích khoảng cách lớn nhất (gap), cuối cùng là giá trị cứng 0.20

#### 2.2.3. Xử lý trường hợp đặc biệt
- Câu bỏ trống: `fill_ratio < threshold` → `None`
- Câu tô nhiều đáp án: `(second / best) > 0.65` → `None` (Ambiguity Check)
- Tô mờ cố ý: `second > 0.35` VÀ `(second / best) > 0.50` → `None`

### 2.3. Học sâu (Deep Learning) trong nhận diện hình ảnh

#### 2.3.1. Mạng nơ-ron tích chập (CNN)
- Kiến trúc tổng quát: Conv → ReLU → MaxPool → Fully Connected
- Kiến trúc CNN tùy chỉnh `SimpleOCR_CNN` (PyTorch):
  - Conv2d(3→16, k=3) → ReLU → MaxPool(2×2)
  - Conv2d(16→32, k=3) → ReLU → MaxPool(2×2)
  - Linear(32×8×8 → 128) → ReLU → Linear(128 → 4)
  - Output: 4 lớp [A, B, C, D]

#### 2.3.2. YOLO (You Only Look Once) — YOLOv8/v9
- Kiến trúc: Backbone (CSPNet) + Neck (FPN/PAN) + Head
- One-stage detector: Phát hiện đối tượng trong một lần forward pass
- Non-Maximum Suppression (NMS): Loại bỏ bounding box trùng lặp (`IoU > 0.4`)
- Các lớp huấn luyện tùy chỉnh: `ques_id` (chứa "Câu X"), `selected_ans` (vùng khoanh tròn)
- Tham số sử dụng: `conf=0.2`, `iou=0.4`, `imgsz=800`

#### 2.3.3. EasyOCR
- Mô hình nhận dạng ký tự quang học đa ngôn ngữ
- Sử dụng để đọc số thứ tự câu hỏi từ vùng `ques_id` box
- Ngôn ngữ: `['vi', 'en']`, ngưỡng tin cậy: `conf >= 0.3`

### 2.4. Các công nghệ xây dựng hệ thống

#### 2.4.1. Backend xử lý ảnh — FastAPI (Python)
- Framework REST API hiệu năng cao, hỗ trợ `async/await`
- Endpoints: `/predict/omr`, `/predict/omr_20`, `/predict/yolo`, `/predict/yolo/batch`
- Containerization: Docker (`Dockerfile` có sẵn)

#### 2.4.2. Backend ứng dụng — Spring Boot (Java)
- RESTful API quản lý người dùng, bài thi, kết quả
- Maven build tool (`pom.xml`)

#### 2.4.3. Frontend — React + Vite + TypeScript
- Framework: React với TypeScript cho type-safety
- Build tool: Vite (nhanh hơn Create React App)
- Giao tiếp với FastAPI và Spring Boot

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Yêu cầu hệ thống

#### 3.1.1. Yêu cầu chức năng
- **UC01:** Upload ảnh phiếu trả lời và nhận kết quả chấm điểm
- **UC02:** Chấm phiếu tô bong bóng (Mẫu 50 câu / 20 câu)
- **UC03:** Chấm bài khoanh vòng đáp án (không form chuẩn)
- **UC04:** Chấm hàng loạt nhiều trang (batch processing)
- **UC05:** Xem ảnh trực quan hóa kết quả (bounding boxes, fill_ratio)
- **UC06:** Quản lý đề thi, đáp án chuẩn, tính điểm
- **UC07:** Xem báo cáo thống kê kết quả lớp học

#### 3.1.2. Yêu cầu phi chức năng
- Thời gian xử lý 1 ảnh: < 3 giây (với GPU), < 10 giây (CPU-only)
- Độ chính xác nhận diện OMR: > 95%
- Độ chính xác nhận diện khoanh vòng (YOLO): > 90%
- API trả về định dạng JSON chuẩn

### 3.2. Kiến trúc tổng thể hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                     Người dùng (GV/HS)                   │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP/HTTPS
┌───────────────────────────▼─────────────────────────────┐
│              Frontend (React + Vite + TypeScript)         │
│          - Upload ảnh  - Xem kết quả  - Thống kê         │
└──────────┬────────────────────────────────┬──────────────┘
           │ REST API                        │ REST API
┌──────────▼──────────┐         ┌───────────▼──────────────┐
│  FastAPI (Python)    │         │   Spring Boot (Java)      │
│  - OMR Pipeline      │         │   - Quản lý người dùng    │
│  - YOLO Pipeline     │         │   - Quản lý bài thi       │
│  - /predict/omr      │         │   - Lưu trữ kết quả       │
│  - /predict/yolo     │         │   - Thống kê              │
└──────────┬──────────┘         └───────────┬──────────────┘
           │                                │
┌──────────▼──────────┐         ┌───────────▼──────────────┐
│   AI Models          │         │   Database                │
│   - best_v9.pt (YOLO)│         │   (MySQL/PostgreSQL)      │
│   - abcd_ocr.pth(CNN)│         │                           │
│   - OpenCV + scipy   │         │                           │
└─────────────────────┘         └──────────────────────────┘
```

### 3.3. Thiết kế luồng xử lý — OMR Truyền thống (Phiếu tô bong bóng)

```
[Ảnh đầu vào]
      │
      ▼
[1. Phát hiện Fiducial Markers] → cv2.findContours + Aspect Ratio
      │
      ▼
[2. Perspective Transform] → cv2.getPerspectiveTransform + cv2.warpPerspective
      │
      ▼
[3. Preprocessing]
   ├── Grayscale
   ├── CLAHE (clipLimit=3.0, tile=16×16)
   ├── Gaussian Blur (5×5)
   ├── Adaptive Threshold (blockSize=51, C=8)
   ├── MORPH_OPEN (ellipse 5×5): xóa đường in mỏng
   └── MORPH_CLOSE (ellipse 7×7): lấp khoảng trống
      │
      ▼
[4. Grid Calibration] → HoughCircles hiệu chỉnh lưới BubbleROI
      │
      ▼
[5. Fill Ratio Measurement] → Circular mask (inner_radius = 0.82 × radius)
      │
      ▼
[6. Adaptive Threshold Computation] → Histogram 50 bins + find_peaks
      │
      ▼
[7. Answer Extraction + Ambiguity Check]
      │
      ▼
[Kết quả JSON: {"1": "A", "2": "C", "3": null, ...}]
```

### 3.4. Thiết kế luồng xử lý — YOLOv8 + CNN (Khoanh vòng đáp án)

```
[Ảnh đầu vào]
      │
      ▼
[1. Deskew] → Canny + HoughLinesP → median angle → cv2.warpAffine
      │
      ▼
[2. YOLO Detection] → best_v9.pt (conf=0.2, iou=0.4, imgsz=800)
   ├── Class ques_id   → ques_boxes[]
   └── Class selected_ans → ans_boxes[]
      │
      ▼
[3. OCR số câu hỏi] → EasyOCR (vi+en) trên crop của ques_boxes
   └── Smart Interpolation: sửa ID nhảy cóc
      │
      ▼
[4. CNN nhận diện đáp án] → abcd_ocr.pth trên crop của ans_boxes
   └── Output: A / B / C / D
      │
      ▼
[5. Global Matching] → Ghép cặp (ques_id, selected_ans) theo TÂM Y (cy)
      │
      ▼
[6. Xử lý đa dấu] → q_counts > 1 → choice = None
      │
      ▼
[Kết quả JSON + Ảnh trực quan hóa]
```

### 3.5. Thiết kế cơ sở dữ liệu
*(Sơ đồ ERD — Vẽ các bảng: User, Exam, Question, AnswerKey, Submission, GradeResult)*

### 3.6. Thiết kế API

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health` | Kiểm tra trạng thái service |
| POST | `/predict/omr` | Chấm phiếu tô bong bóng 50 câu |
| POST | `/predict/omr_20` | Chấm phiếu tô bong bóng 20 câu |
| POST | `/predict/yolo` | Chấm bài khoanh vòng (1 ảnh) |
| POST | `/predict/yolo/batch` | Chấm bài khoanh vòng (nhiều ảnh/trang) |

---

## CHƯƠNG 4: CÀI ĐẶT VÀ THỰC NGHIỆM

### 4.1. Môi trường phát triển

| Thành phần | Công nghệ | Phiên bản |
|---|---|---|
| Ngôn ngữ (AI) | Python | 3.x |
| Computer Vision | OpenCV | cv2 |
| Deep Learning | PyTorch + Ultralytics YOLO | - |
| OCR | EasyOCR | - |
| Backend AI | FastAPI | - |
| Backend Web | Spring Boot (Java) | - |
| Frontend | React + TypeScript + Vite | - |
| Container | Docker | - |

### 4.2. Thu thập và xây dựng bộ dữ liệu

#### 4.2.1. Bộ dữ liệu phiếu tô bong bóng
- Số lượng ảnh thu thập
- Điều kiện chụp: ánh sáng, góc chụp, độ phân giải
- Các biến thể: ảnh bị nghiêng, mờ, ánh sáng không đều

#### 4.2.2. Bộ dữ liệu bài thi dạng khoanh vòng
- Số lượng ảnh và bounding box annotated (`dataset_ocr/`)
- Công cụ annotation: LabelImg/Roboflow
- Phân chia: Train/Val/Test

#### 4.2.3. Bộ dữ liệu huấn luyện CNN OCR (`abcd_ocr.pth`)
- Ảnh crop các ký tự A/B/C/D được khoanh tròn
- Số lượng mẫu mỗi lớp

### 4.3. Huấn luyện mô hình

#### 4.3.1. Huấn luyện YOLOv8/v9 (`best_v9.pt`)
- Cấu hình: epochs, batch size, imgsz, optimizer
- Data augmentation
- Kết quả huấn luyện: mAP@0.5, Precision, Recall

#### 4.3.2. Huấn luyện CNN OCR (`abcd_ocr.pth`)
- Kiến trúc `SimpleOCR_CNN`: 2 khối Conv-ReLU-MaxPool + 2 FC
- Input: `(3, 40, 40)` tensor, Normalize `((0.5,), (0.5,))`
- Output: 4 lớp [A, B, C, D]
- Loss: CrossEntropyLoss, Optimizer: Adam
- Kết quả: Accuracy trên tập test

### 4.4. Cài đặt hệ thống

#### 4.4.1. Module xử lý ảnh OMR truyền thống (`core/`)
- `config.py`: `TemplateConfig`, `BubbleROI`, `ANSWER_MAP`
- `marker.py`: `FiducialMarkerDetector` — phát hiện góc phiếu
- `calibrator.py`: `GridAutoCalibrator` — hiệu chỉnh lưới bằng HoughCircles
- `detector.py`: `FiducialOMRDetector` — toàn bộ pipeline OMR

*(Trình bày các đoạn code quan trọng có chú thích)*

#### 4.4.2. Module YOLO Pipeline (`yolo_pipeline.py`)
- `SimpleOCR_CNN`: Kiến trúc mạng CNN nhận diện A/B/C/D
- `YOLOPipeline`: Pipeline đầy đủ từ deskew → YOLO → OCR → Matching
- `_match_global()`: Thuật toán ghép cặp câu hỏi-đáp án theo tâm Y
- `process_images_batch()`: Xử lý multi-page với virtual y_offset

*(Trình bày các đoạn code quan trọng có chú thích)*

#### 4.4.3. REST API (`app.py`)
- FastAPI setup, endpoints, xử lý file upload tạm thời

#### 4.4.4. Ứng dụng Web (Frontend + Spring Boot Backend)
- Màn hình upload ảnh và hiển thị kết quả
- Màn hình quản lý bài thi, đáp án
- Màn hình thống kê kết quả lớp

### 4.5. Thực nghiệm và đánh giá kết quả

#### 4.5.1. Đánh giá Pipeline OMR truyền thống

| Điều kiện thử nghiệm | Số ảnh | Độ chính xác (câu/bài) | Ghi chú |
|---|---|---|---|
| Ánh sáng tốt, thẳng góc | N | X% | Điều kiện lý tưởng |
| Ánh sáng yếu / không đều | N | X% | CLAHE phát huy tác dụng |
| Ảnh bị nghiêng < 15° | N | X% | Perspective transform |
| Ảnh chụp góc nghiêng | N | X% | Giới hạn của phương pháp |
| Nét bút chì mờ | N | X% | Adaptive threshold |

#### 4.5.2. Đánh giá Pipeline YOLO + CNN

| Metric | Giá trị |
|---|---|
| mAP@0.5 (YOLO `ques_id`) | X% |
| mAP@0.5 (YOLO `selected_ans`) | X% |
| Accuracy (CNN OCR A/B/C/D) | X% |
| Tỷ lệ nhận diện đúng toàn bài | X% |
| Thời gian xử lý 1 ảnh (CPU) | X giây |
| Thời gian xử lý 1 ảnh (GPU) | X giây |

#### 4.5.3. Đánh giá xử lý các trường hợp đặc biệt

| Tình huống | Phương pháp xử lý | Kết quả |
|---|---|---|
| Câu bỏ trống | `fill_ratio < threshold` → None | X% phát hiện đúng |
| Tô 2 đáp án (OMR) | Ambiguity ratio > 0.65 → None | X% phát hiện đúng |
| Khoanh 2 đáp án (YOLO) | `q_counts > 1` → None | X% phát hiện đúng |
| OCR đọc sai số câu | Smart Interpolation | X% sửa đúng |
| Ảnh bị nghiêng (deskew) | HoughLinesP + warpAffine | X% nắn thẳng |

#### 4.5.4. So sánh với các giải pháp hiện có

| Tiêu chí | Chấm tay | Máy OMR chuyên dụng | Hệ thống đề xuất |
|---|---|---|---|
| Chi phí | Thấp | Cao (50–200tr) | Thấp (chỉ cần điện thoại) |
| Tốc độ (40 bài) | 45–90 phút | < 5 phút | < 10 phút |
| Độ chính xác | Trung bình | Rất cao | Cao |
| Hỗ trợ khoanh vòng | Có | Không | **Có** |
| Cần phiếu đặc biệt | Không | Có | Không |
| Thống kê tự động | Không | Có | **Có** |

---

## CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 5.1. Kết quả đạt được
- **Về lý thuyết:** Tổng hợp và áp dụng thành công các kỹ thuật thị giác máy tính (CLAHE, Adaptive Threshold, Perspective Transform, Morphology, Deskew) và Deep Learning (YOLOv8, CNN, EasyOCR) vào bài toán chấm điểm trắc nghiệm.
- **Về kỹ thuật:** Hoàn thiện 2 pipeline xử lý độc lập — OMR truyền thống và YOLO+CNN; REST API FastAPI; web application đầy đủ.
- **Về kết quả thực nghiệm:** Độ chính xác X% trên phiếu tô, Y% trên bài khoanh vòng, thời gian xử lý Z giây/ảnh.
- **Về đóng góp thực tiễn:** Cung cấp giải pháp chi phí thấp, linh hoạt cho các cơ sở giáo dục chưa có điều kiện đầu tư máy OMR chuyên dụng.

### 5.2. Hạn chế
- Độ chính xác giảm khi ảnh chụp quá mờ, ánh sáng quá tệ
- Chưa hỗ trợ nhận diện thông tin thí sinh (SBD, họ tên) tự động
- Chưa hỗ trợ các mẫu phiếu có số câu khác 20/50
- Mô hình YOLO chưa xử lý tốt trường hợp chữ viết tay số câu không rõ ràng

### 5.3. Hướng phát triển
1. **Nhận diện thông tin thí sinh:** OCR tự động đọc SBD/tên từ phiếu
2. **Mở rộng mẫu phiếu:** Hỗ trợ phiếu tùy biến (30, 40 câu) qua template tự định nghĩa
3. **Cải thiện độ bền (robustness):** Data augmentation nặng hơn (blur, noise, shadow)
4. **Mobile App:** Ứng dụng iOS/Android tích hợp trực tiếp
5. **Phân tích câu hỏi:** Thống kê tỷ lệ chọn từng đáp án để phân tích đề thi
6. **Xuất báo cáo:** PDF/Excel tự động

---

## TÀI LIỆU THAM KHẢO

*(Liệt kê theo chuẩn APA hoặc IEEE, ví dụ)*

1. Jocher, G. et al. (2023). *Ultralytics YOLOv8*. Ultralytics. https://github.com/ultralytics/ultralytics
2. Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools.
3. He, K., Zhang, X., Ren, S., & Sun, J. (2016). *Deep Residual Learning for Image Recognition*. CVPR.
4. Paszke, A. et al. (2019). *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. NeurIPS.
5. Bộ Giáo dục và Đào tạo Việt Nam (2017). *Thông tư quy định về tổ chức thi THPT Quốc gia*.
6. Raka, J. M. et al. (2020). *Automated Multiple Choice Answer Sheet Grading Using Image Processing*. IEEE.
7. Javed, A. et al. (2021). *An Efficient OMR System Using Deep Learning*. Journal of AI Research.
8. *(Các tài liệu khác về Computer Vision, Deep Learning, FastAPI, React...)*

---

## PHỤ LỤC

### Phụ lục A: Kết quả khảo sát đầy đủ
*(Bảng số liệu thô từ Google Form)*

### Phụ lục B: Một số ảnh minh họa kết quả hệ thống
- Ảnh phiếu tô bong bóng gốc vs. ảnh sau perspective transform
- Ảnh trực quan hóa fill_ratio từng bong bóng
- Ảnh bài khoanh vòng với bounding box YOLO và nhãn kết quả
- Giao diện web ứng dụng

### Phụ lục C: Hướng dẫn cài đặt và chạy hệ thống
```bash
# FastAPI Service
pip install -r requirements.txt
uvicorn app:app --reload

# Hoặc dùng Docker
docker build -t omr-api .
docker run -p 8000:8000 omr-api

# Frontend
cd codex-frontend
npm install
npm run dev
```

### Phụ lục D: Một số đoạn mã nguồn quan trọng
*(Đưa các hàm quan trọng nhất vào đây để tham chiếu)*
