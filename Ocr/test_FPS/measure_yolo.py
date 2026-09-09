import time
import cv2
from ultralytics import YOLO

# 1. Tải mô hình của bạn (nhớ đổi đường dẫn cho đúng)
model_path = r'D:\Desktop\DATN\Ocr\models\best_v9.pt'
model = YOLO(model_path)

# 2. Đọc bức ảnh bài thi mẫu
image_path = r'D:\Desktop\DATN\Ocr\image_test\khoanh\11.jpg' 
img = cv2.imread(image_path)

if img is None:
    print(" Không tìm thấy ảnh. Vui lòng kiểm tra lại đường dẫn!")
    exit()

print(" Đang khởi động mô hình (Warm-up)...")
# Cần chạy nháp vài lần để GPU/CPU khởi tạo bộ nhớ, giúp đo lường chính xác hơn
for _ in range(5):
    _ = model(img, verbose=False)

print(" Bắt đầu đo tốc độ thực tế...")
iterations = 100  # Số lần dự đoán để lấy trung bình
start_time = time.time()

for _ in range(iterations):
    # Thiết lập verbose=False để terminal không bị tràn log
    results = model(img, verbose=False)

end_time = time.time()

# 3. Tính toán kết quả
total_time = end_time - start_time
fps = iterations / total_time
time_per_image = (total_time / iterations) * 1000  # Đổi ra milliseconds

print("\n" + "="*40)
print(f" BÁO CÁO TỐC ĐỘ:")
print(f" Tốc độ xử lý (FPS):        {fps:.2f} ảnh/giây")
print(f" Thời gian xử lý 1 bài thi:  {time_per_image:.2f} ms")
print("="*40)