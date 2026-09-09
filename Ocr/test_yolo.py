import torch
import matplotlib.pyplot as plt
import pandas as pd
import re

ckpt = torch.load(r'D:\Desktop\DATN\Ocr\models\best_v9.pt', map_location='cpu', weights_only=False)

if 'train_args' in ckpt:
    yolo_base_model = ckpt['train_args'].get('model', 'Không xác định')
    yolo_task = ckpt['train_args'].get('task', 'Không xác định')
    
    print("\n=========================================")
    print(f" THÔNG TIN BẢN YOLO ĐÃ DÙNG HUẤN LUYỆN:")
    print(f" - Model gốc: {yolo_base_model}")
    print(f" - Tác vụ: {yolo_task}")
    print("=========================================\n")

history = ckpt.get('train_results')

if history is not None:
    print(" Đã tìm thấy lịch sử huấn luyện!")
   
    # Lấy dữ liệu toàn bộ epochs
    map50_full = history.get('metrics/mAP50(B)')
    val_box_loss_full = history.get('val/box_loss')
    precision_full = history.get('metrics/precision(B)')
    recall_full = history.get('metrics/recall(B)')
    
    limit = 100
    
    # Thiết lập khung vẽ đồ thị 2x2
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    
    # Đồ thị 1: mAP@0.5 (Cắt mảng bằng [:limit])
    if map50_full:
        y_data = map50_full[:limit]
        axs[0, 0].plot(y_data, label='mAP@0.5', color='green', linewidth=2)
        axs[0, 0].set_title(f'Độ chính xác mAP@0.5 ({limit} Epochs)')
        axs[0, 0].set_xlabel('Epochs')
        axs[0, 0].set_ylabel('mAP')
        axs[0, 0].grid(True, linestyle='--', alpha=0.7)
        axs[0, 0].legend()
        
        # Hiển thị giá trị cuối cùng (định dạng .4f để giữ độ chính xác thập phân)
        last_x = len(y_data) - 1
        last_y = y_data[-1]
        axs[0, 0].annotate(f'{last_y:.4f}', xy=(last_x, last_y), xytext=(5, 5), 
                           textcoords='offset points', color='green', fontweight='bold')
        
    # Đồ thị 2: Box Loss
    if val_box_loss_full:
        y_data = val_box_loss_full[:limit]
        axs[0, 1].plot(y_data, label='Validation Box Loss', color='red', linewidth=2)
        axs[0, 1].set_title(f'Sai số khung Box Loss ({limit} Epochs)')
        axs[0, 1].set_xlabel('Epochs')
        axs[0, 1].set_ylabel('Loss')
        axs[0, 1].grid(True, linestyle='--', alpha=0.7)
        axs[0, 1].legend()

        # Hiển thị giá trị cuối cùng
        last_x = len(y_data) - 1
        last_y = y_data[-1]
        axs[0, 1].annotate(f'{last_y:.4f}', xy=(last_x, last_y), xytext=(5, 5), 
                           textcoords='offset points', color='red', fontweight='bold')

    # Đồ thị 3: Precision
    if precision_full:
        y_data = precision_full[:limit]
        axs[1, 0].plot(y_data, label='Precision', color='blue', linewidth=2)
        axs[1, 0].set_title(f'Precision - Độ chính xác ({limit} Epochs)')
        axs[1, 0].set_xlabel('Epochs')
        axs[1, 0].set_ylabel('Precision')
        axs[1, 0].grid(True, linestyle='--', alpha=0.7)
        axs[1, 0].legend()

        # Hiển thị giá trị cuối cùng
        last_x = len(y_data) - 1
        last_y = y_data[-1]
        axs[1, 0].annotate(f'{last_y:.4f}', xy=(last_x, last_y), xytext=(5, 5), 
                           textcoords='offset points', color='blue', fontweight='bold')

    # Đồ thị 4: Recall
    if recall_full:
        y_data = recall_full[:limit]
        axs[1, 1].plot(y_data, label='Recall', color='orange', linewidth=2)
        axs[1, 1].set_title(f'Recall - Độ bao phủ ({limit} Epochs)')
        axs[1, 1].set_xlabel('Epochs')
        axs[1, 1].set_ylabel('Recall')
        axs[1, 1].grid(True, linestyle='--', alpha=0.7)
        axs[1, 1].legend()
        
        # Hiển thị giá trị cuối cùng
        last_x = len(y_data) - 1
        last_y = y_data[-1]
        axs[1, 1].annotate(f'{last_y:.4f}', xy=(last_x, last_y), xytext=(5, 5), 
                           textcoords='offset points', color='orange', fontweight='bold')
        
    plt.tight_layout(pad=2.0)
    plt.show()

else:
    print(" File .pt này không lưu trữ mảng 'train_results'.")

if 'model' in ckpt:
    model = ckpt['model']
    
    # Kiểm tra xem mô hình có thuộc tính 'names' không
    if hasattr(model, 'names'):
        print("\n=========================================")
        print(f" TÌM THẤY TỔNG CỘNG {len(model.names)} CLASSES:")
        print("=========================================")
        
        # In ra dạng đẹp: ID - Tên Class
        for class_id, class_name in model.names.items():
            print(f"ID {class_id}: {class_name}")
    else:
        print(" Không tìm thấy thuộc tính 'names' trong đối tượng model.")
        
# 1. Xem các khóa (keys) chính có trong file
# Thông thường YOLO sẽ có các keys như: 'epoch', 'best_fitness', 'model', 'optimizer', 'train_args'


# print("Các thành phần trong file .pt:", ckpt.keys())

# 2. Xem thông số huấn luyện (nếu có)
if 'train_args' in ckpt:
    args_to_print = ckpt['train_args'].copy()
    if 'data' in args_to_print:
        del args_to_print['data']
    if 'epochs' in args_to_print:
        del args_to_print['epochs']
            
#    print("\nCác tham số khi huấn luyện (Hyperparameters):")   
#    print(args_to_print)
#    print("\nKết quả Metrics (mAP, Precision, Recall):")
#    print(ckpt['train_metrics'])

# 3. Xem danh sách các tham số (weights) của mô hình
if 'model' in ckpt:
    model = ckpt['model']
    # Nếu 'model' là một object toàn vẹn (entire model)
    if hasattr(model, 'state_dict'):
        state_dict = model.state_dict()
    # Nếu 'model' chỉ là state_dict
    elif isinstance(model, dict):
        state_dict = model
    else:
        state_dict = {}

epochs = list(range(1, limit + 1))
map50_95_full = history.get('metrics/mAP50-95(B)')
# 2. Đóng gói các mảng dữ liệu vào một Dictionary

data_export = {
    'Epoch': epochs,
    'mAP_0.5': map50_full[:limit],
    'mAP_0.5_0.95': map50_95_full[:limit],
    'Val_Box_Loss': val_box_loss_full[:limit],
    'Precision': precision_full[:limit],
    'Recall': recall_full[:limit]
}

# 3. Tạo bảng dữ liệu (DataFrame) bằng Pandas
df = pd.DataFrame(data_export)

# 4. Chỉ định đường dẫn lưu file (lưu cùng thư mục models của bạn)
csv_save_path = r'D:\Desktop\DATN\Ocr\models\training_metrics.csv'

# 5. Xuất ra file CSV
# index=False để không in thêm cột số thứ tự mặc định của Pandas
df.to_csv(csv_save_path, index=False, encoding='utf-8')

print("\n=========================================")
print(f" Đã lưu bảng số liệu thành công!")
print(f" Vị trí file: {csv_save_path}")
print("=========================================")