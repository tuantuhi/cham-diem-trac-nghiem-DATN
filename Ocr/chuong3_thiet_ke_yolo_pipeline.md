# CHƯƠNG 3: THIẾT KẾ VÀ PHÂN TÍCH LUỒNG HOẠT ĐỘNG CHO DẠNG BÀI THI KHOANH TRÒN ĐÁP ÁN TRỰC TIẾP VÀO GIẤY

---

## 3.1. Đặt vấn đề và yêu cầu thiết kế

Trong thực tế giảng dạy tại Việt Nam, không phải bài kiểm tra trắc nghiệm nào cũng được thực hiện trên phiếu trả lời tô bong bóng theo khuôn mẫu chuẩn. Một hình thức phổ biến — đặc biệt ở bậc trung học cơ sở và trung học phổ thông — là học sinh khoanh thẳng chữ cái đáp án (A, B, C, D) vào đề in sẵn. Tờ giấy thi không có vùng định sẵn, không có dấu góc chuẩn, và vị trí của từng câu hỏi cùng đáp án được khoanh hoàn toàn phụ thuộc vào cách trình bày đề bài của giáo viên.

Sự linh hoạt này, dù thuận tiện cho công tác ra đề, lại đặt ra những thách thức đáng kể cho quá trình chấm điểm tự động. Các hệ thống OMR truyền thống hoạt động dựa trên tọa độ ô trả lời cố định được định nghĩa sẵn theo từng mẫu phiếu — phương pháp đó hoàn toàn không khả dụng khi bố cục trang thay đổi theo từng đề in. Hệ thống chấm điểm tự động cho loại hình thi này do vậy cần có khả năng **tự định vị câu hỏi và đáp án** trong bất kỳ ảnh nào, không phụ thuộc vào khuôn mẫu cố định.

Để đáp ứng yêu cầu đó, pipeline được thiết kế theo hướng tiếp cận học sâu thuần túy, với mô hình phát hiện đối tượng YOLOv9 đóng vai trò trung tâm, phối hợp cùng hai mô hình nhận dạng ký tự chuyên biệt. Toàn bộ luồng xử lý gồm sáu giai đoạn tuần tự, được mô tả tổng quan trong Hình 3.1.

---

## 3.2. Tổng quan hệ thống

### 3.2.1. Sơ đồ tổng quan

```
                        ┌─────────────────────────────────────┐
                        │           Đầu vào                   │
                        │  Ảnh bài kiểm tra trắc nghiệm       │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │  Giai đoạn 1: Xử lý ảnh             │
                        │  (Nắn thẳng ảnh bị nghiêng)         │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │  Giai đoạn 2: Phát hiện đối tượng  │
                        │  (Vùng số thứ tự câu hỏi và vùng   │
                        │   đáp án đã được khoanh)            │
                        └──────────────────┬──────────────────┘
                                           │
                                           ▼
                        ┌─────────────────────────────────────┐
                        │  Giai đoạn 3: Nhận diện ký tự      │
                        │  (Ký tự trong nét đã khoanh và      │
                        │   số thứ tự câu hỏi)                │
                        └──────────────────┬──────────────────┘
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          ▼                                ▼                                ▼
┌──────────────────┐          ┌───────────────────────┐         ┌─────────────────┐
│  Giai đoạn 4:    │          │   Giai đoạn 5:        │         │  Giai đoạn 6:   │
│  Ghép cặp        │ ──────►  │   Chấm điểm           │──────►  │  Kết quả điểm  │
│  (Số câu ↔       │          │   (Đối chiếu đáp án   │         │  bài kiểm tra  │
│   đáp án)        │          │    đúng, tổng hợp)    │         │                │
└──────────────────┘          └───────────────────────┘         └─────────────────┘

                               Hình 3.1 – Tổng quan hệ thống dạng khoanh tròn đáp án
```

*Hình 3.1 mô tả tổng quan về hệ thống chấm điểm trắc nghiệm tự động dạng khoanh tròn đáp án. Hệ thống nhận đầu vào là ảnh bài kiểm tra chụp từ thiết bị di động, xử lý qua sáu giai đoạn kế tiếp nhau và xuất ra kết quả điểm bài kiểm tra dưới dạng dữ liệu có cấu trúc.*

Bảng 3.1 tóm tắt vai trò của từng công nghệ cốt lõi trong pipeline:

**Bảng 3.1. Các thành phần kỹ thuật cốt lõi của pipeline**

