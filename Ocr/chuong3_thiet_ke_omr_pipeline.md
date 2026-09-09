# CHƯƠNG 3: THIẾT KẾ VÀ PHÂN TÍCH HỆ THỐNG CHẤM ĐIỂM PHIẾU TRẢ LỜI TÔ ĐEN (OMR)

---

## 3.1. Đặt vấn đề và yêu cầu thiết kế

Trong hệ thống giáo dục Việt Nam, kỳ thi THPT Quốc gia và các bài kiểm tra trắc nghiệm quy mô lớn từ lâu đã sử dụng phiếu trả lời tô bong bóng (bubble sheet) như một công cụ chấm điểm chuẩn hóa. Mỗi học sinh nhận một tờ phiếu trả lời in sẵn, trong đó mỗi câu hỏi có bốn hoặc năm ô hình tròn (bong bóng) tương ứng với các lựa chọn A, B, C, D. Học sinh tô đậm bằng bút chì hoặc bút mực lên ô tương ứng với câu trả lời mình chọn. Sau khi thu bài, tờ phiếu được đưa qua máy chấm OMR chuyên dụng (Optical Mark Recognition) để tự động đọc kết quả.

Tuy nhiên, thực tế triển khai tại các cơ sở giáo dục quy mô nhỏ đến trung bình cho thấy hàng loạt rào cản. Chi phí máy chấm OMR chuyên nghiệp dao động từ 50 đến hơn 200 triệu đồng, vượt xa ngân sách của nhiều trường THCS và THPT ngoài công lập. Bên cạnh đó, phiếu trả lời phải được in trên loại giấy đặc biệt với độ phản xạ quang học theo tiêu chuẩn riêng, không thể thay thế bằng giấy in thông thường. Những ràng buộc về vật chất này buộc nhiều trường phải duy trì phương pháp chấm tay thủ công vốn tốn kém thời gian và dễ xảy ra sai sót.

Xuất phát từ thực trạng đó, hệ thống được đề xuất trong đề tài này hướng đến giải pháp **chấm điểm phiếu tô đen thông qua ảnh chụp từ thiết bị di động**, sử dụng hoàn toàn các thuật toán thị giác máy tính kinh điển trong thư viện OpenCV mà không phụ thuộc vào mô hình học sâu. Cách tiếp cận này giữ cho chi phí triển khai ở mức tối thiểu — thiết bị duy nhất cần có là một chiếc điện thoại thông minh — trong khi vẫn đạt được độ chính xác đủ cao cho yêu cầu thực tế.

Để đáp ứng mục tiêu đó, hệ thống cần giải quyết bốn thách thức kỹ thuật cốt lõi:

1. **Hiệu chỉnh biến dạng hình học:** Ảnh chụp từ điện thoại hầu như luôn bị méo phối cảnh do góc chụp không vuông góc với mặt phiếu. Cần khôi phục tờ phiếu về dạng phẳng chuẩn mực trước mọi bước xử lý tiếp theo.
2. **Đối phó với điều kiện ánh sáng không đồng đều:** Bóng đổ từ tay người chụp, ánh sáng nghiêng từ cửa sổ hay đèn lệch tâm tạo ra gradient độ sáng cục bộ, làm cho các ô bong bóng ở các vùng khác nhau có độ tương phản khác nhau.
3. **Định vị chính xác từng ô bong bóng:** Dù đã hiệu chỉnh phối cảnh, vị trí thực tế của các ô trên ảnh số vẫn có thể lệch so với lưới tọa độ lý thuyết do biến dạng nhỏ khi in hoặc khi quét. Cần cơ chế hiệu chỉnh lưới tự động.
4. **Xác định ngưỡng tô thích nghi:** Mỗi học sinh tô đậm nhạt khác nhau, mỗi loại bút cho ra mức độ phủ mực khác nhau. Ngưỡng phân biệt "đã tô" và "chưa tô" không thể là một hằng số cứng mà phải được học tự động từ dữ liệu của chính tờ phiếu đó.

---

## 3.2. Tổng quan hệ thống

### 3.2.1. Phạm vi và giả định thiết kế

Hệ thống được thiết kế để xử lý hai loại mẫu phiếu trả lời tiêu chuẩn, phù hợp với các kỳ kiểm tra phổ biến trong môi trường giáo dục tại Việt Nam:

**Bảng 3.1. Hai mẫu phiếu trả lời được hỗ trợ**

| Tham số | Mẫu phiếu 20 câu | Mẫu phiếu 50 câu |
|---------|-----------------|-----------------|
| Số câu hỏi | 20 | 50 |
| Số lựa chọn mỗi câu | 4 (A, B, C, D) | 4 (A, B, C, D) |
| Bố cục ô bong bóng | 1 cột | 2 cột (25 câu/cột) |
| Tổng số ô bong bóng | 80 | 200 |
| Điểm đánh dấu góc (Fiducial Marker) | 4 góc | 4 góc |
| Kích thước chuẩn hóa sau xử lý | 700 × 900 px | 700 × 900 px |
| Ứng dụng điển hình | Kiểm tra giữa kỳ | Thi học kỳ, THPT QG |

Các giả định quan trọng của thiết kế là: (1) tờ phiếu được in trên giấy trắng thông thường; (2) ảnh chụp có đủ bốn điểm đánh dấu tham chiếu tại bốn góc; (3) góc chụp lệch không quá 45° so với phương vuông góc; và (4) mỗi câu hỏi học sinh chỉ được tô một đáp án duy nhất hoặc bỏ trống.

### 3.2.2. Sơ đồ tổng quan pipeline

Pipeline OMR truyền thống được thiết kế theo luồng xử lý tuần tự năm giai đoạn kế tiếp nhau. Mỗi giai đoạn nhận đầu vào từ giai đoạn trước và chuyển kết quả sang giai đoạn tiếp theo, như mô tả trong Hình 3.1:

```
  ┌─────────────────────────────────────────────────────┐
  │                     ĐẦU VÀO                         │
  │         Ảnh phiếu trả lời tô đen (JPG/PNG)          │
  │         chụp từ điện thoại di động                  │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │  GIAI ĐOẠN 1: HIỆU CHỈNH PHỐI CẢNH                │
  │  • Phát hiện 4 điểm đánh dấu tham chiếu (Fiducial) │
  │  • Tính ma trận biến đổi phối cảnh (Homography)    │
  │  • Nắn ảnh về kích thước chuẩn                      │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │  GIAI ĐOẠN 2: TIỀN XỬ LÝ ẢNH                      │
  │  • Cân bằng độ tương phản cục bộ (CLAHE)           │
  │  • Làm mờ Gaussian để khử nhiễu                     │
  │  • Nhị phân hóa thích nghi (Adaptive Threshold)    │
  │  • Tinh chỉnh hình thái học (Morphology)            │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │  GIAI ĐOẠN 3: HIỆU CHỈNH LƯỚI TỌA ĐỘ              │
  │  • Xây dựng lưới BubbleROI theo khuôn mẫu lý thuyết│
  │  • Phát hiện vòng tròn bằng HoughCircles            │
  │  • Tinh chỉnh tọa độ tâm từng ô bong bóng           │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │  GIAI ĐOẠN 4: ĐO TỶ LỆ TÔ VÀ XÁC ĐỊNH NGƯỠNG     │
  │  • Tạo mặt nạ tròn cho từng ô bong bóng             │
  │  • Đo fill_ratio = (pixel trắng) / (tổng pixel)     │
  │  • Phân tích histogram phân bố fill_ratio toàn phiếu│
  │  • Xác định ngưỡng phân biệt tự động               │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │  GIAI ĐOẠN 5: TRÍCH XUẤT ĐÁP ÁN VÀ XUẤT KẾT QUẢ  │
  │  • Phân loại từng ô: đã tô / chưa tô                │
  │  • Phát hiện vi phạm đa dấu và bỏ trống            │
  │  • Tổng hợp bản đồ đáp án theo câu hỏi             │
  └──────────────────────┬──────────────────────────────┘
                         │
                         ▼
  ┌─────────────────────────────────────────────────────┐
  │                    ĐẦU RA                            │
  │  Bản đồ đáp án dạng JSON:                          │
  │  {"1": "A", "2": "C", "3": null, "4": "D", ...}    │
  └─────────────────────────────────────────────────────┘

       Hình 3.1 – Tổng quan pipeline OMR năm giai đoạn
```

*Ghi chú: Giá trị `null` trong kết quả JSON biểu thị câu hỏi bị bỏ trống hoặc tô nhiều hơn một đáp án — trường hợp không thể xác định đáp án hợp lệ.*

**Bảng 3.2. Tóm tắt các thành phần kỹ thuật trong pipeline**

| Giai đoạn | Kỹ thuật / Thuật toán | Thư viện | Mục tiêu |
|-----------|----------------------|---------|----------|
| Hiệu chỉnh phối cảnh | Phát hiện contour, Homography, `warpPerspective` | OpenCV | Nắn thẳng méo hình học do góc chụp |
| Tiền xử lý ảnh | CLAHE, Gaussian Blur, Adaptive Threshold, Morphology | OpenCV | Chuẩn hóa chất lượng ảnh, tách ô bong bóng khỏi nền |
| Hiệu chỉnh lưới | HoughCircles, tối ưu hóa tọa độ tâm | OpenCV | Căn chỉnh lưới BubbleROI với vị trí thực tế trên ảnh |
| Đo fill_ratio + Ngưỡng | Mặt nạ tròn, phân tích histogram, `find_peaks` | OpenCV, SciPy | Định lượng mức tô và tự động tìm ngưỡng phân biệt |
| Trích xuất đáp án | So sánh fill_ratio với ngưỡng, kiểm tra ambiguity | Python | Tổng hợp kết quả nhận diện đáp án cuối cùng |

---

## 3.3. Giai đoạn 1 — Hiệu chỉnh phối cảnh

### 3.3.1. Vấn đề biến dạng phối cảnh trong thực tế

Khi giáo viên chụp phiếu trả lời bằng điện thoại di động, trục quang học của camera thường không vuông góc hoàn hảo với mặt phẳng tờ giấy. Sự lệch góc này — dù chỉ vài độ — gây ra hiện tượng biến dạng phối cảnh (Perspective Distortion): tờ giấy hình chữ nhật hoàn hảo bị chụp thành một tứ giác bất kỳ, trong đó các cạnh song song hội tụ về các điểm ảo và các ô bong bóng vốn xếp thành lưới đều bị méo và không đều nhau. Nếu không hiệu chỉnh, lưới tọa độ bong bóng lý thuyết sẽ không khớp với vị trí thực tế của các ô trên ảnh, dẫn đến sai số nhận diện nghiêm trọng.

### 3.3.2. Vai trò của điểm đánh dấu tham chiếu (Fiducial Marker)

Giải pháp cho bài toán hiệu chỉnh phối cảnh là in sẵn bốn **điểm đánh dấu tham chiếu** (Fiducial Marker) tại bốn góc của phiếu trả lời. Đây là các hình vuông nhỏ màu đen, được in với kích thước và vị trí cố định theo thiết kế mẫu phiếu. Vai trò của chúng là đóng vai trò như bốn "điểm neo" — tọa độ thực sự của chúng trong không gian ba chiều đã biết trước, và từ tọa độ của chúng trong ảnh chụp hai chiều, hệ thống có thể tính ngược lại phép biến đổi hình học đã xảy ra.

### 3.3.3. Quy trình phát hiện và hiệu chỉnh

Quá trình hiệu chỉnh phối cảnh thực hiện qua ba bước liên tiếp:

**Bước 1 — Phát hiện điểm tham chiếu:**
Hệ thống trước tiên chuyển ảnh sang dạng xám và áp dụng phân ngưỡng nhị phân để tách các vùng tối (ô đen) ra khỏi nền trắng. Tiếp theo, thuật toán `findContours` của OpenCV xác định tất cả các đường viền khép kín trong ảnh nhị phân. Với mỗi đường viền, hệ thống tính tỷ lệ giữa chiều rộng và chiều cao của hộp bao (aspect ratio). Các điểm tham chiếu là hình vuông nên có tỷ lệ gần bằng 1, và chỉ các vùng có tỷ lệ nằm trong khoảng 0.7 đến 1.3 mới được giữ lại để xem xét tiếp. Bốn vùng đạt điều kiện và có diện tích lớn nhất được xác định là bốn điểm tham chiếu.

