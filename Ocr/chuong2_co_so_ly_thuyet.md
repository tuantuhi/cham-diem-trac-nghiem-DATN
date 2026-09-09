# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

Chương này trình bày các nền tảng lý thuyết cốt lõi làm cơ sở khoa học cho việc xây dựng hệ thống chấm điểm trắc nghiệm tự động. Nội dung được tổ chức theo hai trụ cột chính: (1) lý thuyết xử lý ảnh số và thị giác máy tính truyền thống, vốn là nền tảng của pipeline nhận diện phiếu tô bong bóng; và (2) các lý thuyết học sâu hiện đại, bao gồm mạng nơ-ron tích chập, mô hình phát hiện đối tượng YOLO và nhận dạng ký tự quang học, làm cơ sở cho pipeline xử lý bài thi dạng khoanh tròn tự do. Ngoài ra, chương cũng khái quát các công nghệ phần mềm được sử dụng để xây dựng hệ thống ứng dụng web hoàn chỉnh.

---

## 2.1. Xử lý ảnh số và Thị giác máy tính (Computer Vision)

### 2.1.1. Tổng quan về xử lý ảnh số

Xử lý ảnh số (Digital Image Processing) là một ngành khoa học liên ngành tập trung vào việc áp dụng các phép toán và thuật toán lên các biểu diễn số của hình ảnh nhằm cải thiện chất lượng ảnh hoặc trích xuất thông tin hữu ích từ đó. Về bản chất toán học, một hình ảnh kỹ thuật số được biểu diễn dưới dạng một ma trận hai chiều $I(x, y)$, trong đó $x$ và $y$ là hệ tọa độ không gian rời rạc và $I$ là giá trị cường độ sáng (hoặc màu sắc) tại từng phần tử ảnh (pixel). Đối với ảnh màu theo mô hình RGB, mỗi pixel được biểu diễn bởi một bộ ba giá trị cường độ tương ứng với ba kênh màu Đỏ, Lục và Lam, trong khi ảnh xám (Grayscale) chỉ sử dụng một kênh cường độ duy nhất.

Thị giác máy tính (Computer Vision) là lĩnh vực rộng hơn, đặt mục tiêu xây dựng các hệ thống tự động có khả năng "hiểu" và suy luận về thế giới thực thông qua dữ liệu hình ảnh — mô phỏng khả năng tri giác thị giác của con người. Xử lý ảnh số là nền tảng kỹ thuật của thị giác máy tính, cung cấp các công cụ tiền xử lý, lọc nhiễu, phát hiện đặc trưng và phân tích cấu trúc không gian.

Các phép biến đổi trên ảnh số thường được phân loại thành bốn nhóm chính. Biến đổi điểm (Point Operations) tác động lên từng pixel một cách độc lập, chỉ phụ thuộc vào giá trị của chính pixel đó — ví dụ như điều chỉnh độ sáng, tương phản hay phép nhị phân hóa. Biến đổi cục bộ (Local/Neighborhood Operations) xác định giá trị đầu ra của một pixel dựa trên sự tổ hợp các pixel lân cận trong một vùng cửa sổ nhỏ (kernel), tạo thành cơ sở của các bộ lọc như làm mờ Gaussian hay phát hiện biên Sobel. Biến đổi toàn cục (Global Operations) phân tích đặc trưng phân bố thống kê của toàn bộ ảnh, điển hình là các thuật toán cân bằng histogram hay phân ngưỡng Otsu. Cuối cùng, biến đổi hình học (Geometric Operations) thao tác trên lưới tọa độ pixel để dịch chuyển, xoay, co giãn hay hiệu chỉnh phối cảnh ảnh.

### 2.1.2. Chuyển đổi phối cảnh và điểm đánh dấu tham chiếu (Fiducial Marker)

Trong điều kiện chụp ảnh thực tế bằng camera điện thoại, tờ giấy thi hiếm khi nằm vuông góc hoàn hảo với trục quang học của thiết bị. Góc nghiêng giữa mặt phẳng giấy và cảm biến ảnh tạo ra hiện tượng biến dạng phối cảnh (Perspective Distortion), khiến các đường thẳng song song hội tụ về điểm ảo và các hình chữ nhật bị biến dạng thành tứ giác bất kỳ. Đây là vấn đề nghiêm trọng đối với các thuật toán nhận diện phiếu tô bong bóng, vốn phụ thuộc vào các tọa độ tĩnh đã được định sẵn theo khuôn mẫu.

Giải pháp cho bài toán này là sử dụng các điểm đánh dấu tham chiếu (Fiducial Marker) được in tại các vị trí đã biết trước trên phiếu trả lời, đóng vai trò như những neo tọa độ để hệ thống tính toán phép biến đổi hình học ngược. Từ tọa độ thực tế của bốn điểm tham chiếu này trong ảnh chụp, hệ thống có thể xác định ma trận phép chiếu phối cảnh (Homography Matrix) $\mathbf{H}$, là ma trận $3 \times 3$ mô tả phép ánh xạ tuyến tính projective giữa hai mặt phẳng. Toán học cho thấy để xác định duy nhất ma trận homography có 8 bậc tự do, hệ thống cần tối thiểu bốn cặp điểm tương ứng không thẳng hàng — chính xác là số lượng điểm góc của phiếu trả lời.