| Giai đoạn | Công nghệ sử dụng | Nhiệm vụ cụ thể |
|-----------|------------------|-----------------|
| Xử lý ảnh | OpenCV (Canny + HoughLinesP) | Phát hiện và hiệu chỉnh góc nghiêng của tờ giấy |
| Phát hiện đối tượng | YOLOv9 (huấn luyện tùy chỉnh) | Định vị vùng câu hỏi và vùng đáp án đã khoanh |
| Nhận diện số câu hỏi | EasyOCR | Đọc số thứ tự "Câu X" từ vùng ảnh được cắt ra |
| Nhận diện ký tự đáp án | CNN tùy chỉnh (PyTorch) | Phân loại chữ cái A / B / C / D trong vòng khoanh |
| Ghép cặp | Thuật toán so khớp tọa độ | Liên kết đúng đáp án với đúng câu hỏi |
| Chấm điểm & xuất kết quả | Xử lý logic + JSON | Tổng hợp, phát hiện đa dấu, xuất kết quả |

---

## 3.3. Giai đoạn 1 — Xử lý ảnh: Nắn thẳng ảnh bị nghiêng

### 3.3.1. Vấn đề ảnh nghiêng trong thực tế

Khi giáo viên hoặc học sinh chụp tờ bài kiểm tra bằng điện thoại di động, tờ giấy hầu như không bao giờ nằm hoàn toàn thẳng đứng theo phương vuông góc với ống kính. Góc lệch này có thể chỉ vài độ, nhưng đủ khiến các dòng văn bản vốn nằm ngang trên trang giấy trở nên nghiêng trong ảnh số. Nếu không hiệu chỉnh trước, các thuật toán phát hiện đối tượng sẽ hoạt động kém chính xác hơn, và quan trọng hơn, bước ghép cặp câu hỏi với đáp án dựa trên tọa độ dọc sẽ bị lệch theo.

### 3.3.2. Nguyên lý hoạt động của bước nắn thẳng

Hệ thống xác định góc nghiêng của tờ giấy dựa trên một nguyên lý đơn giản: **trên một tờ đề thi, phần lớn các đường nổi bật đều là đường nằm ngang** — dòng văn bản, đường kẻ bảng, đường dưới tiêu đề. Nếu đo được hướng của các đường đó trong ảnh, ta suy ra được tờ giấy đang nghiêng bao nhiêu độ.

Quy trình thực hiện lần lượt qua bốn bước:

**Bước 1 — Trích xuất biên:** Ảnh màu được chuyển sang dạng xám và làm mờ nhẹ để giảm nhiễu nhỏ. Tiếp đó, thuật toán phát hiện biên Canny tìm ra tất cả các đường nét rõ nét trong ảnh — chủ yếu là viền chữ in và đường kẻ.

**Bước 2 — Tìm các đường thẳng dài:** Từ ảnh biên, biến đổi Hough xác suất quét toàn bộ ảnh và trích xuất các đoạn thẳng dài (chỉ giữ lại những đoạn thẳng vượt quá độ dài tối thiểu nhất định, tương ứng với dòng văn bản, loại bỏ nét ngắn không đặc trưng).

**Bước 3 — Xác định góc trung vị:** Mỗi đoạn thẳng cho biết một góc nghiêng. Hệ thống lọc chỉ giữ lại những góc gần với phương nằm ngang (trong khoảng ±15°), rồi tính **góc trung vị** (median) của toàn bộ tập góc thu được. Việc dùng trung vị thay vì trung bình giúp hệ thống không bị ảnh hưởng bởi các đường thẳng bất thường như khung bảng hay đường gạch chân nghiêng.

**Bước 4 — Xoay ảnh:** Ảnh được xoay ngược một góc bằng góc trung vị vừa tính, bằng phép biến đổi affine với phép nội suy chất lượng cao để đảm bảo ảnh sau xoay không bị vỡ chi tiết.

```
   Ảnh gốc (nghiêng ~3°)           Ảnh sau nắn thẳng
   ────────────────────            ──────────────────
    Câu 1. ...............            Câu 1. ............
     Câu 2. ..............            Câu 2. ............
      Câu 3. .............            Câu 3. ............
        (dòng chữ lệch)               (dòng chữ thẳng)

         Hình 3.2 – Minh họa hiệu ứng của bước nắn thẳng ảnh
```

Nếu ảnh đầu vào quá mờ hoặc không tìm thấy đủ đường thẳng rõ ràng, hệ thống trả về ảnh gốc không thay đổi — đảm bảo pipeline không bị gián đoạn trong mọi điều kiện.

---

## 3.4. Giai đoạn 2 — Phát hiện đối tượng bằng YOLOv9

### 3.4.1. Vai trò của giai đoạn phát hiện đối tượng

Sau khi ảnh đã được nắn thẳng, hệ thống cần giải quyết bài toán cốt lõi: **tờ đề thi chứa những đối tượng nào, và chúng nằm ở đâu?** Đây là bước quyết định toàn bộ chất lượng của pipeline, vì nếu phát hiện sai hoặc bỏ sót đối tượng ở đây, các bước sau không thể bù đắp lại.

Hệ thống sử dụng mô hình YOLOv9 được huấn luyện tùy chỉnh trên bộ dữ liệu ảnh đề thi khoanh tròn thực tế thu thập tại Việt Nam. Mô hình học được hai loại đối tượng đặc thù:

- **Vùng số thứ tự câu hỏi** (`ques_id`): Cụm ký tự "Câu X" hoặc "X." xuất hiện ở đầu mỗi câu hỏi trên đề thi.
- **Vùng đáp án đã được khoanh** (`selected_ans`): Chữ cái A, B, C hoặc D nằm bên trong vòng tròn mà học sinh đã khoanh bằng bút.

### 3.4.2. Lý do lựa chọn YOLO cho bài toán này

So với các phương pháp phát hiện đối tượng truyền thống dựa trên đặc trưng thủ công, YOLO mang lại ba lợi thế quan trọng cho bài toán này. Thứ nhất, YOLO xử lý toàn bộ ảnh trong một lần lan truyền thuận duy nhất, đạt tốc độ đủ nhanh cho ứng dụng thực tế. Thứ hai, mô hình học được đặc trưng phong phú từ dữ liệu thực, cho phép nhận diện tốt trên nhiều kiểu phông chữ và cỡ chữ khác nhau mà không cần can thiệp thủ công. Thứ ba, khả năng phát hiện đồng thời nhiều loại đối tượng trong một lần chạy cho phép hệ thống thu thập thông tin về cả câu hỏi lẫn đáp án chỉ bằng một lần suy luận.

### 3.4.3. Kết quả của giai đoạn

Kết quả đầu ra của giai đoạn này là hai tập hợp hộp bao (bounding box) — mỗi hộp bao gồm tọa độ góc trên-trái và góc dưới-phải của vùng đối tượng, kèm theo điểm tin cậy của mô hình. Một tập chứa tất cả vùng câu hỏi phát hiện được, tập còn lại chứa tất cả vùng đáp án đã khoanh. Hai tập này được chuyển sang hai nhánh xử lý song song ở giai đoạn tiếp theo.

**Bảng 3.2. Hai lớp đối tượng mà mô hình YOLO cần nhận diện**

| Lớp đối tượng | Ký hiệu | Mô tả trực quan | Ví dụ |
|--------------|---------|----------------|-------|
| Số thứ tự câu hỏi | `ques_id` | Cụm chữ in ở đầu câu hỏi | "Câu 3", "3.", "3)" |
| Đáp án đã khoanh | `selected_ans` | Chữ cái trong vòng tròn bút | Chữ "B" bên trong hình tròn |

```
  ┌────────────────────────────────────────────────────────────┐
  │  Câu 1. Thủ đô của Việt Nam là?  ⓐ Hà Nội  B  C  D      │
  │  │──────│                              │──────────│         │
  │  ques_id                              selected_ans          │
  │                                                              │
  │  Câu 2. Sông dài nhất Việt Nam?   A  ⓑ Mê Kông  C  D     │
  │  │──────│                             │──────────│          │
  │  ques_id                             selected_ans           │
  └────────────────────────────────────────────────────────────┘

     Hình 3.3 – Minh họa hai loại đối tượng YOLO cần phát hiện
```

---

## 3.5. Giai đoạn 3 — Nhận diện ký tự

Giai đoạn nhận diện ký tự gồm hai tác vụ chạy song song nhau: đọc số thứ tự câu hỏi từ vùng `ques_id`, và phân loại chữ cái đáp án từ vùng `selected_ans`. Hai tác vụ này đặt ra yêu cầu khác biệt nhau nên được giải quyết bằng hai công nghệ riêng biệt.

### 3.5.1. Nhận diện số thứ tự câu hỏi bằng EasyOCR

#### Đặc điểm của bài toán

Vùng số thứ tự câu hỏi chứa văn bản đa dạng về hình thức: đề thi của các giáo viên khác nhau có thể viết "Câu 1", "Câu 1:", "1.", "1)" hay đơn giản chỉ là "1" — và được in bằng nhiều kiểu phông chữ khác nhau. Đây là bài toán nhận diện văn bản tổng quát, đòi hỏi khả năng khái quát hóa cao trên nhiều phong cách văn bản, nên hệ thống lựa chọn EasyOCR — một thư viện OCR đa ngôn ngữ được huấn luyện trên kho dữ liệu văn bản rất phong phú — để thực hiện tác vụ này.

#### Quy trình xử lý

Với mỗi vùng `ques_id` mà YOLO phát hiện, hệ thống cắt ra vùng ảnh tương ứng từ tờ đề thi, sau đó đưa vào EasyOCR để nhận dạng. Từ chuỗi văn bản trả về (ví dụ "Câu 3"), hệ thống lọc ra chỉ phần số nguyên (lấy ra "3"). Kết quả chỉ được chấp nhận khi điểm tin cậy của OCR vượt ngưỡng tối thiểu — nhằm loại bỏ những lần nhận dạng quá mờ, không đáng tin cậy. Song song với việc đọc số, hệ thống cũng tính và lưu lại **tọa độ tâm dọc** (ký hiệu `cy`) của từng hộp bao câu hỏi — giá trị này sẽ đóng vai trò then chốt trong bước ghép cặp ở giai đoạn sau.

