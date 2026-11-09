import os
import docx
from PIL import Image

def setup_mock_data():
    base_dir = r"d:\baocaotudong\data\S1"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(r"d:\baocaotudong\output", exist_ok=True)

    # 1. Create ghichu.docx
    doc = docx.Document()
    doc.add_heading('Ghi chú khảo sát Ga S1 - Phan Văn Hớn', 0)
    doc.add_paragraph('- Điểm nghẽn: Vỉa hè hẹp, có nhiều hàng rong.')
    doc.add_paragraph('- Lối đi: Có 2 lối đi, lối 1 rộng 5m, lối 2 hẻm nhỏ 2m.')
    doc.add_paragraph('- Bãi đỗ xe: Không có bãi đỗ xe chính thức, người dân gửi xe ở nhà dân.')
    doc.add_paragraph('Chú thích ảnh:')
    doc.add_paragraph('tong_quat.jpg: Ảnh toàn cảnh ga')
    doc.add_paragraph('loi_vao_1.jpg: Lối vào số 1')
    doc.add_paragraph('loi_vao_2.jpg: Lối vào số 2')
    doc.add_paragraph('bai_xe.jpg: Bãi đậu xe tạm')
    doc.save(os.path.join(base_dir, "ghichu.docx"))

    # 2. Create mock images
    colors = {
        'tong_quat.jpg': 'blue',
        'loi_vao_1.jpg': 'green',
        'loi_vao_2.jpg': 'orange',
        'bai_xe.jpg': 'red'
    }
    for name, color in colors.items():
        img = Image.new('RGB', (800, 600), color=color)
        img.save(os.path.join(base_dir, name))
    
    print("Mock data created successfully in data/S1/")

if __name__ == "__main__":
    setup_mock_data()
