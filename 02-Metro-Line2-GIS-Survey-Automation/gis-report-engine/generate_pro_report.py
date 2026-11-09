import os
import docx
from docx.shared import Inches, Pt, Mm, RGBColor
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

def set_cell_background(cell, color_hex):
    """Tô màu nền cho ô"""
    shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_hex))
    cell._tc.get_or_add_tcPr().append(shading_elm)

def style_cell(cell, bold=False, align="left"):
    """Format chữ trong ô"""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for paragraph in cell.paragraphs:
        if align == "center":
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            run.bold = bold

def add_full_row(table, text, color):
    """Thêm 1 dòng gộp 4 cột"""
    row = table.add_row()
    cell = row.cells[0]
    cell.merge(row.cells[3])
    cell.text = text
    set_cell_background(cell, color)
    style_cell(cell, bold=True)
    return row

def add_2_2_row(table, text1, text2, color):
    """Thêm 1 dòng chia làm 2 ô (mỗi ô gộp 2 cột)"""
    row = table.add_row()
    cell1 = row.cells[0]
    cell1.merge(row.cells[1])
    cell1.text = text1
    
    cell2 = row.cells[2]
    cell2.merge(row.cells[3])
    cell2.text = text2
    
    set_cell_background(cell1, color)
    set_cell_background(cell2, color)
    style_cell(cell1, bold=True)
    style_cell(cell2, bold=False)
    return row

def add_4_cols_row(table, t1, t2, t3, t4, color, bold_headers=False):
    """Thêm 1 dòng 4 cột riêng biệt"""
    row = table.add_row()
    texts = [t1, t2, t3, t4]
    for i in range(4):
        row.cells[i].text = str(texts[i])
        set_cell_background(row.cells[i], color)
        style_cell(row.cells[i], bold=(bold_headers and i==0))
    return row

