# BÁO CÁO ĐỒ ÁN TỐT NGHIỆP

## HỆ THỐNG CHẤM ĐIỂM TRẮC NGHIỆM TỰ ĐỘNG BẰNG XỬ LÝ ẢNH VÀ HỌC SÂU

---

**Sinh viên thực hiện:** Nguyễn Tuấn Tú

**Ngành:** Điện tử viễn thông

---

## TÓM TẮT ĐỒ ÁN

Đồ án trình bày quá trình nghiên cứu, thiết kế và hiện thực hóa hệ thống chấm điểm trắc nghiệm tự động mang tên **CODEX** (Computerized Optical Detection and EXamination). Hệ thống hướng tới việc giải quyết bài toán chấm thi trắc nghiệm thông qua hai phương pháp song song:

1. **Phương pháp OMR truyền thống (Optical Mark Recognition):** Sử dụng các kỹ thuật xử lý ảnh số (OpenCV) để nhận diện đáp án trên phiếu trả lời mẫu chuẩn (phiếu tô bong bóng 20 và 50 câu). Quy trình xử lý bao gồm: phát hiện điểm đánh dấu tham chiếu (Fiducial Marker), biến đổi phối cảnh (Perspective Transformation), cân bằng sáng cục bộ (CLAHE), phân ngưỡng thích nghi (Adaptive Threshold) và đo lường tỷ lệ tô đen dựa trên ngưỡng động tự thích ứng (Histogram-based Adaptive Fill Threshold).

2. **Phương pháp AI (YOLOv9 + CNN):** Dành cho bài thi dạng khoanh đáp án tự do (không theo phiếu mẫu chuẩn). Quy trình xử lý sử dụng: nắn thẳng ảnh (Deskew), phát hiện đối tượng bằng mô hình YOLOv9, nhận dạng số thứ tự câu hỏi kết hợp thuật toán nội suy thông minh (Smart Interpolation), nhận diện ký tự đáp án A/B/C/D bằng mạng CNN tùy chỉnh, và ghép cặp câu hỏi — đáp án theo thuật toán phân vùng không gian Y (Y-zone Matching).

Hai luồng xử lý được đóng gói thành dịch vụ AI (Python FastAPI), giao tiếp với hệ thống Web chính (Spring Boot + React) thông qua giao diện REST API. Hệ thống Web cung cấp các chức năng quản lý kỳ thi, sinh viên, tải ảnh bài thi, hiển thị bảng đối chiếu đáp án chi tiết và xuất bảng điểm.

Kết quả thực nghiệm cho thấy phương pháp OMR truyền thống đạt độ chính xác trên 95% trên phiếu mẫu chuẩn, trong khi phương pháp YOLOv9 kết hợp CNN đạt khoảng 85–90% trên đề thi dạng khoanh tự do — một kết quả khả quan cho bài toán có tính phức tạp cao.

**Từ khóa:** OMR, Optical Mark Recognition, YOLOv9, CNN, OCR, Xử lý ảnh, Chấm điểm tự động, Học sâu, Spring Boot, React.

---

## GIỚI THIỆU

Trong bối cảnh giáo dục hiện đại, thi trắc nghiệm là phương pháp đánh giá phổ biến nhất tại Việt Nam. Mỗi năm, hàng triệu lượt bài thi trắc nghiệm được thực hiện trên toàn quốc ở các cấp phổ thông và đại học [43]. Việc chấm điểm thủ công tiêu tốn nhiều thời gian, nhân lực và tiềm ẩn nguy cơ sai sót. Các máy chấm trắc nghiệm quang học (OMR scanner) truyền thống, mặc dù đạt độ chính xác cao, nhưng đòi hỏi chi phí đầu tư lớn và yêu cầu phiếu trả lời chuyên dụng. Bên cạnh đó, theo kết quả khảo sát của nhóm tác giả trên 110 học sinh, sinh viên, khoảng 82% người được hỏi cho biết phương pháp khoanh tròn vào ký tự đặt trước câu trả lời đúng trực tiếp trên đề kiểm tra là phương pháp phổ biến trong các bài kiểm tra trên lớp, trong khi tỷ lệ sử dụng phiếu tô chỉ chiếm 56,5%. Điều này cho thấy nhu cầu về một phương pháp chấm trắc nghiệm tự động trên bài kiểm tra dạng khoanh tròn là cần thiết.

Đồ án này đề xuất hệ thống phần mềm CODEX, cho phép sử dụng camera điện thoại thông minh hoặc máy ảnh để chụp bài thi, sau đó áp dụng các thuật toán thị giác máy tính (Computer Vision) kết hợp mô hình học sâu (Deep Learning) để tự động nhận diện và chấm điểm. Hệ thống được thiết kế với hai luồng xử lý song song:

- **Luồng OMR truyền thống:** Tối ưu cho phiếu trả lời mẫu chuẩn có điểm đánh dấu tham chiếu, đảm bảo tốc độ xử lý nhanh và độ chính xác cao.
- **Luồng AI (YOLOv9 + CNN):** Linh hoạt cho mọi dạng đề thi trắc nghiệm khoanh tay, không yêu cầu phiếu mẫu chuẩn.

Toàn bộ hệ thống được triển khai dưới dạng ứng dụng Web hoàn chỉnh, cho phép giáo viên quản lý kỳ thi, sinh viên, tải ảnh bài thi và xem kết quả chấm điểm trực tuyến.

---

# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

## 1.1. Bối cảnh và đặt vấn đề

### 1.1.1. Thực trạng chấm thi trắc nghiệm tại Việt Nam

Trong hệ thống giáo dục Việt Nam, hình thức thi trắc nghiệm (multiple-choice examination) đã trở thành phương pháp kiểm tra đánh giá chủ đạo ở mọi cấp học. Đặc biệt kể từ năm 2017, khi Bộ Giáo dục và Đào tạo chính thức áp dụng hình thức thi trắc nghiệm khách quan cho hầu hết các môn thi trong kỳ thi Trung học phổ thông (THPT) Quốc gia [43], hình thức này đã tạo ra hiệu ứng lan tỏa mạnh mẽ xuống các bài kiểm tra thường xuyên và định kỳ trên lớp. Mỗi năm, hàng triệu lượt bài thi trắc nghiệm được thực hiện trên toàn quốc, phục vụ các mục đích đánh giá đa dạng từ bài kiểm tra 15 phút, giữa kỳ, cuối kỳ ở cấp phổ thông, đến thi kết thúc học phần ở cấp đại học và cao đẳng. 

Theo một khảo sát do nhóm tác giả thực hiện trên 110 học sinh và sinh viên về mức độ phổ biến của bài thi trắc nghiệm, kết quả cho thấy:
- **Cấp Trung học cơ sở (THCS):** Khoảng 60% học sinh cho biết môn Toán và Tiếng Anh được kiểm tra dưới dạng trắc nghiệm chiếm hơn 70% tổng số lần kiểm tra trên lớp.
- **Cấp Trung học phổ thông (THPT):** Tỷ lệ này còn cao hơn đáng kể, với khoảng 79% học sinh cho biết các bài kiểm tra môn Toán và lên đến 88% cho môn Tiếng Anh được thực hiện dưới dạng trắc nghiệm. 

> **[Hình 1.1]** *Cần chèn: Biểu đồ cột thống kê tỷ lệ các môn học kiểm tra dạng trắc nghiệm hơn 70% số lượng bài kiểm tra trên lớp, phân theo cấp THPT và THCS.*

Sự gia tăng về tần suất kiểm tra trắc nghiệm kéo theo sự đa dạng về phương pháp chọn đáp án của học sinh. Hiện nay, có hai phương pháp làm bài phổ biến nhất:
1. **Khoanh tròn vào ký tự đặt trước câu trả lời đúng (A, B, C, D) trực tiếp trên đề thi:** Theo khảo sát của nhóm tác giả, có đến **81,8%** học sinh, sinh viên được hỏi cho biết đây là phương pháp phổ biến nhất trong các bài kiểm tra trên lớp của họ. Phương pháp này mang tính tự nhiên, giúp giáo viên tiết kiệm chi phí in ấn (không cần in phiếu riêng) và học sinh không bị phân tâm khi phải đối chiếu giữa đề và phiếu trả lời.
2. **Tô đen vào phiếu trả lời trắc nghiệm (bubble sheet) riêng biệt:** Khoảng **56,5%** số người được hỏi thường xuyên sử dụng phương pháp này. Đây là hình thức chuẩn hóa bắt buộc trong các kỳ thi lớn (như THPT Quốc gia, thi tuyển sinh) để phục vụ cho các hệ thống máy quét quang học.

> **[Hình 1.2]** *Cần chèn: Biểu đồ cột thống kê các phương pháp chọn đáp án phổ biến trong bài kiểm tra trắc nghiệm (khoanh câu trả lời, tô vào phiếu tô, tích vào ô, điền câu trả lời vào bảng).*

Sự chênh lệch này cho thấy một thực tế: trong khi phương pháp "khoanh tay" chiếm ưu thế tuyệt đối trong các kỳ thi trên lớp, các công nghệ và giải pháp chấm thi tự động hiện nay lại gần như chỉ tập trung hỗ trợ phương pháp "tô phiếu". Điều này tạo ra một khoảng trống công nghệ rất lớn và là một sự lãng phí tài nguyên của giáo viên khi phải chấm hàng ngàn bài thi khoanh tay một cách thủ công mỗi năm.

### 1.1.2. Các phương pháp chấm trắc nghiệm hiện tại

Hiện nay, quá trình chấm điểm bài thi trắc nghiệm tại Việt Nam chủ yếu dựa vào ba phương pháp chính, mỗi phương pháp đều có những đặc điểm và hạn chế riêng:

**a) Chấm thủ công bằng tay (Manual Grading)**
Giáo viên sử dụng một tờ phiếu đáp án đã được đục lỗ (hoặc đánh dấu) tương ứng với các đáp án đúng, sau đó đặt chồng lên bài làm của học sinh để đối chiếu. 
- *Ưu điểm:* Đơn giản, không yêu cầu bất kỳ thiết bị công nghệ hay phần mềm nào, giáo viên có thể thực hiện mọi lúc mọi nơi.
- *Nhược điểm:* Cực kỳ tốn thời gian (trung bình 2-3 phút cho một bài thi 50 câu). Đối với một giáo viên phụ trách 3-5 lớp, mỗi lớp 45 học sinh, việc chấm một đợt kiểm tra có thể kéo dài hàng chục giờ đồng hồ. Ngoài ra, phương pháp này có tỷ lệ sai sót cao (2-5%) do sự mệt mỏi về thị giác và thiếu tập trung khi phải xử lý số lượng bài lớn.

**b) Máy chấm trắc nghiệm quang học (OMR Scanner chuyên dụng)**
Các hệ thống như Scantron, Sekonic hoặc máy quét OMR trong nước sử dụng phần cứng đọc quang học chuyên dụng. Hệ thống sẽ phát xạ ánh sáng lên mặt giấy và sử dụng cảm biến phản xạ để phát hiện các vùng hấp thụ ánh sáng (vùng tô chì đen) [44].
- *Ưu điểm:* Tốc độ xử lý siêu tốc (hàng trăm bài mỗi phút), độ chính xác gần như tuyệt đối (99,9%).
- *Nhược điểm:* Chi phí đầu tư ban đầu rất lớn (từ hàng chục đến hàng trăm triệu đồng). Yêu cầu bắt buộc phải sử dụng các loại phiếu trả lời trắc nghiệm chuẩn được in trên giấy đặc biệt với kích thước và khoảng cách chính xác. Không thể sử dụng để chấm đề thi dạng khoanh tay thông thường. 

**c) Ứng dụng chấm thi trên thiết bị di động**
Sự bùng nổ của điện thoại thông minh đã thúc đẩy sự ra đời của các ứng dụng chấm thi dựa trên camera như ZipGrade, GradeCam (quốc tế) hoặc Azota, TNMaker (Việt Nam) [45][46]. Các ứng dụng này sử dụng công nghệ xử lý ảnh (Computer Vision) để nhận diện vùng tô đen trên ảnh chụp.
- *Ưu điểm:* Tiện lợi, chi phí rẻ, giáo viên có thể chấm bài mọi lúc mọi nơi chỉ với một chiếc điện thoại di động.
- *Nhược điểm:* Mặc dù đã giảm chi phí thiết bị, **tất cả** các ứng dụng này vẫn bắt buộc người dùng phải in phiếu trả lời trắc nghiệm theo mẫu độc quyền của từng ứng dụng. Quan trọng nhất, **chưa có ứng dụng nào trên thị trường Việt Nam hỗ trợ chấm điểm cho các bài kiểm tra dạng khoanh tròn trực tiếp trên đề thi.**

### 1.1.3. Tổng quan các nghiên cứu liên quan

Lĩnh vực chấm thi tự động bằng Xử lý ảnh (OMR - Optical Mark Recognition) đã thu hút nhiều sự quan tâm của giới nghiên cứu học thuật trên thế giới:
- **Năm 1999**, Chinnasarn và Rangsanseri [60] đã đặt nền móng bằng việc phát triển hệ thống chấm điểm dựa trên máy tính cá nhân (PC) đầu tiên có thể xử lý hình ảnh từ máy quét văn phòng thông thường, thay vì máy quét quang học chuyên dụng đắt tiền.
- **Năm 2010–2011**, Čupić và cộng sự [62][63] công bố một hệ thống chấm tự động mã nguồn mở viết bằng ngôn ngữ Java. Hệ thống này sử dụng các kỹ thuật xử lý ảnh cơ bản để nhận diện cả phiếu đáp án cổ điển và phiếu tích hợp thông tin cá nhân.
- **Năm 2011**, Nguyen và cộng sự [61] đã có bước tiến lớn khi đề xuất sử dụng máy ảnh/webcam để thay thế hoàn toàn máy quét văn bản. Nghiên cứu này phải xử lý thêm các biến dạng hình học (geometric distortions) do góc độ máy ảnh gây ra.
- **Năm 2013**, Sattayakawee [65] đề xuất phương pháp OMR cải tiến, trong đó học sinh có thể đánh dấu "tích" (check-mark) vào ô vuông thay vì phải tô đen toàn bộ vòng tròn, đạt độ chính xác trung bình 99,9%.
- **Năm 2021**, Ascencio và cộng sự [66] giới thiệu một giải pháp hoàn chỉnh, chi phí thấp sử dụng ngôn ngữ Python kết hợp thư viện OpenCV để xây dựng hệ thống xử lý hình ảnh OMR tự động.

Nhìn chung, các nghiên cứu từ trước đến nay đều xoay quanh việc tối ưu hóa thuật toán nhận diện mật độ pixel cho **bài toán OMR truyền thống** (yêu cầu phiếu trả lời in sẵn theo khuôn mẫu). Tính đến thời điểm hiện tại, số lượng các nghiên cứu đề cập đến việc áp dụng Trí tuệ nhân tạo (Học sâu - Deep Learning) để giải quyết **bài toán chấm đề thi khoanh tự do** vẫn còn rất hạn chế. Đây là bài toán mang tính thực tiễn rất cao tại Việt Nam nhưng lại đòi hỏi năng lực nhận dạng đối tượng (Object Detection) và nhận dạng văn bản cảnh (Scene Text Recognition) vô cùng phức tạp. Đồ án này được thực hiện nhằm mục đích lấp đầy khoảng trống nghiên cứu đó.

## 1.2. Khảo sát thực trạng chấm điểm trắc nghiệm tại Việt Nam

### 1.2.1. Hạn chế hiện tại

Thông qua quá trình khảo sát giáo viên tại các trường phổ thông và đánh giá các sản phẩm thương mại hiện hành, nhóm nghiên cứu đã tổng hợp 6 hạn chế mang tính hệ thống yếu kém trong công tác kiểm tra, đánh giá hiện nay:

