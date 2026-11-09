import time
import random
import os
from ultralytics import YOLO

# Khởi tạo mô hình YOLOv8 nano (nhỏ gọn nhất, tải tự động từ mạng nếu chưa có)
# Sẽ tạo file yolov8n.pt trong thư mục gốc
model = YOLO("yolov8n.pt")

def run_mock_inference(batch_id: str, image_path: str = None):
    """
    Sử dụng YOLOv8 để quét ảnh thực tế thay vì giả lập hoàn toàn.
    """
    print(f"[{batch_id}] AI (YOLOv8) is analyzing image...")
    
    # Nếu không có ảnh, dùng fallback logic (để không bị lỗi nếu FE chưa gửi ảnh)
    if not image_path or not os.path.exists(image_path):
        print("Không tìm thấy ảnh, sử dụng giả lập fallback.")
        total_weight_kg = 10.0
        melon_count = 0
    else:
        # Hạ mức tự tin xuống cực thấp (5%) để nó "cố gắng" tìm thêm các vật thể
        # Thêm agnostic_nms=True để ngăn các hộp đè lên nhau bị xóa
        results = model(image_path, conf=0.05, iou=0.4, agnostic_nms=True)
        
        # Đếm số lượng vật thể nhận diện được (bounding boxes)
        box_count = len(results[0].boxes)
            
        melon_count = box_count
        # Giả lập mỗi quả dưa nặng khoảng 1.5kg
        total_weight_kg = box_count * 1.5
        
        # Xóa ảnh tạm sau khi xử lý xong
        try:
            os.remove(image_path)
        except:
            pass

    # Giả lập tỷ lệ lỗi ngẫu nhiên từ 1% đến 5% cho chất lượng (bề mặt)
    error_rate = random.uniform(0.01, 0.05)
    bad_weight = round(total_weight_kg * error_rate, 2)
    type1_weight = round(total_weight_kg - bad_weight, 2)
    
    return {
        "batch_id": batch_id,
        "total_weight": total_weight_kg,
        "melon_count": melon_count, # Thêm thuộc tính đếm số quả dưa
        "type_1": type1_weight,
        "bad_quality": bad_weight,
        "status": "success"
    }
