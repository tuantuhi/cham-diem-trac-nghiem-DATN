import time
import cv2
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import các class Detector của bạn
from omr_20 import OMR20Detector
from omr_50 import OMR50Detector

def benchmark_omr(detector_name: str, detector_instance, image_path: str, num_iterations: int = 50):
    """
    Hàm đo lường chi tiết từng bước trong pipeline chấm thi OMR truyền thống.
    """
    if not os.path.exists(image_path):
        print(f"[Lỗi] Không tìm thấy ảnh test cho {detector_name} tại: {image_path}")
        return

    print("="*60)
    print(f"BẮT ĐẦU BENCHMARK: {detector_name}")
    print("="*60)

    img = cv2.imread(image_path)
    if img is None:
        print("Không thể đọc ảnh bằng OpenCV.")
        return

    print("Đang Warm-up hệ thống...")
    # Chạy mồi 1 lần để đảm bảo các thư viện OpenCV được nạp vào RAM/Cache
    _ = detector_instance.process(image_path)
    print("Warm-up hoàn tất. Bắt đầu đo lường...\n")

    total_warp = 0.0
    total_calib = 0.0
    total_preprocess = 0.0
    total_extract = 0.0
    total_pipeline = 0.0

    for i in range(num_iterations):
        # --- Bắt chước logic của hàm _run_pipeline để đo từng bước ---
        img_copy = img.copy()
        
        t0 = time.perf_counter()
        
        # 1. Perspective Warp (Tìm 4 góc và cắt phẳng)
        warped, fiducial_ok = detector_instance.perspective_transform(img_copy)
        t1 = time.perf_counter()

        # 2. Grid Auto-Calibration (Dò vòng tròn bằng HoughCircles)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        if detector_instance.config.enable_hough_calibration:
            detector_instance._active_config = detector_instance._calibrator.calibrate(gray, detector_instance.config)
        else:
            detector_instance._active_config = detector_instance.config
        detector_instance._build_grid(detector_instance._active_config)
        t2 = time.perf_counter()

        # 3. Preprocessing (CLAHE, Blur, Adaptive Threshold, Morphology)
        binary = detector_instance.preprocess(gray)
        t3 = time.perf_counter()

        # 4. Fill Measurement & Extraction (Đo diện tích pixel và chọn đáp án)
        detector_instance.measure_fill_ratios(binary)
        fill_threshold = detector_instance.compute_adaptive_fill_threshold(detector_instance._grid)
        results = detector_instance.extract_answers(
            detector_instance._grid, fill_threshold, detector_instance.config.total_questions
        )
        t4 = time.perf_counter()

        # Cộng dồn thời gian
        total_warp += (t1 - t0)
        total_calib += (t2 - t1)
        total_preprocess += (t3 - t2)
        total_extract += (t4 - t3)
        total_pipeline += (t4 - t0)

    # --- TỔNG KẾT ---
    avg_warp = total_warp / num_iterations
    avg_calib = total_calib / num_iterations
    avg_preprocess = total_preprocess / num_iterations
    avg_extract = total_extract / num_iterations
    avg_total = total_pipeline / num_iterations

    print(f"KẾT QUẢ TRUNG BÌNH ({detector_name} - {num_iterations} vòng lặp):")
    print(f"1. Warp (Định vị & Cắt 4 góc) : {avg_warp:.4f} giây")
    print(f"2. Calib (HoughCircles)       : {avg_calib:.4f} giây")
    print(f"3. Preprocess (Xử lý ảnh)     : {avg_preprocess:.4f} giây")
    print(f"4. Extraction (Tính điểm)     : {avg_extract:.4f} giây")
    print("-" * 60)
    print(f"TỔNG THỜI GIAN/ẢNH            : {avg_total:.4f} giây (~{1.0/avg_total:.2f} FPS)")
    print("="*60 + "\n")

if __name__ == "__main__":
    # TODO: Thay đổi đường dẫn đến 2 ảnh test tương ứng của bạn
    IMAGE_TEST_20Q = r"D:\Desktop\DATN\Ocr\image_test\20\z7856899392570_7d75ea3e9aa1192412f657b486e773dd.jpg"
    IMAGE_TEST_50Q = r"D:\Desktop\DATN\Ocr\image_test\50\z7855474758101_58b75abdb2e0b5bbba9391c952b09dba.jpg"

    # 1. Test cho mẫu 20 câu
    detector_20 = OMR20Detector()
    benchmark_omr("MẪU 20 CÂU", detector_20, IMAGE_TEST_20Q, num_iterations=50)

    # 2. Test cho mẫu 50 câu
    detector_50 = OMR50Detector()
    benchmark_omr("MẪU 50 CÂU", detector_50, IMAGE_TEST_50Q, num_iterations=50)