| STT | Hạn chế | Phân tích nguyên nhân và Hậu quả |
|:---:|:---|:---|
| 1 | **Chi phí đầu tư và vận hành cao** | Mặc dù máy quét chuyên dụng OMR đã rẻ hơn trước, nhưng việc duy trì in ấn hàng chục ngàn phiếu trả lời tiêu chuẩn mỗi năm vẫn tạo ra gánh nặng tài chính lớn, đặc biệt đối với các trường học ở khu vực nông thôn và vùng sâu vùng xa. |
| 2 | **Thiếu linh hoạt trong định dạng đề thi** | Mọi giải pháp phần cứng và phần mềm hiện hành chỉ tương thích duy nhất với phiếu "Bubble Sheet". Hình thức "khoanh tay trực tiếp" — vốn chiếm tới 81,8% số bài kiểm tra trên lớp — lại hoàn toàn bị bỏ ngỏ, buộc giáo viên phải chấm tay. |
| 3 | **Phụ thuộc vào phần cứng chuyên biệt** | Việc vận hành máy chấm quang học thường được giao cho một nhân sự chuyên trách tại phòng máy của trường. Giáo viên không thể tự chủ động chấm bài ngay tại lớp học hay tại nhà. |
| 4 | **Sai số hệ thống do con người** | Việc chấm thủ công bài khoanh tay gây ra tỷ lệ sai sót hệ thống xấp xỉ 2-5%. Nếu không phát hiện, điều này ảnh hưởng trực tiếp đến quyền lợi và điểm số của người học. |
| 5 | **Sự phân mảnh dữ liệu (Data Fragmentation)** | Các ứng dụng di động hiện tại chỉ trả về điểm số thô. Dữ liệu này không được số hóa toàn diện và khó có thể đồng bộ trực tiếp lên hệ thống quản lý đào tạo (LMS) của nhà trường. |
| 6 | **Rào cản ngôn ngữ và bản địa hóa** | Nhiều phần mềm ngoại nhập uy tín có giao diện tiếng Anh và thiết kế mẫu phiếu trả lời theo chuẩn phương Tây (sử dụng True/False hoặc số thay vì A,B,C,D), gây cản trở cho giáo viên Việt Nam tiếp cận. |

### 1.2.2. Hướng khắc phục đề xuất

Dựa trên việc xác định chính xác các điểm nghẽn, đồ án đề xuất các giải pháp kỹ thuật cụ thể nhằm khắc phục triệt để các hạn chế trên:

| STT | Hạn chế tương ứng | Hướng giải quyết đề xuất | Cơ sở công nghệ áp dụng |
|:---:|:---|:---|:---|
| 1 | Chi phí in ấn phiếu | **Loại bỏ sự phụ thuộc vào phiếu chuẩn.** Hỗ trợ chấm tự động ngay trên tờ đề thi in giấy A4 thông thường. | Mạng nơ-ron tích chập (CNN) và mô hình nhận diện đối tượng YOLOv9. |
| 2 | Thiếu linh hoạt | **Phát triển hệ thống xử lý luồng kép (Dual-pipeline).** Hệ thống tự động nhận dạng: nếu là phiếu chuẩn sẽ dùng luồng OMR cực nhanh, nếu là đề khoanh tay sẽ kích hoạt luồng AI học sâu. | Tích hợp thuật toán xử lý ảnh số học (OpenCV) và Trí tuệ nhân tạo (PyTorch). |
| 3 | Phụ thuộc phần cứng | **Chuyển đổi số toàn diện (Digital Transformation).** Chỉ cần sử dụng camera điện thoại phổ thông để thu nhận ảnh, toàn bộ quá trình tính toán nặng nề được đẩy lên Server máy chủ. | Kiến trúc hướng dịch vụ (Microservices), triển khai trên nền tảng Web. |
| 4 | Sai số con người | **Tự động hóa 100%.** Hệ thống không chỉ xuất điểm mà còn kết xuất hình ảnh đánh dấu màu xanh (đúng) và màu đỏ (sai) trực quan, giúp giáo viên dễ dàng kiểm chứng lại kết quả của AI. | Giao diện đồ họa người dùng tương tác thời gian thực (ReactJS). |
| 5 | Phân mảnh dữ liệu | **Xây dựng hệ sinh thái khép kín.** Cung cấp tài khoản phân quyền Admin/Teacher/Student. Điểm số được lưu trữ vào Cơ sở dữ liệu và có thể kết xuất ra Excel (CSV/XLSX) chuẩn hóa. | Nền tảng Spring Boot Backend, Hệ quản trị CSDL PostgreSQL. |

## 1.3. Mục tiêu đề tài

### 1.3.1. Mục tiêu tổng quát

Mục tiêu tối thượng của đồ án là thiết kế, xây dựng và triển khai thành công một hệ thống phần mềm chấm điểm trắc nghiệm tự động mang tính đột phá, tích hợp linh hoạt kỹ thuật Xử lý ảnh số truyền thống và Trí tuệ nhân tạo hiện đại. Hệ thống phải hoạt động ổn định trên nền tảng ứng dụng Web, cho phép giáo viên ở bất cứ đâu có kết nối Internet đều có thể chụp ảnh bài thi từ camera thiết bị di động, tải lên hệ thống và nhận lại kết quả chấm điểm số hóa với độ chính xác cao trong thời gian tính bằng giây. Đồng thời, hệ thống đóng vai trò như một sổ điểm điện tử, giúp quản lý toàn diện vòng đời của một kỳ kiểm tra.

### 1.3.2. Mục tiêu cụ thể

Để hiện thực hóa mục tiêu tổng quát, nghiên cứu được phân rã thành ba trụ cột mục tiêu cụ thể:

1. **Khía cạnh Xử lý ảnh và Thị giác máy tính (Image Processing):**
   - Thiết kế thuật toán và quy trình (pipeline) xử lý hình ảnh OMR chuyên dụng cho phiếu trả lời mẫu chuẩn (phiếu 20 câu và 50 câu).
   - Tối ưu hóa các kỹ thuật nhận diện điểm chuẩn (Fiducial Markers), nắn chỉnh hình học hình ảnh nghiêng (Perspective Transformation), và cân bằng độ rọi sáng cục bộ bằng thuật toán CLAHE.
   - Phát triển thuật toán Ngưỡng tô tự thích ứng (Adaptive Fill Threshold) tiên tiến, phân tích biểu đồ Histogram để loại bỏ sai số do học sinh tô bằng các loại bút chì nhạt màu khác nhau.
   - **Chỉ tiêu:** Đạt độ chính xác nhận dạng mức câu hỏi $\ge 95\%$ trên dữ liệu phiếu chuẩn thực tế.

2. **Khía cạnh Trí tuệ nhân tạo và Học sâu (Deep Learning):**
   - Thu thập, gán nhãn dữ liệu và tiến hành huấn luyện các biến thể của mạng nơ-ron YOLOv9 (phiên bản mới và tối ưu nhất của dòng họ YOLO) để giải quyết bài toán phát hiện vị trí câu hỏi và vùng đáp án khoanh tay trên giấy không định dạng.
   - Thiết kế và huấn luyện mạng lưới nơ-ron tích chập (CNN) có tham số tối giản để làm nhiệm vụ phân loại ký tự (A, B, C, D) nằm bên dưới lớp mực khoanh tròn của thí sinh.
   - Nghiên cứu và đề xuất thuật toán ghép cặp phân vùng không gian (Spatial Partition Matching) cùng thuật toán nội suy dựa trên chuỗi tuần tự (Sequential Interpolation) để ghép nối đáp án và câu hỏi.
   - **Chỉ tiêu:** Đạt độ chính xác nhận diện tổng thể $\ge 85\%$ đối với bài kiểm tra khoanh tay không định dạng phức tạp.

3. **Khía cạnh Kỹ nghệ phần mềm (Software Engineering):**
   - Áp dụng các mẫu thiết kế phần mềm hiện đại như Clean Architecture (Kiến trúc Sạch) và Hexagonal Architecture (Cổng và Bộ chuyển đổi) vào việc xây dựng hệ thống Backend sử dụng Java Spring Boot.
   - Xây dựng giao diện Frontend Web tương tác thân thiện, đa nền tảng bằng React, hỗ trợ tải lên và xử lý tệp ảnh hàng loạt (batch processing).
   - Module hóa lõi AI học sâu thành các vi dịch vụ (microservices) độc lập sử dụng Python FastAPI, đảm bảo khả năng giao tiếp mượt mà với lõi Backend Spring Boot qua chuẩn API RESTful.

## 1.4. Phạm vi và giới hạn đề tài

### 1.4.1. Phạm vi nghiên cứu

Nghiên cứu được bao hàm trong các khía cạnh công nghệ và kịch bản sử dụng thực tế sau:
- **Đầu vào (Input):** Các tệp hình ảnh kỹ thuật số (định dạng JPG/PNG) của bài thi trắc nghiệm. Hình ảnh được chụp từ thiết bị di động cá nhân hoặc máy ảnh kỹ thuật số với độ phân giải tối thiểu đề nghị là 5 Megapixel để đảm bảo khả năng trích xuất đặc trưng.
- **Dạng thức bài thi được hỗ trợ:**
  1. Phiếu trả lời trắc nghiệm theo mẫu OMR chuyên dụng quy mô 20 câu hỏi (dành cho kiểm tra ngắn).
  2. Phiếu trả lời trắc nghiệm theo mẫu OMR chuyên dụng quy mô 50 câu hỏi (dành cho kiểm tra định kỳ).
  3. Đề thi trắc nghiệm in giấy thường dạng "khoanh tròn chữ cái", mỗi câu hỏi bao gồm 4 lựa chọn (A, B, C, D).
- **Đầu ra (Output):** Cơ sở dữ liệu JSON số hóa trạng thái của toàn bộ câu hỏi trên ảnh, kết xuất điểm số tính trên thang điểm 10, hiển thị giao diện báo cáo lỗi trực quan (đánh dấu màu sắc lên ảnh bài thi), và chức năng xuất kết xuất dữ liệu báo cáo đa định dạng (Excel, CSV).
- **Môi trường vận hành:** Hệ thống là một ứng dụng Web hoàn chỉnh (Full-stack Web Application), được chứa trong các bộ chứa Docker (Containerization) đảm bảo hoạt động độc lập với môi trường máy chủ gốc, người dùng đầu cuối thao tác thông qua các trình duyệt web hiện đại phổ biến (Chrome, Safari, Edge).

### 1.4.2. Giới hạn nghiên cứu

Do hạn chế về mặt thời gian và nguồn lực phần cứng chuyên dụng, hệ thống hiện tại chưa thể bao trùm một số vấn đề phức tạp ngoài biên của bài toán:
- Hệ thống chỉ được thiết kế với giả định chuẩn là các bài kiểm tra trắc nghiệm dạng 4 lựa chọn (A, B, C, D). Thuật toán AI chưa được huấn luyện để phân loại các dạng mở rộng như bài thi 5 lựa chọn (A, B, C, D, E) hoặc dạng bài thi Điền khuyết, Ghép nối.
- Luồng AI sử dụng mô hình YOLOv9 hiện chỉ tập trung đọc thông tin thân bài thi (vùng câu hỏi và đáp án). Các trường siêu dữ liệu (metadata) viết tay như Mã đề (Exam Code), Số báo danh (Student ID) hoặc Tên thí sinh chưa được hệ thống bóc tách tự động do thiếu dữ liệu huấn luyện OCR tiếng Việt viết tay đủ lớn.
- Mô hình AI nhạy cảm với chất lượng hình ảnh đầu vào. Góc chụp từ camera không được phép bị méo phối cảnh quá cực đoan (góc nghiêng của trục Z lớn hơn 15° so với phương vuông góc bề mặt giấy). Mực in của đề thi yêu cầu có độ tương phản chấp nhận được; đề thi sao chụp (photocopy) bị nhòe đen, mất chữ sẽ làm suy giảm nghiêm trọng độ tin cậy của thuật toán phát hiện đối tượng.
- Giao diện kiến trúc hiện tại chưa áp dụng giao thức trao đổi dữ liệu hướng sự kiện hai chiều (như WebSocket hoặc Server-Sent Events) để phản hồi ngay lập tức tiến trình chấm điểm theo thời gian thực (real-time progress bar), mà vẫn dựa trên cơ chế Client gọi API định kỳ (Polling).

---

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

Chương này đi sâu vào việc làm rõ các nền tảng khoa học cốt lõi, từ lý thuyết thị giác máy tính truyền thống đến các thành tựu của Trí tuệ nhân tạo hiện đại, vốn đóng vai trò là "bộ脑" của hệ thống chấm điểm tự động CODEX. Nửa đầu chương trình bày các nguyên lý xử lý ảnh số để tinh chỉnh dữ liệu hình ảnh thô. Nửa sau tập trung giải phẫu chi tiết lý thuyết của mạng nơ-ron học sâu, bao gồm cơ chế trích xuất đặc trưng của CNN, nguyên lý phát hiện đối tượng với dòng chảy tiến hóa của thuật toán YOLO, và các triết lý thiết kế đằng sau bài toán Nhận dạng Ký tự Quang học (OCR).

## 2.1. Xử lý ảnh và Thị giác máy tính (Computer Vision)

Thị giác máy tính là lĩnh vực liên ngành giao thoa giữa Khoa học Máy tính, Toán học và Trí tuệ nhân tạo, tập trung vào việc mô phỏng cách hệ thống thị giác của con người phân tích và thấu hiểu môi trường không gian. Cốt lõi của thị giác máy tính dựa vào Xử lý ảnh số (Digital Image Processing) để trích xuất tín hiệu có ích từ những tín hiệu hình ảnh hỗn độn [1].

### 2.1.1. Tổng quan về xử lý ảnh số

Ra đời từ những năm 1960 với các ứng dụng ban đầu trong chương trình không gian Apollo của cơ quan Hàng không Vũ trụ NASA nhằm cải thiện hình ảnh bề mặt Mặt trăng, xử lý ảnh số ngày nay đã len lỏi vào từng khía cạnh của công nghệ đời sống: từ y học chẩn đoán ảnh chụp X-quang, MRI; xe tự hành nhận dạng chướng ngại vật; hệ thống CCTV thông minh phân tích hành vi; cho đến giáo dục với công nghệ chấm thi tự động.

**Bản chất biểu diễn của ảnh số:**
Dưới lăng kính của phần mềm máy tính, một bức ảnh không phải là tập hợp của màu sắc và ánh sáng, mà được mô hình hóa toán học dưới dạng một ma trận không gian hai chiều $I(x, y)$, trong đó:
- $x$ và $y$ là hệ tọa độ không gian rời rạc biểu diễn vị trí của một phần tử ảnh (pixel - picture element).
- $I$ là cường độ tín hiệu bức xạ điện từ (độ sáng hoặc độ màu) phản xạ từ vật thể tại vị trí tương ứng.

Trong hệ thống xử lý thị giác, có hai không gian màu chủ đạo được áp dụng:
1. **Không gian màu đa kênh (RGB/BGR):** Ảnh màu tiêu chuẩn được biểu diễn bởi một mảng đa chiều kích thước $H \times W \times 3$. Mỗi pixel là một tập hợp gồm ba cường độ màu cơ bản: Đỏ (Red), Lục (Green) và Lam (Blue), mỗi kênh nhận giá trị nguyên từ $0$ đến $255$. Sự phối hợp của 3 kênh này tạo ra không gian biểu diễn lên tới $256^3 \approx 16,77$ triệu màu.
2. **Không gian ảnh xám (Grayscale):** Rất nhiều bài toán xử lý ảnh — bao gồm nhận dạng phiếu OMR — không cần thông tin về màu sắc mà chỉ quan tâm đến mức độ đậm nhạt của nét vẽ. Ảnh xám loại bỏ hai chiều màu sắc, chỉ giữ lại một kênh cường độ sáng duy nhất (Luma). Kích thước ma trận thu gọn thành $H \times W \times 1$. Giá trị pixel bằng $0$ tương ứng với màu đen tuyền tuyệt đối (hấp thụ ánh sáng mạnh nhất), và $255$ tương ứng với màu trắng thuần (phản xạ ánh sáng mạnh nhất).