Sau khi tính toán được ma trận $\mathbf{H}$, thuật toán biến đổi ngược phối cảnh (Inverse Perspective Warping) áp dụng phép chiếu lên toàn bộ ảnh, tạo ra hình ảnh tờ giấy được nắn thẳng phẳng với kích thước và tỷ lệ chuẩn mực, bất kể góc chụp ban đầu. Đây là bước tiền xử lý thiết yếu giúp các bước nhận diện tiếp theo hoạt động chính xác và ổn định.

### 2.1.3. Cân bằng histogram thích nghi có giới hạn tương phản (CLAHE)

Một thách thức phổ biến khác trong ảnh chụp ngoài môi trường thực tế là sự phân bố độ chiếu sáng không đồng đều trên bề mặt ảnh. Hiện tượng bóng đổ từ người chụp, ánh sáng tự nhiên từ cửa sổ hay đèn chiếu lệch tâm tạo ra những vùng cục bộ quá sáng hoặc quá tối. Trong những điều kiện này, các thuật toán phân ngưỡng tĩnh (áp dụng một giá trị ngưỡng chung cho toàn bộ ảnh) sẽ thất bại vì một ô bong bóng chưa tô ở vùng tối có thể có cường độ pixel tương đương với một ô đã tô ở vùng sáng.

Kỹ thuật cân bằng histogram toàn cục (Global Histogram Equalization) là một giải pháp kinh điển nhằm gia tăng độ tương phản tổng thể của ảnh, nhưng lại tồn tại nhược điểm lớn: bằng cách xử lý tất cả pixel theo một thống kê chung, nó có thể khuếch đại nhiễu ở các vùng đồng đều và làm mất chi tiết ở các vùng quá sáng hoặc quá tối.

Thuật toán CLAHE (Contrast Limited Adaptive Histogram Equalization) khắc phục hạn chế này thông qua hai cải tiến quan trọng. Thứ nhất, thay vì xử lý cả ảnh, CLAHE chia bức ảnh thành một lưới các vùng nhỏ (tiles) và tính toán phép cân bằng histogram độc lập cho từng vùng — đây là ý nghĩa của từ "Adaptive" (thích nghi). Thứ hai, CLAHE áp đặt một giới hạn tương phản (Clip Limit) để ngăn chặn sự khuếch đại nhiễu quá mức: các thanh histogram vượt quá ngưỡng cắt sẽ bị phân phối lại đều cho các mức xám khác. Cuối cùng, để tránh hiệu ứng ranh giới gắt giữa các vùng tiles liền kề, phép nội suy song tuyến tính (Bilinear Interpolation) được áp dụng để tạo ra chuyển tiếp độ sáng mượt mà. Kết quả là ảnh có độ tương phản cục bộ được cải thiện đồng đều trên toàn bề mặt, tạo điều kiện thuận lợi cho các bước phân ngưỡng tiếp theo.

### 2.1.4. Phân ngưỡng ảnh (Thresholding)

Phân ngưỡng (Thresholding) là kỹ thuật chuyển đổi ảnh mức xám thành ảnh nhị phân đen-trắng bằng cách so sánh giá trị của từng pixel với một giá trị ngưỡng $T$. Các pixel có giá trị vượt ngưỡng được phân vào một lớp (thường là nền trắng), còn lại thuộc lớp kia (đối tượng đen). Bài toán cốt lõi là xác định ngưỡng $T$ tối ưu một cách tự động.

Thuật toán phân ngưỡng Otsu, công bố năm 1979 bởi Nobuyuki Otsu, giải quyết bài toán này bằng phân tích thống kê histogram của ảnh. Ý tưởng trung tâm là tìm ngưỡng $T^*$ sao cho phương sai liên lớp (Inter-class Variance) giữa hai nhóm pixel — nền và đối tượng — đạt giá trị lớn nhất. Điều này tương đương với việc đảm bảo sự phân tách hai nhóm pixel là rõ ràng nhất có thể. Phương pháp Otsu thích ứng tự động với điều kiện chiếu sáng tổng thể khác nhau mà không cần can thiệp thủ công.

Tuy nhiên, khi ảnh có gradient chiếu sáng cục bộ (sáng không đều trong phạm vi nhỏ), phân ngưỡng thích nghi (Adaptive Thresholding) cho kết quả tốt hơn. Thay vì dùng một ngưỡng $T$ chung, phân ngưỡng thích nghi tính toán ngưỡng riêng cho từng vùng nhỏ của ảnh dựa trên thống kê cục bộ (thường là giá trị trung bình hoặc trung bình Gaussian của vùng lân cận), giúp nhị phân hóa hiệu quả ngay cả khi điều kiện chiếu sáng thay đổi trong phạm vi cùng một bức ảnh.