Trong trường hợp EasyOCR không đọc được số thứ tự (ảnh mờ, phông chữ quá lạ, hoặc điểm tin cậy quá thấp), hệ thống không dừng lại mà tự động gán số thứ tự tuần tự dựa trên vị trí thứ tự của câu hỏi đó theo chiều từ trên xuống. Cơ chế dự phòng này đảm bảo pipeline không bị gián đoạn ngay cả khi OCR gặp khó khăn.

### 3.5.2. Nhận diện ký tự đáp án bằng mạng CNN tùy chỉnh

#### Lý do không dùng EasyOCR cho đáp án

Bài toán phân loại ký tự đáp án có đặc thù khác hẳn: tập lớp chỉ gồm bốn nhãn cố định (A, B, C, D), và vùng ảnh cần phân tích — phần chữ nằm bên trong vòng khoanh — thường nhỏ và có đặc điểm hình ảnh nhất quán. Trong bối cảnh này, dùng một mô hình OCR đa năng sẽ tốn tài nguyên không cần thiết và thậm chí kém chính xác hơn so với một mạng CNN nhỏ gọn được huấn luyện chuyên biệt cho đúng bốn lớp này.

#### Kiến trúc mạng CNN

Mạng CNN tùy chỉnh (`SimpleOCR_CNN`) được thiết kế tối giản nhưng đủ năng lực cho bài toán phân loại bốn lớp. Mạng gồm hai khối tích chập liên tiếp — mỗi khối thực hiện phép tích chập để trích xuất đặc trưng cục bộ rồi áp dụng gộp cực đại để giảm kích thước — tiếp nối bởi hai lớp kết nối đầy đủ để suy luận phân loại.

**Bảng 3.3. Kiến trúc mạng CNN nhận diện ký tự đáp án**

| Lớp | Loại | Kích thước đầu ra | Chức năng |
|-----|------|------------------|-----------|
| Đầu vào | — | 40 × 40 × 3 | Ảnh RGB đã chuẩn hóa |
| Lớp tích chập 1 | Conv2D + ReLU + MaxPool | 19 × 19 × 16 | Trích xuất đặc trưng cơ bản (cạnh, nét) |
| Lớp tích chập 2 | Conv2D + ReLU + MaxPool | 8 × 8 × 32 | Trích xuất đặc trưng phức tạp hơn (hình dạng) |
| Trải phẳng | Flatten | 2048 | Chuyển đặc trưng không gian thành véc-tơ |
| Lớp kết nối 1 | FC + ReLU | 128 | Tổng hợp đặc trưng |
| Lớp kết nối 2 (đầu ra) | FC | 4 | Logit tương ứng với A, B, C, D |

Mỗi vùng đáp án cắt ra từ ảnh được tiền xử lý theo chuỗi: chuyển sang không gian màu RGB, thay đổi kích thước về 40×40 pixel, rồi chuẩn hóa về miền giá trị chuẩn. Mạng suy luận trên ảnh đã tiền xử lý và chọn nhãn có điểm số cao nhất trong bốn lớp A/B/C/D.

```
 Ảnh vùng đáp án                  Đầu ra CNN
 (cắt từ YOLO)
 ┌──────────┐
 │   ⓑ    │  → [tiền xử lý] → CNN → [logit A: 0.1, B: 3.8, C: 0.2, D: 0.1]
 │  khoanh  │                              ↓
 └──────────┘                        Kết quả: "B"

         Hình 3.4 – Luồng phân loại ký tự đáp án qua CNN
```

---

## 3.6. Giai đoạn 4 — Ghép cặp câu hỏi và đáp án

### 3.6.1. Bài toán ghép cặp và thách thức

Sau khi có hai danh sách riêng biệt — danh sách câu hỏi với số thứ tự đã đọc, và danh sách đáp án với ký tự đã phân loại — hệ thống phải giải quyết bài toán **kết hợp**: vòng khoanh nào là câu trả lời cho câu hỏi nào?

Trên tờ đề thi thực tế, không có quy tắc cố định nào về khoảng cách ngang giữa mã số câu hỏi và vị trí đáp án — đề thi dài hay ngắn, một cột hay hai cột, câu hỏi nhiều hay ít đều ảnh hưởng đến bố cục. Tuy nhiên, có một quy luật bất biến: **đáp án của câu N luôn nằm trên cùng một dòng với câu N, tức là xấp xỉ cùng tọa độ dọc trên trang giấy.** Đây là cơ sở thiết kế của thuật toán ghép cặp.

### 3.6.2. Thuật toán ghép cặp theo vùng tọa độ dọc — Chi tiết từng bước

