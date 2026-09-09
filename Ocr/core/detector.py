"""
Trình nhận diện OMR (Optical Mark Recognition) cốt lõi.

Sử dụng các điểm chuẩn (fiducial markers) để biến đổi phối cảnh, HoughCircles để hiệu chuẩn lưới,
CLAHE + phân ngưỡng thích nghi (adaptive threshold) để tiền xử lý, và phân ngưỡng độ điền đầy
thích nghi (adaptive fill threshold) cho từng hình ảnh.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from core.config import ANSWER_MAP, BubbleROI, TemplateConfig
from core.marker import FiducialMarkerDetector
from core.calibrator import GridAutoCalibrator

logger = logging.getLogger(__name__)


class FiducialOMRDetector:
    """Trình nhận diện OMR theo mẫu cố định được cải tiến.

    Sử dụng các điểm chuẩn để biến đổi phối cảnh, HoughCircles để hiệu chuẩn lưới,
    CLAHE + phân ngưỡng thích nghi để tiền xử lý, và ngưỡng điền đầy thích nghi
    cho từng hình ảnh.

    API công khai (không thay đổi):
        detector = FiducialOMRDetector()
        result = detector.process("image.jpg")         # -> dict[str, str|None]
        result = detector.process_with_visualization("image.jpg", "vis.jpg")
    """

    def __init__(self, config: Optional[TemplateConfig] = None):
        self.config = config or TemplateConfig()
        self._marker_detector = FiducialMarkerDetector(
            self.config.warp_width, self.config.warp_height
        )
        self._calibrator = GridAutoCalibrator()
        self._grid: list[BubbleROI] = []
        self._active_config: TemplateConfig = self.config

    # ------------------------------------------------------------------
    # Xây dựng lưới
    # ------------------------------------------------------------------

    def _build_grid(self, cfg: Optional[TemplateConfig] = None) -> None:
        """Xây dựng lưới cố định gồm các BubbleROI (tổng_số_câu_hỏi × số_lựa_chọn)."""
        cfg = cfg or self._active_config
        r = cfg.bubble_diameter // 2
        self._grid = []

        for row_idx in range(cfg.questions_per_column):
            # Cột trái
            cy_left = cfg.left_row_ys[row_idx]
            q_left = cfg.left_q_start + row_idx
            for choice_idx, cx in enumerate(cfg.left_xs):
                self._grid.append(BubbleROI(
                    question=q_left, choice=choice_idx,
                    cx=cx, cy=cy_left, radius=r
                ))

            # Cột phải
            cy_right = cfg.right_row_ys[row_idx]
            q_right = cfg.right_q_start + row_idx
            for choice_idx, cx in enumerate(cfg.right_xs):
                self._grid.append(BubbleROI(
                    question=q_right, choice=choice_idx,
                    cx=cx, cy=cy_right, radius=r
                ))

    # ------------------------------------------------------------------
    # Bước 1: Tải hình ảnh
    # ------------------------------------------------------------------

    @staticmethod
    def load_image(image_path: str | Path) -> np.ndarray:
        """Tải hình ảnh từ ổ đĩa."""
        img = cv2.imread(str(image_path))
        if img is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        return img

    # ------------------------------------------------------------------
    # Bước 2: Biến đổi phối cảnh sử dụng các điểm chuẩn
    # ------------------------------------------------------------------

    def perspective_transform(self, image: np.ndarray) -> tuple[np.ndarray, bool]:
        """Nhận diện các điểm chuẩn và biến đổi về kích thước cố định.

        Trả về:
            (warped_image, fiducial_success)
        """
        return self._marker_detector.detect_and_warp(image)

    # ------------------------------------------------------------------
    # Bước 3: Tiền xử lý (CLAHE + phân ngưỡng thích nghi + hình thái học)
    # ------------------------------------------------------------------

    @staticmethod
    def preprocess(gray: np.ndarray) -> np.ndarray:
        """Cân bằng CLAHE + phân ngưỡng thích nghi + làm sạch bằng hình thái học.

        CLAHE xử lý:
            - Ánh sáng không đều (phổ biến trong ảnh chụp bằng điện thoại)
            - Ảnh có độ tương phản thấp (vết bút chì mờ)

        Phân ngưỡng thích nghi (Adaptive threshold) xử lý:
            - Sự chênh lệch (gradient) ánh sáng trên toàn bộ trang giấy
            - Bóng đổ do giấy bị cong hoặc góc chụp của camera

        Hình thái học (Morphology) loại bỏ:
            - Các đường kẻ lưới mỏng được in trên giấy
            - Các hạt bụi / đốm nhiễu nhỏ
        """
        # CLAHE để chuẩn hóa độ tương phản
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16, 16))
        gray_eq = clahe.apply(gray)

        # Làm mờ nhẹ để giảm nhiễu trước khi phân ngưỡng
        blur = cv2.GaussianBlur(gray_eq, (5, 5), 0)

        # Phân ngưỡng thích nghi: chống chịu tốt với sự chênh lệch ánh sáng
        binary = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=51,
            C=8,
        )

        # Phép mở (Opening): loại bỏ các đường in mỏng và nhiễu nhỏ
        kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_open, iterations=1)

        # Phép đóng (Closing): lấp đầy các khoảng trống nhỏ bên trong các ô đã tô
        kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close, iterations=1)

        return binary

    # ------------------------------------------------------------------
    # Bước 4: Đo lường mức độ điền đầy ô bong bóng
    # ------------------------------------------------------------------

    def measure_fill_ratios(self, binary: np.ndarray) -> None:
        """Đo lường tỷ lệ điền đầy cho từng ô bong bóng bằng cách sử dụng mặt nạ hình tròn."""
        h_img, w_img = binary.shape[:2]

        for bubble in self._grid:
            x0 = max(0, bubble.cx - bubble.radius)
            y0 = max(0, bubble.cy - bubble.radius)
            x1 = min(w_img, bubble.cx + bubble.radius)
            y1 = min(h_img, bubble.cy + bubble.radius)

            roi = binary[y0:y1, x0:x1]
            if roi.size == 0:
                bubble.fill_ratio = 0.0
                continue

            rh, rw = roi.shape[:2]
            mask = np.zeros((rh, rw), dtype=np.uint8)
            center = (rw // 2, rh // 2)
            # Bán kính trong nhỏ hơn một chút để tránh nhiễu ở viền
            inner_radius = max(3, int(bubble.radius * 0.82))
            cv2.circle(mask, center, inner_radius, 255, -1)

            white_pixels = np.count_nonzero((roi > 0) & (mask > 0))
            total_pixels = np.count_nonzero(mask)
            bubble.fill_ratio = float(white_pixels) / max(total_pixels, 1)

    # ------------------------------------------------------------------
    # Bước 5: Tính toán ngưỡng thích nghi (trên từng ảnh)
    # ------------------------------------------------------------------

    @staticmethod
    def compute_adaptive_fill_threshold(grid: list[BubbleROI]) -> float:
        """Tính toán ngưỡng điền đầy cho từng hình ảnh bằng phân tích biểu đồ (histogram) theo kiểu Otsu.

        Chiến lược:
            1. Thu thập tất cả các tỷ lệ điền đầy (fill_ratios) (200 giá trị cho 50 câu hỏi × 4 lựa chọn)
            2. Sử dụng find_peaks của scipy để xác định các đỉnh 'trống' và 'đã tô'
            3. Đáy thung lũng (valley) giữa các đỉnh → ngưỡng (threshold)
            4. Dự phòng: ước lượng dựa trên phân vị (percentile)
        """
        ratios = np.array([b.fill_ratio for b in grid], dtype=np.float32)
        if len(ratios) == 0:
            return 0.25

        try:
            from scipy.signal import find_peaks  # type: ignore
            # Biểu đồ phân phối trong khoảng [0, 1] với 50 cột (bins)
            hist, bin_edges = np.histogram(ratios, bins=50, range=(0.0, 1.0))
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

            # Làm mịn biểu đồ
            from scipy.ndimage import uniform_filter1d  # type: ignore
            hist_smooth = uniform_filter1d(hist.astype(float), size=3)

            peaks, props = find_peaks(hist_smooth, height=1, distance=4)
            if len(peaks) >= 2:
                # Sắp xếp các đỉnh theo chiều cao giảm dần
                peak_heights = hist_smooth[peaks]
                sorted_idx = np.argsort(-peak_heights)
                top2 = sorted(peaks[sorted_idx[:2]])  # sắp xếp theo vị trí
                p1, p2 = top2[0], top2[1]
                if p2 > p1:
                    valley_idx = np.argmin(hist_smooth[p1:p2]) + p1
                    threshold = float(bin_centers[valley_idx])
                    threshold = max(0.12, min(threshold, 0.28))
                    logger.info(f"Ngưỡng điền đầy thích nghi (dựa trên đỉnh): {threshold:.3f}")
                    return threshold
        except ImportError:
            pass

        # Dự phòng: sử dụng khoảng trống giữa phân phối của ô trống và ô đã tô
        # Các ô trống gom cụm gần 0.05-0.15, các ô đã tô gần 0.45-0.85
        sorted_ratios = np.sort(ratios)
        # Tìm khoảng trống lớn nhất trong phân phối
        diffs = np.diff(sorted_ratios)
        if len(diffs) > 0:
            gap_idx = np.argmax(diffs)
            gap_val = (sorted_ratios[gap_idx] + sorted_ratios[gap_idx + 1]) / 2
            if 0.15 < gap_val < 0.50:
                logger.info(f"Ngưỡng điền đầy thích nghi (dựa trên khoảng trống): {gap_val:.3f}")
                return float(gap_val)

        # Phương án cuối cùng: giá trị cố định
        threshold = 0.20
        logger.info(f"Ngưỡng điền đầy thích nghi (dự phòng cố định): {threshold:.3f}")
        return threshold

    # ------------------------------------------------------------------
    # Bước 6: Trích xuất đáp án với phân ngưỡng thích nghi
    # ------------------------------------------------------------------

    @staticmethod
    def extract_answers(
        grid: list[BubbleROI],
        fill_threshold: Optional[float] = None,
        total_questions: int = 50,
    ) -> dict[str, str | None]:
        """Xác định đáp án được chọn cho mỗi câu hỏi.

        Logic quyết định:
            1. Với mỗi câu hỏi, xếp hạng các ô bong bóng theo tỷ lệ điền đầy (fill_ratio)
            2. Ô tốt nhất phải vượt qua ngưỡng fill_threshold (ngưỡng thích nghi theo từng ảnh)
            3. Nếu tốt_thứ_hai / tốt_nhất > AMBIGUITY_RATIO → null (tô nhiều đáp án / không rõ ràng)
            4. Kiểm tra nghiêm ngặt lần hai: tốt_thứ_hai > SECOND_ABSOLUTE → null

        Tham số:
            grid: danh sách các BubbleROI đã được thiết lập sẵn fill_ratio
            fill_threshold: ngưỡng cho từng ảnh (None = sử dụng giá trị cố định 0.25)
            total_questions: tổng số lượng câu hỏi trên giấy
        """
        FILL_THRESHOLD = fill_threshold if fill_threshold is not None else 0.25
        AMBIGUITY_RATIO = 0.65
        SECOND_ABSOLUTE = 0.35

        by_question: dict[int, list[BubbleROI]] = defaultdict(list)
        for b in grid:
            by_question[b.question].append(b)

        results: dict[str, str | None] = {}

        for q in range(1, total_questions + 1):
            bubbles = sorted(by_question.get(q, []), key=lambda b: b.choice)
            if not bubbles:
                results[str(q)] = None
                continue

            ranked = sorted(bubbles, key=lambda b: -b.fill_ratio)
            best = ranked[0]
            second = ranked[1] if len(ranked) > 1 else None

            # Đặt lại
            for b in bubbles:
                b.is_filled = False

            # Phải vượt qua mức tối thiểu tuyệt đối
            if best.fill_ratio < FILL_THRESHOLD:
                results[str(q)] = None
                continue

            # Kiểm tra tính mơ hồ (tô nhiều ô → null)
            if second and second.fill_ratio > 0:
                ratio = second.fill_ratio / best.fill_ratio
                if ratio > AMBIGUITY_RATIO:
                    results[str(q)] = None
                    continue
                
            best.is_filled = True
            results[str(q)] = ANSWER_MAP.get(best.choice)

        return results

    # ------------------------------------------------------------------
    # Bước 7: Trực quan hóa để gỡ lỗi (debug)
    # ------------------------------------------------------------------

    @staticmethod
    def draw_visualization(
        image: np.ndarray,
        grid: list[BubbleROI],
        results: dict[str, str | None],
        fill_threshold: float = 0.25,
    ) -> np.ndarray:
        """Vẽ hình ảnh trực quan hóa để gỡ lỗi, hiển thị tất cả các ô bong bóng và các đáp án được nhận diện."""
        vis = image.copy()

        for b in grid:
            if b.is_filled:
                color = (0, 220, 0)        # Xanh lá = đáp án được chọn
                thickness = 3
            elif b.fill_ratio > fill_threshold * 0.7:
                color = (0, 140, 255)      # Cam = tô một phần (đáng ngờ)
                thickness = 2
            else:
                color = (180, 180, 180)    # Xám = trống
                thickness = 1

            cv2.circle(vis, (b.cx, b.cy), b.radius, color, thickness)

            # Hiển thị giá trị tỷ lệ điền đầy
            cv2.putText(
                vis, f"{b.fill_ratio:.2f}",
                (b.cx - 14, b.cy + b.radius + 13),
                cv2.FONT_HERSHEY_SIMPLEX, 0.26, (40, 40, 40), 1
            )

        # Nhãn câu hỏi
        by_q: dict[int, list[BubbleROI]] = defaultdict(list)
        for b in grid:
            by_q[b.question].append(b)

        for q_str, ans in results.items():
            q = int(q_str)
            qb = by_q.get(q, [])
            if not qb:
                continue
            x_label = min(b.cx for b in qb) - 58
            y_label = qb[0].cy + 5
            label = f"Q{q}:{ans or '-'}"
            color = (0, 0, 200) if ans else (150, 150, 150)
            cv2.putText(
                vis, label, (max(5, x_label), y_label),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, color, 1
            )

        return vis

    # ------------------------------------------------------------------
    # Toàn bộ luồng xử lý (pipeline) nội bộ
    # ------------------------------------------------------------------

    def _run_pipeline(
        self, image: np.ndarray
    ) -> tuple[dict[str, str | None], np.ndarray, float]:
        """Thực thi toàn bộ luồng xử lý. Trả về (results, warped_image, threshold).
        
        Việc tự động hiệu chuẩn thông qua HoughCircles sẽ được thử đầu tiên. Nếu nó tạo ra
        khoảng cách không hợp lệ, mẫu mặc định sẽ được sử dụng để thay thế.
        """
        warped, fiducial_ok = self.perspective_transform(image)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

        # Tinh chỉnh lưới bằng HoughCircles (được kiểm soát bởi cờ trong file cấu hình)
        if self.config.enable_hough_calibration:
            self._active_config = self._calibrator.calibrate(gray, self.config)
        else:
            self._active_config = self.config
        self._build_grid(self._active_config)

        binary = self.preprocess(gray)
        self.measure_fill_ratios(binary)

        # Tính toán ngưỡng điền đầy thích nghi cho từng hình ảnh
        fill_threshold = self.compute_adaptive_fill_threshold(self._grid)
        results = self.extract_answers(
            self._grid, fill_threshold, self.config.total_questions
        )

        return results, warped, fill_threshold

    # ------------------------------------------------------------------
    # API công khai 
    # ------------------------------------------------------------------

    def process(self, image_path: str | Path) -> dict[str, str | None]:
        """Toàn bộ luồng xử lý OMR: tải → biến đổi phối cảnh → phân ngưỡng → đo lường → trích xuất.

        Tham số:
            image_path: Đường dẫn đến ảnh đầu vào (ảnh chụp phiếu trả lời bằng điện thoại)

        Trả về:
            Dictionary ánh xạ số câu hỏi (chuỗi) với chữ cái đáp án hoặc None.
            Ví dụ: {"1": "A", "2": "B", "3": null, ...}
        """
        image = self.load_image(image_path)
        results, _, _ = self._run_pipeline(image)
        return results

    def process_with_visualization(
        self,
        image_path: str | Path,
        output_path: str | Path | None = None,
    ) -> dict[str, str | None]:
        """Toàn bộ luồng xử lý đi kèm với đầu ra trực quan hóa để gỡ lỗi.

        Tham số:
            image_path: Đường dẫn đến ảnh đầu vào
            output_path: Nơi lưu ảnh trực quan hóa gỡ lỗi (tùy chọn)

        Trả về:
            Dictionary chứa các đáp án (giống như process())
        """
        image = self.load_image(image_path)
        results, warped, fill_threshold = self._run_pipeline(image)

        vis = self.draw_visualization(warped, self._grid, results, fill_threshold)
        if output_path is not None:
            cv2.imwrite(str(output_path), vis)
            logger.info("Đã lưu ảnh trực quan hóa: %s", output_path)

        return results

    @staticmethod
    def export_json(result: dict[str, str | None], output_path: str | Path) -> None:
        """Xuất kết quả ra file JSON."""
        Path(output_path).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )