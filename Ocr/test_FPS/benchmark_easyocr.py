import easyocr
import time
import cv2
import torch
import os

def benchmark_easyocr(image_path: str, num_iterations: int = 50):
    """
    Hàm đo lường tốc độ của EasyOCR trên một bức ảnh cụ thể 
    (Tính toán dựa trên Tổng thời gian - Thông lượng).
    """
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy ảnh tại đường dẫn '{image_path}'")
        return

    # 1. Khởi tạo reader
    print("="*40)
    print("Đang khởi tạo EasyOCR...")
    start_init = time.perf_counter()
    
    # Cờ gpu=True mặc định sẽ dùng CUDA nếu có
    has_gpu = torch.cuda.is_available()
    reader = easyocr.Reader(['vi', 'en'], gpu=has_gpu)
    
    print(f"Khởi tạo xong trong {time.perf_counter() - start_init:.2f} giây.")
    print(f"Phần cứng sử dụng: {'GPU (CUDA)' if has_gpu else 'CPU'}")
    print("="*40)

    # 2. Đọc ảnh bằng OpenCV
    img = cv2.imread(image_path)
    
    # 3. Warm-up (Khởi động)
    print("\n Đang warm-up model (chạy nháp 3 lần)...")
    for _ in range(3):
        _ = reader.readtext(img)

    # 4. Đo tốc độ chính thức (Tính trên tổng thời gian)
    print(f"\n Bắt đầu đo tốc độ thực tế với {num_iterations} vòng lặp...")
    
    # Bấm giờ toàn bộ quá trình chạy thay vì từng vòng lặp
    start_time = time.perf_counter()

    for _ in range(num_iterations):
        # Mẹo: Nếu bạn chỉ đọc ID câu hỏi (là số), hãy bật allowlist='0123456789'
        # results = reader.readtext(img, allowlist='0123456789') 
        
        results = reader.readtext(img)

    end_time = time.perf_counter()

    # 5. Tính toán và Thống kê kết quả
    total_time = end_time - start_time
    fps = num_iterations / total_time
    time_per_image = (total_time / num_iterations) * 1000  

    print("\n" + "="*40)
    print(" KẾT QUẢ BENCHMARK EASYOCR:")
    print(f" Tổng thời gian đo      : {total_time:.4f} giây")
    print(f" Tốc độ xử lý (FPS)     : {fps:.4f} ảnh/giây")
    print(f" Thời gian xử lý 1 ảnh  : {time_per_image:.4f} ms")
    print("="*40)

if __name__ == "__main__":
    # Đổi đường dẫn này thành một ảnh crop ID câu hỏi hoặc ảnh full tờ giấy thi của bạn
    TEST_IMAGE = r"D:\Desktop\DATN\Ocr\test_time_easyOCR.png"

    # Chạy thử 50 lần để lấy trung bình
    benchmark_easyocr(TEST_IMAGE, num_iterations=50)