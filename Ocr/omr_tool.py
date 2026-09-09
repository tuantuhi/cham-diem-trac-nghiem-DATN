import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- CẤU HÌNH ---
IMAGE_PATH = r'D:\Desktop\DATN\Ocr\Mau_20.png'
WARP_WIDTH = 1400
WARP_HEIGHT = 2000

clicked_xs = []
clicked_ys = []

def get_four_corners(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    squares = []
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        area = cv2.contourArea(c)
        if len(approx) == 4 and 100 < area < 10000:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                squares.append([cX, cY])
                
    if len(squares) < 4:
        raise ValueError("Không tìm đủ 4 ô đen ở các góc!")
        
    squares = np.array(squares)
    rect = np.zeros((4, 2), dtype="float32")
    s = squares.sum(axis=1)
    rect[0] = squares[np.argmin(s)] 
    rect[2] = squares[np.argmax(s)] 
    
    diff = np.diff(squares, axis=1)
    rect[1] = squares[np.argmin(diff)] 
    rect[3] = squares[np.argmax(diff)] 
    return rect

def onclick(event, ax, warped_rgb):
    """Xử lý sự kiện click trên Matplotlib"""
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        clicked_xs.append(x)
        clicked_ys.append(y)
        print(f" Đã chấm: X = {x}, Y = {y}")
        
        # Vẽ chấm đỏ
        ax.plot(x, y, 'ro', markersize=4)
        plt.draw()

def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(" Không tìm thấy ảnh!")
        return

    print(" Đang xử lý kéo phẳng ảnh...")
    try:
        src_points = get_four_corners(img)
    except Exception as e:
        print(f" Lỗi: {e}")
        return

    dst_points = np.array([
        [0, 0], [WARP_WIDTH - 1, 0],
        [WARP_WIDTH - 1, WARP_HEIGHT - 1], [0, WARP_HEIGHT - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(img, matrix, (WARP_WIDTH, WARP_HEIGHT))
    
    # Chuyển BGR (OpenCV) sang RGB (Matplotlib) để hiển thị màu chuẩn
    warped_rgb = cv2.cvtColor(warped, cv2.COLOR_BGR2RGB)
    
    print(" Đã xử lý xong!")
    print("\n--- HƯỚNG DẪN ---")
    print("1. Click chuột TRÁI vào tâm các ô để lấy tọa độ.")
    print("2. Đóng cửa sổ (dấu X góc phải) để kết thúc và in kết quả.")

    fig, ax = plt.subplots(figsize=(8, 12)) # Kích thước cửa sổ
    ax.imshow(warped_rgb)
    ax.set_title("Click để lấy tọa độ. Đóng cửa sổ để kết thúc.")
    
    # Kết nối sự kiện click chuột
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, ax, warped_rgb))
    
    plt.show() # Hàm này sẽ tạm dừng code cho đến khi bạn đóng cửa sổ

    # In kết quả sau khi đóng cửa sổ
    print("\n" + "="*40)
    print(" KẾT QUẢ TỌA ĐỘ")
    print(f"xs = {clicked_xs}")
    print(f"ys = {clicked_ys}")
    print("="*40)

if __name__ == "__main__":
    main()