def build_professional_report(st_id, st_name):
    print(f"[*] Đang dựng báo cáo CHUYÊN NGHIỆP cho {st_name}...")
    doc = docx.Document()
    
    # ---------------------------------------------------------
    # PHẦN 1: BẢNG 1 - ĐẶC ĐIỂM CƠ BẢN (THỐNG KÊ CHI TIẾT)
    # ---------------------------------------------------------
    title = doc.add_heading(f'PHỤ LỤC: KHẢO SÁT GA {st_name.upper()}', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_heading(f'Bảng TD 1: Đặc điểm cơ bản của nhà ga {st_name}', level=2)
    
    table1 = doc.add_table(rows=0, cols=4)
    table1.style = 'Table Grid'
    
    # Kích thước các cột (Cột 1 to nhất)
    table1.columns[0].width = Inches(3.0)
    table1.columns[1].width = Inches(1.0)
    table1.columns[2].width = Inches(1.0)
    table1.columns[3].width = Inches(1.0)

    # --- Header (Xanh lá) ---
    C_GREEN = "33CC66"
    add_full_row(table1, f"Tên nhà ga: {st_name}", C_GREEN)
    add_2_2_row(table1, f"Mã số nhà ga: {st_id}", "Vị trí đặt ga: Ga ngầm", C_GREEN)
    add_2_2_row(table1, "Lý trình nhà ga: Km1+261.5", "Loại nhà ga: Trung chuyển", C_GREEN)
    add_full_row(table1, "Theo TRICC Km1+830", C_GREEN)

    # --- Dân số (Vàng) ---
    C_YELLOW = "FFFF00"
    add_4_cols_row(table1, "Điều kiện kinh tế - xã hội của khu vực nhà ga", "Phạm vi 500m", "500m-1km", "Tổng cộng", C_YELLOW, True)
    add_4_cols_row(table1, "Dân số (1)", "14278", "42835", "57113", C_YELLOW)
    add_4_cols_row(table1, "Mật độ dân số (người/ha)", "182", "182", "182", C_YELLOW)
    add_4_cols_row(table1, "Số lượng việc làm", "6742", "20227", "26969", C_YELLOW)

    # --- Dự báo (Xanh dương) ---
    C_BLUE = "99CCFF"
    add_4_cols_row(table1, "Dự báo nhu cầu (hàng ngày) (2)", "2020", "2025", "2030", C_BLUE, True)
    add_4_cols_row(table1, "Số lượt khách lên tàu", "35550", "56000", "76450", C_BLUE)
    add_4_cols_row(table1, "Số lượt khách xuống tàu", "35550", "56000", "76450", C_BLUE)

    # --- Địa giới (Cam) ---
    C_ORANGE = "FFCC99"
    add_full_row(table1, "Địa giới hành chính trong phạm vi 1km xung quanh nhà ga metro", C_ORANGE)
    add_2_2_row(table1, "Quận: 1", "Quận lân cận: 3", C_ORANGE)

    doc.add_page_break()

    # ---------------------------------------------------------
    # PHẦN 2: BẢNG 2 - KHẢO SÁT THỰC ĐỊA & HÌNH ẢNH (BẢNG ĐỘNG)
    # ---------------------------------------------------------
    doc.add_heading('PHẦN 2: KHẢO SÁT VÀ ĐÁNH GIÁ SƠ BỘ', level=1)
    doc.add_heading(f'Bảng TD 2: Khảo sát sơ bộ khu vực nhà ga {st_name}', level=2)

    table2 = doc.add_table(rows=1, cols=4)
    table2.style = 'Table Grid'
    
    hdr_cells = table2.rows[0].cells
    for i, text in enumerate(['Số TT', 'Hạng mục khảo sát', 'Nội dung chi tiết (AI Tổng hợp)', 'Hình ảnh minh chứng']):
        hdr_cells[i].text = text
        set_cell_background(hdr_cells[i], "D9D9D9")
        style_cell(hdr_cells[i], bold=True, align="center")

    table2.columns[0].width = Inches(0.5)
    table2.columns[1].width = Inches(1.5)
    table2.columns[2].width = Inches(2.5)
    table2.columns[3].width = Inches(3.0)

    # Các Hạng mục chuẩn theo Master Plan
    categories = [
        ("1", "Hành lang tiếp cận và Lối vào ga", "Vỉa hè hiện trạng rộng 3m, đủ tiêu chuẩn bố trí lối đi bộ. Tuy nhiên, vị trí cửa lên xuống số 1 đang bị vướng cây xanh và trụ điện."),
        ("2", "Hạ tầng Giao thông công cộng (Bus)", "Cách ga 100m có trạm dừng xe buýt số 23, 61. Cần dịch chuyển trạm về sát cửa ga để hành khách dễ dàng trung chuyển."),
        ("3", "Bãi đậu xe (P&R) và PUDO", "Quanh ga không có bãi đất trống lớn để làm bãi giữ xe máy. Đề xuất khoét vỉa hè đường Phan Văn Hớn làm điểm đỗ taxi (PUDO)."),
        ("4", "Tiện ích Xã hội & Thương mại", "Khu vực tập trung đông dân cư, có trường cấp 2 và dãy phố thương mại sầm uất, tiềm năng thu hút lượng lớn khách sử dụng Metro."),
        ("5", "Rào cản & Xung đột giao thông", "Thường xuyên ùn tắc vào giờ cao điểm do hàng rong lấn chiếm vỉa hè. Mạng lưới điện chằng chịt cần ngầm hóa.")
    ]

    data_dir = os.path.join("data", st_id)
    images = []
    if os.path.exists(data_dir):
        images = sorted([f for f in os.listdir(data_dir) if f.lower().endswith(('.jpg', '.png'))])

    for cat_num, cat_title, cat_content in categories:
        row = table2.add_row()
        row.cells[0].text = cat_num
        row.cells[1].text = cat_title
        row.cells[2].text = cat_content
        
        # Nhét 2 ảnh vào mỗi hạng mục (nếu có)
        img_cell = row.cells[3]
        para = img_cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        for _ in range(2):
            if len(images) > 0:
                img_file = images.pop(0)
                run = para.add_run()
                try:
                    run.add_picture(os.path.join(data_dir, img_file), width=Inches(2.5))
                    para.add_run(f"\n{cat_title} - {img_file}\n")
                except: pass
                
        style_cell(row.cells[0], align="center")
        style_cell(row.cells[1], bold=True, align="center")
        style_cell(row.cells[2])

    doc.add_page_break()
    
    # ---------------------------------------------------------
    # PHẦN 3: KẾT LUẬN & ĐỀ XUẤT CỦA CHUYÊN GIA
    # ---------------------------------------------------------
    doc.add_heading('PHẦN 3: KẾT LUẬN & ĐỀ XUẤT', level=1)
    doc.add_paragraph("Dựa trên các dữ liệu khảo sát, nhà ga có tiềm năng tiếp cận rất tốt nhờ hệ thống xe buýt lân cận. Tuy nhiên, rào cản lớn nhất là tình trạng lấn chiếm vỉa hè.")
    doc.add_paragraph("Đề xuất:")
    doc.add_paragraph("- Giải tỏa hàng rong khu vực bán kính 200m.")
    doc.add_paragraph("- Bổ sung thêm bãi giữ xe máy tại vị trí đất trống hẻm 12.")

    os.makedirs("output", exist_ok=True)
    out_path = os.path.join("output", f"BaoCao_Master_{st_id}.docx")
    doc.save(out_path)
    print(f"[+] Hoàn tất! Bản Template Báo cáo Chuẩn đã lưu tại: {out_path}")

if __name__ == "__main__":
    build_professional_report("S1", "Phan Văn Hớn")