Thuật toán hoạt động theo nguyên lý **phân vùng phụ trách theo chiều dọc**: mỗi câu hỏi được giao phụ trách một dải không gian theo trục dọc của trang giấy, và bất kỳ vòng khoanh nào có tọa độ tâm dọc nằm trong dải đó sẽ được ghép vào câu hỏi tương ứng. Toàn bộ quy trình gồm bốn bước tuần tự như mô tả dưới đây.

---

#### Bước 4.1 — Tính tọa độ tâm dọc cho toàn bộ đối tượng

Trước khi ghép cặp, hệ thống cần xác định một giá trị đại diện cho vị trí theo chiều dọc của mỗi đối tượng trong ảnh. Giá trị này được gọi là **tọa độ tâm dọc** (ký hiệu `cy`), được tính là trung điểm giữa cạnh trên và cạnh dưới của hộp bao:

```
               y₁ + y₂
          cy = ────────
                  2

  Trong đó: y₁ là tọa độ cạnh trên, y₂ là tọa độ cạnh dưới của hộp bao
```

Mỗi câu hỏi và mỗi đáp án đều được tính một giá trị `cy` riêng. Giá trị `cy` nhỏ nghĩa là đối tượng nằm gần phía trên trang; giá trị `cy` lớn nghĩa là đối tượng nằm gần phía dưới trang. Đây là "chữ ký vị trí" duy nhất của mỗi đối tượng được sử dụng trong toàn bộ bước ghép cặp.

```
  ┌───────────────────────────────────────────────────────┐
  │  Câu 1 ...  [hộp bao: y₁=80,  y₂=104] → cy =  92   │
  │  Câu 2 ...  [hộp bao: y₁=140, y₂=164] → cy = 152   │
  │  Câu 3 ...  [hộp bao: y₁=200, y₂=224] → cy = 212   │
  └───────────────────────────────────────────────────────┘

  Hình 3.5a – Minh họa tính tọa độ tâm dọc cy cho từng câu hỏi
```

---

#### Bước 4.2 — Sắp xếp câu hỏi và đáp án theo chiều từ trên xuống

Sau khi có giá trị `cy` cho tất cả đối tượng, hệ thống sắp xếp riêng hai danh sách — câu hỏi và đáp án — theo thứ tự `cy` tăng dần (từ trên trang xuống dưới trang). Bước sắp xếp này là tiền đề bắt buộc để thuật toán phân vùng ở bước tiếp theo hoạt động đúng logic: câu hỏi có `cy` nhỏ nhất tương ứng với câu nằm cao nhất trên trang giấy.

**Bảng 3.5. Ví dụ hai danh sách sau khi sắp xếp theo cy tăng dần**

| Thứ tự | Câu hỏi | cy | | Thứ tự | Đáp án (ký tự) | cy |
|--------|---------|----|-|--------|----------------|----|
| 1 | Câu 1 | 92  | | 1 | "A" | 94  |
| 2 | Câu 2 | 152 | | 2 | "C" | 155 |
| 3 | Câu 3 | 212 | | 3 | "B" | 210 |
| 4 | Câu 4 | 272 | | 4 | "D" | 270 |
| 5 | Câu 5 | 332 | | 5 | "A" | 335 |

---

#### Bước 4.3 — Xác định vùng phụ trách của từng câu hỏi

Đây là bước cốt lõi của thuật toán. Với mỗi câu hỏi thứ `i` trong danh sách đã sắp xếp, hệ thống xác định một **dải không gian dọc** mà câu hỏi đó "phụ trách" — bất kỳ vòng khoanh nào có `cy` nằm trong dải này đều được gán cho câu hỏi thứ `i`. Ranh giới của dải được xác định như sau:

- **Ranh giới trên** = `cy` của câu hỏi thứ `i` trừ đi một lượng dịch nhỏ (khoảng 30% chiều cao hộp bao). Khoảng dịch này nhằm xử lý trường hợp vòng khoanh và mã số câu hỏi không nằm hoàn toàn ngang hàng mà lệch nhẹ do cách căn lề của đề in.
- **Ranh giới dưới** = Ranh giới trên của câu hỏi `i+1` (câu tiếp theo trong danh sách). Với câu hỏi cuối cùng, ranh giới dưới là vô cực — không có giới hạn phía dưới.

```
  Trục dọc (cy) ↓

  ─── (cy_1 − offset) ─────────── Ranh giới trên câu 1
        Câu 1 (cy = 92)
        │
        │    Vùng phụ trách câu 1
        │    → Vòng khoanh "A" (cy = 94) nằm trong vùng này ✓
        │
  ─── (cy_2 − offset) ─────────── Ranh giới trên câu 2 = Ranh giới dưới câu 1
        Câu 2 (cy = 152)
        │
        │    Vùng phụ trách câu 2
        │    → Vòng khoanh "C" (cy = 155) nằm trong vùng này ✓
        │
  ─── (cy_3 − offset) ─────────── Ranh giới trên câu 3 = Ranh giới dưới câu 2
        Câu 3 (cy = 212)
        │
        │    Vùng phụ trách câu 3
        │    → Vòng khoanh "B" (cy = 210) nằm trong vùng này ✓
        ...

  Hình 3.5b – Phân vùng phụ trách của từng câu hỏi theo trục dọc
```