### 2.1.5. Các phép toán hình thái học (Morphological Operations)

Sau khi ảnh được nhị phân hóa, kết quả thường chứa các khiếm khuyết hình học như đốm nhiễu nhỏ trên nền, lỗ hổng bên trong đối tượng, hay các nét bị đứt gãy. Xử lý hình thái học (Mathematical Morphology) là tập hợp các công cụ toán học dựa trên hình dạng để gọt giũa và tái cấu trúc các đối tượng trong ảnh nhị phân thông qua việc quét một phần tử cấu trúc (Structuring Element / Kernel) trên ảnh.

Hai phép toán nguyên thủy là phép co (Erosion) — ăn mòn biên vật thể, loại bỏ nhiễu nhỏ — và phép giãn (Dilation) — bồi đắp biên vật thể, lấp đầy lỗ hổng. Kết hợp hai phép toán này theo thứ tự khác nhau tạo ra hai phép toán cấp cao hơn: phép mở (Opening = Co → Giãn) có tác dụng loại bỏ nhiễu nhỏ xung quanh đối tượng mà vẫn bảo toàn kích thước tổng thể; và phép đóng (Closing = Giãn → Co) có tác dụng lấp kín các lỗ hổng bên trong đối tượng và nối liền các nét bị đứt gãy. Trong bài toán nhận diện phiếu tô bong bóng, phép đóng đóng vai trò đặc biệt quan trọng trong việc hợp nhất các nét tô đứt quãng do thí sinh tô không liền tay, biến chúng thành vùng tô liền khối trước khi đo lường diện tích.

### 2.1.6. Phát hiện đường thẳng và nắn thẳng ảnh nghiêng (Deskewing)

Khi ảnh bài thi được chụp với một góc nghiêng nhỏ so với phương vuông góc, các đường văn bản và cấu trúc bài thi không còn nằm ngang phẳng. Hiện tượng này cần được hiệu chỉnh trước khi đưa vào các thuật toán nhận diện đòi hỏi ảnh phải ở trạng thái chuẩn mực — đặc biệt quan trọng với pipeline nhận diện bài thi dạng khoanh tròn tự do.

Phát hiện cạnh Canny là thuật toán nổi tiếng để xác định các điểm biên của đối tượng trong ảnh thông qua bốn bước: làm mờ Gaussian để giảm nhiễu, tính toán gradient cường độ sáng, tỉa không cực đại (Non-Maximum Suppression) và ngưỡng hóa liên kết (Hysteresis Thresholding) để kết nối các điểm biên yếu với biên mạnh. Từ ảnh biên này, biến đổi Hough (Hough Transform) tìm kiếm các đường thẳng nổi bật trong ảnh bằng cách chuyển bài toán sang không gian tham số (không gian Hough). Góc nghiêng trung vị của các đường thẳng phát hiện được dùng làm ước lượng góc lệch của tờ giấy, từ đó hệ thống áp dụng phép biến đổi affine để xoay ảnh về trạng thái thẳng đứng.

---

## 2.2. Nhận diện dấu quang học (Optical Mark Recognition — OMR)

### 2.2.1. Nguyên lý hoạt động của OMR

Nhận diện dấu quang học (Optical Mark Recognition — OMR) là kỹ thuật đọc và diễn giải các dấu hiệu do con người tạo ra trên giấy thông qua quá trình phân tích hình ảnh. Đây là công nghệ nền tảng cho các hệ thống chấm điểm trắc nghiệm tự động truyền thống, sử dụng nguyên lý đo lường mức độ phủ mực (tô đen) trong các vùng ô định sẵn trên phiếu trả lời.

Quy trình OMR cơ bản bao gồm hai giai đoạn chính. Giai đoạn đầu tiên là xây dựng lưới tọa độ (Grid Calibration): dựa trên khuôn mẫu phiếu trả lời đã biết, hệ thống xác định tọa độ trung tâm và bán kính của từng ô bong bóng (Bubble ROI — Region of Interest) tương ứng với mỗi câu hỏi và mỗi lựa chọn. Giai đoạn thứ hai là đo lường tỷ lệ tô (Fill Ratio Measurement): với mỗi ô bong bóng, hệ thống áp dụng một mặt nạ tròn (circular mask) để cô lập vùng ảnh bên trong ô, sau đó đếm số pixel đen (đã tô) và tính tỷ lệ của chúng so với tổng số pixel trong vùng ô. Tỷ lệ này, được gọi là fill ratio, phản ánh mức độ tô đậm của ô bong bóng.

Việc quyết định một ô bong bóng là "đã tô" hay "chưa tô" dựa trên việc so sánh fill ratio với một ngưỡng phân biệt. Thách thức thực tiễn là ngưỡng này không cố định mà phụ thuộc vào loại bút, lực tay người viết, chất lượng ảnh và điều kiện chiếu sáng — dẫn đến sự cần thiết của các thuật toán xác định ngưỡng tự động thích nghi.