Việc chuyển đổi từ ảnh màu RGB sang ảnh xám là một bước tiền xử lý bắt buộc trong nhiều pipeline phân tích nhằm tiết kiệm đến 66% tài nguyên RAM và chu kỳ CPU, đồng thời loại bỏ các nhiễu quang sai màu không đáng có.

> **[Hình 2.1]** *Cần chèn: Sơ đồ minh họa kiến trúc không gian ma trận 3D của ảnh màu RGB và không gian ma trận 2D của ảnh xám Grayscale.*

**Phân loại các phép biến đổi toán học trên ảnh:**
Mọi thuật toán xử lý ảnh phức tạp đều được xây dựng dựa trên nền tảng của 4 họ phép biến đổi cơ bản:
- **Biến đổi Điểm (Point Operations):** Hàm số ánh xạ giá trị cường độ của một pixel đích chỉ phụ thuộc vào chính xác pixel tại vị trí đó ở ảnh gốc ($I'(x,y) = f(I(x,y))$). Ví dụ: thao tác tăng giảm độ sáng, phép đảo ngược màu sắc (Negative), thao tác cắt ngưỡng ảnh.
- **Biến đổi Cục bộ (Local/Neighborhood Operations):** Giá trị của một pixel đích được tính toán dựa trên sự tổ hợp các pixel trong một cửa sổ lân cận (kernel/mask) xung quanh pixel tương ứng ở ảnh gốc. Đây là nền tảng của các bộ lọc (Filters). Ví dụ: bộ lọc làm mờ (Gaussian Blur), bộ lọc tìm đường biên (Sobel Edge Detector).
- **Biến đổi Toàn cục (Global Operations):** Giá trị của pixel đích phụ thuộc vào đặc trưng phân phối tín hiệu của toàn bộ bức ảnh. Ví dụ: phép biến đổi tần số Fourier, giải thuật cân bằng biểu đồ mức xám (Histogram Equalization), thuật toán phân ngưỡng toàn cục Otsu.
- **Biến đổi Hình học (Geometric Operations):** Thay vì thay đổi giá trị mức xám, phép biến đổi này thao tác trên lưới tọa độ, dời chỗ pixel từ vị trí $(x,y)$ sang một vị trí không gian mới $(x',y')$. Ví dụ: thu phóng ảnh (Scaling), xoay ảnh (Rotation), biến đổi phối cảnh nghiêng (Perspective Transformation).

### 2.1.2. Chuyển đổi phối cảnh (Perspective Transformation) dựa trên Fiducial Marker

#### a) Định lý về điểm đánh dấu tham chiếu (Fiducial Marker)

Trong môi trường thực tế, việc sử dụng tay cầm điện thoại để chụp một tờ giấy đặt trên mặt bàn không bao giờ có thể đảm bảo được một góc chụp vuông góc 90° hoàn hảo trục Z. Quang sai của ống kính cùng góc nghiêng tương đối giữa camera và mặt bàn sẽ tạo ra hiện tượng biến dạng phối cảnh (Perspective Distortion): các đường thẳng song song trên thực tế hội tụ về điểm ảo (vanishing point), một hình chữ nhật trên tờ giấy sẽ biến dạng thành một tứ giác bất kỳ trên ảnh. Để các thuật toán chấm điểm quang học dựa trên tọa độ tĩnh (OMR) hoạt động được, hệ thống phải triệt tiêu hiện tượng méo dạng này.

Đây là lý do các mẫu phiếu trả lời trắc nghiệm chuẩn luôn được in kèm các **Fiducial Marker (Điểm đánh dấu tham chiếu)** [7]. Fiducial Marker trong đồ án này được thiết kế là các hình vuông màu đen đặc, in đồng nhất tại 4 góc của khổ giấy A4. Chúng đóng vai trò cung cấp các tọa độ neo hệ quy chiếu tĩnh nhằm phục vụ việc tính toán các ma trận biến đổi nghịch đảo hình học.

Những ưu điểm của thiết kế Marker ô vuông đen:
- Cung cấp độ tương phản cực đại so với nền giấy trắng, tối ưu hóa cho các thuật toán dò tìm đường viền.
- Đảm bảo tính bất biến xoay: Hình vuông luôn có đặc trưng hình học không đổi dù tờ giấy bị đặt ngược hay xoay ngang.
- Loại bỏ nhiễu: Hệ thống có thể thiết lập các bộ lọc toán học dựa trên đặc tính của hình vuông (tỷ lệ giữa hai cạnh luôn xấp xỉ 1,0; tỷ lệ diện tích) để loại trừ các khối hình màu đen nhiễu khác trên phiếu thi.

> **[Hình 2.2]** *Cần chèn: Ảnh minh họa thiết kế phiếu trả lời trắc nghiệm chuẩn, phóng to 4 góc chứa các ô vuông đen Fiducial Marker.*

#### b) Phép biến đổi ma trận phối cảnh (Homography)

Biến đổi phối cảnh là một phép chiếu xạ hình học (Projective Geometry) ánh xạ một đa giác lồi 4 cạnh bất kỳ trên một mặt phẳng $P1$ (mặt phẳng cảm biến ảnh camera) sang một đa giác 4 cạnh trên một mặt phẳng tham chiếu $P2$ (mặt phẳng lý tưởng của tờ giấy). Sự ánh xạ toán học giữa các điểm của hai mặt phẳng này được biểu diễn bằng một ma trận vuông $3 \times 3$ gọi là ma trận **Homography** $\mathbf{H}$ [7]:

$$\lambda \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \mathbf{H} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} h_{11} & h_{12} & h_{13} \\ h_{21} & h_{22} & h_{23} \\ h_{31} & h_{32} & h_{33} \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

Giải hệ phương trình tuyến tính này để tìm tọa độ điểm pixel đích $(x', y')$ sau khi nắn phẳng:

$$x' = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + h_{33}}$$

$$y' = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + h_{33}}$$

Ma trận $\mathbf{H}$ bao gồm 9 phần tử chưa biết. Tuy nhiên, hệ phương trình này có tính chất bất biến theo tỷ lệ đồng dạng (scale factor) $\lambda$, do đó $h_{33}$ thường được chuẩn hóa bằng 1. Như vậy, ma trận thực chất có 8 bậc tự do (Degrees of Freedom). Mỗi cặp tọa độ tương ứng (một điểm gốc trên ảnh và một điểm đích trên khung quy chiếu) đóng góp 2 phương trình tuyến tính. Do đó, để giải hệ và tìm ra 8 ẩn số của ma trận Homography, hệ thống cần và chỉ cần chính xác tọa độ của **tối thiểu 4 điểm tham chiếu không thẳng hàng** — chính là tâm của 4 ô vuông Marker ở bốn góc tờ giấy.

Sau khi tính toán được ma trận $\mathbf{H}$, hệ thống thực hiện phép chiếu ngược (Warp Perspective) áp dụng phép biến đổi lên mọi điểm pixel của bức ảnh thô, tạo ra kết quả là hình ảnh tờ giấy thi vuông vức, với kích thước ma trận được cố định sẵn (ví dụ $1400 \times 2000$ pixel), đảm bảo các bong bóng tròn chứa đáp án đều nằm khít bên trong hệ trục tọa độ lý thuyết định sẵn.

> **[Hình 2.3]** *Cần chèn: Minh họa quá trình Warp Perspective, từ ảnh chụp chéo góc đến hình ảnh phẳng 2D chuẩn mực.*

### 2.1.3. Cân bằng sáng cục bộ (CLAHE)

#### a) Vấn đề phân bố độ rọi sáng không đồng đều

Trong điều kiện thao tác thực tế tại các phòng học hay phòng hội đồng, bài thi hiếm khi được chụp trong một môi trường được setup ánh sáng hoàn hảo (như studio hay máy quét). Các yếu tố ngoại cảnh tác động tiêu cực đến sự phân bố cường độ sáng (Illumination distribution) trên mặt ảnh bao gồm:
- Hiện tượng bóng đổ (Shadow cast) từ cơ thể người chụp, từ cánh tay hay chính từ bản thân thiết bị điện thoại che lấp nguồn sáng trên trần nhà.
- Ánh sáng tự nhiên từ cửa sổ hắt vào tạo ra dốc gradient ánh sáng (một nửa tờ giấy rất sáng, nửa kia chìm trong bóng tối).

Hậu quả của hiện tượng này là các thuật toán lọc ngưỡng phân cực trắng/đen tĩnh sẽ mất phương hướng. Tại vùng tối, một ô chưa tô (màu xám tối) có thể có cường độ pixel thấp y hệt như một ô đã tô đen (màu xám tối) nằm ở vùng được chiếu sáng mạnh.

> **[Hình 2.4]** *Cần chèn: Ví dụ trực quan so sánh lỗi mất chi tiết của các bộ ngưỡng toàn cục trên bức ảnh có vùng bóng đổ đen nặng.*

#### b) Giới hạn của cân bằng biểu đồ toàn cục (Global Histogram Equalization)

Kỹ thuật cân bằng lược đồ mức xám toàn cục (Global Histogram Equalization) là một giải pháp kinh điển nhằm gia tăng độ tương phản của toàn bộ ảnh. Kỹ thuật này hoạt động bằng cách tính toán hàm phân phối tích lũy (Cumulative Distribution Function - CDF) của mọi pixel trên toàn cảnh, sau đó trải rộng biểu đồ phân phối mức xám ra đều dải $[0, 255]$. 
Tuy nhiên, thuật toán này tồn tại yếu điểm chết người: nó xem xét toàn bộ ảnh cùng một lúc. Do đó, nếu ảnh có một vùng nền quá chói hoặc quá tối, phương pháp này sẽ cực đoan hóa vùng đó (ví dụ làm vùng sáng bị "cháy sáng" mất hết chi tiết mực nét bút), làm trầm trọng thêm tình trạng thay vì giải quyết nó.

#### c) Thuật toán CLAHE (Contrast Limited Adaptive Histogram Equalization)

Để giải quyết vấn đề ánh sáng phân cực bất đồng đều, thuật toán CLAHE [6] được áp dụng. Chữ "Adaptive" (Thích nghi) biểu thị rằng thay vì phân tích cả bức ảnh, thuật toán chia cắt ảnh thành hàng chục phân mảnh lưới tọa độ siêu nhỏ (gọi là tiles, kích thước thường dùng là $8 \times 8$ hoặc $16 \times 16$ pixel). 

Tiến trình xử lý của thuật toán CLAHE trải qua các cơ chế phức tạp:
1. **Phân vùng tính toán (Tile Partitioning):** Bức ảnh độ phân giải cao được chia cắt lô-gic thành mạng lưới các ô chữ nhật độc lập nhau.
2. **Xây dựng biểu đồ (Local Histogramization):** Hệ thống tính toán một lược đồ phân phối mức xám (histogram) 256 dải hoàn toàn riêng rẽ cho từng ô nhỏ này.
3. **Cắt gọt giới hạn tương phản (Contrast Limiting / Clip Limiting):** Đây là đóng góp cốt lõi của chữ "CL" (Contrast Limited) phân biệt với thuật toán AHE thông thường. Nếu một lược đồ có một đỉnh gai (spike) tần suất tập trung quá dày đặc tại một mức sáng nhất định (vùng giấy trắng trơn), thuật toán AHE cũ sẽ khuếch đại nhiễu hạt nền của vùng này lên khiến tờ giấy nhìn bị "sần sùi". Để tránh điều này, CLAHE thiết lập một ngưỡng cắt tỉa (Clip Limit). Mọi bin của lược đồ nào vượt quá giới hạn cực đại sẽ bị gọt bỏ đi phần ngọn; phần ngọn diện tích dư thừa này sau đó được đem phân phối rải đều lại cho tất cả các bin còn lại trong lược đồ. 
4. **Nội suy song tuyến tính (Bilinear Interpolation):** Việc xử lý riêng rẽ từng ô sẽ làm xuất hiện các ranh giới mép nối gắt gỏng vuông vức (hiệu ứng kẻ caro / blocking artifacts) giữa các ô liền kề. Để hàn gắn, CLAHE áp dụng phương trình nội suy song tuyến (tính giá trị pixel ranh giới là tổ hợp tuyến tính của tâm 4 ô lưới lân cận nhất), tạo ra sự chuyển tiếp tông sáng mượt mà trơn tru như lụa trên toàn bộ ảnh tổng thể.

> **[Hình 2.5]** *Cần chèn: Lược đồ khối nguyên lý chia lưới, gọt ngưỡng (Clip Limit) và nội suy bề mặt của thuật toán CLAHE.*

### 2.1.4. Phân ngưỡng ảnh (Thresholding)

Kỹ thuật phân ngưỡng (Thresholding) là công cụ quan trọng nhằm tách bóc các đối tượng mục tiêu (chữ viết, nét mực tô - Foreground) ra khỏi vùng giấy không liên quan (nền trắng - Background). Phép toán nhị phân hóa biến mỗi pixel màu xám 8-bit thành một bit nhị phân duy nhất (0 - Đen, hoặc 255 - Trắng):
$$
I_{binary}(x,y) = 
\begin{cases} 
255 & \text{nếu } I_{gray}(x,y) > T \\
0 & \text{nếu } I_{gray}(x,y) \leq T 
\end{cases}
$$
(Lưu ý: Tùy vào định dạng quy ước, thao tác này có thể bị đảo ngược, ví dụ biến mực đen thành vùng sáng trắng 255 để tiện lợi cho thuật toán đo diện tích contour).

