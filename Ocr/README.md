# Hệ Thống AI Chấm Điểm OMR Toàn Diện (YOLOv8 + PyTorch CNN)

Dự án này cung cấp một hệ thống API mạnh mẽ dùng để tự động hóa việc chấm điểm cho 2 thể loại bài thi phổ biến nhất hiện nay:
1. **Bài thi tô đen (Bubble Sheet):** Nhận diện dựa trên mật độ Pixel (Thuật toán Computer Vision truyền thống: HoughCircles + Masking).
2. **Bài thi khoanh tròn chữ cái (Circled Letters):** Dùng AI Deep Learning (YOLOv9 kết hợp Custom PyTorch CNN) để "nhìn" thẳng vào nét khoanh và đọc ra chữ cái bên trong.

Hệ thống được thiết kế hoàn toàn tự chủ, **không phụ thuộc vào công cụ OCR ngoại lai nào (như Tesseract)**, cho tốc độ xử lý tính bằng mili-giây và độ chính xác vượt trội.

## 🌟 Kiến Trúc Hệ Thống

- **Core API:** FastAPI (Uvicorn).
- **Computer Vision:** OpenCV (`cv2`) cho việc tìm mốc 4 góc (fiducial markers), là phẳng trang giấy và căn chỉnh tọa độ.
- **Object Detection (Định vị khoanh tròn):** YOLOv8 (`ultralytics`) xác định chính xác các khung chứa Câu hỏi và các khung chứa Vết khoanh tròn của học sinh.
- **Image Classification (Đọc chữ):** Mạng nơ-ron tích chập (Custom PyTorch CNN) được tự huấn luyện. Nó sẽ quét trực tiếp vùng ảnh do YOLO cắt ra để phân loại thành **A, B, C, D** bất chấp đề thi được dàn trang theo hàng dọc, hàng ngang hay ziczac.

## 🚀 Cài Đặt và Chạy Trực Tiếp (Local)

### 1. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 2. Chạy Server
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Truy cập giao diện Swagger UI tại: `http://localhost:8000/docs`







## 🛠️ Tính Năng Nâng Cao: Tự Huấn Luyện Lại 
Dự án cung cấp sẵn bộ công cụ tự động sinh dữ liệu ảo (Synthetic Data) và tự huấn luyện mô hình nằm trong thư mục `training/`.
Nếu bạn muốn hệ thống nhận diện tốt hơn với font chữ đặc thù của trường bạn:
1. Mở `training/generate_dataset.py`, đổi `font` thành font chữ mong muốn và chạy lệnh để sinh tập 4800 bức ảnh mới.
2. Chạy `training/train_ocr.py` để train lại mạng nơ-ron và nó sẽ tự lưu đè lên `models/abcd_ocr.pth`.