**Bước 2 — Tính ma trận biến đổi phối cảnh:**
Sau khi xác định được bốn điểm tham chiếu trong ảnh, hệ thống biết tọa độ thực tế của chúng trong ảnh (tọa độ nguồn) và biết tọa độ lý tưởng mà chúng phải có trong ảnh chuẩn hóa (tọa độ đích — bốn góc của hình chữ nhật 700×900 pixel). Hàm `getPerspectiveTransform` tính toán ma trận homography $\mathbf{H}$ (kích thước 3×3) biểu diễn phép ánh xạ từ không gian ảnh gốc sang không gian ảnh chuẩn hóa.

**Bước 3 — Biến đổi ảnh:**
Ma trận $\mathbf{H}$ được áp dụng lên toàn bộ ảnh bằng hàm `warpPerspective`, tạo ra ảnh đã được nắn thẳng với kích thước chuẩn hóa cố định. Phép nội suy song tuyến tính (bilinear interpolation) được dùng trong quá trình biến đổi để đảm bảo chất lượng ảnh đầu ra tốt nhất.

```
  Ảnh gốc (góc chụp lệch)         Ảnh sau hiệu chỉnh phối cảnh
  ─────────────────────────        ──────────────────────────────
  ╔══════════════════╗              ┌────────────────────┐
  ║ ■             ■ ║              │ ■               ■ │
  ║   [===][===]    ║              │   [===] [===]      │
  ║   [===][===]    ║    ────►     │   [===] [===]      │
  ║   [===][===]    ║              │   [===] [===]      │
  ║ ■             ■ ║              │ ■               ■ │
  ╚══════════════════╝              └────────────────────┘
  (Tứ giác bất kỳ)                (Hình chữ nhật chuẩn 700×900)

         ■ = Điểm đánh dấu tham chiếu (Fiducial Marker)
         [===] = Vùng ô bong bóng

         Hình 3.2 – Hiệu ứng hiệu chỉnh phối cảnh
```

---

## 3.4. Giai đoạn 2 — Tiền xử lý ảnh

### 3.4.1. Tầm quan trọng của tiền xử lý

Sau khi hiệu chỉnh phối cảnh, ảnh đã có đúng hình dạng hình học nhưng vẫn có thể mang những vấn đề chất lượng từ điều kiện chụp thực tế: ánh sáng không đồng đều, nhiễu hạt, độ tương phản thấp tại một số vùng. Bước tiền xử lý có nhiệm vụ **chuẩn hóa chất lượng ảnh** để đưa nó về trạng thái lý tưởng nhất cho bước đo lường fill_ratio ở giai đoạn sau. Bốn kỹ thuật được áp dụng tuần tự:

### 3.4.2. Cân bằng độ tương phản cục bộ bằng CLAHE

Thách thức thực tế lớn nhất trong xử lý ảnh phiếu thi chụp bằng điện thoại là **sự phân bố ánh sáng không đồng đều**. Bóng đổ từ ngón tay cầm điện thoại, cột nhà hay cửa sổ có thể tạo ra chênh lệch độ sáng đáng kể giữa các vùng khác nhau của cùng một tờ giấy. Trong điều kiện đó, một ô bong bóng chưa tô ở vùng tối có thể có độ sáng tương đương một ô đã tô ở vùng sáng — khiến các thuật toán phân ngưỡng toàn cục (tính một ngưỡng chung cho cả ảnh) thất bại hoàn toàn.

CLAHE (Contrast Limited Adaptive Histogram Equalization) giải quyết vấn đề này bằng cách chia ảnh thành một lưới các vùng nhỏ (gọi là tiles) và thực hiện cân bằng histogram riêng cho từng vùng. Kết quả là độ tương phản cục bộ được cải thiện đồng đều ở mọi vùng của ảnh, bất kể điều kiện chiếu sáng ban đầu khác nhau như thế nào. Một cơ chế giới hạn clip (Clip Limit) được áp dụng để ngăn khuếch đại quá mức nhiễu trong các vùng đồng đều. Trong hệ thống này, các tham số được chọn là `clipLimit = 3.0` và `tileGridSize = (16, 16)` — cho mỗi vùng tile có kích thước khoảng 43×56 pixel với ảnh 700×900.

```
  Ảnh trước CLAHE                  Ảnh sau CLAHE
  ─────────────────────────        ──────────────────────────────
  ╔══════════════════╗              ┌────────────────────────────┐
  ║ Vùng tối:       ║              │ Vùng tối đã cải thiện:    │
  ║  ○ ○ ● ○        ║              │  ○ ○ ● ○                  │
  ║ (○ và ● khó     ║  ────►      │ (○ và ● dễ phân biệt)     │
  ║  phân biệt)     ║              │                            │
  ║ Vùng sáng:      ║              │ Vùng sáng giữ nguyên:     │
  ║  ○ ● ○ ○        ║              │  ○ ● ○ ○                  │
  ╚══════════════════╝              └────────────────────────────┘

         ○ = Ô bong bóng chưa tô    ● = Ô bong bóng đã tô

         Hình 3.3 – Tác dụng của CLAHE trong điều kiện ánh sáng không đều
```

### 3.4.3. Làm mờ Gaussian để giảm nhiễu

Sau CLAHE, ảnh được làm mờ nhẹ bằng bộ lọc Gaussian với kernel kích thước 5×5. Mục đích của bước này là loại bỏ nhiễu hạt (grain noise) mịn xuất hiện do cảm biến camera di động — loại nhiễu có thể tạo ra các điểm trắng nhỏ bất thường bên trong vùng đã tô, ảnh hưởng đến độ chính xác khi đo fill_ratio. Phép làm mờ Gaussian có ưu điểm là bảo toàn tốt các biên sắc nét của ô bong bóng trong khi loại bỏ hiệu quả các biến động nhiễu tần số cao.

### 3.4.4. Nhị phân hóa thích nghi (Adaptive Thresholding)

