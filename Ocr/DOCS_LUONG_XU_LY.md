# TÀI LIỆU KỸ THUẬT VÀ LUỒNG XỬ LÝ (DEEP DIVE PIPELINE)

Tài liệu này cung cấp cái nhìn chuyên sâu (về mặt kỹ thuật, hàm, biến và thuật toán) của các phương pháp chấm điểm OMR truyền thống và YOLO Khoanh đáp án trong dự án.

---

## 1. PHƯƠNG PHÁP OMR TRUYỀN THỐNG (Mẫu 50 Câu và 20 Câu)

Phương pháp này được thiết kế để quét phiếu tô bong bóng (bubble sheet). Toàn bộ luồng được định nghĩa trong class `FiducialOMRDetector` (nằm ở `core/detector.py`), sử dụng OpenCV thuần túy, không dùng Deep Learning.

### Luồng thực thi chi tiết (Hàm `_run_pipeline`):

1. **Đọc ảnh (`load_image`)**:
   - Dùng `cv2.imread` để nạp ảnh đầu vào.

2. **Nắn chỉnh phối cảnh (`perspective_transform`)**:
   - Gọi `self._marker_detector.detect_and_warp(image)`.
   - Tìm kiếm 4 Marker (Fiducial Marker) thường là ô vuông đen ở 4 góc giấy. Code tìm contour, so khớp tỷ lệ Aspect Ratio để xác định 4 góc.
   - Tính toán ma trận biến đổi phối cảnh (`cv2.getPerspectiveTransform`) và cắt/nắn (`cv2.warpPerspective`) ảnh gốc về kích thước cố định (`warp_width`, `warp_height` được định nghĩa trong `TemplateConfig`).

3. **Tiền xử lý ảnh - Preprocessing (`preprocess`)**:
   - Đưa ảnh về ảnh xám (Grayscale).
   - **CLAHE** (`cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16,16))`): Cân bằng histogram cục bộ. Bước này cực kỳ quan trọng giúp khắc phục việc ánh sáng không đều (chỗ sáng chỗ tối do bóng điện thoại đổ xuống).
   - **Gaussian Blur** `(5, 5)`: Làm mịn nhẹ bề mặt để triệt tiêu nhiễu pixel nhỏ.
   - **Adaptive Threshold** (`cv2.adaptiveThreshold(blockSize=51, C=8)`): Nhị phân hóa ảnh (về 0 và 255). Ngưỡng động giúp phân tách mực chì và nền giấy dựa vào độ tương phản xung quanh thay vì 1 ngưỡng cố định.
   - **Morphology**:
     - `MORPH_OPEN` (kernel `3x3`): Xóa các vạch in mỏng của giấy thi và bụi bẩn.
     - `MORPH_CLOSE` (kernel `4x4`): Lấp đầy các lấm tấm trắng bên trong vùng học sinh đã tô mực.

4. **Xây dựng lưới tọa độ chuẩn (`_build_grid`)**:
   - Dựa trên `TemplateConfig` (vd: `TemplateConfig50`), code sinh ra một danh sách các đối tượng `BubbleROI`.
   - Mỗi `BubbleROI` quản lý: `cx`, `cy` (tọa độ tâm), `radius` (bán kính), `question` (câu số mấy), `choice` (đáp án nào 0,1,2,3 tương đương A,B,C,D).

5. **Đo đạc tỷ lệ tô đen (`measure_fill_ratios`)**:
   - Duyệt qua từng `BubbleROI`. Cắt (crop) vùng roi `[y0:y1, x0:x1]` từ ảnh nhị phân.
   - Tạo một mặt nạ tròn (circular mask). Bán kính mặt nạ được thu nhỏ (`inner_radius = int(radius * 0.82)`) nhằm tránh đo nhầm vào viền tròn mực in của form giấy.
   - Tính `fill_ratio = số_pixel_trắng / tổng_pixel_mặt_nạ`.

6. **Tự động tìm Ngưỡng tô (`compute_adaptive_fill_threshold`)**:
   - Trích xuất toàn bộ `fill_ratio` của hàng trăm bong bóng trên giấy.
   - Khởi tạo 1 Histogram với 50 bins trong dải `[0, 1]`.
   - Làm mượt Histogram bằng `scipy.ndimage.uniform_filter1d`.
   - Dùng thuật toán `scipy.signal.find_peaks` tìm các đỉnh đồ thị. Thông thường sẽ ra 2 đỉnh: Đỉnh trái (các ô trống, dao động 5%-15%), Đỉnh phải (các ô tô chì, dao động 45%-85%).
   - Tìm "điểm trũng" (valley_idx) thấp nhất nằm giữa 2 đỉnh này. Ép giới hạn ngưỡng cắt vào dải an toàn `[0.12, 0.28]`. Fallback mặc định là `0.20` nếu ảnh quá mờ không vẽ được đỉnh.