**Thuật toán phân ngưỡng tự động Nobuyuki Otsu (Otsu's Threshold)**
Vấn đề lớn nhất của phân ngưỡng là làm sao để chọn được giá trị ngưỡng $T$ (chạy từ 0 đến 255) một cách tối ưu tự động, thay vì phải hard-code bằng tay, vốn rất yếu kém khi điều kiện môi trường thay đổi. Thuật toán Otsu [5] là một công trình kinh điển dựa trên phân tích thống kê phương sai.

Ý tưởng trung tâm của nhà khoa học Otsu là: Việc nhị phân hóa phân chia biểu đồ mức xám làm hai cụm (cụm C0 là Background, cụm C1 là Foreground). Một ngưỡng $T$ được gọi là hoàn hảo nhất nếu sự hỗn tạp nội bộ của từng cụm (Phương sai nội lớp - Intra-class variance $\sigma^2_w$) là nhỏ nhất, hoặc tương đương với việc khoảng cách tách biệt giữa tâm của hai cụm này (Phương sai liên lớp - Inter-class variance $\sigma^2_b$) đạt giá trị lớn nhất.

Thuật toán duyệt vét cạn (brute-force search) qua toàn bộ 256 giá trị $T \in [0, 255]$ và tính toán:

**1. Trọng số xác suất của từng lớp:**
$$ \omega_0(T) = \sum_{i=0}^{T} p_i \quad \text{(Xác suất pixel thuộc nền)} $$
$$ \omega_1(T) = \sum_{i=T+1}^{255} p_i = 1 - \omega_0(T) \quad \text{(Xác suất pixel thuộc mực in)} $$
*(trong đó $p_i$ là xác suất xuất hiện của pixel có mức xám $i$ trên toàn bộ ảnh)*

**2. Giá trị cường độ trung bình của từng lớp:**
$$ \mu_0(T) = \frac{\sum_{i=0}^{T} i \cdot p_i}{\omega_0(T)} $$
$$ \mu_1(T) = \frac{\sum_{i=T+1}^{255} i \cdot p_i}{\omega_1(T)} $$

**3. Phương sai liên lớp (Inter-class variance):**
$$ \sigma^2_b(T) = \omega_0(T)\omega_1(T) \left[ \mu_0(T) - \mu_1(T) \right]^2 $$

Thuật toán sẽ tự động trả về giá trị ngưỡng tối ưu $T^*$ tại đó hàm mục tiêu $\sigma^2_b(T)$ đạt cực đại vô đối. Sự xuất sắc của phương pháp Otsu nằm ở khả năng thích ứng thông minh với sự xê dịch độ sáng chói tổng thể của bức ảnh mà không cần bất cứ sự can thiệp thủ công nào.

### 2.1.5. Các phép toán hình thái học (Morphological Operations)

Sau khi ảnh được nhị phân hóa, kết quả thường không hoàn hảo. Nét in của chữ có thể bị rỗ, đứt đoạn li ti do cảm biến camera bị nhiễu bụi; hoặc nền giấy trắng có lấm tấm các đốm đen nhỏ ly ti (Salt and Pepper Noise). Xử lý hình thái học học (Mathematical Morphology) là bộ công cụ toán học dựa trên hình dạng dùng để gọt giũa và tái cấu trúc lại các khuyết tật hình học này của vật thể trong ảnh nhị phân.

Hai phép toán nguyên thủy là Cấu trúc co (Erosion) và Cấu trúc giãn (Dilation):
- **Phép co (Erosion):** Sử dụng một phần tử cấu trúc (Structuring Element / Kernel) ví dụ như ma trận vuông $3 \times 3$, quét trượt qua toàn bộ ảnh nhị phân. Một pixel đích chỉ giữ giá trị Trắng (Foreground) nếu TẤT CẢ các pixel dưới mạng lưới quét cũng là Trắng, nếu có bất kỳ pixel nào là Đen (Background), pixel đó biến thành Đen. Hiệu ứng: ăn mòn ranh giới vật thể, làm các khối chữ mỏng đi, "tẩy bay" hoàn toàn các nhiễu đốm sáng nhỏ lẻ loi trên nền tối.
- **Phép giãn (Dilation):** Ngược lại với Erosion. Một pixel đích biến thành Trắng nếu CÓ ÍT NHẤT một pixel dưới mạng lưới quét là Trắng. Hiệu ứng: bồi đắp vật thể, làm nét chữ dày thêm ra, hàn gắn các khe nứt đứt gãy nhỏ bên trong nội bộ thân chữ.

Dựa trên hai hạt nhân này, thị giác máy tính phát sinh hai phép toán cấu trúc phức hợp:
- **Phép mở (Opening) = Co trước, Giãn sau:** Có công năng dọn dẹp các đốm nhiễu lốm đốm xung quanh vật thể lớn, và tách đứt hai vật thể đang bị dính nhẹ vào nhau, mà vẫn bảo toàn khá nguyên vẹn kích thước diện tích tổng thể của vật thể chính ban đầu.
- **Phép đóng (Closing) = Giãn trước, Co sau:** Có chức năng trám kín các hố đen lỗ hổng nhỏ li ti nằm bên trong lõi cấu trúc của vật thể lớn, hoặc nối liền kết dính lại một nét chữ, nét đường biên đang bị nứt gãy đứt đoạn hở hang.

Trong hệ thống chấm bài của đồ án, thuật toán Closing được sử dụng mạnh mẽ để "bồi đắp" và hợp nhất các nét đứt gãy của dấu mực do thí sinh tô chì không liền tay, biến chúng thành một hình tròn bong bóng liền khối vững chắc trước khi tiến hành tính toán đo lường diện tích hạt mực.

---

## 2.2. Trí tuệ nhân tạo và Học sâu (Deep Learning)

Mặc dù xử lý ảnh truyền thống thể hiện sự ưu việt trong môi trường có quy tắc cứng (phiếu mẫu chuẩn), nhưng chúng trở nên vô vọng khi đối mặt với dữ liệu phi quy tắc (đề kiểm tra khoanh tay không định dạng). Để giải quyết lớp bài toán nhận thức mức cao này, hệ thống buộc phải dựa vào học sâu (Deep Learning) — một kỷ nguyên mới của trí tuệ máy móc có khả năng tự động khám phá và trừu tượng hóa các quy luật.

### 2.2.1. Tổng quan về Học sâu

Trí tuệ nhân tạo (AI) là giấc mơ về một cỗ máy có nhận thức. Học máy (Machine Learning - ML) là một tập hợp các công cụ toán học thống kê để dạy cỗ máy cách học từ dữ liệu. Và **Học sâu (Deep Learning - DL)** là tầng sâu nhất, chuyên biệt nhất của Học máy, được truyền cảm hứng trực tiếp từ kiến trúc mạng lưới tế bào thần kinh sinh học của bộ não loài người [2]. 

Con đường tiến hóa của Học sâu đã trải qua những giai đoạn thăng trầm lịch sử:
- Khái niệm về tế bào nơ-ron điện toán xuất hiện lần đầu năm 1943 với mô hình logic McCulloch-Pitts [3].
- Năm 1962, nhà tâm lý học Frank Rosenblatt kiến tạo ra mô hình Perceptron [4], khai sinh ý tưởng về trọng số học tập (learnable weights).
- Sự đột phá đến vào năm 1986 khi nhóm nghiên cứu của Geoffrey Hinton, Rumelhart và Williams công bố nền tảng của thuật toán Lan truyền ngược sai số (Back-propagation Algorithm) [6] — trái tim động cơ cho phép hiệu chỉnh hàng triệu tham số của các lớp ẩn đa tầng một cách tinh tế.
- Năm 2006 đánh dấu sự hồi sinh của AI với khái niệm "Deep Belief Networks" (DBN) của Hinton [8]. Từ mốc thời gian này, kết hợp cùng vụ nổ dữ liệu lớn (Big Data) và kỷ nguyên sức mạnh tính toán song song vũ bão của các kiến trúc card đồ họa (GPU), Học sâu trỗi dậy và xô đổ mọi kỷ lục của giới khoa học trong các bài toán Thị giác máy tính (ImageNet 2012) và Xử lý ngôn ngữ tự nhiên.

Sức mạnh định danh của Học sâu so với Học máy truyền thống nằm ở khái niệm **Tự động trích xuất đặc trưng đa tầng (Hierarchical Feature Representation)**. Trong khi các thuật toán cũ (như SVM hay Random Forest) yêu cầu các chuyên gia con người phải tự tay thiết kế và tính toán các đặc trưng (Hand-crafted features như viền, góc, HOG, SIFT) để mớm cho máy tính; Mạng học sâu tự thân nó sẽ tiêu hóa dữ liệu điểm ảnh thô (raw pixels). Các tầng nơ-ron nông đầu tiên học cách nhận diện các cạnh thẳng; tầng sâu hơn kết hợp các cạnh đó lại để nhìn ra các kết cấu hình học (hình vuông, chữ O); và các tầng cực sâu cuối cùng tổ hợp chúng lại để nhìn thấy hình bóng của một con mèo, hay khuôn mặt một học sinh.

### 2.2.2. Mạng nơ-ron nhân tạo (Artificial Neural Network - ANN)

**Cấu tạo tế bào Nơ-ron nhân tạo:**
Đơn vị tính toán nhỏ nguyên tử của mạng Học sâu là nơ-ron. Một nơ-ron nhân tạo hoạt động như một cỗ máy tính tổng hàm tuyến tính:
$$Z = \mathbf{W}^T\mathbf{X} + b = \sum_{i=1}^{n} w_i x_i + b$$
Trong đó:
- $\mathbf{X} = [x_1, x_2, ..., x_n]$ là véc-tơ tín hiệu đầu vào từ các nơ-ron lớp trước.
- $\mathbf{W} = [w_1, w_2, ..., w_n]$ là véc-tơ các hệ số trọng lượng (Weights) — đại diện cho sức mạnh và tầm quan trọng của dòng thông tin truyền qua các khớp xi-náp kết nối. 
- $b$ là hệ số độ lệch (Bias) — đóng vai trò như một ngưỡng kích thích nội tại, dịch chuyển hàm số.

**Hàm kích hoạt (Activation Function):**
Nếu hệ thống chỉ tính tổng tuyến tính $\mathbf{W}^T\mathbf{X} + b$ cho một tỷ nơ-ron, thì toán học chứng minh nó cũng chỉ tương đương với một mạng lưới có một nơ-ron duy nhất. Do đó, hàm kích hoạt $\Phi(Z)$ được bổ sung ngay phía sau phép cộng tuyến tính để nhúng tính phi tuyến (Non-linearity) vào hệ thống. Thiếu tính phi tuyến, mạng lưới không thể giải quyết được bất kỳ bài toán phức tạp nào trên đời (như phân chia ranh giới vật thể uốn lượn hình sin). 
Các hàm kích hoạt kinh điển bao gồm:
- **Sigmoid:** $\sigma(z) = \frac{1}{1 + e^{-z}}$. Nén mọi giá trị đầu ra vào khoảng trơn $[0, 1]$, xuất sắc để biểu diễn xác suất toán học. Nhược điểm: làm triệt tiêu dần đạo hàm ở vùng hai biên bão hòa (Vanishing Gradient), gây tê liệt mạng nơ-ron ở các tầng quá sâu.
- **ReLU (Rectified Linear Unit):** $f(z) = \max(0, z)$. Đơn giản hóa mức cực đoan: chặn mọi giá trị âm về số 0 cứng, và giữ nguyên giá trị nếu dương. Hàm này giải quyết ngoạn mục hiện tượng tiêu biến đạo hàm của Sigmoid, mang lại tốc độ học nhanh gấp hàng chục lần và trở thành tiêu chuẩn công nghiệp cấu tạo mạng nơ-ron sâu ngày nay.

**Thuật toán Lan truyền ngược (Back-propagation):**
Làm cách nào cỗ máy học được tập trọng số $\mathbf{W}$ từ hàng triệu con số vô nghĩa lúc khởi tạo? 
Mọi chu trình huấn luyện bắt đầu bằng một **Hàm mất mát (Loss Function - $\mathcal{L}$)**. Nó là thước đo định lượng xem dự đoán của mô hình hiện tại (ví dụ dự đoán là ảnh con gấu) bị sai lệch tồi tệ cỡ nào so với sự thật mặt đất (ảnh thực chất là con chó).
Giải thuật Lan truyền ngược sẽ sử dụng nguyên lý quy tắc dây chuyền toán học của Vi phân đa biến (Chain Rule in Calculus). Nó tính toán đạo hàm riêng (Gradient) của sự thất bại (Hàm mất mát) ứng với từng biến số trọng số nhỏ bé ở tận sâu trong hàng trăm lớp mạng $\frac{\partial \mathcal{L}}{\partial \mathbf{W}}$. 
Thông qua đạo hàm gradient định hướng này, thuật toán Tối ưu hóa (Optimizer) như Stochastic Gradient Descent (SGD) hoặc thuật toán Adam sẽ khẽ nhích điều chỉnh các giá trị của $\mathbf{W}$ theo hướng đi ngược chiều lại sườn dốc của hàm mất mát. Quá trình này được lặp lại hàng nghìn, hàng triệu vòng lặp luân hồi (Epochs) cho đến khi sai số của mô hình chạm tới thung lũng đáy cực tiểu hội tụ.

### 2.2.3. Mạng nơ-ron tích chập (Convolutional Neural Network - CNN)

Mạng đa tầng nơ-ron kết nối đầy đủ (Fully Connected ANN) sở hữu cấu trúc mỗi nơ-ron tầng này đan chéo với tất cả nơ-ron tầng trước. Khi đưa vào một bức ảnh màu có kích thước khiêm tốn $224 \times 224$ pixel, chỉ một nơ-ron ẩn ở tầng đầu đã phải kéo theo $224 \times 224 \times 3 = 150.528$ kết nối trọng số. Một mạng có ngàn nơ-ron sẽ đòi hỏi một ngân sách tham số lên đến hàng tỷ, dẫn đến sự hủy diệt bộ nhớ máy tính và hậu quả thảm khốc của việc học vẹt quá khớp (Overfitting). Thêm vào đó, mạng lưới phẳng 1 chiều hoàn toàn phá hủy trật tự liên kết không gian topology 2D của điểm ảnh.

Năm 1998, giáo sư Yann LeCun công bố kiến trúc Mạng nơ-ron Tích chập (CNN) thông qua hệ thống nhận diện chữ số bưu điện LeNet-5 [10], tạo ra cuộc cách mạng kiến trúc vĩnh viễn thay đổi lịch sử Trí tuệ nhân tạo thị giác. 
Nguyên lý của CNN chia lưới thành ba loại thành phần (Lớp) với triết lý thiết kế tối thượng: Chia sẻ tham số (Parameter Sharing) và Kết nối cục bộ thưa (Local Connectivity).

1. **Lớp Tích chập (Convolutional Layer):**
   Thay vì nơ-ron nhận tín hiệu từ cả bức ảnh, CNN sử dụng các bộ lọc màng lưới nhỏ (Filters/Kernels) ma trận kích thước thường là $3 \times 3$ hoặc $5 \times 5$ trượt chầm chậm (sliding window) quét dọc theo bề mặt bức ảnh 2 chiều. Tại mỗi ô tọa độ lưới, phép nhân ma trận chập dot-product được thực thi để tính toán giá trị một pixel cho một "Bản đồ đặc trưng" (Feature Map) đầu ra. 
   Một bộ lọc (Filter) đóng vai trò như một kính lúp chuyên dò một mẫu hình dạng nhất định (ví dụ kính lúp chuyên tìm nét gạch chéo góc 45 độ, hoặc chuyên tìm các vùng chuyển sắc độ từ đen sang trắng). Việc chỉ sử dụng một ma trận nhỏ xíu $3 \times 3$ (có vỏn vẹn 9 trọng số) trượt khắp toàn bộ bề mặt ảnh nghìn pixel giúp hệ thống đạt được "Tính bất biến tịnh tiến" (Translation Invariance) — một con mèo ở góc trên bên trái hay ở góc dưới bên phải thì bộ lọc trượt qua cũng vẫn sẽ tìm được nó bằng chính 9 trọng số đó. Sự giảm thiểu hàng tỷ tham số dư thừa xuống còn hàng vạn khiến mạng CNN hội tụ vô cùng thần tốc và tránh được học vẹt một cách ngoạn mục.

2. **Lớp Gộp không gian (Pooling Layer):**
   Lớp này đóng vai trò như một cơ chế "giảm độ phân giải" (Down-sampling). Các bản đồ đặc trưng khổng lồ từ lớp chập được đẩy qua lớp Gộp. Kỹ thuật Gộp cực đại (Max Pooling) trượt một khung $2 \times 2$ (có bước nhảy Stride=2) qua dữ liệu, và chỉ giữ lại một pixel có cường độ kích thích cao nhất sừng sững trong khung 4 ô đó, và vứt bỏ 3 ô còn lại.
   Điều này giảm kích thước chiều rộng và chiều cao của không gian dữ liệu đi 75%, tiêu diệt một lượng khổng lồ phép tính máy tính ở các tầng sâu. Triết lý của Max Pooling cực kỳ thanh lịch: Mô hình không cần biết chính xác tọa độ ly ti đến cấp độ pixel của cái tai con mèo đang nằm ở đâu, nó chỉ cần biết sự thật chắc chắn rằng khu vực góc 1/4 kia "CÓ TỒN TẠI" một cái tai mèo.

3. **Lớp Kết nối đầy đủ (Fully Connected - FC Layer):**
   Nằm ở đoạn chót cùng của mạng nơ-ron, tất cả các bản đồ đặc trưng đa chiều đã được trừu tượng hóa cực sâu sẽ được duỗi phẳng (Flatten) thành một chuỗi mảng một chiều dài dằng dặc. Ở tầng này, mạng quay lại kiến trúc gốc truyền thống ANN. Nó đóng vai trò như một bộ tư duy biện luận logic (Classifier), đánh giá xem với tất cả hàng ngàn các đặc trưng (mắt, mũi, cong, vuông) mà các lớp Tích chập vừa gặt hái được phía trước, thì tỷ lệ tổng hợp chung cuộc bức ảnh này là Chó hay là Mèo, là chữ A hay chữ B. Hàm Softmax thường được đặt ở tận cùng đuôi mạng để xuất ra một véc-tơ tổng 100% tỷ lệ xác suất cho các lớp dự đoán.

### 2.2.4. Phát hiện đối tượng (Object Detection)

#### a) Định nghĩa của bài toán
Nếu như mạng lưới phân loại (Image Classification) như ResNet hay VGG chỉ có khả năng nhìn vào một bức tranh phong cảnh và trả lời câu hỏi: "Trong tranh có cái ô tô không?", thì **Phát hiện đối tượng (Object Detection)** là bài toán thị giác máy tính đẳng cấp cao hơn có nghĩa vụ trả lời hai câu hỏi cùng lúc vô cùng phức tạp: "Trong tranh có bao nhiêu cái ô tô? Và chính xác từng chiếc ô tô đang nằm ở hệ tọa độ pixel nào?".
Mô hình phát hiện đối tượng không chỉ trả về nhãn phân loại lớp (Class label) mà còn xuất ra một hộp bao chữ nhật (Bounding Box) chốt chặt vào hình hài của vật thể, thường được định nghĩa bằng 4 biến tọa độ: $(x, y, w, h)$ tương ứng là điểm tâm trục $x$, trục $y$, chiều rộng $w$ và chiều cao $h$ của khung bao [18]. Đi kèm với đó là một điểm số tin cậy đo lường sự chắc chắn (Confidence Score).

> **[Hình 2.16]** *Cần chèn: Ví dụ trực quan minh họa Phát hiện đối tượng — ảnh một ngã tư đường với các bounding box ôm sát xe hơi, người đi bộ, xe máy, hiển thị kèm nhãn phân loại dự đoán.*

#### b) Phân luồng kiến trúc phát hiện: Hai giai đoạn và Một giai đoạn
Khởi nguồn từ những năm 2014, bức tranh kiến trúc Deep Learning cho việc phát hiện đối tượng bị thống trị bởi cuộc phân cực giữa hai hệ tư tưởng lớn:

1. **Kiến trúc mạng Hai giai đoạn (Two-stage Detectors):**
   Ông vua của trường phái này là họ hàng gia tộc dòng R-CNN (Region-based CNN), Fast R-CNN, Faster R-CNN, và Mask R-CNN. 
   Hệ thống làm việc theo quy trình hai buồng độc lập. Giai đoạn buồng 1: Một mạng lưới đề xuất khu vực thông minh (Region Proposal Network - RPN) quét lướt qua bức ảnh để khoanh đại ra khoảng 2000 mảnh vỡ ứng cử viên mù (những khối mảng có màu sắc cấu trúc nghi ngờ là có vật thể). Giai đoạn buồng 2: Hệ thống cắt rời từng mảnh ứng cử viên này ra, phóng to lên rồi tống lần lượt từng cái một vào bộ tư duy CNN chuyên biệt để thẩm định kỹ lưỡng xem nó rốt cục là con chó hay chỉ là đống rác nhiễu nền, rồi mới hiệu chỉnh lại tọa độ box cho khít.
   *Ưu điểm:* Cung cấp sự hoàn hảo tuyệt đối trong độ chính xác phân giải vật thể, vô địch trong các cuộc thi.
   *Khuyết điểm:* Gánh nặng tính toán khổng lồ dẫn đến tốc độ khung hình thảm hại rùa bò (thường dưới 5 FPS ở thời điểm bấy giờ), hoàn toàn vô vọng cho các ứng dụng xe tự lái thời gian thực hay camera giao thông.

2. **Kiến trúc mạng Một giai đoạn (One-stage Detectors):**
   Vào năm 2016, hệ tư tưởng Một giai đoạn do YOLO (You Only Look Once) và SSD (Single Shot MultiBox Detector) khởi xướng đã gây chấn động nền công nghiệp. Ý tưởng cách mạng phá bỏ hoàn toàn khâu tìm kiếm rà soát mù RPN. Thay vào đó, mạng nơ-ron nhìn bao quát toàn bộ bức ảnh tổng thể CHỈ TRONG MỘT LẦN DUYỆT TRUYỀN DUY NHẤT (Look Once).
   Kiến trúc này chia cắt bức hình đầu vào thành một mạng lưới kẻ caro $S \times S$ đều nhau tăm tắp. Mỗi mắt xích của mạng lưới lưới sẽ phải tự đứng ra gánh vác trách nhiệm đưa ra dự đoán độc lập: Nếu tâm lõi của một vật thể rơi trúng vào lãnh thổ của ô lưới nào, thì ô lưới đó phải tự tính toán phun ra các ma trận dự đoán gồm hộp bao bounding box và xác suất vật thể đó là con mèo hay con chó. Mọi thao tác này diễn ra trên hệ thống mạng nơ-ron song song đồng loạt một mạch từ đầu đến đuôi mà không có một vòng lặp nhai lại nào.
   *Ưu điểm:* Tốc độ bùng nổ siêu âm thời gian thực kinh ngạc (YOLO thời kỳ đầu đã đạt 45-150 FPS).
   *Khuyết điểm:* Ban đầu, chúng chật vật để định vị các chùm vật thể bé tí hon đứng chen chúc dính chùm vào nhau (ví dụ một đàn chim xa tít chân trời), dẫn đến độ chính xác bị Faster R-CNN bỏ xa. Tuy nhiên, qua nhiều năm tiến hóa thiết kế các nhánh tính toán tinh xảo, nhược điểm này đã được thế hệ YOLO hiện đại triệt tiêu thành công.

> **[Hình 2.17]** *Cần chèn: Lược đồ minh họa hai triết lý thiết kế song hành: Kiến trúc đường ống nối tiếp nhiều buồng của Faster R-CNN so với triết lý kiến trúc quy hoạch mạng lưới đánh phủ song song của YOLO.*

#### c) Các chỉ số cơ bản của thuật toán: IoU và NMS

Để các kiến trúc hộp bao (Bounding Box) có thể hoạt động học tập được, ngành học máy phát triển hai công cụ kỹ thuật vô cùng độc đáo đo lường hình học không gian:

**Độ đo chỉ số IoU (Intersection over Union)**
Trong bài toán nhận diện hộp chữ nhật, làm sao để đánh giá hộp mà AI vẽ ra sai lệch cỡ nào so với hộp do chuyên gia con người vẽ bằng tay (Ground Truth)? Không thể dùng phép đo khoảng cách hai điểm đơn thuần vì hộp còn có kích cỡ to nhỏ dài rộng. Chỉ số IoU ra đời làm thước đo vàng [18]. Nó tính toán bằng công thức toán tập hợp học: lấy diện tích phần diện tích giao nhau (chồng lấn) của hộp máy và hộp người chia cho diện tích tổng không gian hình hộp được phủ bởi cả hai hộp.
$$ \text{IoU} = \frac{\text{Area of Intersection}}{\text{Area of Union}} $$
Giá trị IoU là một điểm tỷ lệ từ $0.0$ đến $1.0$. Nếu giá trị bằng $0$, hai hộp không chạm vào nhau một milimet nào. Nếu bằng $1$, hai hộp xếp chồng khít chặt hoàn mỹ. Trong tiêu chuẩn đánh giá, một dự đoán thường được coi là hợp lệ (True Positive) nếu nó có IoU $\ge 0.5$.

**Kỹ thuật Triệt tiêu phi cực đại (Non-Maximum Suppression - NMS)**
Trong quá trình phỏng đoán một giai đoạn của YOLO, khi một con chó đi ngang qua khung hình, thay vì chỉ có một ô lưới phát hiện ra, thường sẽ có tới ba hoặc bốn ô lưới lân cận nhau cùng hào hứng đưa ra các hộp bao bao quanh con chó đó. Kết quả trên màn hình là con chó bị bao quanh bởi một mớ bòng bong 5-6 hộp hình nhằng nhịt đè lên nhau. Kỹ thuật hậu xử lý làm sạch NMS được kích hoạt để dẹp loạn:
1. Nó tập hợp tất cả các hộp bao đang dự đoán là "Chó", lôi hộp bao có điểm tự tin (Confidence Score) chót vót cao nhất ra để phong làm "Hộp chuẩn".
2. Bắt đầu rà quét lấy "Hộp chuẩn" so sánh IoU với tất cả đám hộp lon ton còn lại. Bất cứ hộp nào mà có IoU với "Hộp chuẩn" lớn hơn một ngưỡng (ví dụ 0.4 - nghĩa là chồng lấn quá lớn), NMS sẽ thẳng tay xóa sổ vĩnh viễn hộp đó vì khẳng định rằng nó đang dự đoán lại trùng vào con chó mà "Hộp chuẩn" đã bắt được.
3. Kỹ thuật lặp đi lặp lại với hộp xếp hạng confidence số hai (nếu nó chưa bị xóa), loại bỏ tiếp các hộp trùng, lặp cho đến khi hết danh sách. Kết quả trả về là không gian trở nên quang đãng, mỗi đối tượng chỉ được khóa bởi một và chỉ một hộp bao ranh giới hoàn mỹ nhất.

### 2.2.5. Họ mô hình YOLO và kiến trúc YOLOv9

YOLO (You Only Look Once) [3] đã vượt ra khỏi danh xưng một thuật toán đơn lẻ để trở thành một hệ tư tưởng thống trị toàn cầu lĩnh vực phát hiện đối tượng liên tục trong gần một thập kỷ. Được thai nghén và công bố lần đầu tiên bởi nhà nghiên cứu thiên tài Joseph Redmon vào năm 2016, hệ phả YOLO đã trải qua vô vàn lần chuyển giao thế hệ công nghệ thông qua các cộng đồng khoa học mã nguồn mở khổng lồ.

**Dòng chảy biên niên sử của hệ phả YOLO:**
- **YOLOv1, v2, v3 (2016 - 2018):** Những kiệt tác sáng tạo gốc rễ của Joseph Redmon. Chúng xác lập cơ chế mạng lưới Grid, phát minh ra Anchor Boxes (các hộp mẫu tiên nghiệm) và kiến trúc Darknet huyền thoại được lập trình bằng ngôn ngữ C thuần túy để tối đa hóa tốc độ xung nhịp máy tính.
- **YOLOv4 (2020):** Alexey Bochkovskiy [22] đã kế thừa mảng mã nguồn Darknet khi Joseph Redmon giải nghệ. Phiên bản này nhồi nhét thành công một loạt các kỹ thuật toán học đột phá cực mạnh "Bag of Specials" (Mish activation, PANet) và "Bag of Freebies" (Mosaic data augmentation, CutMix) để đẩy mAP của giới hạn thời gian thực lên đỉnh cao mới.
- **YOLOv5, v8 của Ultralytics:** Đánh dấu kỷ nguyên chuyển dịch nền tảng sang framework siêu linh hoạt PyTorch của Python [21]. Kiến trúc trở nên cực kỳ thân thiện với doanh nghiệp triển khai, ứng dụng thiết kế vô mỏ neo (Anchor-free) phân tách luồng (Decoupled head) vô cùng sáng tạo.
- **YOLOv9 (Ra mắt tháng 2 năm 2024):** Công trình học thuật uyên bác do giáo sư Chien-Yao Wang (cũng là đồng tác giả của YOLOv7) phát triển [23]. Đây là phiên bản mang tính cách mạng về triết lý lý thuyết dòng chảy thông tin nơ-ron, được chọn làm xương sống lõi phát hiện đối tượng AI cho đồ án này.

#### a) Hiện tượng Nút thắt cổ chai thông tin (Information Bottleneck)

Vấn đề muôn thuở của học sâu hiện đại là sự ám ảnh việc xây dựng những mạng lưới sâu hun hút (với hàng trăm hàng nghìn tầng layer layer) để mong mô hình "thông minh hơn". Tuy nhiên, một định lý khốc liệt về dòng chảy nén thông tin trong khoa học máy tính được gọi là **Nguyên lý Nút thắt cổ chai thông tin (Information Bottleneck Principle)** đã phơi bày một nghịch lý: Khi dữ liệu (như hình ảnh bức tranh) bị chảy và nhào nặn lần lượt xuyên qua quá nhiều các tầng tích chập và gộp liên tiếp, thông tin gốc ban đầu sẽ bị mất mát, rơi vãi và bị bóp méo dần dần theo chiều dài tầng sâu.
Hệ lụy trực tiếp: Đến khi tín hiệu chạm được đến đáy của mạng lưới chót cùng để tính toán Hàm mất mát và kích hoạt quá trình Lan truyền ngược (Back-propagation), thì bản thân đạo hàm Gradient tạo ra đã trở nên nghèo nàn, biến dạng do bị mất phương hướng nguồn gốc. Khi gradient bị méo đi ngược trở lại để cập nhật trọng số, mạng lưới sẽ học một cách lệch lạc, dẫn đến hiện tượng mạng càng sâu nhưng độ chính xác lại suy giảm (Degradation problem).

#### b) Trụ cột công nghệ số 1: Thông tin gradient khả trình (Programmable Gradient Information — PGI)

Để vá lỗ hổng suy thoái dòng chảy trên, YOLOv9 không sử dụng lại các kỹ thuật cũ kỹ rườm rà. Hệ thống đề xuất ra kết cấu ma trận phức hợp tên là PGI, chia kiến trúc xử lý thành ba nhánh sông song song chảy [23]:

1. **Nhánh sông chính (Main Branch):** Đây là mạng lưới backbone xương sống thiết yếu, được dùng thường trực cả khi huấn luyện mô hình lẫn khi đưa mô hình ra thế giới thực dự đoán. Cấu trúc của nhánh sông chính tuân theo thiết kế thu nhỏ thon gọn để đảm bảo quá trình dự đoán chạy nhanh như điện xẹt.
2. **Nhánh sông đảo ngược phụ trợ (Auxiliary Reversible Branch):** Đây là con ác chủ bài cực kỳ tinh vi. Nhánh này được thiết lập song song bên cạnh, với kiến trúc toán học có đặc tính "Đảo ngược hoàn hảo" (Reversible). Nó bảo hành tuyệt đối rằng không một bit dữ liệu nào của bức ảnh gốc bị tiêu biến khi chảy qua nó. Nhờ vậy, khi tính đạo hàm mất mát ở đuôi nhánh này, dòng gradient truyền về sẽ là dòng gradient tinh khiết thuần túy vô cùng mạnh mẽ, không bị vấy bẩn bởi Information Bottleneck. Kì diệu hơn, dòng gradient tinh khiết này sẽ được bẻ lái bơm rót ngang sang để định hướng chỉ bảo (update trọng số) cho mạng Nhánh sông chính học cách trích xuất tốt hơn. Đỉnh cao thiết kế nằm ở chỗ: Nhánh sông phụ trợ này là một công cụ *chỉ để huấn luyện*. Một khi huấn luyện xong, nhánh phụ trợ này sẽ bị tháo dỡ vứt bỏ hoàn toàn khỏi mô hình, giúp mô hình Nhánh chính đem đi thực chiến không hề bị tăng thêm một ounce tạ nào về dung lượng hay tốc độ tính toán.
3. **Mạng thông tin phụ trợ đa cấp (Multi-level Auxiliary Information):** Thông thường các tầng nông nhận diện vật thể khổng lồ, tầng sâu nhận diện các chấm vật thể ly ti. Kỹ thuật này trích xuất gradient và luân chuyển thông tin đan chéo ngữ nghĩa, giúp mạng nơ-ron nhìn thấy được đặc trưng đa chiều của cả đồ vật to lẫn đồ vật cực nhỏ ở tất cả các lớp biểu diễn.

#### c) Trụ cột công nghệ số 2: Mạng tổng hợp tầng hiệu quả tổng quát (GELAN)

Thay vì chạy đua bằng các phép tính nhồi nhét đắt đỏ như Depthwise Convolution hay Transformer Attention. YOLOv9 cấu trúc lại xương sống của mình bằng khối vật liệu mới mang tên GELAN (Generalized Efficient Layer Aggregation Network).

Khối vật liệu GELAN là sự kết hôn kỹ thuật hoàn hảo giữa hai triết lý thiết kế mạng vĩ đại nhất:
- Cơ chế của **CSPNet (Cross Stage Partial Network) [24]:** Ở mỗi điểm khối tầng, chia luồng khối lượng nước dữ liệu thành hai nửa. Một nửa cho chạy băng băng nhảy cóc bỏ qua hẳn các phép tính (bypass), nửa kia cho chui vào khu vực tích chập tính toán nặng nhọc, sau đó ở đoạn cuối lại gộp hai nửa sông này lại. Mẹo này giúp khối lượng tham số FLOPs giảm đi ngót nghét một nửa mà không hề suy suyển thông tin, đồng thời tạo ra đường hầm ngầm cho gradient chạy thẳng băng về đích không rào cản.
- Cơ chế của **ELAN (Efficient Layer Aggregation Network) [25]:** Điều phối cực độ cấu trúc mạng bằng cách thiết kế số lượng luồng đường truyền song song xen kẽ với chiều sâu khối, qua đó tối ưu thuật toán tìm độ dài của chặng đường truyền gradient dài nhất và ngắn nhất.
Thiết kế của GELAN chứng minh năng lực toán học mạnh mẽ của mình: Hệ thống hoàn toàn vứt bỏ được thao tác nhân chập theo chiều sâu phức tạp, chỉ cần dùng những hàm Tích chập truyền thống đơn sơ nhất mà vẫn đè bẹp các đối thủ tân tiến nhất.

**Sức mạnh kiểm chứng thực tế:**
Thực nghiệm benchmark trên dữ liệu tiêu chuẩn công nghiệp gắt gao thế giới MS COCO cho thấy, với cùng một khối lượng cân nặng tham số, YOLOv9 hoạt động tiết kiệm tính toán tham số đi hơn 42% và tiết kiệm tài nguyên sức mạnh số học vãi ra (FLOPs) đi 21% so với các mạng thuộc gia phả YOLOv7, trong khi độ chính xác trung bình (mAP) lại vượt trội mạnh mẽ thiết lập nên tiêu chuẩn State-of-the-art đỉnh cao thế giới mới ở thời điểm hiện tại.

> **[Hình 2.22]** *Cần chèn: Sơ đồ biểu đồ bong bóng Scatter plot so sánh tổng hợp các hệ mô hình YOLO đời v5, v7, v8, v9: Đặt mAP lên trục tung và số lượng Tham số lên trục hoành. Thể hiện vị trí đắc địa của YOLOv9 phá vỡ ranh giới đường cong Pareto Frontier.*

### 2.2.6. Bài toán Nhận dạng ký tự quang học (OCR)

#### a) Tổng quan về tiến hóa của OCR

Nhận dạng ký tự quang học (Optical Character Recognition - OCR) được định nghĩa là công nghệ thị giác trí tuệ phân tích hình ảnh của các văn bản vật lý (viết tay, đánh máy, hoặc biển hiệu) và giải mã (Decode) chúng thành các dạng chuỗi mã nhị phân kỹ thuật số như ASCII hay bảng mã ký tự Unicode để phần mềm máy tính có thể lập trình, biên tập và tra cứu lưu trữ [26]. 
Trong ngữ cảnh của đồ án chấm thi tự động này, mô hình phát hiện đối tượng YOLOv9 mới chỉ giải quyết nửa bài toán: nó vẽ vòng tròn chỉ ra vị trí chính xác của "Câu 1" hoặc "Khối ô đáp án A được chọn". Để máy tính thực sự "hiểu" được cái khối hình ảnh đen trắng đó mang ý nghĩa ký tự A hay ký tự C, một hệ thống OCR buộc phải được triệu gọi nối tiếp ngay sau YOLO.

> **[Hình 2.23]** *Cần chèn: Minh họa mô phỏng quy trình OCR nối tiếp (Pipeline): Đầu vào là ảnh crop nhỏ cắt từ bài thi chứa chữ "A" bị nét bút bi khoanh đè lên, qua bộ hộp đen OCR, nhả ra mã ASCII chữ 'A' trên Console.*

Con đường lịch sử của công nghệ OCR đã tiến hóa qua 3 kỷ nguyên biến đổi chất:
1. **Kỷ nguyên Mẫu cấu trúc (Structural Pattern Recognition - SPR):** Kỷ nguyên sơ khai. Thuật toán cố gắng đo lường độ dài, đếm số đoạn thẳng, số độ cong cung tròn, hay các giao điểm chéo (ví dụ chữ X có 2 nét cắt chéo, chữ O là 1 hình oval khép kín). Phương pháp này chỉ chạy được trên font in máy móc cực kỳ chuẩn mực khô khan [30].
2. **Kỷ nguyên Học máy thống kê (Traditional Machine Learning):** Giai đoạn bùng nổ của các thuật toán trích xuất đặc trưng toán học nhân tạo HOG (Histogram of Oriented Gradients) hay SIFT. Đặc trưng vector số của chữ sẽ được đẩy vào các cỗ máy học thuần túy Support Vector Machines (SVMs) để lập mặt phẳng cắt phân loại đa chiều [30]. 
3. **Kỷ nguyên Học sâu End-to-End (Deep Learning OCR):** Cấu trúc mạng quy nạp toàn diện bằng cách tống thẳng ảnh nhiễu khổng lồ vào mạng nơ-ron Tích chập chắt lọc, đẩy qua Mạng hồi quy RNN/LSTM học chuỗi tuần tự, và xài hàm mất mát CTC (Connectionist Temporal Classification) [32] để không cần gán nhãn từng tọa độ chữ. Thành tựu lớn nhất là nhận diện thành công chữ viết tay bác sĩ, chữ trên biến báo giao thông bị mờ nhòe (Scene Text Recognition) — một khả năng viễn tưởng ở thập niên 90 [29].

#### b) Phân tách trường phái giải thuật: Context-free vs. Context-aware

Khi các mô hình học sâu OCR tiếp cận với ngôn ngữ của con người, một bức tường cản trở xuất hiện: Ảnh chụp quá xấu dẫn tới chữ "m" nhìn y hệt như tổ hợp của chữ "r" và "n" ghép lại. Để xử lý ranh giới mờ nhạt này, khoa học hiện đại chia đôi phương pháp:

**- Nhóm thuật toán Không nhận thức ngữ cảnh (Context-free OCR):**
Các mô hình loại này tuân thủ nguyên tắc khắc kỷ: Chữ nào nhìn giống cái gì thì đoán cái đó, hoàn toàn phớt lờ ý nghĩa từ vựng của cả đoạn văn bản. Công nghệ nền tảng của họ này là kiến trúc CNN + CTC. Đặc trưng của ảnh được trích xuất thẳng băng ra chuỗi. 
*Ưu điểm:* Cực kỳ nhẹ, tốc độ nhanh kinh hoàng, độ trễ gần bằng không. 
*Khuyết điểm:* Mù lòa khi một phần chữ bị vết ố dơ che khuất.

**- Nhóm thuật toán Nhận thức ngữ cảnh (Context-aware OCR):**
Đây là hướng đi của các mô hình hạng nặng tinh túy nhất thế giới (ví dụ mạng PARSeq [27], TrOCR, hay các hệ thống kết hợp Transformer Attention). Thuật toán không chỉ nhìn vào điểm ảnh của chữ đó, mà nó nhìn vào 3 chữ cái đứng đằng trước và 2 chữ cái đứng đằng sau, sau đó tra cứu TỪ ĐIỂN NGÔN NGỮ (Language Model) trong bộ não của nó để tự điền vào chỗ bị mất. Ví dụ: Máy chỉ nhìn mờ mờ thấy chữ "E - L - E - P - H - [mờ] - N - T", bằng vốn từ vựng khổng lồ, thuật toán tự động kết luận dứt khoát đó là chữ "A" để tạo thành từ con voi "ELEPHANT". 
Nhóm này thường có kiến trúc Encoder (đọc ảnh) lai ghép với Decoder (Sinh ngôn ngữ tự nhiên NLP). 

#### c) Lựa chọn chiến lược kiến trúc OCR chuyên biệt cho bài toán chấm thi

Trong đồ án này, dữ liệu hình ảnh của bài thi mang các đặc tính cực đoan rất độc đáo:
1. **Từ vựng bị đóng cứng ngặt nghèo:** Hệ thống không phải đọc các câu tiểu thuyết văn học đa dạng hàng chục ngàn từ, mà chỉ phải đọc một tệp nhãn đơn lẻ bị giới hạn tuyệt đối ở đúng 4 lớp phân loại: Mực khoanh đáp án **A**, **B**, **C**, hoặc **D**. Việc sử dụng các mô hình ngôn ngữ siêu nặng nề Transformer (Context-aware) để tìm ngữ cảnh cho chữ A đứng một mình cô đơn là sự lãng phí máy móc một cách ngớ ngẩn.
2. **Nhiễu cấu trúc dị biệt:** Các chữ cái A, B, C, D không hề đứng sạch sẽ phơi bày phông chữ, mà chúng bị bao trùm bọc nghẹt thở bởi muôn vàn các dạng nét mực đậm nhạt khoanh tròn của bút bi, bút chì, vẽ elip ngoằn ngoèo cắt chéo vào đùi chữ cái. Các bộ nhận diện phổ quát nổi tiếng (như Tesseract OCR, Google Cloud Vision) đều thất bại tủi nhục vì bị nét mực khoanh tròn đánh lừa cấu trúc quang học.

Đứng trước sự mâu thuẫn này, một chiến lược thu hẹp kiến trúc (Architecture Pruning) được định hình: **Xây dựng và huấn luyện lại từ đầu một mạng Nơ-ron Tích chập (CNN) phân loại đa lớp (Multi-class Classification) siêu tối giản siêu nhỏ gọn chỉ với 4 lớp nơ-ron xuất.**
Thay vì ép máy tính phải đọc hiểu mọi chữ cái Latinh, mạng lưới CNN này chỉ tập trung dồn sức càn quét phân tích các nếp gấp cuộn xoắn của các đường thẳng, nếp cong cục bộ để định vị được cốt lõi thân trụ của chữ A, B, C, D dưới lớp ngụy trang nhiễu hạt khổng lồ của hình vẽ nét khoanh elip từ người dùng thực tế. Việc tinh giảm mạng lưới mang lại kết quả ngoại hạng: Thời gian suy luận dự đoán cho một crop chữ đáp án tụt dốc xuống chỉ tính bằng milli-giây, cung cấp năng lực thông lượng xử lý đáp ứng bài toán thi cử hàng loạt (Batch Examination) mà vẫn duy trì độ chuẩn xác phân loại 4 lớp vượt trội.

#### b) Họ mô hình YOLO — # CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

## 3.1. Phân tích yêu cầu và Thiết kế kiến trúc tổng thể

### 3.1.1. Phân tích yêu cầu

Hệ thống chấm trắc nghiệm tự động được thiết kế nhằm giải quyết bài toán tự động hóa quy trình đánh giá kết quả học tập. Hệ thống cần đáp ứng các yêu cầu chức năng cốt lõi:
- **Quản lý dữ liệu người dùng và kỳ thi:** Hỗ trợ phân quyền người dùng (giáo viên, học sinh), tạo lập kỳ thi, cấu hình loại đề (phiếu chuẩn hoặc khoanh tự do), và nhập đáp án chuẩn (ground truth).
- **Thu thập và số hóa dữ liệu:** Tiếp nhận hình ảnh bài thi thông qua giao diện ứng dụng, hỗ trợ xử lý hàng loạt.
- **Xử lý hình ảnh và nhận dạng:** Khả năng gọi dịch vụ học máy để trích xuất thông tin từ ảnh chụp, bao gồm việc nắn chỉnh ảnh, phát hiện vùng chứa đáp án và nhận dạng ký tự.
- **Tính toán và xuất kết quả:** Ghép cặp đáp án, so sánh với đáp án chuẩn, tính toán điểm số và xuất kết quả dưới dạng bảng tính để tích hợp vào hệ thống quản lý điểm.

Về yêu cầu phi chức năng, hệ thống phải đảm bảo tính mở rộng (scalability) cao, khả năng đáp ứng thời gian thực (real-time processing) để thời gian chấm mỗi bài thi không vượt quá ngưỡng cho phép, và tính bảo mật toàn vẹn dữ liệu kết quả thi.

### 3.1.2. Thiết kế kiến trúc tổng thể

Để đáp ứng yêu cầu tính toán chuyên sâu của các mô hình học sâu và khả năng phục vụ nhiều người dùng đồng thời, hệ thống áp dụng kiến trúc hướng dịch vụ (Service-Oriented Architecture - SOA) kết hợp vi dịch vụ (Microservices):
- **Tầng ứng dụng khách (Client Tier):** Cung cấp giao diện tương tác đa nền tảng (Web và Mobile). Đóng vai trò thu thập dữ liệu ảnh và hiển thị kết quả trực quan.
- **Tầng dịch vụ cốt lõi (Core Backend Services):** Đóng vai trò là trung tâm điều phối, xử lý các logic nghiệp vụ như quản lý kỳ thi, định tuyến luồng dữ liệu hình ảnh, và tính toán điểm số dựa trên luật (rule-based grading). Kiến trúc tầng này được thiết kế theo mô hình Clean Architecture (Kiến trúc Sạch), phân tách rõ ràng giữa lớp miền (Domain) và cơ sở hạ tầng (Infrastructure).
- **Tầng dịch vụ Trí tuệ nhân tạo (AI Services):** Là một vi dịch vụ độc lập, chuyên biệt xử lý các khối lượng tính toán lớn liên quan đến thị giác máy tính và mạng nơ-ron nhân tạo. Tầng này nhận ảnh thô, thực hiện các pipeline nhận dạng và trả về kết quả số hóa dạng cấu trúc (JSON). Sự phân tách này cho phép hệ thống triển khai tầng AI trên các máy chủ trang bị GPU một cách linh hoạt mà không ảnh hưởng đến dịch vụ cốt lõi.

> **[Hình 3.1]** *Cần chèn: Sơ đồ kiến trúc tổng thể của hệ thống, thể hiện sự phân tách giữa Client, Core Backend, AI Service và Database.*

## 3.2. Thiết kế luồng xử lý OMR truyền thống (Phiếu mẫu chuẩn)

Luồng xử lý OMR (Optical Mark Recognition) truyền thống được thiết kế để áp dụng cho các phiếu trả lời có thiết kế định sẵn, sử dụng cấu trúc lưới cố định và các điểm neo tham chiếu (Fiducial Markers).

### 3.2.1. Nhận diện và Nắn chỉnh phối cảnh

Dữ liệu đầu vào của hệ thống thường là ảnh chụp từ thiết bị di động, chịu biến dạng phối cảnh do góc chụp không vuông góc. Để thiết lập lại không gian tọa độ chuẩn:
- Hệ thống quét và trích xuất các điểm neo ở bốn góc của phiếu bằng phương pháp phân tích đường viền (contour analysis) kết hợp các bộ lọc hình thái học.
- Dựa trên tọa độ bốn điểm này, ma trận biến đổi phối cảnh (Homography) được tính toán. Phép biến đổi này chiếu xạ các pixel từ mặt phẳng ảnh nghiêng về một mặt phẳng hai chiều chuẩn mực.
- Kết quả thu được là một hình ảnh đã được nắn chỉnh thẳng góc, đảm bảo tính nhất quán không gian với lưới tọa độ thiết kế ban đầu.

### 3.2.2. Tiền xử lý ảnh

Trước khi trích xuất thông tin, ảnh cần được tăng cường chất lượng để giảm thiểu sai số do môi trường ánh sáng:
- Chuyển đổi ảnh màu sang không gian ảnh xám cường độ (intensity grayscale).
- Áp dụng thuật toán cân bằng biểu đồ histogram thích nghi cục bộ (CLAHE) để triệt tiêu các vùng bị đổ bóng cục bộ, đồng đều hóa độ tương phản trên toàn mặt giấy.
- Sử dụng bộ lọc Gaussian để làm mượt ảnh, giảm thiểu nhiễu hạt sinh ra từ cảm biến camera.

### 3.2.3. Xây dựng và Hiệu chuẩn lưới

Dựa trên tọa độ thiết kế vật lý của phiếu trả lời, hệ thống sinh ra một lưới tọa độ lý thuyết gồm các vùng quan tâm (Region of Interest - ROI), mỗi vùng bao quanh một ô chọn đáp án (bong bóng). Tuy nhiên, do sai số trong quá trình in ấn và nắn chỉnh, lưới lý thuyết có thể bị lệch. 

Hệ thống sử dụng phép biến đổi Hough cho đường tròn (Hough Circle Transform) để dò tìm các tâm thực tế của ô tròn trên ảnh. Từ đó, mạng lưới ROI được tinh chỉnh cục bộ (calibration) để bao khít vị trí vùng tô thực tế, giảm thiểu hiện tượng lệch ô gây sai lệch nhận dạng.

### 3.2.4. Thuật toán Ngưỡng động và trích xuất đáp án

Quá trình phân tích đáp án được thực hiện bằng cách đo lường tỷ lệ phân bố pixel mực đen bên trong mỗi ROI:
- **Ngưỡng động thích nghi:** Mật độ mực tô khác nhau tùy thuộc vào loại bút (bút chì, bút bi). Hệ thống phân tích biểu đồ phân bố phân số lấp đầy (fill-ratio histogram) của tất cả các ô trong bài. Bằng cách tìm giá trị cực tiểu cục bộ giữa cụm ô trống và cụm ô đã tô, một ngưỡng phân biệt động (dynamic threshold) được xác định tự động.
- **Trích xuất logic:** Trong mỗi câu hỏi, các ROI được đối chiếu với ngưỡng động này. Thuật toán kiểm tra số lượng ô vượt ngưỡng để xử lý các ngoại lệ như bỏ trống (không có ô vượt ngưỡng) hoặc chọn nhiều đáp án (có trên một ô vượt ngưỡng).

> **[Hình 3.2]** *Cần chèn: Sơ đồ luồng thuật toán OMR truyền thống, từ ảnh thô, nắn chỉnh, lưới ROI đến trích xuất kết quả.*

## 3.3. Thiết kế luồng xử lý AI - YOLOv9 VÀ CNN (Khoanh tự do)

Với các bài kiểm tra được giáo viên in tự do không theo khuôn mẫu chuẩn, học sinh thường khoanh tròn ký tự đứng trước đáp án. Bài toán lúc này chuyển từ xác định vị trí cố định sang phát hiện đối tượng tự do (Object Detection) và nhận dạng văn bản (Text Recognition). Phương pháp được đề xuất gồm bốn giai đoạn chính.

### 3.3.1. Tiền xử lý và Nắn thẳng ảnh

Bài kiểm tra dạng khoanh tự do không có điểm neo (fiducial markers) ở các góc. Vì vậy, để nắn thẳng ảnh, hệ thống trích xuất thông tin định hướng từ văn bản:
- Thuật toán trích xuất biên (Edge Detection) kết hợp biến đổi Hough đường thẳng (Hough Line Transform) dò tìm các đường kẻ hoặc dòng chữ ngang trên giấy.
- Góc nghiêng trung vị của các đường này được tính toán để đại diện cho độ lệch của trang giấy.
- Phép biến đổi Affine được áp dụng để xoay ảnh ngược lại, đưa trang giấy về phương thẳng đứng, tạo tiền đề tối ưu cho việc trích xuất theo trục Y ở giai đoạn sau.

### 3.3.2. Phát hiện đối tượng bằng YOLOv9

- **Vùng câu hỏi (ques_id):** Vùng chứa số thứ tự câu hỏi (ví dụ: "Câu 1", "Câu 2",...).
- **Vùng đáp án đã chọn (selected_ans):** Vùng chứa ký tự đáp án đã được khoanh tròn.

Đầu ra là danh sách các hộp bao (bounding box) cho mỗi loại, bao gồm tọa độ $(x_1, y_1, x_2, y_2)$ và độ tin cậy (confidence). Cơ chế NMS tự động được áp dụng với ngưỡng IoU = 0,4 để loại bỏ các hộp bao trùng lặp.

### 3.3.3. Nhận dạng ký tự (OCR và CNN)

**a) Đọc số thứ tự câu hỏi:**