Sau khi làm mờ, ảnh được nhị phân hóa — chuyển từ ảnh mức xám 256 cấp thành ảnh đen-trắng thuần túy. Thay vì dùng một ngưỡng T chung cho toàn bộ ảnh, hệ thống áp dụng **phân ngưỡng thích nghi**: với mỗi pixel, ngưỡng được tính dựa trên thống kê cục bộ của vùng lân cận pixel đó, thường là giá trị trung bình Gaussian của vùng lân cận kích thước `blockSize × blockSize` trừ đi một hằng số C. Cách tiếp cận này đặc biệt hiệu quả khi gradient ánh sáng vẫn tồn tại sau CLAHE. Tham số được dùng: `blockSize = 51` và `C = 8`.

Tham số `blockSize = 51` có ý nghĩa là mỗi pixel được phân ngưỡng dựa trên vùng lân cận 51×51 pixel xung quanh nó. Kích thước này đủ lớn để bao phủ nhiều hơn một ô bong bóng (giúp tham chiếu ngữ cảnh tốt) nhưng đủ nhỏ để phản ánh điều kiện sáng cục bộ.

### 3.4.5. Tinh chỉnh hình thái học (Morphological Operations)

Sau nhị phân hóa, ảnh thường còn chứa những bất hoàn hảo hình học cần được làm sạch:
- **Các đường in mỏng** (đường kẻ ô, đường viền câu hỏi) xuất hiện như những đường trắng mỏng trong nền đen, có thể nhiễu loạn việc phát hiện vòng tròn ở giai đoạn sau.
- **Các lỗ hổng nhỏ** bên trong vùng tô do học sinh tô không liền tay hoặc mực bút không phủ đều.

Hai phép toán hình thái học được áp dụng tuần tự để giải quyết hai vấn đề này:

- **Phép mở (Morphological Opening)** với kernel hình elip 3×3 được áp dụng trước: phép mở = Co → Giãn, có tác dụng loại bỏ các đường in mỏng và nhiễu nhỏ trong khi bảo toàn kích thước tổng thể của các vùng ô lớn.
- **Phép đóng (Morphological Closing)** với kernel hình elip 4×4 được áp dụng sau: phép đóng = Giãn → Co, có tác dụng lấp kín các lỗ hổng nhỏ bên trong vùng đã tô và nối liền các nét bị đứt gãy, làm cho vùng tô trở nên liền khối hơn để đo fill_ratio chính xác hơn.

**Bảng 3.3. Tổng hợp các bước tiền xử lý và tham số sử dụng**

| Bước | Kỹ thuật | Tham số chính | Vấn đề được giải quyết |
|------|---------|--------------|----------------------|
| 1 | Chuyển ảnh xám (Grayscale) | — | Giảm chiều dữ liệu, loại thông tin màu không cần thiết |
| 2 | CLAHE | clipLimit=3.0, tileGridSize=(16,16) | Cân bằng ánh sáng cục bộ không đồng đều |
| 3 | Gaussian Blur | Kernel 5×5 | Làm mịn, loại nhiễu hạt mịn từ cảm biến camera |
| 4 | Adaptive Threshold | blockSize=51, C=8 | Nhị phân hóa thích nghi với gradient ánh sáng |
| 5 | Morphological Opening | Kernel elip 3×3 | Loại đường in mỏng, nhiễu biên nhỏ |
| 6 | Morphological Closing | Kernel elip 4×4 | Lấp lỗ hổng trong vùng tô, nối nét đứt gãy |

---

## 3.5. Giai đoạn 3 — Hiệu chỉnh lưới tọa độ bong bóng

### 3.5.1. Khái niệm BubbleROI và lưới tọa độ lý thuyết

Mỗi ô bong bóng trên phiếu trả lời được biểu diễn trong hệ thống bằng một cấu trúc dữ liệu gọi là **BubbleROI** (Bubble Region of Interest), chứa bốn thông tin: tọa độ tâm `(cx, cy)`, bán kính `r`, số câu hỏi tương ứng, và lựa chọn (A, B, C hoặc D). Tập hợp tất cả BubbleROI tạo thành **lưới tọa độ lý thuyết** — bản đồ vị trí các ô bong bóng như chúng nên xuất hiện trong ảnh chuẩn hóa lý tưởng, được tính toán từ thông số thiết kế của mẫu phiếu (vị trí ô đầu tiên, khoảng cách giữa các ô theo hàng và cột).

Tuy nhiên, do sai số in ấn và các biến dạng nhỏ còn sót lại sau bước hiệu chỉnh phối cảnh, vị trí thực tế của các ô trên ảnh số thường lệch vài pixel so với lưới lý thuyết. Đây không phải là vấn đề lớn với các ô ở giữa phiếu, nhưng với những ô ở các vị trí cực đoan (góc phiếu), độ lệch tích lũy có thể đủ lớn để ảnh hưởng đến phép đo fill_ratio.

### 3.5.2. Hiệu chỉnh lưới bằng HoughCircles

Để tinh chỉnh lưới tọa độ lý thuyết về khớp với thực tế, hệ thống áp dụng thuật toán phát hiện vòng tròn HoughCircles lên ảnh nhị phân sau tiền xử lý. HoughCircles phát hiện tất cả các hình tròn trong ảnh bằng cách tích lũy phiếu bầu trong không gian tham số (tâm x, tâm y, bán kính). Sau khi thu được danh sách vòng tròn phát hiện được, hệ thống thực hiện bài toán **khớp cặp tốt nhất** (best-match assignment): với mỗi BubbleROI trong lưới lý thuyết, hệ thống tìm vòng tròn được HoughCircles phát hiện có khoảng cách tâm gần nhất, miễn là khoảng cách đó không vượt quá một ngưỡng chấp nhận (thường là 15 pixel). Nếu tìm thấy, tọa độ tâm của BubbleROI được cập nhật sang tọa độ thực tế của vòng tròn phát hiện được.

```
  Lưới lý thuyết (●)           Vòng tròn phát hiện (○)        Lưới đã hiệu chỉnh
  ──────────────────────        ──────────────────────          ──────────────────────
  ● ● ● ●                       ○ ○  ○ ○                       ○ ○ ○ ○
  ● ● ● ●     ────────►          ○ ○ ○  ○      ────────►       ○ ○ ○ ○
  ● ● ● ●                         ○ ○ ○ ○                      ○ ○ ○ ○
  (Tọa độ lý tưởng)             (Phát hiện thực tế,            (Tọa độ thực tế
                                  lệch vài pixel)               từ phiếu ảnh)

         Hình 3.4 – Quy trình hiệu chỉnh lưới BubbleROI
```

