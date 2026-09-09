"""
Trình nhận diện OMR cho phiếu trả lời trắc nghiệm 50 câu.

Kế thừa toàn bộ luồng xử lý từ FiducialOMRDetector và sử dụng/ghi đè
cấu hình mẫu cho bố cục 50 câu hỏi.
"""
from __future__ import annotations

from dataclasses import dataclass

from core.detector import FiducialOMRDetector
from core.config import TemplateConfig


@dataclass
class TemplateConfig50(TemplateConfig):
    """Tọa độ mẫu cho định dạng phiếu OMR 50 câu hỏi.
    Kế thừa tất cả các tọa độ và cấu hình mặc định (mặc định là 50 câu).
    """
    pass


class OMR50Detector(FiducialOMRDetector):
    """Trình nhận diện OMR cho phiếu trả lời 50 câu hỏi.

    Kế thừa toàn bộ luồng xử lý từ FiducialOMRDetector:
        - Nhận diện điểm chuẩn + biến đổi phối cảnh
        - Tiền xử lý bằng CLAHE + Phân ngưỡng thích nghi + Hình thái học
        - Đo lường tỷ lệ điền đầy bằng mặt nạ hình tròn (có thu hẹp bán kính bên trong)
        - Trích xuất đáp án dựa trên tỷ lệ mơ hồ (xử lý các vết tẩy xóa)
        - Ngưỡng điền đầy thích nghi cho từng hình ảnh
        - Tự động hiệu chuẩn lưới bằng HoughCircles 
        - Trực quan hóa để gỡ lỗi + Xuất file JSON

    Cách sử dụng:
        detector = OMR50Detector()
        result = detector.process("path/to/image.jpg")
    """
    def __init__(self):
        super().__init__(config=TemplateConfig50())