Thiết kế này mang lại tính **bất biến theo chiều ngang**: dù vòng khoanh nằm gần hay xa mã số câu hỏi theo chiều ngang — ở cột trái, cột giữa hay cột phải của trang giấy — miễn là tọa độ dọc đúng vùng thì vẫn ghép chính xác. Điều này phù hợp hoàn toàn với sự đa dạng bố cục của đề thi thực tế.

---

#### Bước 4.4 — Duyệt, ghép cặp và xử lý câu bị thiếu số thứ tự

Sau khi đã có vùng phụ trách của từng câu hỏi, hệ thống duyệt qua danh sách đáp án và kiểm tra từng vòng khoanh xem nó nằm trong vùng phụ trách của câu hỏi nào. Cụ thể, với mỗi câu hỏi `i`, hệ thống lọc ra tất cả vòng khoanh có `cy` thỏa mãn điều kiện nằm trong khoảng `[ranh giới trên câu i, ranh giới trên câu i+1)` rồi ghép chúng vào câu hỏi đó.

Một ràng buộc quan trọng được áp dụng: mỗi vòng khoanh chỉ được ghép đúng một lần. Ngay sau khi một vòng khoanh được ghép vào một câu hỏi, nó được đánh dấu "đã sử dụng" và không được xét thêm cho bất kỳ câu hỏi nào khác, loại trừ khả năng một đáp án bị tính trùng cho hai câu khác nhau.

**Bảng 3.6. Kết quả ghép cặp trong ví dụ minh họa**

| Số câu | cy câu hỏi | cy vòng khoanh | Nằm trong vùng? | Ký tự | Kết quả |
|--------|-----------|---------------|----------------|-------|---------|
| Câu 1 | 92 | 94  | ✓ Vùng câu 1 | A | Câu 1 → **A** |
| Câu 2 | 152 | 155 | ✓ Vùng câu 2 | C | Câu 2 → **C** |
| Câu 3 | 212 | 210 | ✓ Vùng câu 3 | B | Câu 3 → **B** |
| Câu 4 | 272 | 270 | ✓ Vùng câu 4 | D | Câu 4 → **D** |
| Câu 5 | 332 | 335 | ✓ Vùng câu 5 | A | Câu 5 → **A** |

**Xử lý câu hỏi bị thiếu số thứ tự:** Trong trường hợp EasyOCR ở giai đoạn 3 không đọc được số thứ tự của một câu hỏi nào đó, hệ thống không loại bỏ câu hỏi đó mà tự động gán số thứ tự theo vị trí thứ tự của nó trong danh sách đã sắp xếp theo chiều dọc. Ví dụ, nếu câu hỏi đứng vị trí thứ 3 trong danh sách (từ trên xuống) không đọc được số, nó được tự động gán số thứ tự là 3. Cơ chế dự phòng này đảm bảo không có câu hỏi nào bị bỏ qua chỉ vì lỗi OCR đơn lẻ.

---

### 3.6.3. Sơ đồ tóm tắt luồng ghép cặp

```
  [Danh sách câu hỏi]            [Danh sách đáp án]
  (từ YOLO + EasyOCR)            (từ YOLO + CNN)
          │                              │
          ▼                              ▼
  ┌──────────────────┐          ┌──────────────────┐
  │   Bước 4.1       │          │   Bước 4.1       │
  │   Tính cy cho    │          │   Tính cy cho    │
  │   từng câu hỏi   │          │   từng đáp án    │
  └────────┬─────────┘          └────────┬─────────┘
           │                             │
           ▼                             ▼
  ┌──────────────────┐          ┌──────────────────┐
  │   Bước 4.2       │          │   Bước 4.2       │
  │   Sắp xếp câu    │          │   Sắp xếp đáp    │
  │   hỏi theo cy↑   │          │   án theo cy↑    │
  └────────┬─────────┘          └────────┬─────────┘
           │                             │
           ▼                             │
  ┌──────────────────┐                   │
  │   Bước 4.3       │                   │
  │   Xác định vùng  │                   │
  │   phụ trách của  │                   │
  │   từng câu hỏi   │                   │
  └────────┬─────────┘                   │
           │                             │
           └──────────────┬──────────────┘
                          ▼
                 ┌──────────────────┐
                 │   Bước 4.4       │
                 │   Duyệt & ghép   │
                 │   cặp + đánh dấu │
                 │   đã dùng + xử   │
                 │   lý câu thiếu   │
                 │   số thứ tự      │
                 └────────┬─────────┘
                          ▼
           [Danh sách kết quả ghép cặp]
       { câu 1 → A, câu 2 → C, câu 3 → B, ... }

  Hình 3.6 – Sơ đồ tóm tắt bốn bước của giai đoạn ghép cặp
```