Đây là bước quan trọng nhưng không phải lúc nào cũng cần thiết: trong điều kiện ảnh chụp tốt và in ấn chuẩn, lưới lý thuyết đã đủ chính xác. HoughCircles đóng vai trò như một "biện pháp bảo hiểm" giúp hệ thống hoạt động ổn định hơn trong điều kiện thực tế đa dạng.

---

## 3.6. Giai đoạn 4 — Đo tỷ lệ tô và xác định ngưỡng thích nghi

### 3.6.1. Đo tỷ lệ tô (Fill Ratio Measurement)

Sau khi có lưới BubbleROI đã hiệu chỉnh, hệ thống thực hiện phép đo định lượng cốt lõi của toàn bộ pipeline: xác định mức độ tô của từng ô bong bóng. Thay vì sử dụng toàn bộ hình vuông bao quanh ô, hệ thống tạo ra một **mặt nạ tròn** (circular mask) với bán kính bằng `0.82 × r` (gọi là inner_radius). Lý do co lại 18% bán kính là để tránh vùng viền ngoài của ô bong bóng — nơi các đường in của ô có thể tạo ra pixel trắng giả và làm sai lệch phép đo.

Trong vùng mặt nạ tròn đã xác định, hệ thống đếm số pixel trắng (giá trị 255 trong ảnh nhị phân) và tính tỷ lệ:

```
                Số pixel trắng trong mặt nạ tròn
  fill_ratio = ─────────────────────────────────────
                    Tổng số pixel trong mặt nạ tròn
```

Giá trị fill_ratio nằm trong khoảng [0, 1]. Một ô bong bóng hoàn toàn trắng (chưa tô) có fill_ratio ≈ 1.0, trong khi một ô được tô đầy bằng bút chì sẽ có fill_ratio nhỏ (≈ 0.1 đến 0.3) vì phần lớn pixel sẽ màu đen sau nhị phân hóa.

*Lưu ý về quy ước: Sau bước Adaptive Thresholding với kiểu `THRESH_BINARY_INV`, nền giấy (trắng) trở thành đen (0) và mực tô (đen) trở thành trắng (255). Do đó fill_ratio cao đồng nghĩa với "đã tô nhiều".*

```
  Mặt nạ tròn trên ảnh nhị phân

  ┌──────────────────────────────┐
  │         (Nền đen)            │
  │    ┌──────────────┐          │
  │    │  Viền ô in   │  Bán kính r
  │    │  ┌────────┐  │          │
  │    │  │████████│  │  Bán kính inner_radius = 0.82r
  │    │  │████████│  │          │
  │    │  │████████│  │          │
  │    │  └────────┘  │          │
  │    │  (Mặt nạ đo) │          │
  │    └──────────────┘          │
  │                              │
  └──────────────────────────────┘

  ██ = Pixel trắng trong mặt nạ (tô bằng bút) → Đóng góp vào fill_ratio
       Viền giữa r và inner_radius bị loại trừ để tránh nhiễu từ đường in

         Hình 3.5 – Cơ chế đo fill_ratio với mặt nạ tròn thu nhỏ
```

### 3.6.2. Thách thức trong việc xác định ngưỡng phân biệt

Sau khi có fill_ratio cho tất cả ô bong bóng (80 giá trị cho mẫu 20 câu, 200 giá trị cho mẫu 50 câu), bước tiếp theo là phân biệt ô nào "đã tô" và ô nào "chưa tô" bằng cách so sánh fill_ratio với một ngưỡng T.

Thách thức là ngưỡng T này **không thể là một hằng số cứng** vì:
- Học sinh tô khác nhau: người tô đậm có fill_ratio ≈ 0.7; người tô nhạt có fill_ratio ≈ 0.3.
- Loại bút ảnh hưởng lớn: bút chì HB tạo ra fill_ratio thấp hơn nhiều so với bút bi đen.
- Chất lượng ảnh thay đổi: ảnh chụp tối hơn hoặc sáng hơn làm thay đổi toàn bộ phân bố fill_ratio.

Nếu đặt ngưỡng T quá cao, những ô tô nhạt bị nhận nhầm là "chưa tô" (bỏ sót đáp án). Nếu đặt T quá thấp, nhiễu nhỏ trong ô chưa tô bị nhận nhầm là "đã tô" (phát hiện đáp án giả).

### 3.6.3. Thuật toán xác định ngưỡng thích nghi dựa trên phân tích histogram

Hệ thống giải quyết bài toán ngưỡng hóa bằng một chiến lược thông minh: **học ngưỡng từ chính dữ liệu của phiếu thi đang xử lý**, dựa trên một quan sát thực tiễn quan trọng:

> Trong một bài thi trắc nghiệm đầy đủ, số lượng ô "chưa tô" luôn nhiều hơn đáng kể số ô "đã tô". Với phiếu 50 câu 4 lựa chọn, tổng có 200 ô bong bóng, nhưng học sinh chỉ tô tối đa 50 ô (mỗi câu 1 ô), để trống 150 ô còn lại. Điều này tạo ra phân bố fill_ratio có **hai đỉnh rõ ràng** trên histogram: đỉnh lớn bên trái tương ứng với nhóm ô "chưa tô" (fill_ratio thấp), và đỉnh nhỏ bên phải tương ứng với nhóm ô "đã tô" (fill_ratio cao).

```
  Phân bố fill_ratio điển hình trên histogram

  Số lượng ô ▲
             │
          80 │  ██
             │  ██
          60 │  ██ ██
             │  ██ ██
          40 │  ██ ██
             │  ██ ██ ██
          20 │  ██ ██ ██         ██ ██
             │  ██ ██ ██ ██ ██  ██ ██ ██
           0 └──────────────────────────────►
             0   0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8  fill_ratio
             │◄── Đỉnh "Chưa tô" ──►│ ◄── Đỉnh "Đã tô" ──►│
                                     ▲
                                Điểm trũng
                              = Ngưỡng tối ưu T

         Hình 3.6 – Phân bố hai đỉnh fill_ratio và ngưỡng phân biệt tối ưu
```