### 2.2.2. Xác định ngưỡng tô thích nghi dựa trên phân tích histogram

Trong khi phân ngưỡng Otsu hoạt động trên phân phối cường độ pixel, bài toán OMR đặc thù hơn: thay vì phân tích giá trị pixel đơn lẻ, hệ thống phân tích phân phối của toàn bộ tập hợp các giá trị fill ratio của tất cả ô bong bóng trong một phiếu thi. Về mặt lý thuyết, tập hợp này sẽ thể hiện phân phối hai đỉnh (bimodal distribution): một cụm giá trị thấp tập trung ở những ô chưa tô, và một cụm giá trị cao ở những ô đã tô. Điểm trũng (valley) giữa hai đỉnh histogram này chính là ngưỡng phân biệt tối ưu.

Phương pháp xác định hai đỉnh trong histogram thường dựa trên các thuật toán phát hiện cực trị cục bộ (peak detection) sau khi làm mịn histogram để loại bỏ nhiễu thống kê. Ngưỡng phân biệt được xác định tại điểm có giá trị cực tiểu nằm giữa hai đỉnh. Phương pháp này cho phép hệ thống tự động thích nghi với đặc tính tô đậm/nhạt đặc thù của từng bài thi, thay vì phụ thuộc vào một ngưỡng cứng định sẵn.

Ngoài việc phân biệt ô tô và ô trống, hệ thống OMR cũng cần xử lý trường hợp đặc biệt khi thí sinh tô nhiều đáp án cho cùng một câu. Điều này được phát hiện bằng cách so sánh fill ratio của ô có điểm số cao nhất với fill ratio của ô cao thứ hai: nếu tỷ lệ giữa hai giá trị này vượt một ngưỡng cho trước, câu hỏi được đánh dấu là không hợp lệ (đa dấu).

---

## 2.3. Học sâu (Deep Learning) trong nhận diện hình ảnh

### 2.3.1. Nền tảng của học sâu và mạng nơ-ron nhân tạo

Học sâu (Deep Learning) là một nhánh chuyên biệt của học máy (Machine Learning), được lấy cảm hứng từ cơ chế xử lý thông tin của mạng lưới tế bào thần kinh sinh học trong não bộ. Điểm khác biệt cốt lõi so với các phương pháp học máy truyền thống là khả năng tự động học các biểu diễn đặc trưng phân cấp (hierarchical feature representation) trực tiếp từ dữ liệu thô mà không cần thiết kế đặc trưng thủ công (hand-crafted features). Điều này cho phép các mô hình học sâu xử lý hiệu quả các bài toán có độ phức tạp cao, nơi mà việc định nghĩa đặc trưng bằng tay là không khả thi.

Đơn vị cơ bản của mạng nơ-ron nhân tạo là nơ-ron — một hàm số nhận một véc-tơ đầu vào, tính tổng có trọng số, cộng thêm hệ số độ lệch (bias), rồi áp dụng một hàm kích hoạt phi tuyến để tạo ra tín hiệu đầu ra. Hàm kích hoạt là yếu tố thiết yếu giúp mạng nơ-ron có khả năng mô hình hóa các quan hệ phi tuyến phức tạp — nếu không có nó, một mạng nhiều lớp về mặt toán học sẽ tương đương với một mạng một lớp tuyến tính. Hai hàm kích hoạt phổ biến nhất là Sigmoid, thường dùng ở đầu ra để biểu diễn xác suất, và ReLU (Rectified Linear Unit), là tiêu chuẩn công nghiệp cho các lớp ẩn nhờ khả năng giải quyết hiệu quả hiện tượng tiêu biến gradient (Vanishing Gradient).

Quá trình học của mạng nơ-ron diễn ra thông qua thuật toán lan truyền ngược (Backpropagation). Trong mỗi vòng lặp huấn luyện, mạng nhận dữ liệu đầu vào, tính toán đầu ra dự đoán, sau đó đo lường sai số so với nhãn thực bằng một hàm mất mát (Loss Function). Thuật toán lan truyền ngược áp dụng quy tắc dây chuyền trong vi tích phân để tính đạo hàm riêng (gradient) của hàm mất mát theo từng tham số (trọng số và bias) trong toàn bộ mạng. Cuối cùng, một thuật toán tối ưu hóa — thường là các biến thể của Gradient Descent như Adam hay SGD — cập nhật các tham số theo hướng giảm thiểu hàm mất mát, lặp đi lặp lại qua hàng nghìn vòng (epochs) cho đến khi mô hình hội tụ.

### 2.3.2. Mạng nơ-ron tích chập (Convolutional Neural Network — CNN)

