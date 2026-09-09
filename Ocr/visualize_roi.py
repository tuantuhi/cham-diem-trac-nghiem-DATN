import cv2
import numpy as np

# Import trực tiếp từ hệ thống thực tế của bạn
from core.config import TemplateConfig
from core.calibrator import GridAutoCalibrator

def main():
    print("Đang khởi tạo trình trực quan hóa ROI...")

    # 1. Khởi tạo cấu hình thực tế
    # TemplateConfig mặc định có warp_width=1400, warp_height=2000 và các tọa độ left_xs, right_xs...
    config = TemplateConfig()
    
    # 2. Tạo ảnh nền giả lập mô phỏng ảnh đã qua biến đổi phối cảnh (Warped Image)
    # Kích thước 1400 x 2000, nền trắng
    warped_img = np.ones((config.warp_height, config.warp_width, 3), dtype=np.uint8) * 255
    
    # Vẽ các đường gióng lưới mờ để dễ quan sát (Tùy chọn)
    for x in config.left_xs + config.right_xs:
        cv2.line(warped_img, (x, 0), (x, config.warp_height), (245, 245, 245), 2)
    for y in config.left_row_ys + config.right_row_ys:
        cv2.line(warped_img, (0, y), (config.warp_width, y), (245, 245, 245), 2)

    # 3. Vẽ các ô bong bóng (bubbles) lên ảnh dựa trên tọa độ thực tế từ config
    r = config.bubble_diameter // 2
    color_bubble = (180, 180, 180) # Màu xám nhạt
    
    # Vẽ cột trái (Q1-25)
    for cy in config.left_row_ys:
        for cx in config.left_xs:
            cv2.circle(warped_img, (cx, cy), r, color_bubble, 3)
            
    # Vẽ cột phải (Q26-50)
    for cy in config.right_row_ys:
        for cx in config.right_xs:
            cv2.circle(warped_img, (cx, cy), r, color_bubble, 3)

    # 4. Sử dụng hàm cắt thực tế từ GridAutoCalibrator
    calibrator = GridAutoCalibrator()
    gray_warped = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    
    # Hàm này sẽ sử dụng lề: Trên -20, Trái -60, Dưới +60, Phải +80
    roi, x_start, y_start = calibrator._extract_answer_roi(gray_warped, config)
    
    # 5. Tính toán tọa độ để vẽ khung Bounding Box lên ảnh gốc
    h_roi, w_roi = roi.shape
    x_end = x_start + w_roi
    y_end = y_start + h_roi
    
    # Khung màu đỏ bao quanh khu vực cắt (độ dày 4px)
    cv2.rectangle(warped_img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 4)
    
    # Thêm nhãn tọa độ để dễ debug
    cv2.putText(
        warped_img, 
        f"Answer ROI: X({x_start}->{x_end}) Y({y_start}->{y_end})", 
        (x_start, y_start - 15), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        0.8, 
        (0, 0, 255), 
        2
    )

    # 6. Hiển thị kết quả
    # Ảnh 1400x2000 quá lớn so với màn hình máy tính thông thường, ta thu nhỏ lại 35%
    scale = 0.35
    display_img = cv2.resize(warped_img, (0,0), fx=scale, fy=scale)
    
    print("-" * 50)
    print(f"Kích thước ảnh mục tiêu (Warped): {config.warp_width}x{config.warp_height} pixels")
    print(f"Tọa độ góc trên-trái ROI:       X={x_start}, Y={y_start}")
    print(f"Tọa độ góc dưới-phải ROI:       X={x_end}, Y={y_end}")
    print(f"Kích thước của phần ROI bị cắt: {w_roi}x{h_roi} pixels")
    print("-" * 50)
    print("Bấm phím bất kỳ trên cửa sổ ảnh để thoát...")

    cv2.imwrite("debug_1_full_warped_roi.jpg", display_img)
    cv2.imwrite("debug_2_extracted_roi.jpg", roi)
    print("Đã lưu 2 ảnh debug ra thư mục hiện tại. Vui lòng mở file để xem!")

if __name__ == "__main__":
    main()