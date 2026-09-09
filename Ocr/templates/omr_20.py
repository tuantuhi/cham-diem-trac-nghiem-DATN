"""
Trình nhận diện OMR cho phiếu trả lời trắc nghiệm 20 câu của Việt Nam.

Kế thừa toàn bộ luồng xử lý từ FiducialOMRDetector và chỉ ghi đè
cấu hình mẫu (tọa độ ô bong bóng, số lượng câu hỏi).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.detector import FiducialOMRDetector
from core.config import TemplateConfig


@dataclass
class TemplateConfig20(TemplateConfig):
    """Tọa độ mẫu cho định dạng phiếu OMR 20 câu hỏi.

    Bố cục: 2 cột × 10 hàng = 20 câu hỏi.
        Cột trái:  Q1–Q10   (left_q_start=1)
        Cột phải: Q11–Q20  (right_q_start=11)

    Cả hai cột đều dùng chung vị trí Y (row_ys).
    """
    # Ghi đè các giá trị mặc định cho bố cục 20 câu hỏi (56)
    left_xs: list[int] = field(default_factory=lambda: [415, 471, 527, 583])
    right_xs: list[int] = field(default_factory=lambda: [764, 820, 876, 932])

    # Vị trí Y — giống nhau cho cả hai cột (được hiệu chỉnh thực nghiệm cho các mẫu mới) (62)
    left_row_ys: list[int] = field(
        default_factory=lambda: [1294, 1357, 1419, 1481, 1548, 1614, 1679, 1740, 1807, 1870]
    )
    right_row_ys: list[int] = field(
        default_factory=lambda: [1294, 1357, 1419, 1481, 1548, 1614, 1679, 1740, 1807, 1870]
    )

    bubble_diameter: int = 38           # ban đầu sử dụng radius=15 → diameter=30

    # Bố cục câu hỏi
    total_questions: int = 20
    questions_per_column: int = 10
    choices_per_question: int = 4
    left_q_start: int = 1
    right_q_start: int = 11

    # Kích hoạt HoughCircles cho mẫu 20 câu hỏi 
    enable_hough_calibration: bool = False


class OMR20Detector(FiducialOMRDetector):
    """Trình nhận diện OMR cho phiếu trả lời 20 câu hỏi.

    Kế thừa toàn bộ luồng xử lý từ FiducialOMRDetector:
        - Nhận diện điểm chuẩn + biến đổi phối cảnh
        - Tiền xử lý bằng CLAHE + Phân ngưỡng thích nghi + Hình thái học
        - Đo lường tỷ lệ điền đầy bằng mặt nạ hình tròn (có thu hẹp bán kính bên trong)
        - Trích xuất đáp án dựa trên tỷ lệ mơ hồ (xử lý các vết tẩy xóa)
        - Ngưỡng điền đầy thích nghi cho từng hình ảnh
        - Tự động hiệu chuẩn lưới bằng HoughCircles
        - Trực quan hóa để gỡ lỗi + Xuất file JSON

    Cách sử dụng:
        detector = OMR20Detector()
        result = detector.process("path/to/image.jpg")
    """
    def __init__(self):
        super().__init__(config=TemplateConfig20())