Với mỗi vùng câu hỏi, hệ thống cắt phần ảnh tương ứng và đưa vào EasyOCR để nhận dạng văn bản. Kết quả được lọc để trích xuất phần số (digits). Tuy nhiên, OCR không phải lúc nào cũng đạt độ chính xác cao do sự đa dạng về font chữ và chất lượng ảnh crop nhỏ.

**Thuật toán nội suy thông minh (Smart Interpolation):** Để khắc phục hạn chế của OCR, hệ thống khai thác tính tuần tự tự nhiên của số thứ tự câu hỏi (1, 2, 3,...). Các vùng câu hỏi được sắp xếp theo tọa độ Y từ trên xuống dưới. Nếu phát hiện giá trị nhảy cóc bất thường (ví dụ: 1, 2, rồi 8) hoặc OCR trả về kết quả rỗng, hệ thống tự động gán giá trị bằng số thứ tự tiếp theo hợp lý. Kỹ thuật này nâng độ chính xác đọc số câu từ khoảng 80–85% lên 93–95%.

**b) Nhận diện ký tự đáp án (A/B/C/D):**

Với mỗi vùng đáp án, hệ thống cắt phần ảnh tương ứng, chuyển sang hệ màu RGB, thu phóng về kích thước 40×40 pixel, chuẩn hóa giá trị pixel, rồi đưa vào mạng CNN để phân loại thành một trong bốn lớp (A, B, C, D).

