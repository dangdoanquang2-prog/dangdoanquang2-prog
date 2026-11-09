import sys
import os
import datetime
import io
from PIL import Image
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"
st01_dir = os.path.join(base_dir, "ST01")
output_docx = os.path.join(base_dir, "MRT2S_KSGT_NV8_02_Phu_Luc_Hinh_Anh_Hien_Truong_ST01.docx")

print("=== BẮT ĐẦU TẠO TẬP HỒ SƠ PHỤ LỤC ẢNH HIỆN TRƯỜNG TIMEMARK GPS - GA ST01 ===")

# Helpers format
def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=40, bottom=40, left=50, right=50):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), val)
            border.set(qn('w:sz'), sz)
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), color)
            borders.append(border)
        tblPr[0].append(borders)

def add_scaled_picture(p, img_path, max_w_in=3.35, max_h_in=2.5):
    im = Image.open(img_path)
    w_px, h_px = im.size
    aspect = w_px / h_px
    
    calc_w = max_w_in
    calc_h = calc_w / aspect
    if calc_h > max_h_in:
        calc_h = max_h_in
        calc_w = calc_h * aspect
        
    run = p.add_run()
    run.add_picture(img_path, width=Inches(calc_w), height=Inches(calc_h))

# Lấy toàn bộ danh sách 84 ảnh và sắp xếp theo thời gian
files = [f for f in os.listdir(st01_dir) if f.lower().endswith('.jpg')]
records = []
for f in files:
    parts = f.split('_')
    epoch_ms = int(parts[0])
    dt = datetime.datetime.fromtimestamp(epoch_ms / 1000.0)
    records.append((dt, os.path.join(st01_dir, f)))

records.sort(key=lambda x: x[0])
print(f"Tìm thấy tổng cộng: {len(records)} hình ảnh hiện trường có định vị GPS Timemark.")

# Nhóm thành các cụm khảo sát
bursts = []
curr_burst = [records[0]]
for r in records[1:]:
    if (r[0] - curr_burst[-1][0]).total_seconds() > 300:
        bursts.append(curr_burst)
        curr_burst = [r]
    else:
        curr_burst.append(r)
if curr_burst:
    bursts.append(curr_burst)

burst_names = [
    "CỤM 1: TUYẾN ĐƯỜNG TRƯỜNG CHINH & KHU VỰC THƯƠNG MẠI - DỊCH VỤ - CHỢ (MÃ MS1)",
    "CỤM 2: KHU DÂN CƯ ĐÔNG HƯNG THUẬN & CÁC KHU NHÀ Ở LÂN CẬN (MÃ RS1)",
    "CỤM 3: TUYẾN ĐƯỜNG PHAN VĂN HỚN, TÂN THỚI NHẤT & CÁC CÔNG TRÌNH GIÁO DỤC (MÃ SS1 & MS1)"
]

doc = Document()

# Cấu hình lề A4
section = doc.sections[0]
section.top_margin = Inches(0.55)
section.bottom_margin = Inches(0.55)
section.left_margin = Inches(0.65)
section.right_margin = Inches(0.55)
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)

# Header & Footer
header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hrun = hp.add_run("HỒ SƠ ẢNH HIỆN TRƯỜNG TIMEMARK GPS | PHỤ LỤC MRT2S - KSGT - NV8 - 02")
hrun.font.name = "Arial"
hrun.font.size = Pt(8.5)
hrun.font.color.rgb = RGBColor(120, 120, 120)

footer = section.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
frun = fp.add_run("Dự án Tuyến Metro số 2 & Tuyến 2S TP.HCM – Nhiệm vụ 8: Khảo sát các điểm phát sinh nhu cầu lớn")
frun.font.name = "Arial"
frun.font.size = Pt(8)
frun.font.color.rgb = RGBColor(140, 140, 140)

# ==============================================================================
# TRANG BÌA TẬP HỒ SƠ PHỤ LỤC ẢNH
# ==============================================================================
p_gov = doc.add_paragraph()
p_gov.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_gov.paragraph_format.space_before = Pt(35)
p_gov.paragraph_format.space_after = Pt(2)
r_gov = p_gov.add_run("ỦY BAN NHÂN DÂN THÀNH PHỐ HỒ CHÍ MINH\nBAN QUẢN LÝ ĐƯỜNG SẮT ĐÔ THỊ (MAUR)")
r_gov.font.name = "Arial"
r_gov.font.size = Pt(11)
r_gov.font.bold = True
r_gov.font.color.rgb = RGBColor(30, 45, 75)