7. **Trích xuất và chấm kết quả (`extract_answers`)**:
   - Gom nhóm 4 `BubbleROI` theo từng câu hỏi.
   - Sắp xếp 4 ô này theo `fill_ratio` giảm dần (`best` và `second`).
   - `best.fill_ratio < FILL_THRESHOLD` -> Đánh dấu trống (`None`).
   - **Kiểm tra vi phạm đa dấu**:
     - Nếu `(second / best) > 0.65`: Học sinh tô 2 đáp án (độ đậm hệt nhau) -> `None`.
     - Nếu `second > 0.35` (cố tình tô mờ) VÀ `(second / best) > 0.50` -> `None`.
   - Lưu kết quả của `best.choice` vào Output.

---

## 2. PHƯƠNG PHÁP YOLOV8 + CNN (Dạng Khoanh Vòng Trắc Nghiệm)

Dành cho giấy thi không form chuẩn. Luồng thực thi nằm trong class `YOLOPipeline` (file `yolo_pipeline.py`).

### Luồng thực thi chi tiết (`process_image`):

1. **Nắn thẳng ảnh - Deskew (`deskew_image`)**:
   - Dùng Canny Edge Detection tìm các cạnh chữ trên trang.
   - Dùng `cv2.HoughLinesP` dò các đoạn thẳng dài tạo bởi dòng văn bản.
   - Trích xuất các góc (angle) và tính Median Angle. Nếu góc lệch nằm trong dải `[-10, 10]` độ, dùng ma trận xoay `cv2.warpAffine` để nắn ảnh cho thẳng, giúp YOLO và hệ tọa độ chạy chuẩn hơn.

2. **Dò quét bằng YOLOv8 (`_extract_boxes`)**:
   - Đưa ảnh vào model YOLOv8 (`best_v9.pt` đã train custom) thông qua hàm `self.yolo_model(img, conf=0.25)`.
   - Model trả ra các Boxes thuộc 5 nhóm Class: `0: ques`, `1: ans_A`, `2: ans_B`, `3: ans_C`, `4: ans_D`.
   - Áp dụng **Non-Max Suppression** (IoU > 0.5): Tránh việc 1 vùng bị dự đoán sinh ra 2 hộp đè lên nhau, giữ lại hộp có `confidence` cao nhất.
   - Chia kết quả ra làm 2 mảng: `ques_boxes` (chứa chữ "Câu X") và `ans_boxes` (các khoanh mực).

3. **Đọc số thứ tự câu hỏi - CNN OCR (`_read_question_ids`)**:
   - Gửi các `ques_boxes` bị cắt ra (crop) vào mạng CNN custom (`abcd_ocr.pth`).
   - Preprocess cho OCR: Cắt ROI -> chuyển xám -> Nhị phân hóa (Otsu threshold) -> Resize về `(32, 32)` tensor.
   - CNN trả ra `raw_id` (là một chữ số).
   - **Smart Interpolation (Khôi phục ID bị thiếu/sai)**:
     - Duyệt `ques_boxes` theo thứ tự từ trên xuống dưới (trục Y).
     - Hệ thống giữ 1 biến đếm `last_id`.
     - Nếu OCR đọc sai (vd: đọc được 1, 2, xong 8), code sẽ check tính hợp lý: nếu `raw_id` nhảy cóc bất thường so với `last_id`, code sẽ ép nó bằng `last_id + 1` (ví dụ tự điền 3).

4. **Thuật toán ghép cặp Nearest-Neighbor (`_match_and_read_answers`)**:
   - Mục tiêu: Tìm xem 1 vết khoanh tròn là đáp án của câu nào.
   - Duyệt qua từng ô `ans_box`. Tính tọa độ tâm `ad["cx"]`, `ad["cy"]`.
   - Lọc từ tập `ques_boxes` các ứng viên phù hợp theo điều kiện khắc nghiệt:
     1. Câu hỏi nằm bên trái khoanh: `q_cx < ad["cx"] + avg_w * 2`
     2. Câu hỏi nằm ngang hoặc cao hơn: `q_cy < ad["cy"] + avg_h * 0.5`
     3. Giới hạn tầm với dọc (không với xa): `dy = ad["cy"] - q_cy < avg_h * 8`
     4. Giới hạn tầm với ngang: `dx < avg_w * 12`
   - Chọn ứng viên có khoảng cách **Euclidean nhỏ nhất** (`dist = dx*dx + dy*dy`).

5. **Giải quyết Exception 1 Câu Nhiều Đáp Án**:
   - Ở cuối hàm `process_image`, danh sách `ans_results` chứa các đáp án. Code thực hiện `q_counts` để đếm xem 1 `question_index` xuất hiện mấy lần (trường hợp học sinh khoanh cả 2 ô A và B trên cùng 1 hàng ngang -> Thuật toán Matching phía trên cho phép cả 2 nhận chung 1 câu hỏi).
   - Nếu `q_counts[q_idx] > 1`, code sẽ gộp các bản ghi trùng lặp này lại, chỉ lưu 1 bản ghi duy nhất và ép `"choice": None` (tương đương `null` trong JSON) biểu thị cho lỗi đa dấu.

6. **Hoàn tất (Visualization & JSON)**:
   - File JSON/API xuất ra cấu trúc dạng từ điển: `{"1": "A", "2": "C", "3": null}`.
   - Ảnh Visualization (`_draw_visualization`) vẽ các bounding box và text hiển thị (`Q1: B`). Đặc biệt ảnh giữ nguyên minh họa lỗi khoanh nhiều đáp án để kiểm định.
