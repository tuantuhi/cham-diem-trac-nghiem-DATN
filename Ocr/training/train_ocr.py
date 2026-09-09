import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

class SimpleOCR_CNN(nn.Module):
    def __init__(self):
        super(SimpleOCR_CNN, self).__init__()
        # Đầu vào: 3 x 40 x 40
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3) # -> 16 x 38 x 38
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2, 2)              # -> 16 x 19 x 19
        
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3) # -> 32 x 17 x 17
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2, 2)               # -> 32 x 8 x 8
        
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(128, 4) # 4 lớp (classes): A, B, C, D

    def forward(self, x):
        x = self.pool1(self.relu1(self.conv1(x)))
        x = self.pool2(self.relu2(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 8)
        x = self.relu3(self.fc1(x))
        x = self.fc2(x)
        return x

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Đang huấn luyện trên thiết bị: {device}")

    # Biến đổi dữ liệu
    transform = transforms.Compose([
        transforms.Resize((40, 40)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    # Tải tập dữ liệu
    train_dataset = datasets.ImageFolder(root=r'D:\Desktop\DATN\Ocr\dataset_ocr\train', transform=transform)
    val_dataset = datasets.ImageFolder(root=r'D:\Desktop\DATN\Ocr\dataset_ocr\val', transform=transform)

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    model = SimpleOCR_CNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 25
    print("Bắt đầu quá trình huấn luyện...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        train_acc = 100 * correct / total
        
        # Đánh giá (Validation)
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
                
        val_acc = 100 * val_correct / val_total
        print(f"(Epoch) {epoch+1}/{epochs} - Train Loss: {running_loss/len(train_loader):.4f}, Train Acc: {train_acc:.2f}% | Val Loss: {val_loss/len(val_loader):.4f}, Val Acc: {val_acc:.2f}%")

    torch.save(model.state_dict(), '../models/abcd_ocr.pth')
    print("Đã lưu mô hình tại ../models/abcd_ocr.pth")

if __name__ == "__main__":
    main()