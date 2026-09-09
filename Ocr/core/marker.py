"""
Nhận diện điểm chuẩn (fiducial marker) và biến đổi phối cảnh (perspective warp).

Phát hiện 4 điểm đánh dấu hình vuông màu đen ở các góc trên phiếu trả lời và
sử dụng chúng để thực hiện phép biến đổi phối cảnh chính xác lên một khung ảnh có kích thước cố định.
Sẽ dự phòng (fallback) sang phương pháp nhận diện viền giấy dựa trên thuật toán Canny nếu
không tìm thấy các điểm đánh dấu.
"""
from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class FiducialMarkerDetector:
    """Phát hiện 4 điểm đánh dấu hình vuông màu đen trong khu vực trả lời.

    Phiếu trả lời trắc nghiệm của Việt Nam có các hình vuông được tô đen tại 4 góc của
    khu vực tô đáp án (không phải ở các góc của tờ giấy). Các điểm này cung cấp
    mục tiêu biến đổi (warp target) đáng tin cậy hơn nhiều so với mép giấy.

    Chiến lược nhận diện:
        1. Chuyển sang ảnh xám, áp dụng CLAHE để chuẩn hóa ánh sáng
        2. Phân ngưỡng Otsu → ảnh nhị phân (vật thể tối trên nền sáng)
        3. Tìm đường viền (contours), lọc theo:
            - Diện tích: [min_area, max_area]
            - Tỷ lệ khung hình gần bằng 1.0 (hình vuông)
            - Độ đặc (Solidity) > 0.85 (hình dạng được tô đặc)
        4. Nếu tìm thấy ≥ 4 ứng viên, chọn 4 ứng viên tốt nhất theo diện tích, sắp xếp theo thứ tự Trái-Trên → Phải-Trên → Phải-Dưới → Trái-Dưới (TL→TR→BR→BL)
        5. Tính toán ma trận biến đổi phối cảnh từ 4 điểm đó → warp_width × warp_height
    """

    def __init__(self, warp_width: int = 1400, warp_height: int = 2000):
        self.warp_width = warp_width
        self.warp_height = warp_height

    def detect_and_warp(self, image: np.ndarray) -> tuple[np.ndarray, bool]:
        """Nhận diện các điểm chuẩn và trả về hình ảnh đã được hiệu chỉnh phối cảnh.

        Trả về:
            (warped_image, success): success=True nếu tìm thấy các điểm đánh dấu,
            False nếu phương pháp dự phòng (biến đổi toàn bộ tờ giấy) được sử dụng để thay thế.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Sử dụng CLAHE để xử lý ánh sáng không đều
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_eq = clahe.apply(gray)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        
        # Phương pháp chính: Phân ngưỡng Otsu (nhanh, hiệu quả)
        _, binary_otsu = cv2.threshold(gray_eq, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        binary_otsu = cv2.morphologyEx(binary_otsu, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        markers = self._find_square_markers(binary_otsu, image.shape)
        
        # Phương pháp dự phòng cho nền tối khi Otsu thất bại
        if markers is None or len(markers) < 4:
            logger.info("Otsu không tìm thấy điểm đánh dấu, đang thử adaptiveThreshold...")
            binary_adapt = cv2.adaptiveThreshold(
                gray_eq, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 51, 15
            )
            binary_adapt = cv2.morphologyEx(binary_adapt, cv2.MORPH_CLOSE, kernel, iterations=2)
            markers = self._find_square_markers(binary_adapt, image.shape)

        if markers is not None and len(markers) >= 4:
            pts = self._order_four_points(markers)
            warped = self._warp(image, pts)
            logger.info("Đã tìm thấy điểm chuẩn – áp dụng biến đổi chính xác")
            return warped, True

        # Dự phòng: phát hiện ranh giới tờ giấy (phương pháp Canny)
        logger.warning("Không tìm thấy điểm chuẩn – chuyển sang dự phòng biến đổi theo mép giấy")
        warped = self._fallback_warp(image, gray)
        return warped, False

    # ------------------------------------------------------------------

    def _find_square_markers(
        self, binary: np.ndarray, img_shape: tuple
    ) -> Optional[np.ndarray]:
        """Trả về tọa độ tâm của 4 điểm chuẩn ở góc, hoặc None.

        Chiến lược:
            1. Tìm tất cả các khối (blobs) màu tối, đặc, có dạng gần vuông trong khoảng kích thước dự kiến
            2. Lọc ra một cụm có kích thước đồng nhất (tất cả các điểm đánh dấu đều có cùng kích thước)
            3. Từ tập hợp đã lọc, chọn khối gần nhất với từng góc trong 4
               góc của hình ảnh (Trái-Trên, Phải-Trên, Phải-Dưới, Trái-Dưới)
            Cách này xử lý tốt các mẫu giấy có từ 8-15+ điểm đánh dấu.
        """
        h, w = img_shape[:2]
        img_area = h * w

        # Phạm vi diện tích: các điểm đánh dấu là những hình vuông nhỏ, ~0.008%-0.8% diện tích hình ảnh
        min_area = img_area * 0.00008
        max_area = img_area * 0.008  # giới hạn trên nghiêm ngặt hơn để loại bỏ các khối không hợp lệ

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            if bw == 0 or bh == 0:
                continue
            # Phải có hình dạng gần vuông
            aspect = min(bw, bh) / max(bw, bh)
            if aspect < 0.50:
                continue

            # Phải đặc (được tô kín, không phải hình nhẫn/vòng)
            rect = cv2.minAreaRect(cnt)
            box_area = rect[1][0] * rect[1][1]
            if box_area == 0:
                continue
            rotated_extent = area / box_area
            if rotated_extent < 0.60:
                continue
                
            hull_area = cv2.contourArea(cv2.convexHull(cnt))
            if hull_area == 0:
                continue
            solidity = area / hull_area
            if solidity < 0.72:
                continue

            # Không được quá dài/dẹt về kích thước tuyệt đối
            side = (bw + bh) / 2
            if side < 15 or side > 120:
                continue

            cx = x + bw // 2
            cy = y + bh // 2
            candidates.append((cx, cy, area, side))

        if len(candidates) < 4:
            logger.warning("Không tìm thấy điểm chuẩn (có ít hơn 4 ứng viên phù hợp).")
            return None

        # Lọc thành cụm có kích thước đồng nhất:
        # Tất cả các điểm đánh dấu thật phải có diện tích tương đồng nhau (trong phạm vi 3.5 lần so với trung vị)
        areas = np.array([c[2] for c in candidates])
        median_area = np.median(areas)
        
        consistent_cands = []
        for c in candidates:
            if median_area / 3.5 <= c[2] <= median_area * 3.5:
                consistent_cands.append(c)
                
        if len(consistent_cands) < 4:
            logger.debug(f"Chỉ tìm thấy {len(consistent_cands)} điểm đánh dấu phù hợp")
            return None

        # Chọn chính xác 4 điểm (gần nhất với mỗi góc của hình ảnh)
        corners = np.array([[0, 0], [w, 0], [w, h], [0, h]])
        pts_arr = np.array([[c[0], c[1]] for c in consistent_cands])
        
        selected_pts = []
        used_indices = set()
        
        for corner in corners:
            dists = np.linalg.norm(pts_arr - corner, axis=1)
            # Loại trừ các điểm đã được sử dụng
            for idx in used_indices:
                dists[idx] = np.inf
                
            best_idx = int(np.argmin(dists))
            used_indices.add(best_idx)
            selected_pts.append(pts_arr[best_idx])

        return np.array(selected_pts, dtype="float32")

    @staticmethod
    def _order_four_points(pts: np.ndarray) -> np.ndarray:
        """Sắp xếp 4 điểm theo thứ tự trên-trái, trên-phải, dưới-phải, dưới-trái."""
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]   # TL (Trái-Trên): x+y nhỏ nhất
        rect[2] = pts[np.argmax(s)]   # BR (Phải-Dưới): x+y lớn nhất
        d = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(d)]   # TR (Phải-Trên): y-x nhỏ nhất
        rect[3] = pts[np.argmax(d)]   # BL (Trái-Dưới): y-x lớn nhất
        return rect

    def _warp(self, image: np.ndarray, src_pts: np.ndarray) -> np.ndarray:
        """Biến đổi phối cảnh từ src_pts sang toàn bộ khung ảnh."""
        dst = np.array([
            [0, 0],
            [self.warp_width - 1, 0],
            [self.warp_width - 1, self.warp_height - 1],
            [0, self.warp_height - 1],
        ], dtype="float32")
        M = cv2.getPerspectiveTransform(src_pts, dst)
        return cv2.warpPerspective(image, M, (self.warp_width, self.warp_height))

    def _fallback_warp(self, image: np.ndarray, gray: np.ndarray) -> np.ndarray:
        """Phát hiện ranh giới tờ giấy dựa trên Canny ."""
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        img_area = image.shape[0] * image.shape[1]

        for canny_lo, canny_hi, dilate_n in [
            (30, 100, 2), (50, 150, 3), (20, 80, 2), (40, 120, 2)
        ]:
            edges = cv2.Canny(blur, canny_lo, canny_hi)
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=dilate_n)
            edges = cv2.erode(edges, kernel, iterations=1)

            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            for cnt in contours[:5]:
                if cv2.contourArea(cnt) < img_area * 0.2:
                    continue
                peri = cv2.arcLength(cnt, True)
                for eps in [0.02, 0.03, 0.04, 0.05]:
                    approx = cv2.approxPolyDP(cnt, eps * peri, True)
                    if len(approx) == 4:
                        pts = self._order_four_points(
                            approx.reshape(4, 2).astype("float32")
                        )
                        return self._warp(image, pts)
  
        logger.warning("Không tìm thấy ranh giới giấy")
        raise ValueError("Hình ảnh không phù hợp. Vui lòng chụp lại!")