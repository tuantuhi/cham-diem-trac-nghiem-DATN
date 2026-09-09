import torch
import torch.nn as nn
import time
from torchvision import transforms
from PIL import Image
import os

# 1. Khai báo kiến trúc (Giữ nguyên cấu trúc của bạn)
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

def measure_fps(image_path, model_path='../models/abcd_ocr.pth', iterations=1000):
    if not os.path.exists(image_path):
        print(f"Lỗi: Không tìm thấy ảnh tại '{image_path}'")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f" Đang chạy kiểm tra trên thiết bị: {device}")
    
    # Khởi tạo mô hình
    model = SimpleOCR_CNN().to(device)
    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
    except Exception as e:
        print(f"Lỗi khi load mô hình: {e}")
        return

    # Tiền xử lý (Được đưa ra ngoài vòng lặp đo thời gian)
    transform = transforms.Compose([
        transforms.Resize((40, 40)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    image = Image.open(image_path).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)

    # --- BƯỚC 1: WARM-UP (Khởi động nóng) ---
    print(" Đang làm nóng (Warm-up) mô hình...")
    with torch.no_grad():
        for _ in range(50):
            _ = model(input_tensor)
            
    # Bắt buộc phải đồng bộ hóa GPU trước khi bắt đầu bấm giờ
    if device.type == 'cuda':
        torch.cuda.synchronize()

    # --- BƯỚC 2: ĐO LƯỜNG CHÍNH THỨC ---
    print(f" Bắt đầu đo tốc độ thực tế với {iterations} vòng lặp...")
    start_time = time.time()

    with torch.no_grad():
        for _ in range(iterations):
            _ = model(input_tensor)
            
    # Bắt buộc phải đồng bộ hóa GPU sau khi kết thúc để tính chuẩn thời gian
    if device.type == 'cuda':
        torch.cuda.synchronize()
        
    end_time = time.time()

   # --- BƯỚC 3: TÍNH TOÁN KẾT QUẢ ---
    total_time = end_time - start_time
    fps = iterations / total_time
    time_per_image = (total_time / iterations) * 1000  # ms

    # Hiển thị số liệu với giá trị thập phân chính xác
    print("\n=========================================")
    print(" BÁO CÁO TỐC ĐỘ (MÔ HÌNH THUẦN TÚY):")
    print(f" Tốc độ xử lý (FPS):        {fps:.4f} ảnh/giây") 
    print(f" Thời gian xử lý 1 ảnh:     {time_per_image:.4f} ms")
    print("=========================================")

if __name__ == "__main__":
    test_image_path = r"D:\Desktop\DATN\Ocr\dataset_ocr\train\D\0c8b3600.jpg"
    # Thay đổi số iterations tùy theo độ mạnh của máy, mặc định là 1000
    measure_fps(test_image_path, model_path=r"D:\Desktop\DATN\Ocr\models\abcd_ocr.pth", iterations=1000)