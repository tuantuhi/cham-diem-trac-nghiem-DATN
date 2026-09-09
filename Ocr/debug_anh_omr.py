# visualize_pipeline.py
import os
import cv2
import numpy as np
from pathlib import Path
from templates.omr_50 import OMR50Detector  # Kế thừa cấu hình 50 câu hỏi

class OMRStepVisualizer(OMR50Detector):
    """
    Trình trực quan hóa bóc tách chi tiết từng bước xử lý của pipeline OMR.
    Ghi lại ảnh kết quả sau mỗi thuật toán chính để phục vụ debug và nghiên cứu.
    """
    def __init__(self, output_dir: str = "omr_debug_steps"):
        super().__init__()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_and_export_all_steps(self, image_path: str | Path):
        print(f"[*] Bắt đầu phân tích pipeline cho ảnh: {image_path}")
        image_name = Path(image_path).stem
        
        # ------------------------------------------------------------------
        # BƯỚC 1: Đọc ảnh gốc (Load Image)
        # ------------------------------------------------------------------
        img = self.load_image(image_path)
        cv2.imwrite(str(self.output_dir / f"{image_name}_01_original.jpg"), img)
        print("  [>] Đã xuất: 01_original.jpg (Ảnh thô ban đầu)")

        # ------------------------------------------------------------------
        # BƯỚC 2: Căn chỉnh phối cảnh (Perspective Transform)
        # ------------------------------------------------------------------
        # Trích xuất ma trận phối cảnh dựa trên 4 điểm chuẩn góc vuông đen
        warped, fiducial_ok = self.perspective_transform(img)
        cv2.imwrite(str(self.output_dir / f"{image_name}_02_warped.jpg"), warped)
        print(f"  [>] Đã xuất: 02_warped.jpg (Trạng thái phẳng 1400x2000. Điểm chuẩn thành công: {fiducial_ok})")

        # ------------------------------------------------------------------
        # BƯỚC 3: Chuyển đổi ảnh xám (Grayscale Conversion)
        # ------------------------------------------------------------------
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(self.output_dir / f"{image_name}_03_gray.jpg"), gray)
        print("  [>] Đã xuất: 03_gray.jpg (Chuẩn hóa kênh màu)")

        # ------------------------------------------------------------------
        # BƯỚC 4: Hiệu chỉnh lưới ô bong bóng (Grid Auto Calibration)
        # ------------------------------------------------------------------
        # Thuật toán chính: Dùng HoughCircles để dò tìm vòng tròn thực tế rồi gom cụm 1D
        
        # 4a. Vẽ lưới lý thuyết (Template mặc định cố định) để so sánh
        img_template_grid = warped.copy()
        self._build_grid(self.config)  # Dùng cấu hình gốc chưa hiệu chỉnh
        for b in self._grid:
            cv2.circle(img_template_grid, (b.cx, b.cy), b.radius, (255, 0, 0), 2)  # Màu xanh dương
        cv2.imwrite(str(self.output_dir / f"{image_name}_04a_template_grid.jpg"), img_template_grid)
        
        # 4b. Tiến hành chạy thuật toán hiệu chuẩn tự động HoughCircles
        if self.config.enable_hough_calibration:
            self._active_config = self._calibrator.calibrate(gray, self.config)
        else:
            self._active_config = self.config
        self._build_grid(self._active_config)  # Xây dựng lại lưới thực tế sau chỉnh sửa
        
        # Vẽ lưới thực tế sau khi đã bám dính vào các ô tròn trên giấy
        img_calibrated_grid = warped.copy()
        for b in self._grid:
            cv2.circle(img_calibrated_grid, (b.cx, b.cy), b.radius, (0, 165, 255), 2)  # Màu cam
        cv2.imwrite(str(self.output_dir / f"{image_name}_04b_calibrated_grid.jpg"), img_calibrated_grid)
        print("  [>] Đã xuất: 04a_template_grid.jpg (Lưới thiết kế gốc)")
        print("  [>] Đã xuất: 04b_calibrated_grid.jpg (Lưới thực tế sau hiệu chuẩn HoughCircles)")

        # ------------------------------------------------------------------
        # BƯỚC 5: Tiền xử lý toán học (CLAHE + Adaptive Threshold + Morphology)
        # ------------------------------------------------------------------
        # Thuật toán chính: Cân bằng sáng cục bộ, phân ngưỡng thích ứng khử bóng đổ và lọc hình thái học
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
        gray_eq = clahe.apply(gray)
        blur = cv2.GaussianBlur(gray_eq, (5, 5), 0)
        
        # 5.2 Phân ngưỡng thích nghi (CHƯA CÓ MORPHOLOGY)
        binary_raw = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 8
        )
        cv2.imwrite(str(self.output_dir / f"{image_name}_05a_thresh_only.jpg"), binary_raw)
        
        # 5.3 Phép Mở (Opening) - Xóa nhiễu li ti
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary_opened = cv2.morphologyEx(binary_raw, cv2.MORPH_OPEN, kernel_open, iterations=1)
        cv2.imwrite(str(self.output_dir / f"{image_name}_05b_after_opening.jpg"), binary_opened)
        
        # 5.4 Phép Đóng (Closing) - Lấp lỗ rỗng vết chì
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        binary_final = cv2.morphologyEx(binary_opened, cv2.MORPH_CLOSE, kernel_close, iterations=1)
        cv2.imwrite(str(self.output_dir / f"{image_name}_05c_after_closing.jpg"), binary_final)
        
        # Gán lại để truyền cho Bước 6
        binary = binary_final
        
        # ------------------------------------------------------------------
        # BƯỚC 6: Đo tỷ lệ điền đầy & Tính toán ngưỡng thích ứng (Adaptive Fill Threshold)
        # ------------------------------------------------------------------
        self.measure_fill_ratios(binary)  # Quét mặt nạ hình tròn thu nhỏ 18%
        fill_threshold = self.compute_adaptive_fill_threshold(self._grid)  # Thuật toán Otsu-like tìm thung lũng Histogram
        print(f"  [i] Ngưỡng điền đầy tự động tính toán riêng cho ảnh này: {fill_threshold:.3f}")

        # ------------------------------------------------------------------
        # BƯỚC 7: Logic nhận diện đáp án & Xuất đồ họa cuối cùng
        # ------------------------------------------------------------------
        # Thuật toán chính: Phân hạng điểm đậm, lọc tẩy xóa mờ và chồng lấn đáp án
        results = self.extract_answers(self._grid, fill_threshold, self.config.total_questions)
        
        # Vẽ phủ màu kết quả: Xanh lá (đã chọn), Cam (nghi ngờ/tẩy xóa), Xám (trống)
        vis = self.draw_visualization(warped, self._grid, results, fill_threshold)
        cv2.imwrite(str(self.output_dir / f"{image_name}_06_final_result.jpg"), vis)
        print("  [>] Đã xuất: 06_final_result.jpg (Ảnh trực quan hóa kết quả chấm điểm)")

        # Xuất file dữ liệu JSON đi kèm
        json_path = self.output_dir / f"{image_name}_data.json"
        self.export_json(results, json_path)
        print(f"  [>] Đã xuất: {json_path.name} (File cấu trúc dữ liệu text kết quả)")
        
        print("[*] Hoàn thành xuất toàn bộ các bước xử lý ảnh thành công!\n")
        return results

if __name__ == "__main__":
    # KHAI BÁO ĐƯỜNG DẪN ẢNH ĐỂ CHẠY THỬ NGHIỆM
    # Vui lòng thay thế bằng đường dẫn ảnh chụp phiếu 50 câu thực tế của bạn
    TEST_IMAGE = r"D:\Desktop\DATN\Ocr\image_test\50\z7894180360933_211f89dab8317c30071ac2366eeae60b.jpg"
    
    if not os.path.exists(TEST_IMAGE):
        print(f"[!] Lỗi: Không tìm thấy file ảnh mẫu tại đường dẫn '{TEST_IMAGE}'.")
        print("[i] Hãy tạo thư mục 'data', bỏ ảnh của bạn vào và cập nhật lại biến TEST_IMAGE.")
    else:
        # Khởi tạo bộ visualize và chỉ định thư mục xuất ảnh ra
        visualizer = OMRStepVisualizer(output_dir="omr_pipeline_debug")
        visualizer.process_and_export_all_steps(TEST_IMAGE)