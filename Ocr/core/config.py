"""
Cấu trúc dữ liệu và cấu hình cho engine OMR.

Bao gồm:
    - ANSWER_MAP: Ánh xạ chỉ số lựa chọn (0-3) sang chữ cái (A-D)
    - TemplateConfig: Tọa độ và bố cục cho một mẫu phiếu trả lời OMR
    - BubbleROI: Một vùng quan tâm (ROI - Region of Interest) của một ô bong bóng duy nhất kèm theo đo lường mức độ điền đầy
"""
from __future__ import annotations

from dataclasses import dataclass, field

ANSWER_MAP = {0: "A", 1: "B", 2: "C", 3: "D"}


@dataclass
class TemplateConfig:
    """Các tọa độ mẫu cố định cho phiếu trả lời OMR.

    Các tọa độ được tính bằng pixel trên hình ảnh ĐÃ BIẾN ĐỔI PHỐI CẢNH (WARPED) (warp_width × warp_height).
    Chúng đóng vai trò là ước lượng BAN ĐẦU; và sẽ được tự động tinh chỉnh bởi HoughCircles
    khi có kết quả nhận diện hình tròn tốt.

    Hỗ trợ số lượng câu hỏi tùy ý (20, 50, v.v.) thông qua các trường left_q_start,
    right_q_start, questions_per_column, và total_questions.
    """
    # Kích thước mục tiêu sau khi biến đổi phối cảnh (warp)
    warp_width: int = 1400
    warp_height: int = 2000

    # Vị trí tâm X cho mỗi lựa chọn (A, B, C, D) – cột trái (Q1-25)
    # Đo lường thực tế: (khoảng cách ~102px)
    left_xs: list[int] = field(default_factory=lambda: [275, 377, 479, 581])

    # Vị trí tâm X cho mỗi lựa chọn (A, B, C, D) – cột phải (Q26-50)
    # Đo lường thực tế: (khoảng cách ~102px)
    right_xs: list[int] = field(default_factory=lambda: [920, 1022, 1124, 1226])

    # Vị trí tâm Y cho 25 hàng – CỘT TRÁI (Q1-25)
    # Đo lường từ ảnh 101.jpg: Q1 bắt đầu tại y=767, khoảng cách đều đặn là ~47px.
    left_row_ys: list[int] = field(default_factory=lambda: [
        # Nhóm 1 (Q1-5)
        767, 814, 861, 908, 955,
        # Nhóm 2 (Q6-10)
        1003, 1050, 1097, 1144, 1191,
        # Nhóm 3 (Q11-15)
        1239, 1286, 1337, 1384, 1429,
        # Nhóm 4 (Q16-20)
        1482, 1529, 1576, 1623, 1670,
        # Nhóm 5 (Q21-25)
        1718, 1765, 1812, 1859, 1906,
    ])

    # Vị trí tâm Y cho 25 hàng – CỘT PHẢI (Q26-50)
    # Cột phải Q26 bắt đầu ở chính xác cùng vị trí Y với Q1 
    right_row_ys: list[int] = field(default_factory=lambda: [
        # Nhóm 1 (Q26-30)
        767, 814, 861, 908, 955,
        # Nhóm 2 (Q31-35)
        1003, 1050, 1097, 1144, 1191,
        # Nhóm 3 (Q36-40)
        1239, 1286, 1337, 1384, 1429,
        # Nhóm 4 (Q41-45)
        1482, 1529, 1576, 1623, 1670,
        # Nhóm 5 (Q46-50)
        1718, 1765, 1812, 1859, 1906,
    ])

    # Đường kính ô bong bóng ROI (tính bằng pixel trong ảnh đã biến đổi)
    bubble_diameter: int = 32

    # Bố cục câu hỏi
    total_questions: int = 50
    questions_per_column: int = 25
    choices_per_question: int = 4       # A, B, C, D (có thể mở rộng lên 5)
    left_q_start: int = 1               # số thứ tự câu hỏi đầu tiên ở cột trái
    right_q_start: int = 26             # số thứ tự câu hỏi đầu tiên ở cột phải

    # Công tắc bật/tắt tự động hiệu chuẩn bằng HoughCircles
    enable_hough_calibration: bool = True  


@dataclass(slots=True)
class BubbleROI:
    """Một vùng quan tâm (ROI) của ô bong bóng đơn lẻ."""
    question: int       # 1-50
    choice: int         # 0=A, 1=B, 2=C, 3=D
    cx: int             # tâm X trên ảnh đã biến đổi
    cy: int             # tâm Y trên ảnh đã biến đổi
    radius: int         # bán kính ô bong bóng
    fill_ratio: float = 0.0
    is_filled: bool = False