### 3.3.4. Thuật toán ghép cặp (Matching)

**Mục tiêu:** Xác định mỗi vùng khoanh tròn (ans_box) thuộc câu hỏi nào (ques_box).

**Thuật toán ghép cặp toàn cục (Global Matching):**

Hệ thống sử dụng thuật toán ghép cặp dựa trên phân vùng không gian Y: (1) Sắp xếp các vùng câu hỏi theo tọa độ tâm Y tăng dần; (2) Sắp xếp các vùng đáp án theo tọa độ tâm Y tăng dần; (3) Mỗi câu hỏi "quản lý" một vùng Y từ tâm Y của nó (trừ biên dự phòng 15 pixel phía trên) đến tâm Y của câu hỏi tiếp theo; (4) Đáp án nào có tâm Y nằm trong vùng quản lý sẽ được ghép cho câu hỏi đó.

**Xử lý trường hợp đa dấu:** Sau bước ghép cặp, hệ thống kiểm tra số lượng đáp án cho mỗi câu hỏi. Nếu một câu có nhiều hơn một đáp án được ghép, tất cả đáp án của câu đó được đánh dấu là lỗi đa dấu (None).

**Xử lý đề thi nhiều trang (Batch Processing):** Đối với đề thi dài gồm nhiều trang, hệ thống xử lý YOLOv9 và OCR cho từng trang riêng biệt, sau đó cộng offset Y ảo cho mỗi trang để gộp tất cả vùng câu hỏi và đáp án vào không gian Y chung. Thuật toán ghép cặp toàn cục sau đó chạy trên toàn bộ dữ liệu đã gộp, cho phép hệ thống xử lý đề thi có số câu hỏi trải dài trên nhiều trang.