p_line1 = doc.add_paragraph()
p_line1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_line1.paragraph_format.space_before = Pt(2)
p_line1.paragraph_format.space_after = Pt(25)
r_l1 = p_line1.add_run("━━━━━━━ ★ ━━━━━━━")
r_l1.font.size = Pt(9)
r_l1.font.color.rgb = RGBColor(180, 40, 40)

p_proj = doc.add_paragraph()
p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_proj.paragraph_format.space_after = Pt(25)
r_proj = p_proj.add_run(
    "DỰ ÁN ĐẦU TƯ XÂY DỰNG TUYẾN TÀU ĐIỆN NGẦM SỐ 2 TP. HỒ CHÍ MINH\n"
    "(ĐOẠN THAM LƯƠNG – AN HẠ VÀ TUYẾN 2S AN HẠ – CỦ CHI)"
)
r_proj.font.name = "Arial"
r_proj.font.size = Pt(12)
r_proj.font.bold = True
r_proj.font.color.rgb = RGBColor(40, 70, 120)

p_t1 = doc.add_paragraph()
p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_t1.paragraph_format.space_before = Pt(20)
p_t1.paragraph_format.space_after = Pt(8)
r_t1 = p_t1.add_run("HỒ SƠ TÀI LIỆU MINH CHỨNG KHẢO SÁT THỰC ĐỊA")
r_t1.font.name = "Arial"
r_t1.font.size = Pt(18)
r_t1.font.bold = True
r_t1.font.color.rgb = RGBColor(180, 40, 40)

p_t2 = doc.add_paragraph()
p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_t2.paragraph_format.space_after = Pt(35)
r_t2 = p_t2.add_run(
    "PHỤ LỤC MRT2S - KSGT - NV8 - 02:\n"
    "ALBUM HÌNH ẢNH KHẢO SÁT HIỆN TRƯỜNG ĐÓNG DẤU TIMEMARK GPS\n"
    "KHU VỰC NHÀ GA ST01 (TÂN SƠN NHẤT / PHAN VĂN HỚN)"
)
r_t2.font.name = "Arial"
r_t2.font.size = Pt(13)
r_t2.font.bold = True
r_t2.font.color.rgb = RGBColor(20, 50, 100)

tbl_info = doc.add_table(rows=4, cols=2)
tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_info, color="B0C4DE", sz="4")
info_meta = [
    ("Nhiệm vụ khảo sát:", "Nhiệm vụ 8: Khảo sát các điểm phát sinh nhu cầu lớn (Trip Generation)"),
    ("Địa bàn khảo sát:", "Khu vực bán kính R ≈ 1.000m quanh tim nhà ga ST01 (Quận 12, TP.HCM)"),
    ("Tổng số ảnh hiện trường:", f"{len(records)} hình ảnh (chụp tự động định vị tọa độ GPS WGS-84, ngày giờ thực tế)"),
    ("Đơn vị thực hiện:", "LIÊN DANH TƯ VẤN THIẾT KẾ & KHẢO SÁT GIAO THÔNG")
]
tbl_widths = [Inches(2.2), Inches(4.3)]
for r_i, (lbl, val) in enumerate(info_meta):
    row_obj = tbl_info.rows[r_i]
    cell_l = row_obj.cells[0]
    cell_r = row_obj.cells[1]
    cell_l.width = tbl_widths[0]
    cell_r.width = tbl_widths[1]
    cell_l.text = lbl
    cell_r.text = val
    
    pl = cell_l.paragraphs[0]
    pl.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    rl = pl.runs[0]
    rl.font.name = "Arial"
    rl.font.size = Pt(8.5)
    rl.font.bold = True
    rl.font.color.rgb = RGBColor(30, 50, 90)
    set_cell_background(cell_l, "F4F7FA")
    set_cell_margins(cell_l, top=40, bottom=40, left=50, right=50)
    
    pr = cell_r.paragraphs[0]
    pr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rr = pr.runs[0]
    rr.font.name = "Arial"
    rr.font.size = Pt(8.5)
    rr.font.color.rgb = RGBColor(40, 40, 40)
    set_cell_background(cell_r, "FFFFFF")
    set_cell_margins(cell_r, top=40, bottom=40, left=50, right=50)