Mạng nơ-ron tích chập (CNN) là kiến trúc học sâu được thiết kế đặc biệt cho dữ liệu có cấu trúc không gian lưới, điển hình là hình ảnh. CNN được giới thiệu lần đầu bởi Yann LeCun và cộng sự năm 1989, và đạt được sự công nhận rộng rãi với kiến trúc LeNet-5 năm 1998. So với mạng kết nối đầy đủ (Fully Connected Network), CNN có hai đặc tính kiến trúc nổi bật: kết nối cục bộ (Local Connectivity) — mỗi nơ-ron chỉ kết nối với một vùng nhỏ của lớp trước — và chia sẻ tham số (Parameter Sharing) — cùng một bộ trọng số (kernel/filter) được áp dụng trên toàn bộ bề mặt ảnh.

Hai đặc tính này mang lại ý nghĩa sâu sắc về mặt nhận thức: phép tích chập là bất biến tịnh tiến (Translation Invariant), nghĩa là một đặc trưng (ví dụ: vòng tròn khoanh đáp án) có thể được phát hiện bất kể nó nằm ở vị trí nào trong ảnh. Đồng thời, việc tái sử dụng cùng một kernel trên toàn ảnh giảm đáng kể số lượng tham số cần học, giúp tránh hiện tượng học vẹt (Overfitting) và tăng tốc quá trình huấn luyện.

Một mạng CNN điển hình bao gồm ba loại lớp chính. Lớp tích chập (Convolutional Layer) sử dụng các bộ lọc trượt qua ảnh để tạo ra các bản đồ đặc trưng (Feature Maps), trong đó mỗi bản đồ biểu diễn sự hiện diện của một mẫu hình dạng cụ thể tại các vị trí khác nhau. Lớp gộp không gian (Pooling Layer) giảm kích thước không gian của các bản đồ đặc trưng, tóm lược thông tin và tăng bất biến tịnh tiến; Max Pooling — lấy giá trị lớn nhất trong từng vùng — là phương pháp phổ biến nhất. Lớp kết nối đầy đủ (Fully Connected Layer) ở cuối mạng đóng vai trò phân loại dựa trên các đặc trưng bậc cao đã được trích xuất bởi các lớp tích chập, với hàm Softmax ở đầu ra để tạo phân phối xác suất trên các lớp phân loại.

Về mặt lý thuyết học biểu diễn (Representation Learning), các lớp tích chập nông đầu tiên học cách phát hiện các đặc trưng cơ bản như cạnh thẳng, góc cạnh và gradient màu sắc. Các lớp sâu hơn kết hợp các đặc trưng đơn giản này thành các cấu trúc phức tạp hơn như hình dạng và kết cấu. Các lớp sâu nhất học các khái niệm ngữ nghĩa cấp cao như hình dạng ký tự hay khuôn mặt. Chuỗi phân cấp học biểu diễn từ thấp đến cao này là sức mạnh đặc trưng của học sâu và lý giải tại sao CNN vượt trội so với các phương pháp truyền thống trong nhận diện ký tự.

### 2.3.3. Phát hiện đối tượng (Object Detection)

Bài toán phân loại ảnh (Image Classification) đặt câu hỏi "Ảnh này thuộc lớp nào?", trong khi phát hiện đối tượng (Object Detection) giải quyết một bài toán khó hơn nhiều: xác định đồng thời vị trí (bounding box) và nhãn lớp của tất cả đối tượng trong ảnh. Đây là một bài toán kết hợp giữa hồi quy (Regression) để dự đoán tọa độ hộp bao và phân loại (Classification) để nhận diện lớp đối tượng.

Chỉ số IoU (Intersection over Union) là thước đo chuẩn đánh giá mức độ khớp giữa hộp bao dự đoán và hộp bao thực tế (Ground Truth). IoU được tính bằng tỷ lệ giữa diện tích giao nhau và diện tích hợp của hai hộp bao, với giá trị từ 0 (không chồng lấn) đến 1 (khớp hoàn toàn). Một dự đoán thường được coi là chính xác khi IoU ≥ 0.5. Dựa trên ngưỡng IoU, các chỉ số đánh giá chuẩn của bài toán phát hiện đối tượng — Precision (tỷ lệ dự đoán đúng trên tổng dự đoán), Recall (tỷ lệ dự đoán đúng trên tổng đối tượng thực) và mAP (mean Average Precision) — được tính toán.

Kiến trúc các mô hình phát hiện đối tượng chia thành hai trường phái lớn. Phương pháp hai giai đoạn (Two-stage, tiêu biểu là họ R-CNN) trước tiên đề xuất các vùng ứng cử viên có thể chứa đối tượng, sau đó phân loại và tinh chỉnh từng vùng một cách riêng biệt — cho độ chính xác cao nhưng tốc độ chậm. Phương pháp một giai đoạn (One-stage, tiêu biểu là YOLO và SSD) xử lý toàn bộ ảnh trong một lần lan truyền thuận duy nhất, đồng thời dự đoán tất cả hộp bao và nhãn phân loại — đạt tốc độ thời gian thực nhưng ban đầu có độ chính xác thấp hơn. Các thế hệ YOLO gần đây đã thu hẹp đáng kể khoảng cách về độ chính xác trong khi vẫn duy trì lợi thế tốc độ, khiến chúng trở thành lựa chọn ưu tiên cho các ứng dụng thực tiễn.