Thuật toán xác định ngưỡng diễn ra theo bốn bước:

**Bước 1 — Vẽ histogram:** Tập hợp toàn bộ fill_ratio được biểu diễn dưới dạng histogram với 50 cột (bins), mỗi cột đếm số ô bong bóng có fill_ratio trong một khoảng giá trị nhất định.

**Bước 2 — Làm mịn histogram:** Histogram thô thường có nhiều gợn không đều do tính chất rời rạc của dữ liệu. Hàm `uniform_filter1d` của SciPy được dùng để làm mịn histogram, tạo ra đường cong phân bố mượt hơn, dễ tìm đỉnh hơn.

**Bước 3 — Phát hiện hai đỉnh:** Hàm `find_peaks` của SciPy quét histogram đã làm mịn và tìm tất cả cực trị cục bộ (đỉnh). Trong hầu hết trường hợp bình thường, sẽ xuất hiện ít nhất hai đỉnh rõ ràng tương ứng với hai nhóm ô.

**Bước 4 — Tìm điểm trũng:** Giữa hai đỉnh tìm được, hệ thống quét để tìm điểm có giá trị histogram nhỏ nhất — đây là điểm trũng (valley), là ngưỡng phân biệt tối ưu theo nguyên lý phân tích phân bố hai đỉnh. Để đảm bảo kết quả không bất thường, ngưỡng tìm được bị giới hạn trong khoảng `[0.12, 0.28]`.

**Cơ chế dự phòng:** Nếu histogram không xuất hiện đủ hai đỉnh rõ ràng (ví dụ ảnh chất lượng quá thấp hoặc học sinh tô quá đồng đều), hệ thống lần lượt thử các chiến lược dự phòng: phân tích khoảng cách lớn nhất giữa các ô fill_ratio (gap analysis), và cuối cùng là giá trị hằng số cứng `T = 0.20` nếu tất cả phương pháp tự động đều thất bại.

**Bảng 3.4. Các chiến lược xác định ngưỡng theo thứ tự ưu tiên**

| Ưu tiên | Phương pháp | Điều kiện áp dụng | Đặc điểm |
|---------|------------|------------------|----------|
| 1 | Phân tích histogram hai đỉnh | Histogram có ≥ 2 đỉnh rõ ràng | Chính xác nhất, thích nghi với từng phiếu |
| 2 | Phân tích khoảng cách lớn nhất (Gap Analysis) | Phân bố fill_ratio có khoảng trống rõ | Ít phụ thuộc hình dạng phân bố |
| 3 | Ngưỡng cứng cố định T = 0.20 | Tất cả phương pháp tự động thất bại | Giá trị kinh nghiệm từ thực nghiệm |

---

## 3.7. Giai đoạn 5 — Trích xuất đáp án và xử lý trường hợp đặc biệt

### 3.7.1. Phân loại ô bong bóng và gom nhóm theo câu hỏi

Sau khi có ngưỡng T, hệ thống phân loại từng ô bong bóng:
- Nếu `fill_ratio ≥ T`: ô được đánh dấu là **"đã tô"**.
- Nếu `fill_ratio < T`: ô được đánh dấu là **"chưa tô"**.

Tiếp theo, hệ thống gom nhóm các ô theo câu hỏi: bốn ô A, B, C, D của câu hỏi số `i` tạo thành một nhóm. Trong mỗi nhóm, hệ thống sắp xếp bốn ô theo fill_ratio giảm dần, xác định ô có fill_ratio lớn nhất là `best` (ứng viên đáp án được chọn) và ô có fill_ratio lớn thứ hai là `second`.

### 3.7.2. Phát hiện và xử lý các trường hợp đặc biệt

Không phải mọi câu hỏi đều có đáp án hợp lệ. Hệ thống nhận diện và xử lý ba tình huống ngoại lệ phổ biến:

**Trường hợp 1 — Câu bỏ trống:** Nếu `best.fill_ratio < T`, tức là ngay cả ô có fill_ratio cao nhất trong nhóm cũng chưa vượt ngưỡng phân biệt "đã tô", điều này có nghĩa là học sinh bỏ trống câu hỏi này. Hệ thống ghi nhận kết quả là `None`.

**Trường hợp 2 — Tô nhiều đáp án (Ambiguity):** Nếu tỷ lệ giữa fill_ratio của ô thứ hai và ô tốt nhất vượt quá 65%, tức là `second.fill_ratio / best.fill_ratio > 0.65`, điều này cho thấy có hai ô được tô với độ đậm tương tự nhau — học sinh có thể đã khoanh nhầm rồi tô lại, hoặc cố tình tô nhiều đáp án. Hệ thống không thể phán quyết đáp án nào là ý định thực sự và ghi nhận kết quả là `None`.

**Trường hợp 3 — Tô mờ cố ý:** Trường hợp đặc biệt hơn: học sinh tô nhạt nhưng hai ô cùng nhạt tương đương nhau (`second > 0.35` và `second/best > 0.50`). Đây là dấu hiệu của việc tô mờ có thể gây hiểu nhầm, và kết quả cũng được ghi nhận là `None`.

**Trường hợp 4 — Câu trả lời hợp lệ:** Nếu không rơi vào bất kỳ trường hợp đặc biệt nào, ô có fill_ratio lớn nhất được xác nhận là đáp án được chọn và ký tự tương ứng (A, B, C hoặc D) được ghi nhận.

**Bảng 3.5. Quy tắc phân loại kết quả từng câu hỏi**

| Tình huống | Điều kiện kiểm tra | Kết quả ghi nhận | Ý nghĩa |
|------------|-------------------|-----------------|---------|
| Đáp án hợp lệ | `best.fill ≥ T` và `second/best ≤ 0.65` | `"A"` / `"B"` / `"C"` / `"D"` | Học sinh tô dứt khoát một đáp án |
| Bỏ trống | `best.fill < T` | `null` | Học sinh không tô ô nào |
| Tô nhiều đáp án | `best.fill ≥ T` và `second/best > 0.65` | `null` | Hai ô hoặc hơn được tô đậm gần nhau |
| Tô mờ không rõ | `second > 0.35` và `second/best > 0.50` | `null` | Hai ô tô mờ, không phân biệt rõ ý định |

