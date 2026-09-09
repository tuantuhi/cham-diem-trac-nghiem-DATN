"""
Tự động hiệu chuẩn lưới dựa trên thuật toán HoughCircles.

Sau khi biến đổi phối cảnh, các vòng tròn điền đáp án sẽ nằm ở vị trí gần đúng với tọa độ
trên mẫu . Module này sử dụng thuật toán HoughCircles để tìm các vị trí thực tế của
vòng tròn, sau đó gom cụm chúng để tinh chỉnh chính xác các tọa độ X của cột và Y của hàng.

Sẽ dự phòng sang tọa độ của mẫu nếu chất lượng nhận diện kém.
"""
from __future__ import annotations

import logging
from dataclasses import replace
from typing import Optional

import cv2
import numpy as np

from core.config import TemplateConfig

logger = logging.getLogger(__name__)


class GridAutoCalibrator:
    """Sử dụng HoughCircles để tinh chỉnh tọa độ lưới các ô bong bóng.
    """

    # Phạm vi bán kính dự kiến của bong bóng (ô tròn) trong ảnh đã biến đổi (tính bằng pixel)
    MIN_RADIUS = 10
    MAX_RADIUS = 22

    def calibrate(
        self,
        gray_warped: np.ndarray,
        config: TemplateConfig,
    ) -> TemplateConfig:
        """Trả về một TemplateConfig (có thể đã được tinh chỉnh).
        
        Sử dụng thuật toán HoughCircles để tìm tâm các bong bóng, sau đó gom cụm chúng
        thành các tọa độ lưới. Kiểm tra tính hợp lệ của khoảng cách trước khi chấp nhận.
        """
        answer_roi, roi_x0, roi_y0 = self._extract_answer_roi(gray_warped, config)
        circles = self._detect_circles(answer_roi)

        expected_circles = config.total_questions * config.choices_per_question
        min_circles = max(20, expected_circles // 4)
        if circles is None or len(circles) < min_circles:
            logger.info("Bỏ qua tự động hiệu chuẩn (không phát hiện đủ số vòng tròn)")
            return config

        logger.info(f"HoughCircles tìm thấy {len(circles)} vòng tròn – đang hiệu chuẩn lưới")

        # Bù trừ (offset) trở lại hệ tọa độ của ảnh đã biến đổi
        abs_circles = [(cx + roi_x0, cy + roi_y0, r)
                       for (cx, cy, r) in circles]

        left_xs, right_xs = self._cluster_x_columns(abs_circles, config)
        left_ys, right_ys = self._cluster_y_rows(abs_circles, config)

        # Kiểm tra tính hợp lệ: Các cột X phải khớp với số lựa chọn mỗi câu (choices_per_question),
        # các hàng Y phải khớp với số câu mỗi cột (questions_per_column). Khoảng cách X phải hợp lý.
        n_choices = config.choices_per_question
        n_rows = config.questions_per_column
        valid = (
            len(left_xs) == n_choices and len(right_xs) == n_choices
            and len(left_ys) == n_rows and len(right_ys) == n_rows
        )
        
        if valid:
            # Kiểm tra khoảng cách X có hợp lý không (không quá hẹp so với mẫu)
            left_spacing = (left_xs[-1] - left_xs[0]) / 3
            right_spacing = (right_xs[-1] - right_xs[0]) / 3
            min_spacing = ((config.left_xs[-1] - config.left_xs[0]) / 3) * 0.65
            if left_spacing < min_spacing or right_spacing < min_spacing:
                logger.info(
                    f"Từ chối hiệu chuẩn: Khoảng cách X quá nhỏ "
                    f"(trái={left_spacing:.0f}px, phải={right_spacing:.0f}px, tối_thiểu_yêu_cầu={min_spacing:.0f}px)"
                )
                valid = False

        if valid:
            refined = replace(
                config,
                left_xs=left_xs,
                right_xs=right_xs,
                left_row_ys=left_ys,
                right_row_ys=right_ys,
            )
            logger.info("Hiệu chuẩn lưới thành công")
            return refined

        logger.info(
            f"Các cụm hiệu chuẩn không hoàn chỉnh "
            f"(lx={len(left_xs)},rx={len(right_xs)},ly={len(left_ys)},ry={len(right_ys)}) "
            f"– sử dụng giá trị mặc định của mẫu"
        )
        return config

    # ------------------------------------------------------------------

    @staticmethod
    def _roi_offsets(config: TemplateConfig) -> tuple[int, int]:
        """Góc trên-trái của khu vực trả lời tổng hợp trong ảnh đã biến đổi."""
        y_start = min(config.left_row_ys[0], config.right_row_ys[0]) - 25
        x_start = min(config.left_xs[0], config.right_xs[0]) - 60
        return max(0, y_start), max(0, x_start)

    def _extract_answer_roi(
        self, gray: np.ndarray, config: TemplateConfig
    ) -> tuple[np.ndarray, int, int]:
        """Trích xuất khu vực trả lời dưới dạng (roi, x_offset, y_offset)."""
        y_start = max(0, min(config.left_row_ys[0], config.right_row_ys[0]) - 25)
        x_start = max(0, min(config.left_xs[0], config.right_xs[0]) - 60)
        y_end = min(gray.shape[0], max(config.left_row_ys[-1], config.right_row_ys[-1]) + 60)
        # Giới hạn X chỉ trong khu vực ô bong bóng trả lời (loại trừ khu vực điền số ở bên phải)
        x_end = min(gray.shape[1], max(config.left_xs[-1], config.right_xs[-1]) + 60)
        return gray[y_start:y_end, x_start:x_end], x_start, y_start

    def _detect_circles(self, gray_roi: np.ndarray) -> Optional[list]:
        blur = cv2.GaussianBlur(gray_roi, (7, 7), 1.5)
        circles = cv2.HoughCircles(
            blur,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=18,
            param1=60,
            param2=22,
            minRadius=self.MIN_RADIUS,
            maxRadius=self.MAX_RADIUS,
        )
        if circles is None:
            return None
        return [(int(c[0]), int(c[1]), int(c[2])) for c in circles[0]]

    @staticmethod
    def _cluster_1d(values: list[float], n_clusters: int,
                    tol: int = 15) -> list[int]:
        """Thuật toán gom cụm mean-shift 1 chiều (1-D) đơn giản → trả về các tâm cụm đã được sắp xếp.
        
        Đồng thời đệm/cắt kết quả để đạt chính xác n_clusters bằng phương pháp nội suy tuyến tính
        nếu không tìm đủ số cụm tự nhiên.
        """
        if not values:
            return []
        values_sorted = sorted(values)
        clusters: list[list[float]] = []
        current = [values_sorted[0]]
        for v in values_sorted[1:]:
            if v - current[-1] <= tol:
                current.append(v)
            else:
                clusters.append(current)
                current = [v]
        clusters.append(current)
        # Giữ lại các cụm lớn nhất
        clusters.sort(key=len, reverse=True)
        centers = sorted(int(np.mean(c)) for c in clusters[:n_clusters])
        
        # Nếu có ít hơn số lượng cần thiết, sử dụng nội suy để điền thêm
        if len(centers) == n_clusters:
            return centers
        if len(centers) >= 2 and len(centers) >= n_clusters - 2:
            # Nội suy các mục bị thiếu
            spacing = (centers[-1] - centers[0]) / (n_clusters - 1)
            interpolated = [int(centers[0] + i * spacing) for i in range(n_clusters)]
            return interpolated
        return centers  # trả về bất cứ kết quả nào hiện có, hàm gọi (caller) sẽ kiểm tra tính hợp lệ

    def _cluster_x_columns(
        self, circles: list, config: TemplateConfig
    ) -> tuple[list[int], list[int]]:
        """Tách tâm X của các cột trái/phải (mỗi bên 4 cột).
        
        Khoảng trống giữa cột trái và phải lớn hơn khoảng trống giữa các cột
        lựa chọn riêng lẻ. Chúng ta phân chia tại điểm chính giữa của hai nhóm cột.
        """
        # Sắp xếp tất cả các giá trị X và tìm khoảng trống lớn giữa nhóm trái/phải
        all_cx = sorted([c[0] for c in circles])
        if len(all_cx) < 8:
            return [], []
        
        # Tìm khoảng trống lớn nhất để chia nhóm trái và phải
        diffs = np.diff(all_cx)
        # Làm mịn các khoảng trống
        gap_idx = int(np.argmax(diffs))
        split_x = (all_cx[gap_idx] + all_cx[gap_idx + 1]) / 2
        
        left_cx = [c[0] for c in circles if c[0] < split_x]
        right_cx = [c[0] for c in circles if c[0] >= split_x]

        left_xs = self._cluster_1d(left_cx, config.choices_per_question, tol=20)
        right_xs = self._cluster_1d(right_cx, config.choices_per_question, tol=20)
        return left_xs, right_xs

    def _cluster_y_rows(
        self, circles: list, config: TemplateConfig
    ) -> tuple[list[int], list[int]]:
        """Tách các hàng Y bên trái/phải."""
        # Tìm điểm X phân tách từ file cấu hình (config)
        mid_x = (max(config.left_xs) + min(config.right_xs)) / 2
        left_cy = [c[1] for c in circles if c[0] < mid_x]
        right_cy = [c[1] for c in circles if c[0] >= mid_x]

        n_rows = config.questions_per_column
        left_ys = self._cluster_1d(left_cy, n_rows, tol=20)
        right_ys = self._cluster_1d(right_cy, n_rows, tol=20)
        return left_ys, right_ys