Sau khi mô hình tạo ra nhiều hộp bao cho cùng một đối tượng, thuật toán Triệt tiêu phi cực đại (Non-Maximum Suppression — NMS) được áp dụng để làm sạch kết quả: giữ lại hộp bao có điểm tin cậy cao nhất và loại bỏ các hộp bao khác có IoU với hộp đó vượt quá một ngưỡng nhất định, đảm bảo mỗi đối tượng chỉ được phát hiện một lần.

### 2.3.4. Kiến trúc YOLO và YOLOv9

YOLO (You Only Look Once) là họ mô hình phát hiện đối tượng một giai đoạn được giới thiệu lần đầu bởi Redmon và cộng sự năm 2016. Ý tưởng cốt lõi là phân chia ảnh đầu vào thành lưới các ô (grid cells), và mỗi ô chịu trách nhiệm dự đoán các hộp bao và phân loại đối tượng có tâm nằm trong ô đó. Toàn bộ quá trình dự đoán diễn ra trong một lần lan truyền thuận qua mạng nơ-ron, đạt tốc độ xử lý thời gian thực.

Về mặt kiến trúc, các mô hình YOLO hiện đại được tổ chức thành ba thành phần chính. Backbone (xương sống) là mạng CNN trích xuất đặc trưng đa tỷ lệ từ ảnh đầu vào, thường được xây dựng dựa trên các kiến trúc như CSPNet (Cross Stage Partial Network) nhằm cân bằng giữa độ sâu học biểu diễn và hiệu suất tính toán. Neck (cổ) là thành phần tổng hợp và khuếch đại đặc trưng từ nhiều tỷ lệ không gian khác nhau thông qua các cơ chế như FPN (Feature Pyramid Network) và PAN (Path Aggregation Network), giúp mô hình phát hiện đối tượng ở nhiều kích thước khác nhau. Head (đầu ra) là thành phần thực hiện dự đoán hộp bao và nhãn lớp trên các đặc trưng đã tổng hợp.

YOLOv9, công bố đầu năm 2024, đề xuất hai đổi mới kiến trúc quan trọng nhằm giải quyết vấn đề mất mát thông tin qua các lớp mạng sâu — gọi là "nút thắt cổ chai thông tin" (Information Bottleneck). Thứ nhất, Thông tin gradient khả trình (Programmable Gradient Information — PGI) tạo ra một nhánh phụ trợ song song với nhánh chính trong quá trình huấn luyện: nhánh phụ trợ này có kiến trúc khả nghịch hoàn toàn, đảm bảo không mất thông tin, do đó cung cấp gradient huấn luyện thuần khiết để định hướng học tập cho nhánh chính. Sau huấn luyện, nhánh phụ trợ được loại bỏ, không làm tăng chi phí tính toán khi triển khai thực tế. Thứ hai, Mô-đun tổng hợp gradient có thể học (GELAN — Generalized Efficient Layer Aggregation Network) cho phép chọn lựa linh hoạt các khối tính toán khác nhau (như CSP hay ELAN) tùy theo yêu cầu về tốc độ và độ chính xác, tạo ra kiến trúc vừa hiệu quả về tính toán vừa đạt hiệu suất cao.

### 2.3.5. Nhận dạng ký tự quang học (Optical Character Recognition — OCR)

Nhận dạng ký tự quang học (OCR) là công nghệ chuyển đổi hình ảnh chứa văn bản thành dữ liệu ký tự có thể đọc và xử lý bởi máy tính. Bài toán OCR hiện đại được tiếp cận theo kiến trúc tổng thể bao gồm ba giai đoạn: phát hiện vùng văn bản (Text Detection) — xác định vị trí các vùng chứa ký tự trong ảnh; nhận diện ký tự (Text Recognition) — phân loại từng ký tự hoặc chuỗi ký tự; và hậu xử lý (Post-processing) — sửa lỗi ngữ cảnh và chuẩn hóa kết quả.

Hai hướng tiếp cận chính trong nhận dạng ký tự là: (1) phương pháp dựa trên học sâu thuần túy với các kiến trúc như CRNN (Convolutional Recurrent Neural Network) kết hợp CNN trích xuất đặc trưng và RNN xử lý chuỗi, thường được huấn luyện với hàm mất mát CTC (Connectionist Temporal Classification); và (2) phương pháp transformer-based với cơ chế attention, cho phép mô hình chú ý đến ngữ cảnh rộng hơn khi nhận diện ký tự.