### 3.7.3. Luồng quyết định trích xuất đáp án

```
  Với mỗi câu hỏi (nhóm 4 ô A, B, C, D):
  │
  ├─ Sắp xếp 4 ô theo fill_ratio giảm dần
  │         → best (ô tô nhất), second (ô tô nhì)
  │
  ├─ Kiểm tra: best.fill < Ngưỡng T ?
  │   ├─ Có → Kết quả: null (Bỏ trống)     ────────────────────┐
  │   └─ Không → Tiếp tục kiểm tra:                            │
  │                                                             │
  ├─ Kiểm tra: second / best > 0.65 ?                          │
  │   ├─ Có → Kết quả: null (Đa dấu)       ────────────────────┤
  │   └─ Không → Tiếp tục kiểm tra:                            │
  │                                                             │
  ├─ Kiểm tra: second > 0.35 VÀ second/best > 0.50 ?          │
  │   ├─ Có → Kết quả: null (Tô mờ)        ────────────────────┤
  │   └─ Không →                                               │
  │                                                             │
  └─ Kết quả: best.choice (A/B/C/D) ───────────────────────────┘
                                                  │
                                                  ▼
                                        Ghi vào bản đồ kết quả:
                                        {câu_số: đáp_án_hoặc_null}

              Hình 3.7 – Cây quyết định trích xuất đáp án từng câu hỏi
```

---

## 3.8. Định dạng kết quả đầu ra

### 3.8.1. Cấu trúc dữ liệu JSON

Kết quả cuối cùng của pipeline được xuất ra dưới dạng chuỗi JSON phẳng, trong đó mỗi cặp khóa-giá trị tương ứng với một câu hỏi và đáp án được nhận diện:

```json
{
  "1": "A",
  "2": "C",
  "3": null,
  "4": "B",
  "5": "D",
  ...
  "50": "A"
}
```

Dữ liệu JSON này được trả về cho tầng backend (Spring Boot) thông qua REST API của FastAPI. Backend nhận JSON, phân tích cú pháp thành `Map<String, String>` và đối chiếu từng câu hỏi với đáp án chuẩn để tính điểm.

**Bảng 3.6. Cấu trúc đầy đủ dữ liệu phản hồi từ AI Service**

| Trường dữ liệu | Kiểu | Mô tả |
|---------------|------|-------|
| `answers` | Object (JSON) | Bản đồ đáp án: `{"1": "A", "2": null, ...}` |
| `total_questions` | Integer | Tổng số câu hỏi phát hiện được |
| `answered_questions` | Integer | Số câu có đáp án hợp lệ (không null) |
| `null_questions` | Integer | Số câu bỏ trống hoặc đa dấu |
| `execution_time_ms` | Float | Thời gian xử lý toàn pipeline (millisecond) |
| `template_type` | String | Loại mẫu phiếu: `"OMR_20"` hoặc `"OMR_50"` |

### 3.8.2. Ảnh trực quan hóa kết quả

Bên cạnh dữ liệu JSON, pipeline có thể tạo ra một ảnh trực quan hóa bằng cách vẽ các chú thích lên ảnh đã hiệu chỉnh phối cảnh. Với mỗi ô bong bóng, hệ thống vẽ một vòng tròn màu xanh lá (nếu đó là đáp án được chọn) hoặc màu xám mờ (nếu chưa tô). Bên cạnh mỗi câu hỏi, nhãn đáp án được in ra để người dùng có thể kiểm tra trực quan. Ảnh trực quan hóa này được lưu cùng với kết quả JSON và có thể được hiển thị trên giao diện web để giáo viên xác nhận kết quả.

---

## 3.9. Thiết kế xử lý lỗi và trường hợp ngoại lệ

### 3.9.1. Phân loại các tình huống lỗi thường gặp

Trong điều kiện thực tế, ảnh chụp phiếu thi không phải lúc nào cũng đạt chất lượng lý tưởng. Hệ thống được thiết kế để xử lý một cách duyên dáng (graceful degradation) các tình huống lỗi phổ biến thay vì dừng hoàn toàn:

**Bảng 3.7. Phân loại tình huống lỗi và cách xử lý**

| Loại lỗi | Nguyên nhân | Cơ chế xử lý | Tác động đến kết quả |
|----------|------------|--------------|---------------------|
| Không phát hiện đủ 4 điểm tham chiếu | Góc chụp quá lệch, tờ giấy bị gập, ánh sáng đặc biệt | Trả về lỗi HTTP 422 với thông báo rõ ràng | Pipeline không chạy được |
| Ảnh quá mờ hoặc thiếu tương phản | Camera chất lượng thấp, rung tay | CLAHE và Adaptive Threshold vẫn cố gắng xử lý | Độ chính xác giảm nhưng vẫn có kết quả |
| Histogram không xuất hiện 2 đỉnh rõ | Học sinh tô quá ít câu, tô rất đều | Kích hoạt cơ chế dự phòng (Gap Analysis → Ngưỡng cứng) | Một số câu có thể bị nhận sai |
| HoughCircles không phát hiện vòng tròn | Ảnh nhị phân kém chất lượng | Dùng lưới tọa độ lý thuyết thay thế | Độ lệch tọa độ ô, fill_ratio kém chính xác |
| Tô mờ hoặc tô không rõ | Bút chì quá nhạt, tô không lấp đầy ô | Ghi nhận `null` (ambiguity) | Câu bị mất điểm do không nhận được đáp án |

### 3.9.2. Nguyên tắc "không bao giờ trả về kết quả im lặng sai"

Một triết lý thiết kế quan trọng của hệ thống là **luôn báo cáo trạng thái thực tế**, không bao giờ âm thầm bỏ qua một câu hỏi hay tự điền đáp án khi không chắc chắn. Cụ thể:
- Câu bỏ trống → `null`, không tự điền đáp án bất kỳ.
- Câu đa dấu → `null`, không tự chọn "đáp án có vẻ đậm hơn".
- Câu không xác định được → `null`, luôn để giáo viên quyết định.