---

# CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ

## 4.1. Bộ dữ liệu thử nghiệm

### 4.1.1. Dữ liệu OMR truyền thống

Bộ dữ liệu OMR bao gồm khoảng 30–45 ảnh phiếu trả lời mẫu chuẩn (20–30 ảnh phiếu 50 câu và 10–15 ảnh phiếu 20 câu). Ảnh được chụp bằng camera điện thoại thông minh (12–48MP) trong điều kiện ánh sáng phòng bình thường, cho phép góc nghiêng ±15°. Bộ dữ liệu bao gồm các trường hợp đa dạng: bài tô rõ ràng, bài tô mờ (chì nhạt), bài tô nhiều đáp án, bài có vết xóa/tẩy.

### 4.1.2. Dữ liệu YOLOv9 + CNN

Bộ dữ liệu bao gồm khoảng 25–45 ảnh đề thi trắc nghiệm dạng khoanh tay thu thập từ các bài thi thực tế tại Việt Nam (Toán, Vật lý, Hóa học, Sinh học, Tiếng Anh). Đặc điểm đa dạng: khoanh bằng bút bi (xanh, đen) hoặc bút chì; nhiều font đề, layout và số câu hỏi khác nhau.

### 4.1.3. Dữ liệu huấn luyện CNN (OCR)

Bộ dữ liệu tổng hợp (synthetic dataset) được sinh tự động, gồm 4.800 ảnh (1.000 ảnh huấn luyện + 200 ảnh kiểm định cho mỗi lớp A, B, C, D). Quá trình sinh dữ liệu mô phỏng các điều kiện thực tế: nền xám ngẫu nhiên (mô phỏng giấy thi), chữ cái với font và kích thước đa dạng, hình elip bao quanh mô phỏng vết khoanh tay với màu sắc ngẫu nhiên (bút bi xanh, đen, bút chì xám), và áp dụng Gaussian Blur nhẹ mô phỏng ảnh chất lượng thấp.

## 4.2. Các chỉ số đánh giá

### 4.2.1. Độ chính xác mức câu hỏi (Question-level Accuracy)

$$\text{Question Accuracy} = \frac{\text{Số câu nhận diện đúng}}{\text{Tổng số câu}} \times 100\%$$

Một câu được coi là "đúng" khi: đáp án nhận diện khớp chính xác với đáp án thực tế (ground truth); câu bỏ trống được nhận diện đúng là trống (None = None); câu đa dấu được nhận diện đúng là đa dấu (None = None).

### 4.2.2. Độ chính xác mức bài thi (Sheet-level Accuracy)

$$\text{Sheet Accuracy} = \frac{\text{Số bài chấm hoàn toàn đúng}}{\text{Tổng số bài}} \times 100\%$$

Một bài được coi là "hoàn toàn đúng" khi tất cả câu hỏi trong bài đều được nhận diện chính xác (100% Question Accuracy).

### 4.2.3. Tốc độ xử lý

- **Thời gian xử lý (Processing Time):** Thời gian xử lý một ảnh, bao gồm tất cả các bước trong pipeline.
- **Thông lượng (Throughput):** Số bài thi xử lý được trong một phút.

## 4.3. Đánh giá OMR truyền thống (Dạng tô đen theo phiếu mẫu)

### 4.3.1. Kết quả thực nghiệm phiếu 50 câu

| Chỉ số | Kết quả |
|--------|---------|
| Độ chính xác mức câu hỏi | ≥ 95% |
| Độ chính xác mức bài thi | ~85–90% |
| Thời gian xử lý trung bình | ~0,5–1,0 giây/ảnh |
| Tỷ lệ phát hiện marker thành công | ~95% |
| Tỷ lệ phát hiện đa dấu chính xác | ~90% |

Hệ thống xử lý tốt các trường hợp: ảnh chụp chuẩn với ánh sáng đều, bài tô rõ ràng với mực đậm, bốn marker rõ ràng không bị che khuất. Các trường hợp gây sai sót bao gồm: bài tô mờ (chì nhạt) khiến fill ratio gần ngưỡng, bài có vết xóa/tẩy tạo fill ratio bất thường, marker bị che khuất hoặc cắt mất, và ánh sáng phân bố cực kỳ không đều.

### 4.3.2. Kết quả thực nghiệm phiếu 20 câu

| Chỉ số | Kết quả |
|--------|---------|
| Độ chính xác mức câu hỏi | ≥ 96% |
| Độ chính xác mức bài thi | ~90–93% |
| Thời gian xử lý trung bình | ~0,3–0,8 giây/ảnh |

Phiếu 20 câu cho kết quả tốt hơn so với phiếu 50 câu nhờ: số lượng bong bóng ít hơn (80 so với 200) giảm xác suất sai sót; bong bóng có kích thước lớn hơn giúp fill ratio phân biệt rõ ràng hơn; và thuật toán hiệu chuẩn HoughCircles hoạt động hiệu quả hơn với mật độ bong bóng thưa hơn.

### 4.3.3. Phân tích sai sót và giải pháp

| Loại sai sót | Tần suất | Nguyên nhân | Giải pháp đã áp dụng |
|-------------|----------|-------------|----------------------|
| False Empty (bỏ sót ô đã tô) | ~2% | Chì tô quá nhạt | Ngưỡng tô tự thích ứng |
| False Multi-mark (nhầm đa dấu) | ~1% | Vết xóa chưa sạch | Kiểm tra kết hợp tỷ lệ + ngưỡng tuyệt đối |
| Wrong Answer (nhận sai đáp án) | ~0,5% | Lỗi hiệu chuẩn lưới | HoughCircles với fallback về mẫu mặc định |
| Marker Not Found | ~5% | Marker bị che khuất | Fallback bằng phát hiện biên Canny |

## 4.4. Đánh giá YOLOv9 + CNN (Dạng khoanh tròn)

### 4.4.1. Kết quả thực nghiệm

| Chỉ số | Kết quả |
|--------|---------|
| YOLOv9 Detection — vùng câu hỏi (ques_id) | ~90–95% (mAP@0.5) |
| YOLOv9 Detection — vùng đáp án (selected_ans) | ~88–93% (mAP@0.5) |
| CNN OCR Accuracy (A/B/C/D) | ~92–96% |
| EasyOCR Question ID Accuracy (raw) | ~80–85% |
| EasyOCR Question ID Accuracy (với Smart Interpolation) | ~93–95% |
| Độ chính xác end-to-end mức câu hỏi | ~85–90% |
| Thời gian xử lý trung bình | ~2–4 giây/ảnh |

### 4.4.2. Phân tích hiệu năng từng thành phần

**a) YOLOv9 Object Detection:** Mô hình hoạt động hiệu quả trên các đề thi in rõ ràng với font chuẩn. Sai sót xảy ra khi: đề thi photocopy mờ, chữ viết tay thay vì in, hoặc layout đặc biệt (đề chia ba cột thay vì hai). Ngưỡng confidence thấp (0,2) giúp giảm tỷ lệ bỏ sót nhưng làm tăng nhẹ tỷ lệ dương tính giả — được kiểm soát bởi NMS.

**b) EasyOCR:** Độ chính xác thô khoảng 80–85% do sự đa dạng font đề thi và kích thước ảnh crop nhỏ. Thuật toán Smart Interpolation khai thác tính tuần tự của số câu hỏi, nâng độ chính xác lên 93–95%. Tuy nhiên, vẫn còn sai sót khi câu hỏi bắt đầu từ số lớn (31–50) hoặc font trang trí.

**c) CNN OCR:** Đạt độ chính xác 92–96% trên tập test. Hoạt động tốt nhất với khoanh bút bi đậm. Sai sót khi: khoanh quá nhẹ/mờ, khoanh bằng bút highlight, hoặc có vết bẩn trên giấy.

**d) Thuật toán Matching:** Hoạt động hiệu quả khi câu hỏi và đáp án nằm trên cùng hàng ngang. Sai sót khi layout đề thi phức tạp (đáp án ở xa câu hỏi) hoặc đề chia nhiều cột.

### 4.4.3. So sánh hai phương pháp

| Tiêu chí | OMR Truyền thống | YOLOv9 + CNN |
|----------|-------------------|--------------|
| Độ chính xác | ≥ 95% | 85–90% |
| Tốc độ xử lý | 0,3–1,0 giây/ảnh | 2–4 giây/ảnh |
| Yêu cầu đầu vào | Phiếu mẫu chuẩn có Fiducial Marker | Bất kỳ đề thi dạng khoanh tay |
| Sử dụng Học sâu | Không | Có (YOLOv9 + CNN + OCR) |
| Kích thước mô hình | 0 MB | ~52 MB (YOLOv9) + ~1 MB (CNN) |
| Yêu cầu GPU | Không | Không bắt buộc (hỗ trợ GPU) |
| Xử lý nhiều trang | Không | Có (batch processing) |
| Phát hiện đa dấu | Có (dựa trên histogram) | Có (đếm số lượng) |

