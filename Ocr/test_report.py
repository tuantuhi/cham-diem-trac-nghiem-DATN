import os
import glob
import json
from yolo_pipeline import YOLOPipeline
from templates import OMR50Detector, OMR20Detector

def main():
    base_input_dir = r"D:\Desktop\DATN\Ocr\image_test"
    base_output_dir = r"D:\Desktop\DATN\Ocr\image_test_results\report_final"
    
    yolo_model_path = r"D:\Desktop\DATN\Ocr\models\best_v9.pt"
    ocr_model_path = r"D:\Desktop\DATN\Ocr\models\abcd_ocr.pth"
    
    print("Đang tải các hệ thống AI (YOLO + OMR 50 + OMR 20)...")
    yolo_pipeline = YOLOPipeline(yolo_model_path, ocr_model_path)
    omr50_detector = OMR50Detector()
    omr20_detector = OMR20Detector()
    
    folders = ["khoanh", "50", "20"]
    
    for folder in folders:
        input_dir = os.path.join(base_input_dir, folder)
        output_dir = os.path.join(base_output_dir, folder)
        
        if not os.path.exists(input_dir):
            print(f"Không tìm thấy thư mục: {input_dir}")
            continue
            
        os.makedirs(output_dir, exist_ok=True)
        
        image_paths = glob.glob(os.path.join(input_dir, "*.jpg")) + glob.glob(os.path.join(input_dir, "*.png"))
        
        print(f"\n--- Đang xử lý thư mục {folder} ({len(image_paths)} ảnh) ---")
        
        for i, img_path in enumerate(image_paths, 1):
            filename = os.path.basename(img_path)
            print(f"[{i}/{len(image_paths)}] Đang xử lý: {filename}...")
            
            # Tạo đường dẫn lưu kết quả
            base_name = os.path.splitext(filename)[0]
            out_json = os.path.join(output_dir, f"{base_name}_result.json")
            out_vis = os.path.join(output_dir, f"{base_name}_vis.jpg")
            
            try:
                if folder == "khoanh":
                    # Luồng YOLO cho đề thi dạng khoanh tay
                    yolo_pipeline.process(img_path, out_json, out_vis)
                elif folder == "50":
                    # Luồng tô bong bóng 50 câu
                    results = omr50_detector.process_with_visualization(img_path, out_vis)
                    with open(out_json, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                elif folder == "20":
                    # Luồng tô bong bóng 20 câu
                    results = omr20_detector.process_with_visualization(img_path, out_vis)
                    with open(out_json, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Lỗi khi xử lý {filename}: {str(e)}")
            
    print(f"\nHoàn tất! Hệ thống đã xuất toàn bộ ảnh và kết quả json vào thư mục: {base_output_dir}")

if __name__ == "__main__":
    main()
