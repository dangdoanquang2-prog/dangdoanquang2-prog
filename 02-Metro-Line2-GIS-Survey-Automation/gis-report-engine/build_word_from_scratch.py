import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

def set_cell_background(cell, color_hex):
    """Hàm tùy chỉnh để tô màu nền cho ô trong bảng (vì python-docx không hỗ trợ sẵn)"""
    shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_hex))
    cell._tc.get_or_add_tcPr().append(shading_elm)

def create_report_from_scratch(st_id, st_name):
    print(f"[*] Đang tự động vẽ báo cáo Word từ con số 0 cho ga {st_name}...")
    doc = docx.Document()

    # 1. TIÊU ĐỀ
    title = doc.add_heading(f'PHỤ LỤC: KHẢO SÁT GA {st_name.upper()}', 0)
    title.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER

    # 2. BẢNG KHẢO SÁT SƠ BỘ (Tương tự Bảng TD 2)
    doc.add_heading('Bảng 2: Khảo sát sơ bộ khu vực nhà ga', level=2)
    
    # Tạo bảng 4 cột
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    
    # Header
    hdr_cells = table.rows[0].cells
    headers = ['Số tham khảo', 'Thành phần', 'Nội dung', 'Hình TDvẽ']
    for i, text in enumerate(headers):
        hdr_cells[i].text = text
        set_cell_background(hdr_cells[i], "D9D9D9") # Màu xám nhạt

    # Chỉnh độ rộng cột (tương đối)
    table.columns[0].width = Inches(0.8)
    table.columns[1].width = Inches(1.0)
    table.columns[2].width = Inches(2.5)
    table.columns[3].width = Inches(3.0)

    # 3. ĐỌC DỮ LIỆU TỪ THƯ MỤC
    data_dir = os.path.join("data", st_id)
    if os.path.exists(data_dir):
        # Lấy danh sách ảnh
        images = [f for f in os.listdir(data_dir) if f.lower().endswith(('.jpg', '.png'))]
        
        # Tạo Row 1 (Ví dụ: Lối vào)
        row_cells = table.add_row().cells
        row_cells[0].text = "I"
        row_cells[1].text = "Vị trí (1)\ntrong Hình"
        row_cells[2].text = "LỐI VÀO GA:\nHiện tại có các lối vào nhà ga bị vướng vỉa hè..."
        
        # Chèn ảnh vào cột 4
        if len(images) > 0:
            img_path = os.path.join(data_dir, images[0])
            paragraph = row_cells[3].paragraphs[0]
            run = paragraph.add_run()
            run.add_picture(img_path, width=Inches(2.5))
            paragraph.add_run(f"\nHình: Lối vào nhà ga")
            images.pop(0)

        # Tạo Row 2 (Ví dụ: Bãi xe)
        row_cells = table.add_row().cells
        row_cells[0].text = "II"
        row_cells[1].text = "Vị trí (2)"
        row_cells[2].text = "BÃI ĐẬU XE:\nHiện tại có bãi đậu xe với quy mô nhỏ..."
        
        if len(images) > 0:
            img_path = os.path.join(data_dir, images[0])
            paragraph = row_cells[3].paragraphs[0]
            run = paragraph.add_run()
            run.add_picture(img_path, width=Inches(2.5))
            paragraph.add_run(f"\nHình: Bãi đậu xe hiện hữu")

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"BaoCao_TuSinh_{st_id}.docx")
    doc.save(out_path)
    print(f"[+] Đã tạo thành công: {out_path}")

if __name__ == "__main__":
    create_report_from_scratch("S1", "Phan Văn Hớn")