p_date = doc.add_paragraph()
p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_date.paragraph_format.space_before = Pt(65)
r_date = p_date.add_run("THÀNH PHỐ HỒ CHÍ MINH – THÁNG 9/2026")
r_date.font.name = "Arial"
r_date.font.size = Pt(11)
r_date.font.bold = True
r_date.font.color.rgb = RGBColor(100, 100, 100)

doc.add_page_break()

# ==============================================================================
# NỘI DUNG ALBUM ẢNH PHÂN THEO TỪNG CỤM
# ==============================================================================
global_img_idx = 1

for b_idx, burst in enumerate(bursts):
    b_title = burst_names[b_idx] if b_idx < len(burst_names) else f"CỤM {b_idx+1}: KHẢO SÁT THỰC ĐỊA BỔ SUNG"
    
    p_bh = doc.add_paragraph()
    p_bh.paragraph_format.space_before = Pt(4)
    p_bh.paragraph_format.space_after = Pt(2)
    r_bh = p_bh.add_run(b_title)
    r_bh.font.name = "Arial"
    r_bh.font.size = Pt(11.5)
    r_bh.font.bold = True
    r_bh.font.color.rgb = RGBColor(180, 40, 40)
    
    t_start = burst[0][0].strftime('%d/%m/%Y %H:%M')
    t_end = burst[-1][0].strftime('%H:%M')
    
    p_bd = doc.add_paragraph()
    p_bd.paragraph_format.space_after = Pt(4)
    r_bd = p_bd.add_run(
        f"Thời gian khảo sát: {t_start} – {t_end} | Số lượng ảnh ghi nhận: {len(burst)} ảnh. "
        f"Các hình ảnh đều được chụp trực tiếp qua ứng dụng định vị chuyên dụng Timemark có đóng dấu GPS tọa độ WGS-84 tự động:"
    )
    r_bd.font.name = "Arial"
    r_bd.font.size = Pt(8.5)
    
    # Bảng 2 ảnh / hàng
    num_rows = (len(burst) + 1) // 2 * 2
    tbl = doc.add_table(rows=num_rows, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, val="none")
    
    for i in range(0, len(burst), 2):
        row_img = tbl.rows[(i // 2) * 2]
        row_cap = tbl.rows[(i // 2) * 2 + 1]
        
        # Ảnh trái
        dt_l, path_l = burst[i]
        c_il = row_img.cells[0]
        c_cl = row_cap.cells[0]
        c_il.width = Inches(3.5)
        c_cl.width = Inches(3.5)
        
        pl = c_il.paragraphs[0]
        pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pl.paragraph_format.space_after = Pt(0)
        add_scaled_picture(pl, path_l, max_w_in=3.4, max_h_in=2.5)
        
        pcl = c_cl.paragraphs[0]
        pcl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pcl.paragraph_format.space_before = Pt(1)
        pcl.paragraph_format.space_after = Pt(4)
        rcl = pcl.add_run(f"Ảnh TM-{global_img_idx:02d}: Hiện trường khảo sát ({dt_l.strftime('%H:%M:%S - %d/%m/%Y')})")
        rcl.font.name = "Arial"
        rcl.font.size = Pt(7.5)
        rcl.font.italic = True
        global_img_idx += 1
        
        # Ảnh phải (nếu có)
        if i + 1 < len(burst):
            dt_r, path_r = burst[i+1]
            c_ir = row_img.cells[1]
            c_cr = row_cap.cells[1]
            c_ir.width = Inches(3.5)
            c_cr.width = Inches(3.5)
            
            pr = c_ir.paragraphs[0]
            pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pr.paragraph_format.space_after = Pt(0)
            add_scaled_picture(pr, path_r, max_w_in=3.4, max_h_in=2.5)
            
            pcr = c_cr.paragraphs[0]
            pcr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pcr.paragraph_format.space_before = Pt(1)
            pcr.paragraph_format.space_after = Pt(4)
            rcr = pcr.add_run(f"Ảnh TM-{global_img_idx:02d}: Hiện trường khảo sát ({dt_r.strftime('%H:%M:%S - %d/%m/%Y')})")
            rcr.font.name = "Arial"
            rcr.font.size = Pt(7.5)
            rcr.font.italic = True
            global_img_idx += 1
            
    if b_idx < len(bursts) - 1:
        doc.add_page_break()

doc.save(output_docx)
print(f"\n>>> ĐÃ TẠO THÀNH CÔNG TẬP HỒ SƠ PHỤ LỤC ẢNH HIỆN TRƯỜNG: {output_docx}")
print(f"    Kích thước file: {os.path.getsize(output_docx):,} bytes")
