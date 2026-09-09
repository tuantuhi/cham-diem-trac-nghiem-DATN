import time
import cv2
import os


from yolo_pipeline import YOLOPipeline 

def benchmark_full_pipeline(yolo_path: str, ocr_path: str, image_path: str, num_iterations: int = 5):
    """
    Hàm đo lường chi tiết từng bước trong pipeline chấm thi.
    """
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy ảnh tại '{image_path}'")
        return

    print("="*60)
    print("KHỞI TẠO PIPELINE...")
    start_init = time.perf_counter()
    pipeline = YOLOPipeline(yolo_model_path=yolo_path, ocr_model_path=ocr_path)
    print(f"Hoàn tất khởi tạo trong {time.perf_counter() - start_init:.2f} giây.")
    print("="*60)

    img = cv2.imread(image_path)
    if img is None:
        print("Không thể đọc ảnh bằng OpenCV.")
        return

    print("\nĐang Warm-up hệ thống...")
    _ = pipeline.process_image(img)
    print("Warm-up hoàn tất. Bắt đầu đo lường chính thức...\n")

    # Các biến lưu tổng thời gian của từng bước
    total_deskew = 0.0
    total_yolo = 0.0
    total_easyocr = 0.0
    total_cnn = 0.0
    total_vis = 0.0
    total_pipeline = 0.0

    for i in range(num_iterations):
        print(f"--- Vòng lặp {i+1}/{num_iterations} ---")
        
        # 1. Deskew (Xoay ảnh)
        t0 = time.perf_counter()
        img_deskewed = pipeline.deskew_image(img.copy())
        t1 = time.perf_counter()
        
        # 2. YOLO (Tìm Bounding Box)
        ques_boxes, ans_boxes = pipeline._extract_boxes(img_deskewed)
        t2 = time.perf_counter()
        
        # 3. EasyOCR (Đọc ID câu hỏi)
        ques_with_ids = pipeline._read_question_ids(img_deskewed, ques_boxes)
        t3 = time.perf_counter()
        
        # 4. Custom CNN & Ghép cặp (Đọc đáp án A, B, C, D)
        ans_results = pipeline._match_and_read_answers(img_deskewed, ans_boxes, ques_with_ids)
        t4 = time.perf_counter()
        
        # 5. Vẽ kết quả (Visualization)
        vis_img = pipeline._draw_visualization(img_deskewed, ques_boxes, ans_results)
        t5 = time.perf_counter()

        # Tính toán thời gian từng bước
        deskew_time = t1 - t0
        yolo_time = t2 - t1
        easyocr_time = t3 - t2
        cnn_time = t4 - t3
        vis_time = t5 - t4
        pipeline_time = t5 - t0

        total_deskew += deskew_time
        total_yolo += yolo_time
        total_easyocr += easyocr_time
        total_cnn += cnn_time
        total_vis += vis_time
        total_pipeline += pipeline_time

        print(f"  Deskew  : {deskew_time:.4f}s")
        print(f"  YOLO    : {yolo_time:.4f}s")
        print(f"  EasyOCR : {easyocr_time:.4f}s")
        print(f"  CNN/Match: {cnn_time:.4f}s")
        print(f"  Tổng    : {pipeline_time:.4f}s\n")

    # --- TỔNG KẾT ---
    print("="*60)
    print(f"KẾT QUẢ TRUNG BÌNH (Sau {num_iterations} lần chạy):")
    print(f"1. Tiền xử lý (Deskew) : {total_deskew / num_iterations:.4f} giây")
    print(f"2. YOLO (Extract box)  : {total_yolo / num_iterations:.4f} giây")
    print(f"3. EasyOCR (Đọc số)    : {total_easyocr / num_iterations:.4f} giây")
    print(f"4. CNN (Đọc ABCD)      : {total_cnn / num_iterations:.4f} giây")
    print(f"5. Vẽ ảnh Output       : {total_vis / num_iterations:.4f} giây")
    print("-" * 60)
    
    avg_total = total_pipeline / num_iterations
    print(f"TỔNG THỜI GIAN/ẢNH     : {avg_total:.4f} giây (~{1.0/avg_total:.2f} FPS)")
    print("="*60)

if __name__ == "__main__":
    # Điền chính xác đường dẫn đến model và 1 ảnh test kích thước đầy đủ 
    YOLO_MODEL = r"D:\Desktop\DATN\Ocr\models\best_v9.pt"
    OCR_MODEL = r"D:\Desktop\DATN\Ocr\models\abcd_ocr.pth"
    TEST_IMAGE = r"D:\Desktop\DATN\Ocr\image_test\khoanh\z7867306955370_64c59b19f68b47bf9c574c589f0aef37.jpg"

    # Chạy thử 10 lần để lấy kết quả trung bình
    benchmark_full_pipeline(YOLO_MODEL, OCR_MODEL, TEST_IMAGE, num_iterations=10)