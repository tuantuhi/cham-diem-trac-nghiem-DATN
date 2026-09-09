import cv2
import numpy as np
import logging
import os

# Cấu hình logging để xem thông báo góc xoay
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deskew_image(image: np.ndarray, edges_save_path: str = None) -> np.ndarray:
    """Tự động phát hiện góc nghiêng và xoay phẳng hình ảnh."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    if edges_save_path:
        cv2.imwrite(edges_save_path, edges)
        logger.info(f"Đã lưu ảnh sau bước tìm cạnh tại: {edges_save_path}")

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
    
    logger.info("Không phát hiện độ nghiêng (hoặc ảnh đã thẳng).")
    return image

if __name__ == "__main__":
    # 1. Đường dẫn ảnh đầu vào
    input_image_path = r"D:\Desktop\DATN\Ocr\image_test\khoanh\z7901132293599_49405a654cc9eac01b9c07a2da1067d9.jpg"
    
    # 2. CHỈ ĐỊNH THƯ MỤC LƯU KẾT QUẢ CHUNG
    output_dir = r"D:\Desktop\DATN\Ocr\Output_Images_Deskew"

    # Tự động tạo thư mục này nếu nó chưa tồn tại trên máy tính
    os.makedirs(output_dir, exist_ok=True)

    # 3. Tạo đường dẫn chi tiết cho 2 file bằng os.path.join
    edges_image_path = os.path.join(output_dir, "test_edges_only.jpg")
    output_image_path = os.path.join(output_dir, "test_deskew_only.jpg")

    # 4. Đọc ảnh gốc
    img = cv2.imread(input_image_path)
    if img is None:
        logger.error(f"Không thể đọc ảnh từ: {input_image_path}")
    else:
        logger.info(f"Đã đọc ảnh thành công. Kích thước: {img.shape}")
        
        # 5. Chạy hàm xoay phẳng ảnh
        deskewed_img = deskew_image(img, edges_save_path=edges_image_path)
        
        # 6. Lưu ảnh kết quả
        cv2.imwrite(output_image_path, deskewed_img)
        logger.info(f"Đã lưu ảnh sau khi xoay tại: {output_image_path}")
        logger.info(f"Cả 2 ảnh đã được lưu chung vào thư mục: {output_dir}")