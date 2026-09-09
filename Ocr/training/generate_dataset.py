import cv2
import numpy as np
import os
import random
from pathlib import Path

def create_synthetic_image(letter, img_size=40):
    # 1. Background (nền xám/trắng nhiễu như giấy thi)
    bg_color = random.randint(220, 255)
    img = np.full((img_size, img_size, 3), bg_color, dtype=np.uint8)
    
    # Noise nhẹ
    noise = np.random.randint(0, 15, (img_size, img_size, 3), dtype=np.uint8)
    img = cv2.subtract(img, noise)

    # 2. Draw the Letter (A, B, C, D)
    # Dùng font Complex để giống font serif trong đề thi
    font = cv2.FONT_HERSHEY_COMPLEX
    font_scale = random.uniform(0.7, 0.9)
    thickness = random.randint(1, 2)
    
    # Calculate text size and center it
    text_size, _ = cv2.getTextSize(letter, font, font_scale, thickness)
    text_x = (img_size - text_size[0]) // 2 + random.randint(-2, 2)
    text_y = (img_size + text_size[1]) // 2 + random.randint(-2, 2)
    
    # Màu chữ đen hoặc xám đậm
    char_color = (random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
    cv2.putText(img, letter, (text_x, text_y), font, font_scale, char_color, thickness, cv2.LINE_AA)

    # 3. Draw a simulated hand-drawn circle/ellipse
    center_x = img_size // 2 + random.randint(-4, 4)
    center_y = img_size // 2 + random.randint(-4, 4)
    axes_x = img_size // 2 - random.randint(2, 6)
    axes_y = img_size // 2 - random.randint(2, 6)
    angle = random.randint(0, 360)
    
    # Bút bi (xanh, đen) hoặc bút chì (xám)
    pen_types = [
        (random.randint(150, 255), random.randint(0, 50), random.randint(0, 50)), # Blue ink (BGR)
        (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)),    # Black ink
        (random.randint(80, 120), random.randint(80, 120), random.randint(80, 120)) # Pencil
    ]
    pen_color = random.choice(pen_types)
    pen_thickness = random.randint(1, 2)
    
    # Draw ellipse
    cv2.ellipse(img, (center_x, center_y), (axes_x, axes_y), angle, 0, 360, pen_color, pen_thickness, cv2.LINE_AA)

    # 4. Final Blur to simulate low-res crop
    if random.random() > 0.5:
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
    return img

def main():
    base_dir = Path("dataset_ocr")
    classes = ['A', 'B', 'C', 'D']
    
    for split in ['train', 'val']:
        for cls in classes:
            (base_dir / split / cls).mkdir(parents=True, exist_ok=True)
            
    num_train = 1000
    num_val = 200
    
    print("Generating Synthetic Dataset for OCR ABCD...")
    for cls in classes:
        print(f"Generating {cls}...")
        for i in range(num_train):
            img = create_synthetic_image(cls)
            cv2.imwrite(str(base_dir / 'train' / cls / f"{i:04d}.jpg"), img)
            
        for i in range(num_val):
            img = create_synthetic_image(cls)
            cv2.imwrite(str(base_dir / 'val' / cls / f"{i:04d}.jpg"), img)
            
    print("Dataset generation complete!")

if __name__ == "__main__":
    main()