---


## 3.7. Giai đoạn 5 — Chấm điểm và xử lý trường hợp đặc biệt

### 3.7.1. Phát hiện và xử lý đa dấu

Một tình huống thường gặp trong thực tế là học sinh khoanh nhầm rồi khoanh lại đáp án khác, hoặc không biết câu trả lời nên khoanh nhiều ô. Trong những trường hợp này, YOLO có thể phát hiện nhiều hơn một vòng khoanh nằm trong vùng phụ trách của cùng một câu hỏi — dẫn đến kết quả ghép cặp ra nhiều đáp án cho một câu.

Hệ thống phát hiện tình huống này bằng cách đếm số lần mỗi câu hỏi xuất hiện trong danh sách kết quả. Khi một câu có nhiều hơn một đáp án được ghép vào, toàn bộ kết quả của câu đó bị gộp lại thành một bản ghi duy nhất với giá trị đáp án được đặt thành `null` (không xác định), biểu thị rằng câu này bị vi phạm quy tắc đa dấu và cần xem xét riêng.

**Bảng 3.4. Quy tắc xử lý các trường hợp đặc biệt**

| Tình huống | Số đáp án phát hiện được | Kết quả được ghi nhận |
|------------|--------------------------|----------------------|
| Khoanh đúng một đáp án | 1 | Chữ cái đáp án hợp lệ (A/B/C/D) |
| Khoanh hai đáp án trở lên | ≥ 2 | `null` — đa dấu, không hợp lệ |
| Không phát hiện vòng khoanh | 0 | Không có bản ghi cho câu đó |

Quyết định thiết kế ghi `null` thay vì tự chọn đáp án "có vẻ đúng hơn" là có chủ đích: trong chấm thi, quyền xử lý câu đa dấu thuộc về giáo viên hoặc quy chế thi — phần mềm chỉ có trách nhiệm phát hiện và báo cáo trung thực, không phán quyết thay người dùng.

### 3.7.2. Chấm điểm

Sau khi danh sách kết quả cuối cùng đã được làm sạch (loại bỏ và gộp các trường hợp đa dấu), hệ thống thực hiện đối chiếu với đáp án chuẩn. Mỗi câu hỏi được so sánh giữa đáp án học sinh khoanh và đáp án đúng trong bộ đáp án chuẩn do giáo viên nhập vào hệ thống. Câu trả lời đúng được ghi nhận điểm theo thang điểm cài đặt sẵn; câu đa dấu hoặc không có đáp án đều được tính là sai.

---

## 3.8. Giai đoạn 6 — Kết quả và trực quan hóa

### 3.8.1. Định dạng kết quả

Kết quả cuối cùng của pipeline được xuất ra dưới hai hình thức song song: dữ liệu có cấu trúc (JSON) dùng cho hệ thống phần mềm phía sau xử lý tiếp, và ảnh trực quan hóa dùng cho kiểm định thủ công.

Mỗi câu hỏi trong kết quả JSON chứa đầy đủ thông tin: số thứ tự câu hỏi, ký tự đáp án được khoanh (hoặc `null` nếu đa dấu), tọa độ vùng đáp án trong ảnh, và điểm tin cậy của YOLO khi phát hiện vòng khoanh đó.

**Bảng 3.5. Cấu trúc một bản ghi kết quả trong JSON đầu ra**

| Trường dữ liệu | Kiểu | Ý nghĩa |
|---------------|------|---------|
| `question_index` | Số nguyên | Số thứ tự câu hỏi |
| `choice` | Chuỗi ký tự / null | Đáp án được khoanh ('A'–'D'), hoặc null nếu đa dấu |
| `bbox` | Mảng 4 số | Tọa độ hộp bao của vòng khoanh [x₁, y₁, x₂, y₂] |
| `confidence` | Số thực | Mức độ tin cậy của YOLO khi phát hiện vòng khoanh |

Khi hệ thống được gọi qua giao diện API, kết quả được đơn giản hóa thành dạng từ điển phẳng để tiện tích hợp: mỗi số câu là một khóa ánh xạ đến ký tự đáp án tương ứng — ví dụ `{"1": "A", "2": "C", "3": null, "4": "D"}`.

### 3.8.2. Ảnh trực quan hóa

Bên cạnh dữ liệu JSON, pipeline tạo ra một ảnh trực quan hóa bằng cách vẽ các chú thích lên ảnh gốc sau khi đã nắn thẳng. Mỗi vùng câu hỏi được đánh dấu bằng hộp bao màu xanh dương, mỗi vòng khoanh đáp án được đánh dấu bằng hộp bao màu xanh lá, và nhãn "Q3: B" được hiển thị ngay phía trên vòng khoanh để người dùng dễ dàng kiểm tra kết quả ghép cặp.

