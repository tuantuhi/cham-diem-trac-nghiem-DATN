import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

def plot_adaptive_threshold(ratios: list[float], threshold: float, save_path: str = None):
    """
    Vẽ biểu đồ phân phối tỷ lệ điền đầy (Fill Ratio Histogram) và hiển thị ngưỡng.
    
    Tham số:
        ratios: Danh sách các tỷ lệ điền đầy (từ 0.0 đến 1.0) của tất cả các ô bong bóng.
        threshold: Ngưỡng thích nghi đã được tính toán ở Bước 5.
        save_path: Đường dẫn để lưu ảnh (nếu muốn lưu thay vì chỉ hiển thị).
    """
    ratios_arr = np.array(ratios, dtype=np.float32)
    
    # 1. Tái hiện lại logic tính toán Histogram như trong Bước 5 của bạn
    hist, bin_edges = np.histogram(ratios_arr, bins=50, range=(0.0, 1.0))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    # Làm mịn biểu đồ để tìm đỉnh dễ hơn
    hist_smooth = uniform_filter1d(hist.astype(float), size=3)
    
    # Tìm các đỉnh (Peaks) để hiển thị lên biểu đồ
    peaks, _ = find_peaks(hist_smooth, height=1, distance=4)
    
    # 2. Thiết lập biểu đồ
    plt.figure(figsize=(10, 6))
    
    # Vẽ biểu đồ cột (Histogram gốc)
    plt.bar(bin_centers, hist, width=1/50, alpha=0.4, color='gray', 
            edgecolor='black', label='Phân phối thực tế (Histogram)')
    
    # Vẽ đường cong làm mịn (Smoothed curve)
    plt.plot(bin_centers, hist_smooth, color='blue', linewidth=2, 
             label='Đường cong phân phối (Smoothed)')
    
    # Đánh dấu các đỉnh tìm được
    if len(peaks) > 0:
        plt.plot(bin_centers[peaks], hist_smooth[peaks], "x", color='red', 
                 markersize=8, markeredgewidth=2, label='Các đỉnh (Peaks)')
    
    # Vẽ đường thẳng đứng thể hiện Ngưỡng (Threshold)
    plt.axvline(x=threshold, color='green', linestyle='--', linewidth=2.5, 
                label=f'Ngưỡng phân tách = {threshold:.3f}')
    
    # Tùy chỉnh màu nền cho 2 vùng: Trống và Đã tô
    plt.axvspan(0, threshold, alpha=0.1, color='red', label='Vùng nhận diện: TRỐNG')
    plt.axvspan(threshold, 1, alpha=0.1, color='green', label='Vùng nhận diện: ĐÃ TÔ')
    
    # 3. Định dạng nhãn và hiển thị
    plt.title("Biểu đồ phân phối tỷ lệ điền đầy (Fill Ratio) & Ngưỡng thích nghi", fontsize=14, fontweight='bold')
    plt.xlabel("Tỷ lệ điền đầy (Fill Ratio: 0.0 -> 1.0)", fontsize=12)
    plt.ylabel("Số lượng ô bong bóng (Count)", fontsize=12)
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='upper right', framealpha=0.9)
    plt.tight_layout()
    
    # Lưu hoặc Hiển thị
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Đã lưu biểu đồ tại: {save_path}")
    else:
        plt.show()

# ==========================================
# KHỐI CHẠY THỬ VỚI DỮ LIỆU GIẢ LẬP
# ==========================================
if __name__ == "__main__":
    # Giả lập tỷ lệ điền đầy của một bài thi:
    # - 150 ô trống (tỷ lệ quanh mức 0.05 - 0.15 do nhiễu giấy/bút chì mờ)
    # - 50 ô đã tô (tỷ lệ quanh mức 0.6 - 0.8)
    empty_bubbles = np.random.normal(loc=0.08, scale=0.03, size=150)
    filled_bubbles = np.random.normal(loc=0.70, scale=0.08, size=50)
    
    # Gộp chung và giới hạn giá trị trong khoảng [0, 1]
    mock_ratios = np.clip(np.concatenate([empty_bubbles, filled_bubbles]), 0.0, 1.0).tolist()
    
    # Giả sử hàm compute_adaptive_fill_threshold của bạn tính ra ngưỡng là 0.35
    mock_computed_threshold = 0.35
    
    # Gọi hàm để hiển thị
    plot_adaptive_threshold(mock_ratios, mock_computed_threshold)