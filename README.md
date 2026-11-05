✨ 1. Tính Năng Nổi Bật
- Tích hợp đa phương pháp nhận diện : Hệ thống hỗ trợ song song hai luồng xử lý: phương pháp quang học sử dụng điểm chuẩn góc và phương pháp phát hiện đối tượng sử dụng AI bằng mô hình YOLOv9.   
- Tiền xử lý ảnh chống nhiễu mạnh mẽ: Xử lý hiệu quả ảnh chụp từ điện thoại bị thiếu sáng hoặc bóng đổ nhờ kết hợp cân bằng biểu đồ CLAHE, phân ngưỡng thích nghi và các phép toán hình thái học. Hệ thống cũng tự động đo góc nghiêng và xoay phẳng ảnh bằng thuật toán HoughLinesP trước khi nhận diện.   
- Hiệu chuẩn lưới tọa độ động: Thay vì dùng khung cứng, hệ thống sử dụng thuật toán HoughCircles kết hợp gom cụm để tự động dò tìm vị trí các ô điền đáp án thực tế. Điều này giúp tinh chỉnh chính xác tọa độ X của cột và Y của hàng ngay cả khi giấy in bị lệch.   
 -Ngưỡng điền đầy thích nghi: Hệ thống tự động phân tích biểu đồ tỷ lệ pixel bị tô đen của các ô tròn để tìm đáy thung lũng  giữa các đỉnh. Dựa vào đó, ngưỡng để xác định ô nào "được tô" hay "bỏ trống" được thiết lập linh hoạt theo từng ảnh cụ thể, thay vì cố định một mức duy nhất.   
- Cảnh báo và xử lý ngoại lệ: Khả năng phát hiện lỗi tô nhiều đáp án bằng cách so sánh tỷ lệ độ mờ giữa ô tô đậm nhất và ô tô mờ thứ hai. Hệ thống sẽ gán kết quả là vô hiệu (None) nếu phát hiện tình trạng tô hai đáp án hoặc số lượng đáp án trùng lặp cho cùng một câu hỏi.

🏗️ 2. Kiến Trúc Hệ Thống 
- Core Computer Vision Engine (Nhận diện truyền thống): Được cấu trúc bởi lớp FiducialMarkerDetector để tìm 4 điểm đánh dấu hình vuông ở góc và biến đổi không gian ảnh. Lớp GridAutoCalibrator phụ trách định hình lại lưới bong bóng, trong khi FiducialOMRDetector trực tiếp đo lường tỷ lệ điền đầy của các ô.   
- Deep Learning Engine (Nhận diện bằng AI): Nằm trong module YOLOPipeline xử lý ảnh hoàn toàn độc lập. Phân hệ này sử dụng mô hình YOLOv9 để trích xuất phân vùng câu hỏi/đáp án, thư viện EasyOCR để đọc số thứ tự câu hỏi, và một mạng học sâu PyTorch tùy chỉnh để phân loại chữ cái A, B, C, D.   
- Backend & API Routing (FastAPI): Triển khai trong tệp app.py, chịu trách nhiệm phơi bày các API endpoint (/predict, /grade) hỗ trợ gửi ảnh lên để nhận diện đơn lẻ hoặc xử lý hàng loạt. Module này dùng Pydantic (AnswerKey) để cấu trúc hóa và kiểm tra tính hợp lệ của đáp án chuẩn.  
- Web Dashboard (Flask): Ứng dụng giao diện Web được đặt trong web_server.py. Phân hệ này quản lý luồng người dùng tạo phiếu, tải ảnh lên giao diện, tự động dọn dẹp các tệp ảnh/json cũ, và render bảng phân tích chi tiết kết quả đúng/sai ra màn hình.

🧠 3. Luồng Xử Lý Dữ Liệu và Trí Tuệ Nhân Tạo 
Hệ thống cho phép người dùng hoặc hệ thống gọi đến một trong hai luồng xử lý độc lập:
- Luồng 1: Xử lý Quang học OMR Dựa Trên Khuôn Mẫu
    Dò tìm điểm chuẩn: Ảnh đầu vào được chuyển sang ảnh xám, áp dụng bộ lọc CLAHE và phân ngưỡng Otsu để quét tìm 4 khối đen đạt chuẩn về diện tích và độ đặc ở 4 góc.   
    Biến đổi phối cảnh: Từ 4 tọa độ tìm được, hệ thống áp dụng biến đổi ma trận để kéo dãn, sửa méo và chuẩn hóa kích thước ảnh về một tỷ lệ phẳng duy nhất.   
    Hiệu chuẩn và trích xuất: Tọa độ mẫu của 50 câu hỏi được ánh xạ lên ảnh. Thuật toán HoughCircles tìm lại tâm thực tế của các bọt bong bóng. Hệ thống đếm lượng pixel trắng trong mặt nạ hình tròn tại các tọa độ này.   
    Phân loại ngưỡng: Thuật toán xác định một ngưỡng phân chia thích nghi dựa trên biểu đồ phân bố pixel, sau đó gán nhãn A, B, C, D cho ô có mật độ pixel cao nhất vượt qua ngưỡng.   
- Luồng 2: Xử lý Học Sâu (YOLO + CNN Pipeline)
    Cân chỉnh không gian: Hình ảnh đầu vào được nhận diện cạnh bằng Canny và HoughLinesP để tìm góc nghiêng, sau đó tự động xoay phẳng.   
    Trích xuất vùng hiển thị: Ảnh xoay phẳng chạy qua mô hình YOLOv9 để xuất ra các hộp giới hạn của ID câu hỏi và đáp án người dùng khoanh.   
    Nhận dạng ký tự:
        + Các hộp chứa ID câu hỏi được cắt và nạp qua EasyOCR để đọc văn bản và trích xuất ra số thứ tự nguyên.   
        + Các hộp khoanh đáp án được cắt, chuyển thành tensor có kích thước 40x40, và đẩy qua mạng CNN SimpleOCR_CNN để mô hình dự đoán ra chữ cái tương ứng.   
    Hậu xử lý và Ghép nối: Do YOLO nhận diện rời rạc, hệ thống tính toán tọa độ TÂM của từng khu vực. Hệ thống sẽ duyệt dọc theo trục Y để ghép đúng cặp "Số thứ tự câu hỏi" với "Chữ cái đáp án" tương ứng nằm trên cùng một hàng không gian, sau đó kết xuất kết quả. Dữ liệu nhận diện hoàn chỉnh được gửi về app.py hoặc web_server.py để đối chiếu với đáp án chuẩn và tính điểm.   