Ảnh trực quan hóa là công cụ quan trọng trong quá trình kiểm định hệ thống: giáo viên có thể nhìn vào ảnh để xác nhận rằng các vùng phát hiện đúng vị trí, các cặp ghép đúng logic, và kết quả nhận diện ký tự chính xác — từ đó phát hiện kịp thời các trường hợp hệ thống xử lý sai cần can thiệp thủ công.

---

## 3.9. Hỗ trợ xử lý nhiều trang ảnh (Batch Processing)

Trong thực tế, một bài kiểm tra có thể được chụp thành nhiều trang ảnh riêng biệt (khi đề thi dài hơn một trang). Pipeline hỗ trợ xử lý theo lô: toàn bộ ảnh các trang được đưa vào cùng lúc, và hệ thống xử lý chúng một cách liên kết thay vì độc lập.

Chiến lược xử lý theo lô sử dụng khái niệm **offset ảo theo chiều dọc**: mỗi trang ảnh được phát hiện đối tượng và nhận diện ký tự riêng lẻ, nhưng tọa độ dọc của tất cả câu hỏi và đáp án sau đó được cộng thêm một giá trị tích lũy bằng tổng chiều cao các trang trước đó. Nhờ cơ chế này, câu hỏi từ trang 2 và câu hỏi từ trang 1 sẽ có tọa độ dọc hoàn toàn tách biệt nhau trong không gian tọa độ chung, loại trừ khả năng một câu hỏi ở cuối trang 1 bị ghép nhầm với đáp án ở đầu trang 2.

**Bảng 3.6. So sánh chế độ xử lý đơn lẻ và theo lô**

| Tiêu chí | Xử lý đơn lẻ | Xử lý theo lô |
|---------|-------------|--------------|
| Số ảnh đầu vào | 1 | Nhiều ảnh (nhiều trang) |
| Thuật toán ghép cặp | Chạy riêng cho từng ảnh | Chạy một lần trên không gian tọa độ chung |
| Xử lý câu trải 2 trang | Không hỗ trợ | Hỗ trợ qua offset ảo |
| Phù hợp với | Bài thi một trang | Bài thi nhiều trang |

---

## 3.10. Tổng kết chương

Chương này đã trình bày đầy đủ thiết kế và phân tích luồng hoạt động của hệ thống chấm điểm trắc nghiệm dạng khoanh tròn đáp án trực tiếp vào giấy. Pipeline được tổ chức thành sáu giai đoạn kế tiếp nhau: nắn thẳng ảnh nghiêng, phát hiện đối tượng bằng YOLO, nhận diện ký tự bằng EasyOCR và CNN, ghép cặp câu hỏi với đáp án, chấm điểm và xử lý đa dấu, cuối cùng là xuất kết quả.

Điểm đặc sắc của thiết kế là nguyên lý "đặt đúng công nghệ cho đúng bài toán": YOLO đảm nhận việc định vị không gian linh hoạt không phụ thuộc khuôn mẫu, EasyOCR xử lý văn bản đa dạng phông chữ, còn mạng CNN nhỏ gọn phân loại nhanh trong tập lớp hẹp. Ba thành phần phối hợp qua thuật toán ghép cặp theo vùng tọa độ dọc — đơn giản, dễ giải thích, và bền vững trước sự đa dạng của bố cục đề thi thực tế.

Cơ chế xử lý ngoại lệ — dự phòng số thứ tự tuần tự khi OCR thất bại, và ghi nhận `null` cho câu đa dấu — đảm bảo pipeline luôn trả về thông tin đầy đủ để người dùng nhận biết và quyết định xử lý thêm, thay vì lặng lẽ bỏ qua hoặc đưa ra kết quả sai mà không có cảnh báo.

---

## Tài liệu tham khảo (Chương 3)

[1] Wang, C. Y., Yeh, I. H., & Liao, H. Y. M. (2024). *YOLOv9: Learning What You Want to Learn Using Programmable Gradient Information*. arXiv preprint arXiv:2402.13616.

[2] Jocher, G., Chaurasia, A., & Qiu, J. (2023). *Ultralytics YOLO* (Version 8.0.0) [Computer software]. Ultralytics. https://github.com/ultralytics/ultralytics

[3] JaidedAI. (2020). *EasyOCR: Ready-to-use OCR with 80+ Languages*. GitHub Repository. https://github.com/JaidedAI/EasyOCR

[4] Paszke, A., Gross, S., Massa, F., et al. (2019). *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. In *Advances in NeurIPS*, 32.

[5] Canny, J. (1986). *A Computational Approach to Edge Detection*. IEEE Transactions on PAMI, 8(6), 679–698.

[6] Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools.

[7] LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). *Gradient-Based Learning Applied to Document Recognition*. Proceedings of the IEEE, 86(11), 2278–2324.