Trong bối cảnh nhận diện số thứ tự câu hỏi trên ảnh đề thi với sự đa dạng cao về font chữ và chất lượng ảnh, các framework OCR đa ngôn ngữ được huấn luyện trước trên tập dữ liệu lớn — như EasyOCR — có lợi thế về khả năng khái quát hóa tốt. Tuy nhiên, OCR vẫn có thể gặp sai sót, đặc biệt với ảnh crop nhỏ và font đề thi phi chuẩn. Chiến lược kết hợp OCR với các ràng buộc ngữ cảnh (ví dụ: tính tuần tự của số câu hỏi) giúp nâng cao độ chính xác tổng thể của hệ thống.

---

## 2.4. Kiến trúc và công nghệ phần mềm hệ thống

### 2.4.1. Kiến trúc microservices và giao tiếp REST API

Kiến trúc microservices phân rã hệ thống phần mềm lớn thành các dịch vụ nhỏ độc lập, mỗi dịch vụ đảm nhận một nhiệm vụ kinh doanh cụ thể và có thể được phát triển, triển khai, mở rộng quy mô độc lập. So với kiến trúc nguyên khối (Monolithic), microservices cải thiện tính module hóa, khả năng bảo trì và độ linh hoạt về công nghệ — mỗi dịch vụ có thể sử dụng ngôn ngữ lập trình và framework phù hợp nhất với nhiệm vụ của nó.

REST (Representational State Transfer) là phong cách kiến trúc cho hệ thống phân tán, sử dụng giao thức HTTP và các phương thức chuẩn (GET, POST, PUT, DELETE) để trao đổi dữ liệu giữa các thành phần. RESTful API cung cấp giao diện giao tiếp chuẩn hóa, stateless (không lưu trạng thái phiên) và dễ tích hợp giữa các dịch vụ viết bằng các ngôn ngữ khác nhau — là lựa chọn tự nhiên để kết nối dịch vụ AI (Python) với backend nghiệp vụ (Java) và frontend (JavaScript).

### 2.4.2. Framework backend — FastAPI và Spring Boot

FastAPI là framework web Python hiện đại, được thiết kế cho phát triển API nhanh chóng với hiệu suất cao. Điểm nổi bật của FastAPI là hỗ trợ lập trình bất đồng bộ (async/await) theo chuẩn ASGI, cho phép xử lý nhiều yêu cầu đồng thời mà không bị chặn — đặc biệt quan trọng khi tích hợp các tác vụ I/O nặng như đọc/ghi file ảnh. FastAPI cũng tự động sinh tài liệu API tương tác (Swagger UI) từ type annotations của Python, đơn giản hóa việc kiểm thử và tích hợp.

Spring Boot là framework Java hiệu dụng xây dựng trên nền Spring Framework, cung cấp cấu hình tự động (auto-configuration) và phương pháp tiếp cận "convention over configuration" giúp giảm thiểu boilerplate code. Spring Boot tích hợp sẵn hệ sinh thái phong phú bao gồm Spring Security cho xác thực và phân quyền, Spring Data JPA cho truy cập cơ sở dữ liệu hướng đối tượng, và Spring MVC cho xây dựng RESTful API. Với hệ sinh thái trưởng thành và cộng đồng lớn, Spring Boot là lựa chọn phổ biến cho các hệ thống doanh nghiệp yêu cầu tính ổn định và bảo mật cao.

### 2.4.3. Phát triển frontend với React và TypeScript

React là thư viện JavaScript cho phát triển giao diện người dùng, được Facebook phát triển và mã nguồn mở hóa năm 2013. Kiến trúc component-based của React cho phép xây dựng giao diện từ các thành phần UI tái sử dụng, mỗi thành phần quản lý trạng thái và giao diện của riêng mình. Cơ chế Virtual DOM của React tối ưu hóa việc cập nhật giao diện bằng cách chỉ cập nhật những phần DOM thực sự thay đổi, cải thiện hiệu suất kết xuất.

TypeScript là ngôn ngữ mở rộng của JavaScript với hệ thống kiểu tĩnh (Static Typing), cho phép phát hiện lỗi tại thời điểm biên dịch thay vì thời gian chạy. Trong phát triển ứng dụng frontend phức tạp, TypeScript cải thiện đáng kể chất lượng mã và khả năng bảo trì thông qua việc tự động hoàn thành mã, gợi ý lỗi inline và tài liệu kiểu dữ liệu sống. Kết hợp React với TypeScript là tiêu chuẩn phổ biến trong phát triển frontend hiện đại.

### 2.4.4. Containerization với Docker

Docker là nền tảng containerization cho phép đóng gói ứng dụng cùng toàn bộ dependencies (thư viện, runtime, cấu hình) vào một container độc lập và di động. Container Docker cô lập môi trường chạy ứng dụng khỏi máy chủ vật lý, đảm bảo ứng dụng chạy nhất quán trên bất kỳ môi trường nào — từ máy tính phát triển cá nhân đến máy chủ sản xuất. Điều này giải quyết vấn đề "works on my machine" phổ biến trong phát triển phần mềm và đơn giản hóa quá trình triển khai (deployment) đáng kể.