## 4.5. Hiện thực hóa hệ thống và Phát triển Web thực tế

### 4.5.1. Công nghệ sử dụng

**a) Backend (Java Spring Boot):**

Hệ thống backend được xây dựng trên nền tảng Java 21, Spring Boot 3.3.5. Các thành phần chính bao gồm: Spring Security cho xác thực và phân quyền, Spring Data JPA cho tầng truy cập dữ liệu, Spring Cloud OpenFeign cho giao tiếp với dịch vụ AI, PostgreSQL làm hệ quản trị cơ sở dữ liệu quan hệ, Flyway cho quản lý phiên bản cơ sở dữ liệu, MapStruct cho ánh xạ đối tượng, và SpringDoc OpenAPI cho tài liệu API tự động.

**b) Frontend (React TypeScript):**

Giao diện người dùng được xây dựng bằng React 19 kết hợp TypeScript, sử dụng Vite làm công cụ build. Thư viện thành phần giao diện Ant Design đảm bảo tính nhất quán và chuyên nghiệp. Quản lý trạng thái server-side bằng TanStack Query (React Query), quản lý trạng thái client-side bằng Zustand. Giao tiếp HTTP với backend thông qua Axios.

**c) Dịch vụ AI (Python FastAPI):**

Dịch vụ AI được xây dựng bằng Python 3.12, sử dụng framework FastAPI với máy chủ ASGI Uvicorn. Các thư viện chính bao gồm: OpenCV cho xử lý ảnh, PyTorch cho Học sâu, Ultralytics cho YOLOv9, EasyOCR cho nhận dạng văn bản, NumPy cho tính toán số học, và SciPy cho phân tích histogram.

### 4.5.2. Giao diện người dùng

Hệ thống cung cấp giao diện Web hiện đại với các trang chính:

- **Đăng nhập / Đăng ký:** Form xác thực với JWT, hỗ trợ phân quyền Admin, Teacher, Student. Mật khẩu được mã hóa BCrypt.
- **Dashboard:** Tổng quan nhanh về số lượng kỳ thi, sinh viên và bài đã chấm.
- **Quản lý Kỳ thi:** Danh sách kỳ thi dạng bảng, hỗ trợ CRUD, cấu hình loại đề (OMR_20, OMR_50, YOLO) và nhập đáp án chuẩn.
- **Chi tiết Kỳ thi:** Danh sách sinh viên với trạng thái chấm điểm, giao diện upload ảnh hỗ trợ kéo thả (drag-and-drop), xem trước ảnh thumbnail, sắp xếp thứ tự trang, hiển thị kết quả dưới dạng bảng đối chiếu đáp án chi tiết.
- **Quản lý Sinh viên:** CRUD thông tin sinh viên, hỗ trợ import danh sách từ tệp Excel.
- **Kết quả:** Bảng kết quả chính thức, tìm kiếm theo tên sinh viên hoặc tên kỳ thi, nút xuất điểm sang tệp Excel.

### 4.5.3. Bảo mật hệ thống

**a) Xác thực (Authentication):** Sử dụng JWT (JSON Web Token) với thuật toán ký HMAC-SHA256. Token chứa thông tin: tên người dùng, vai trò, thời điểm phát hành và thời hạn hết hạn. Token được gửi kèm trong header HTTP Authorization.

**b) Phân quyền (Authorization):** Hệ thống áp dụng mô hình phân quyền dựa trên vai trò (Role-Based Access Control — RBAC) với ba vai trò: ADMIN (toàn quyền), TEACHER (quản lý kỳ thi, sinh viên, chấm điểm) và STUDENT (xem kết quả).

**c) Bảo mật mật khẩu:** Mật khẩu được mã hóa bằng thuật toán BCrypt (10 vòng lặp mặc định) trước khi lưu vào cơ sở dữ liệu, đảm bảo không lưu trữ mật khẩu dạng văn bản rõ.

### 4.5.4. Triển khai hệ thống

- **Dịch vụ AI:** Được đóng gói bằng Docker container dựa trên Python 3.12, cài đặt PyTorch phiên bản CPU và các thư viện phụ thuộc, chạy trên cổng 8000.
- **Backend:** Đóng gói dưới dạng Spring Boot JAR, chạy trên Java 21.
- **Frontend:** Build bằng Vite thành tệp tĩnh (static files), phục vụ qua Nginx hoặc Spring Boot static resource handler.

---

# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## Đóng góp của đề tài

Đồ án đã xây dựng thành công hệ thống chấm điểm trắc nghiệm tự động CODEX với các đóng góp chính:

1. **Hai pipeline xử lý song song:**
   - Pipeline OMR truyền thống sử dụng Fiducial Marker, biến đổi phối cảnh, CLAHE, phân ngưỡng thích nghi và ngưỡng tô tự thích ứng, đạt độ chính xác ≥ 95% trên phiếu mẫu chuẩn.
   - Pipeline AI kết hợp YOLOv9, EasyOCR, CNN tùy chỉnh và thuật toán ghép cặp phân vùng Y, đạt độ chính xác 85–90% trên đề thi dạng khoanh tay.

2. **Thuật toán ngưỡng tô tự động (Adaptive Fill Threshold):** Phân tích histogram fill ratio để tìm điểm valley giữa hai đỉnh phân phối (ô trống và ô đã tô), tự động điều chỉnh ngưỡng theo điều kiện ảnh cụ thể, loại bỏ hoàn toàn việc tinh chỉnh ngưỡng thủ công.

3. **Thuật toán nội suy thông minh (Smart Interpolation) cho OCR:** Khai thác tính tuần tự của số thứ tự câu hỏi để phát hiện và sửa lỗi OCR, nâng độ chính xác đọc số câu từ khoảng 80% lên khoảng 95%.

4. **Hệ thống Web hoàn chỉnh:** Backend Spring Boot theo kiến trúc Hexagonal, frontend React với giao diện hiện đại, tích hợp end-to-end từ tải ảnh đến hiển thị kết quả chấm điểm.

5. **Xử lý hàng loạt (Batch Processing):** Hỗ trợ đề thi nhiều trang thông qua kỹ thuật xếp chồng Y ảo (Y-offset virtual stacking), cho phép chấm điểm hoàn chỉnh các đề thi dài.

## Hạn chế hiện tại

1. Chỉ hỗ trợ bốn lựa chọn (A–D), chưa mở rộng cho năm lựa chọn (A–E).
2. Chưa nhận dạng tự động mã đề và số báo danh trên phiếu tô.
3. Hiệu năng phụ thuộc vào chất lượng ảnh đầu vào: ảnh quá mờ, nghiêng trên 15° hoặc bị che phần marker có thể gây sai sót.
4. Bộ dữ liệu huấn luyện CNN (4.800 ảnh tổng hợp) có quy mô nhỏ, chưa bao phủ đầy đủ các trường hợp thực tế.
5. Chưa triển khai cơ chế trả kết quả thời gian thực qua WebSocket.
6. Chưa thiết lập pipeline CI/CD tự động cho quy trình build, test và deploy.

## Hướng phát triển

1. **Mở rộng OMR:** Hỗ trợ phiếu năm lựa chọn (A–E); nhận diện tự động mã đề và số báo danh; hỗ trợ đa dạng mẫu phiếu trả lời.

2. **Nâng cấp thành phần AI:** Huấn luyện YOLOv9 trên bộ dữ liệu quy mô lớn và đa dạng hơn; thay thế EasyOCR bằng mô hình OCR chuyên biệt (PaddleOCR, TrOCR); huấn luyện CNN trên dữ liệu thực (không chỉ synthetic).

3. **Cải thiện trải nghiệm người dùng:** Tích hợp WebSocket cho kết quả thời gian thực; phát triển Progressive Web App (PWA) cho thiết bị di động; chụp ảnh trực tiếp từ camera trên Web; bổ sung dashboard phân tích thống kê (phân phối điểm, câu hỏi khó, phân tích sai sót).

4. **Mở rộng hạ tầng:** Sử dụng hàng đợi thông điệp (Redis/Kafka) cho xử lý bất đồng bộ; triển khai GPU inference server cho dịch vụ AI; sử dụng lưu trữ đối tượng (MinIO/S3) cho ảnh bài thi; triển khai trên Kubernetes để đảm bảo tính sẵn sàng cao.

5. **Tích hợp hệ thống quản lý học tập (LMS):** Xây dựng API tích hợp với Moodle, Google Classroom; hỗ trợ xuất kết quả theo chuẩn LTI (Learning Tools Interoperability).

---

# TÀI LIỆU THAM KHẢO

[1] R. C. Gonzalez and R. E. Woods, *Digital Image Processing*, 4th ed. Pearson, 2018.

[2] I. Goodfellow, Y. Bengio, and A. Courville, *Deep Learning*. MIT Press, 2016.

[3] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, "You Only Look Once: Unified, Real-Time Object Detection," in *Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)*, 2016, pp. 779–788.

[4] A. Paszke et al., "PyTorch: An Imperative Style, High-Performance Deep Learning Library," in *Adv. Neural Inf. Process. Syst. (NeurIPS)*, 2019, vol. 32.

[5] N. Otsu, "A Threshold Selection Method from Gray-Level Histograms," *IEEE Trans. Syst. Man Cybern.*, vol. 9, no. 1, pp. 62–66, Jan. 1979.

[6] K. Zuiderveld, "Contrast Limited Adaptive Histogram Equalization," in *Graphics Gems IV*, P. S. Heckbert, Ed. Academic Press, 1994, pp. 474–485.

[7] R. Hartley and A. Zisserman, *Multiple View Geometry in Computer Vision*, 2nd ed. Cambridge University Press, 2003.

[8] S. Tiramisu, "EasyOCR: Ready-to-use OCR with 80+ Languages Supported," 2020. [Online]. Available: https://github.com/JaidedAI/EasyOCR

[9] OpenCV Team, "OpenCV Documentation," 2024. [Online]. Available: https://docs.opencv.org/

[10] Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, "Gradient-Based Learning Applied to Document Recognition," *Proc. IEEE*, vol. 86, no. 11, pp. 2278–2324, Nov. 1998.

[11] Spring Team, "Spring Boot Reference Documentation," 2024. [Online]. Available: https://docs.spring.io/spring-boot/

[12] A. Cockburn, "Hexagonal Architecture (Ports and Adapters)," 2005. [Online]. Available: https://alistair.cockburn.us/hexagonal-architecture/

[13] React Team, "React Documentation," 2024. [Online]. Available: https://react.dev/

[14] D. P. Kingma and J. Ba, "Adam: A Method for Stochastic Optimization," in *Proc. Int. Conf. Learn. Represent. (ICLR)*, 2015.

[15] FastAPI, "FastAPI Documentation," 2024. [Online]. Available: https://fastapi.tiangolo.com/

[16] J. Canny, "A Computational Approach to Edge Detection," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. PAMI-8, no. 6, pp. 679–698, Nov. 1986.

[17] P. V. C. Hough, "Method and Means for Recognizing Complex Patterns," U.S. Patent 3 069 654, Dec. 18, 1962.

[18] TanStack, "TanStack Query (React Query) Documentation," 2024. [Online]. Available: https://tanstack.com/query/

[19] Ant Design Team, "Ant Design Documentation," 2024. [Online]. Available: https://ant.design/

[20] PostgreSQL Global Development Group, "PostgreSQL Documentation," 2024. [Online]. Available: https://www.postgresql.org/docs/

[21] Ultralytics, "Ultralytics Documentation," 2024. [Online]. Available: https://docs.ultralytics.com/

[22] B. Bochkovskiy, C.-Y. Wang, and H.-Y. M. Liao, "YOLOv4: Optimal Speed and Accuracy of Object Detection," *arXiv preprint arXiv:2004.10934*, 2020.

[23] C.-Y. Wang, I.-H. Yeh, and H.-Y. M. Liao, "YOLOv9: Learning What You Want to Learn Using Programmable Gradient Information," *arXiv preprint arXiv:2402.13616*, 2024.

[24] C.-Y. Wang, H.-Y. M. Liao, Y.-H. Wu, P.-Y. Chen, J.-W. Hsieh, and I.-H. Yeh, "CSPNet: A New Backbone that can Enhance Learning Capability of CNN," in *Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)*, 2020.

[25] C.-Y. Wang, H.-Y. M. Liao, and I.-H. Yeh, "Designing Network Design Strategies Through Gradient Path Analysis," *arXiv preprint arXiv:2211.04800*, 2022.

[26] R. Smith, "An Overview of the Tesseract OCR Engine," in *Proc. Int. Conf. Document Anal. Recognit. (ICDAR)*, 2007.

[27] D. Bautista and R. Atienza, "Scene Text Recognition with Permuted Autoregressive Sequence Models," in *Proc. European Conf. Comput. Vis. (ECCV)*, 2022.

[43] Bộ Giáo dục và Đào tạo, "Quy chế thi THPT Quốc gia," 2017.

[44] Scantron Corporation, "OMR Scanner Documentation," 2020.

[45] Azota, "Ứng dụng chấm thi trắc nghiệm Azota," 2023.

[46] TNMaker, "Phần mềm tạo đề thi và chấm điểm trắc nghiệm," 2023.

---

# PHỤ LỤC

## Phụ lục A: Cấu trúc thư mục dự án

```
DA/
├── codex-backend/               # Java Spring Boot Backend
│   ├── pom.xml                  # Maven dependencies
│   └── src/main/java/com/codex/backend/
│       ├── auth/                # Module xác thực
│       ├── exam/                # Module quản lý kỳ thi
│       ├── student/             # Module quản lý sinh viên
│       ├── submission/          # Module nộp bài & gọi AI
│       ├── grading/             # Module chấm điểm
│       ├── result/              # Module kết quả
│       └── common/              # Module dùng chung
│
├── codex-frontend/              # React TypeScript Frontend
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx              # Root component + routing
│       ├── api/                 # API resource layer
│       ├── store/               # State management
│       └── features/            # Feature modules
│
├── Ocr/                         # Python AI Service
│   ├── app.py                   # FastAPI entry point
│   ├── Dockerfile
│   ├── core/                    # OMR Engine
│   ├── yolo_pipeline.py         # YOLOv9 Pipeline
│   ├── models/                  # Pre-trained models
│   └── training/                # Training scripts
│
└── Docs/                        # Project documentation
```

## Phụ lục B: Ví dụ JSON kết quả chấm điểm

**OMR truyền thống (50 câu):**
```json
{
  "1": "A",
  "2": "B",
  "3": "C",
  "4": null,
  "5": "D",
  "...": "...",
  "49": "B",
  "50": "C"
}
```
- Giá trị `null` biểu thị câu trống (chưa tô) hoặc câu đa dấu (tô nhiều đáp án).

**YOLOv9 + CNN (khoanh tay):**
```json
{
  "1": "A",
  "2": "C",
  "3": null,
  "5": "B",
  "7": "D"
}
```
- Các câu không xuất hiện (4, 6) cho biết YOLOv9 không phát hiện được đáp án cho câu đó.
- Giá trị `null` biểu thị phát hiện đa dấu (khoanh hai đáp án cho cùng một câu).

## Phụ lục C: Thuật toán tính điểm

Điểm số được tính theo công thức:

$$\text{Score} = \frac{\text{correctCount} \times 10}{\text{totalQuestions}}$$

trong đó correctCount là số câu mà đáp án nhận diện khớp chính xác với đáp án chuẩn, và totalQuestions là tổng số câu hỏi trong đề thi. Kết quả được làm tròn đến hai chữ số thập phân.

**Ví dụ:** Đề 50 câu, nhận diện đúng 42 câu → Điểm = 42 × 10 / 50 = 8,40.