Điều này đảm bảo rằng kết quả JSON luôn phản ánh trung thực những gì hệ thống nhìn thấy, và giáo viên được trao quyền xử lý tất cả các trường hợp ngoại lệ theo quy chế thi của mình.

---

## 3.10. So sánh với phương pháp chấm điểm thay thế

### 3.10.1. Ưu điểm của tiếp cận truyền thống không học sâu

Việc xây dựng pipeline OMR chỉ bằng OpenCV (không sử dụng học sâu) mang lại một số lợi thế thực tiễn đáng kể:

- **Chi phí tính toán thấp:** Toàn bộ pipeline có thể chạy nhanh ngay cả trên CPU đơn lõi mà không cần GPU — thời gian xử lý một ảnh thường dưới 500ms trên phần cứng phổ thông.
- **Không cần dữ liệu huấn luyện:** Không có mô hình học sâu nào cần được huấn luyện hay thu thập dữ liệu annotation. Hệ thống hoạt động dựa hoàn toàn vào thiết kế thuật toán.
- **Khả năng giải thích cao:** Mỗi quyết định của pipeline đều có thể giải thích và kiểm tra được thông qua ảnh trực quan hóa — không có "hộp đen" học sâu.
- **Dễ tùy chỉnh mẫu phiếu:** Thêm mẫu phiếu mới chỉ cần điều chỉnh các tham số cấu hình (số câu, tọa độ ô đầu, khoảng cách) mà không cần huấn luyện lại bất cứ mô hình nào.

### 3.10.2. Giới hạn và điều kiện hoạt động

Tuy nhiên, tiếp cận này có một số giới hạn cần nhận thức rõ:

**Bảng 3.8. So sánh pipeline OMR truyền thống với giải pháp học sâu**

| Tiêu chí | Pipeline OMR (OpenCV) | Giải pháp học sâu |
|----------|----------------------|-----------------|
| Yêu cầu phần cứng | CPU đơn lõi là đủ | Thường cần GPU để đạt tốc độ tốt |
| Dữ liệu huấn luyện | Không cần | Cần hàng nghìn ảnh annotation |
| Tốc độ xử lý (CPU) | < 500ms / ảnh | Vài giây / ảnh (tùy mô hình) |
| Khả năng xử lý ảnh rất tệ | Hạn chế | Tốt hơn nhờ augmentation |
| Phụ thuộc mẫu phiếu cố định | Có (cần 4 fiducial marker) | Không (có thể phát hiện bất kỳ bố cục) |
| Chi phí triển khai | Rất thấp | Cao hơn (cần tài nguyên tính toán) |
| Khả năng giải thích | Cao | Thấp (hộp đen) |
| Phù hợp với | Phiếu chuẩn, điều kiện ảnh trung bình | Phiếu đa dạng, điều kiện khắc nghiệt |

---

## 3.11. Tổng kết chương

Chương này đã trình bày đầy đủ thiết kế và phân tích hệ thống chấm điểm phiếu trả lời tô đen theo phương pháp OMR truyền thống. Pipeline được tổ chức thành năm giai đoạn xử lý tuần tự: hiệu chỉnh phối cảnh bằng Fiducial Marker và Homography, tiền xử lý ảnh với chuỗi CLAHE → Gaussian Blur → Adaptive Threshold → Morphology, hiệu chỉnh lưới BubbleROI bằng HoughCircles, đo fill_ratio và xác định ngưỡng thích nghi từ histogram phân bố hai đỉnh, cuối cùng là trích xuất đáp án với xử lý đầy đủ các trường hợp đặc biệt.

Điểm nổi bật của thiết kế nằm ở ba nguyên lý cốt lõi. **Nguyên lý thích nghi:** mọi bước xử lý quan trọng — từ cân bằng độ tương phản (CLAHE) đến nhị phân hóa (Adaptive Threshold) đến xác định ngưỡng tô (Histogram Analysis) — đều tự điều chỉnh dựa trên đặc tính của từng ảnh cụ thể, thay vì dùng hằng số cứng. **Nguyên lý chắc chắn:** hệ thống có nhiều lớp cơ chế dự phòng (fallback) đảm bảo luôn trả về kết quả hoàn chỉnh ngay cả khi một bước nào đó gặp khó khăn. **Nguyên lý minh bạch:** mọi trường hợp không chắc chắn được báo cáo trung thực qua giá trị `null`, không bao giờ âm thầm bỏ qua hay tự đưa ra phán quyết.

Sự kết hợp của ba nguyên lý này tạo ra một hệ thống vừa đủ mạnh để hoạt động trong điều kiện thực tế đa dạng, vừa đủ minh bạch để giáo viên tin tưởng sử dụng trong môi trường học đường.

---

## Tài liệu tham khảo (Chương 3)

[1] Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools, 25(11), 120–125.

[2] Gonzalez, R. C., & Woods, R. E. (2018). *Digital Image Processing* (4th ed.). Pearson Education.

[3] Pizer, S. M., Amburn, E. P., Austin, J. D., et al. (1987). *Adaptive Histogram Equalization and Its Variations*. Computer Vision, Graphics, and Image Processing, 39(3), 355–368.

[4] Otsu, N. (1979). *A Threshold Selection Method from Gray-Level Histograms*. IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62–66.

[5] Illingworth, J., & Kittler, J. (1988). *A Survey of the Hough Transform*. Computer Vision, Graphics, and Image Processing, 44(1), 87–116.

[6] Hartley, R., & Zisserman, A. (2003). *Multiple View Geometry in Computer Vision* (2nd ed.). Cambridge University Press.

[7] Serra, J. (1982). *Image Analysis and Mathematical Morphology*. Academic Press.

[8] Virtanen, P., Gommers, R., Oliphant, T. E., et al. (2020). *SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python*. Nature Methods, 17(3), 261–272.

[9] Hussain, M., Bird, J. J., & Ferne, D. R. (2018). *A Study on CNN Transfer Learning for Image Classification*. In *UK Workshop on Computational Intelligence (UKCI)*, pp. 191–202.

[10] Raka, J. M., Pawar, V. R., & Paratkar, P. (2020). *Automated OMR Sheet Checking Using Image Processing*. In *International Conference on Communication and Signal Processing (ICCSP)*, pp. 1235–1239.