Đối với hệ thống AI có nhiều dependency phức tạp (CUDA cho GPU, các thư viện học sâu như PyTorch, Ultralytics YOLO), Docker đặc biệt hữu ích trong việc chuẩn hóa môi trường và đảm bảo tái lập (reproducibility) kết quả thực nghiệm. Kết hợp với Docker Compose, nhiều container (dịch vụ AI Python, backend Java, frontend, cơ sở dữ liệu) có thể được định nghĩa và quản lý tập trung, đơn giản hóa việc triển khai hệ thống đa dịch vụ.

---

## 2.5. Tổng kết chương

Chương này đã trình bày hệ thống lý thuyết nền tảng bao gồm hai nhóm chính. Nhóm thứ nhất là các kỹ thuật xử lý ảnh số và thị giác máy tính truyền thống, bao gồm: phép biến đổi phối cảnh để hiệu chỉnh méo dạng hình học ảnh chụp từ điện thoại; thuật toán CLAHE để cân bằng chiếu sáng cục bộ không đồng đều; phân ngưỡng Otsu và phân ngưỡng thích nghi để nhị phân hóa ảnh; các phép toán hình thái học để tinh chỉnh vùng ảnh nhị phân; và thuật toán nắn thẳng ảnh nghiêng. Nhóm thứ hai là các lý thuyết học sâu hiện đại, bao gồm: kiến trúc CNN với cơ chế tích chập, gộp và phân loại; nguyên lý phát hiện đối tượng với các chỉ số đánh giá IoU, NMS và mAP; kiến trúc YOLO một giai đoạn với các đổi mới PGI và GELAN trong YOLOv9; và bài toán nhận dạng ký tự OCR. Bên cạnh đó, các công nghệ phần mềm triển khai hệ thống cũng được giới thiệu khái quát.

Những kiến thức lý thuyết này tạo thành nền tảng vững chắc để hiểu và đánh giá các quyết định thiết kế trong chương tiếp theo — Phân tích và Thiết kế hệ thống — nơi các lý thuyết được áp dụng cụ thể vào từng thành phần của hệ thống chấm điểm CODEX.

---

## Tài liệu tham khảo (Chương 2)

[1] Gonzalez, R. C., & Woods, R. E. (2018). *Digital Image Processing* (4th ed.). Pearson.

[2] Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. https://www.deeplearningbook.org

[3] Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016). *You Only Look Once: Unified, Real-Time Object Detection*. In *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 779–788.

[4] LeCun, Y., Bottou, L., Bengio, Y., & Haffner, P. (1998). *Gradient-Based Learning Applied to Document Recognition*. Proceedings of the IEEE, 86(11), 2278–2324.

[5] Otsu, N. (1979). *A Threshold Selection Method from Gray-Level Histograms*. IEEE Transactions on Systems, Man, and Cybernetics, 9(1), 62–66.

[6] Pizer, S. M., Amburn, E. P., Austin, J. D., et al. (1987). *Adaptive Histogram Equalization and Its Variations*. Computer Vision, Graphics, and Image Processing, 39(3), 355–368.

[7] Hartley, R., & Zisserman, A. (2003). *Multiple View Geometry in Computer Vision* (2nd ed.). Cambridge University Press.

[8] Canny, J. (1986). *A Computational Approach to Edge Detection*. IEEE Transactions on Pattern Analysis and Machine Intelligence, 8(6), 679–698.

[9] Bradski, G. (2000). *The OpenCV Library*. Dr. Dobb's Journal of Software Tools, 25(11), 120–125.

[10] Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). *Learning Representations by Back-propagating Errors*. Nature, 323(6088), 533–536.

[11] He, K., Zhang, X., Ren, S., & Sun, J. (2016). *Deep Residual Learning for Image Recognition*. In *Proceedings of the IEEE CVPR*, pp. 770–778.

[12] Wang, C. Y., Yeh, I. H., & Liao, H. Y. M. (2024). *YOLOv9: Learning What You Want to Learn Using Programmable Gradient Information*. arXiv preprint arXiv:2402.13616.

[13] Jocher, G., Chaurasia, A., & Qiu, J. (2023). *Ultralytics YOLO* (Version 8.0.0) [Computer software]. Ultralytics. https://github.com/ultralytics/ultralytics

[14] Paszke, A., Gross, S., Massa, F., et al. (2019). *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. In *Advances in Neural Information Processing Systems (NeurIPS)*, 32.

[15] JaidedAI. (2020). *EasyOCR: Ready-to-use OCR with 80+ Supported Languages*. GitHub Repository. https://github.com/JaidedAI/EasyOCR

[16] Nayak, A., Bhargava, H., & Bhingarde, A. (2021). *REST API Design: Best Practices for a Pragmatic Design*. Apress.

[17] Merkel, D. (2014). *Docker: Lightweight Linux Containers for Consistent Development and Deployment*. Linux Journal, 2014(239), 2.
