import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import os
import cv2  # Thư viện OpenCV
import numpy as np

# 1. Khai báo lại cấu trúc mô hình
class SimpleOCR_CNN(nn.Module):
    def __init__(self):
        super(SimpleOCR_CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 4)

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 8)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

def predict_image(image_path, model_path='../models/abcd_ocr.pth'):
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy ảnh tại đường dẫn '{image_path}'")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 2. Khởi tạo mô hình
    model = SimpleOCR_CNN().to(device)
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
    except Exception as e:
        print(f"Lỗi khi load mô hình: {e}")
        return

    # 3. Định nghĩa Transforms
    transform = transforms.Compose([
        transforms.Resize((40, 40)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # 4. Đọc và xử lý ảnh (để đưa vào AI)
    image_pil = Image.open(image_path).convert('RGB')
    input_tensor = transform(image_pil).unsqueeze(0).to(device)

    # 5. Dự đoán
    classes = ['A', 'B', 'C', 'D']
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)
        
        predicted_class = classes[predicted_idx.item()]
        confidence_percent = confidence.item() * 100

    print(f"--- Kết quả Nhận diện ---")
    print(f"Ảnh đầu vào: {image_path}")
    print(f"Dự đoán:     {predicted_class}")
    print(f"Độ tin cậy:  {confidence_percent:.4f}%")
    
    print("\nChi tiết xác suất từng lớp:")
    prob_list = probabilities[0].cpu().numpy()
    for i, cls in enumerate(classes):
        print(f"- Lớp {cls}: {prob_list[i] * 100:.4f}%")


    # --- 6. VẼ TOÀN BỘ THÔNG TIN LÊN ẢNH ---
    
    # Đọc lại ảnh bằng OpenCV
    img_cv = cv2.imread(image_path)
    
    # Phóng to ảnh để có không gian vẽ (kích thước 512x512)
    target_size = (512, 512)
    img_drawing = cv2.resize(img_cv, target_size, interpolation=cv2.INTER_CUBIC)
    
    # Cấu hình phông chữ chung
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 6.1. Vẽ dự đoán chính (Màu xanh lá - BGR: 0, 255, 0)
    main_text = f"Ket qua: {predicted_class} ({confidence_percent:.2f}%)"
    cv2.putText(img_drawing, main_text, (20, 50), font, 1.2, (0, 255, 0), 2, cv2.LINE_AA)
    
    # 6.2. Vẽ tiêu đề cho danh sách chi tiết (Màu đỏ - BGR: 0, 0, 255)
    cv2.putText(img_drawing, "Chi tiet tung lop", (20, 110), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
    
    # 6.3. Vẽ từng lớp A, B, C, D bằng vòng lặp
    start_y = 150 # Tọa độ y bắt đầu cho danh sách
    line_spacing = 40 # Khoảng cách giữa các dòng
    
    for i, cls in enumerate(classes):
        # Tính toán xác suất %
        prob_percent = prob_list[i] * 100
        
        # Chuẩn bị văn bản (Ví dụ: "- Lop A: 0.0000%")
        text_detail = f"- Lop {cls}: {prob_percent:.4f}%"
        
        # Tọa độ x lùi vào một chút (40) cho đẹp, tọa độ y cộng dồn
        org = (40, start_y + (i * line_spacing))
        
        # Vẽ dòng chữ lên ảnh
        cv2.putText(img_drawing, text_detail, org, font, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    
    # Lưu ảnh kết quả
    output_path = image_path.replace('.jpg', '_predicted_details.jpg')
    cv2.imwrite(output_path, img_drawing)
    
    print(f"\nĐã lưu ảnh kết quả chứa đầy đủ xác suất tại: {output_path}")

if __name__ == "__main__":
    # Điền chính xác đường dẫn ảnh test của bạn vào đây
    test_image_path = r"D:\Desktop\DATN\Ocr\dataset_ocr\train\A\0d089c66.jpg"
    
    print("Đang khởi động quá trình kiểm thử và vẽ thông tin...")
    predict_image(test_image_path)