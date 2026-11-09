import sys
import os
import zipfile
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
out_dir = os.path.join(base_dir, "ketqua")
os.makedirs(out_dir, exist_ok=True)
output_docx = os.path.join(out_dir, "Bao_cao_Tong_hop_Nhiem_vu_8_Ga_ST01.docx")

print("=== BẮT ĐẦU TẠO BÁO CÁO TỔNG HỢP NHIỆM VỤ 8 - GA ST01 ===")

# 1. Trích xuất ảnh mặt tiền từ ST01_Số liệu.docx
raw_docx_path = os.path.join(base_dir, "ST01_Số liệu.docx")
facade_images = {}
with zipfile.ZipFile(raw_docx_path, 'r') as z:
    for i in range(1, 12):
        name = f"word/media/image{i}.png"
        try:
            b = z.read(name)
            facade_images[i] = b
        except KeyError:
            pass

# 2. Ánh xạ sơ đồ PUDO từ ST01 MÔ TẢ
mota_dir = os.path.join(base_dir, "ST01 MÔ TẢ")
pudo_map = {
    1: os.path.join(mota_dir, "Screenshot 2026-09-16 162834.png"),
    2: os.path.join(mota_dir, "Screenshot 2026-09-16 163024.png"),
    3: os.path.join(mota_dir, "Screenshot 2026-09-16 162440.png"),
    4: os.path.join(mota_dir, "Screenshot 2026-09-16 163323.png"),
    5: os.path.join(mota_dir, "Screenshot 2026-09-16 163527.png"),
    6: os.path.join(mota_dir, "Screenshot 2026-09-16 164027.png"),
    7: os.path.join(mota_dir, "Screenshot 2026-09-18 115140.png"),
    8: os.path.join(mota_dir, "Screenshot 2026-09-16 164817.png"),
    9: os.path.join(mota_dir, "Screenshot 2026-09-16 161626.png"),
    10: os.path.join(mota_dir, "Screenshot 2026-09-16 162010.png"),
    11: os.path.join(mota_dir, "Screenshot 2026-09-16 165231.png"),
}
overview_map_path = os.path.join(mota_dir, "Screenshot 2026-09-18 122910.png")

# 3. Trích xuất thông tin chi tiết 11 công trình
raw_doc = Document(raw_docx_path)
facility_data = []

for idx in range(1, 12):
    t_info = raw_doc.tables[(idx - 1) * 2 + 1]
    t_spec = raw_doc.tables[(idx - 1) * 2 + 2]
    
    info_rows = []
    for r in t_info.rows:
        cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
        dedup = []
        for ct in cells:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        info_rows.append(dedup)
        
    spec_rows = []
    for r in t_spec.rows:
        cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
        dedup = []
        for ct in cells:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        spec_rows.append(dedup)
        
    facility_data.append({
        "id": idx,
        "name": info_rows[0][1] if len(info_rows[0]) > 1 else f"Công trình {idx}",
        "type": info_rows[0][3] if len(info_rows[0]) > 3 else "N/A",
        "addr": info_rows[1][1] if len(info_rows[1]) > 1 else "N/A",
        "info_rows": info_rows,
        "spec_rows": spec_rows
    })

# Helpers format
def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=45, bottom=45, left=70, right=70):
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

def add_scaled_picture(p, img_source, max_w_in=3.35, max_h_in=2.45):
    if isinstance(img_source, (bytes, bytearray)):
        im = Image.open(io.BytesIO(img_source))
        stream = io.BytesIO(img_source)
    else:
        im = Image.open(img_source)
        stream = img_source
        
    w_px, h_px = im.size
    aspect = w_px / h_px
    
    calc_w = max_w_in
    calc_h = calc_w / aspect
    if calc_h > max_h_in:
        calc_h = max_h_in
        calc_w = calc_h * aspect
        
    run = p.add_run()
    run.add_picture(stream, width=Inches(calc_w), height=Inches(calc_h))

# Tạo document mới
doc = Document()

# Thiết lập lề A4 chuẩn
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
hrun = hp.add_run("BÁO CÁO TỔNG HỢP KẾT QUẢ KHẢO SÁT | NHIỆM VỤ 8 - GA ST01 (PHAN VĂN HỚN)")
hrun.font.name = "Arial"
hrun.font.size = Pt(8.5)
hrun.font.color.rgb = RGBColor(120, 120, 120)

footer = section.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
frun = fp.add_run("Dự án Tuyến Metro số 2 & Tuyến 2S TP.HCM – Nghiên cứu Trip Rate phục vụ mô hình PTV VISUM")
frun.font.name = "Arial"
frun.font.size = Pt(8)
frun.font.color.rgb = RGBColor(140, 140, 140)

# ==============================================================================
# TRANG BÌA: BÁO CÁO TỔNG HỢP NHIỆM VỤ 8 - GA ST01 (CHUẨN TƯ VẤN THIẾT KẾ)
# ==============================================================================
p_gov = doc.add_paragraph()
p_gov.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_gov.paragraph_format.space_before = Pt(25)
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

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(15)
p_title.paragraph_format.space_after = Pt(8)
r_t = p_title.add_run("BÁO CÁO TỔNG HỢP KẾT QUẢ KHẢO SÁT")
r_t.font.name = "Arial"
r_t.font.size = Pt(20)
r_t.font.bold = True
r_t.font.color.rgb = RGBColor(180, 40, 40)

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(35)
r_sub = p_sub.add_run(
    "NHIỆM VỤ 8: KHẢO SÁT CÁC ĐIỂM PHÁT SINH NHU CẦU LỚN\n"
    "(TRIP GENERATION / ATTRACTION SURVEY)\n"
    "KHU VỰC NHÀ GA ST01 (TÂN SƠN NHẤT / PHAN VĂN HỚN)"
)
r_sub.font.name = "Arial"
r_sub.font.size = Pt(13)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(20, 50, 100)

# Khung thông tin kỹ thuật dự án
tbl_info = doc.add_table(rows=3, cols=2)
tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_info, color="B0C4DE", sz="4")
info_meta = [
    ("Đơn vị thực hiện:", "LIÊN DANH TƯ VẤN THIẾT KẾ & KHẢO SÁT GIAO THÔNG"),
    ("Địa bàn khảo sát:", "Khu vực bán kính R ≈ 1.000m quanh tim nhà ga ST01 (Quận 12, TP.HCM)"),
    ("Mục tiêu kỹ thuật:", "Thu thập đặc trưng 11 công trình và tính toán Trip Rate phục vụ mô hình PTV VISUM")
]
tbl_widths = [Inches(2.0), Inches(4.5)]
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
    set_cell_margins(cell_l, top=45, bottom=45, left=60, right=60)
    
    pr = cell_r.paragraphs[0]
    pr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rr = pr.runs[0]
    rr.font.name = "Arial"
    rr.font.size = Pt(8.5)
    rr.font.color.rgb = RGBColor(40, 40, 40)
    set_cell_background(cell_r, "FFFFFF")
    set_cell_margins(cell_r, top=45, bottom=45, left=60, right=60)

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
# PHẦN THÂN BÁO CÁO: MỤC 1 & MỤC 2
# ==============================================================================

# 1. KẾT QUẢ THỰC HIỆN
p_s1 = doc.add_paragraph()
p_s1.paragraph_format.space_before = Pt(0)
p_s1.paragraph_format.space_after = Pt(4)
r_s1 = p_s1.add_run("1. KẾT QUẢ THỰC HIỆN KHẢO SÁT KHU VỰC GA ST01")
r_s1.font.name = "Arial"
r_s1.font.size = Pt(13)
r_s1.font.bold = True
r_s1.font.color.rgb = RGBColor(180, 40, 40)

# 1.1. Bản đồ tổng thể
p_s11 = doc.add_paragraph()
p_s11.paragraph_format.space_before = Pt(4)
p_s11.paragraph_format.space_after = Pt(2)
r_s11 = p_s11.add_run("1.1. Bản đồ tổng thể hành lang ga và các điểm phát sinh nhu cầu lớn")
r_s11.font.name = "Arial"
r_s11.font.size = Pt(11)
r_s11.font.bold = True
r_s11.font.color.rgb = RGBColor(20, 50, 100)

p_s11_desc = doc.add_paragraph()
p_s11_desc.paragraph_format.space_after = Pt(4)
r_s11_d = p_s11_desc.add_run(
    "Khu vực khảo sát Ga ST01 (Tân Sơn Nhất / Phan Văn Hớn) được xác lập trong phạm vi bán kính ảnh hưởng R ≈ 1.000m quanh tim nhà ga. "
    "Tổng cộng 11 điểm phát sinh và thu hút nhu cầu lớn nhất đã được xác định, định vị tọa độ GIS (WGS-84) và khảo sát thực địa bao gồm: "
    "04 công trình giáo dục, 01 bệnh viện đa khoa quy mô lớn, 04 khu chung cư cao tầng quy mô lớn, 01 đại siêu thị và 01 chợ đầu mối truyền thống."
)
r_s11_d.font.name = "Arial"
r_s11_d.font.size = Pt(8.5)

if os.path.exists(overview_map_path):
    p_map = doc.add_paragraph()
    p_map.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_map.paragraph_format.space_before = Pt(1)
    p_map.paragraph_format.space_after = Pt(1)
    run_map = p_map.add_run()
    run_map.add_picture(overview_map_path, width=Inches(6.8), height=Inches(6.2))
    
    p_map_cap = doc.add_paragraph()
    p_map_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_map_cap.paragraph_format.space_after = Pt(0)
    r_mc = p_map_cap.add_run("Hình 1.1: Bản đồ tổng thể phân bố 11 công trình phát sinh/thu hút nhu cầu lớn trong bán kính 1km quanh Ga ST01\n(Ký hiệu: M - Thương mại/Chợ; H - Bệnh viện; R - Chung cư/Nhà ở; S - Trường học; Hướng tuyến Metro số 2: Xanh lá)")
    r_mc.font.name = "Arial"
    r_mc.font.size = Pt(8)
    r_mc.font.italic = True
    r_mc.font.color.rgb = RGBColor(80, 80, 80)

doc.add_page_break()

# 1.2. Thống kê tổng hợp theo nhóm chức năng
p_s12 = doc.add_paragraph()
p_s12.paragraph_format.space_before = Pt(0)
p_s12.paragraph_format.space_after = Pt(2)
r_s12 = p_s12.add_run("1.2. Thống kê tổng hợp công trình theo nhóm chức năng sử dụng đất")
r_s12.font.name = "Arial"
r_s12.font.size = Pt(11)
r_s12.font.bold = True
r_s12.font.color.rgb = RGBColor(20, 50, 100)

p_s12_desc = doc.add_paragraph()
p_s12_desc.paragraph_format.space_after = Pt(4)
r_s12_d = p_s12_desc.add_run(
    "Dựa trên kết quả khảo sát thực tế, tổng diện tích sàn xây dựng (GFA) của 11 công trình đạt 390.530 m². "
    "Cơ cấu diện tích sàn và năng lực bãi đỗ xe được tổng hợp chuẩn hóa theo Bảng 1.1:"
)
r_s12_d.font.name = "Arial"
r_s12_d.font.size = Pt(8.5)

# Bảng 1.1: Tổng hợp theo chức năng
tbl_func = doc.add_table(rows=6, cols=6)
tbl_func.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_func, color="999999", sz="4")

func_headers = ["Nhóm chức năng", "Số công trình", "Tổng DT sàn (m²)", "Tỷ trọng (%)", "Số bãi/cổng đỗ", "Đặc trưng quy mô nổi bật"]
func_widths = [Inches(1.8), Inches(0.8), Inches(1.1), Inches(0.8), Inches(0.9), Inches(1.6)]

func_data = [
    ["Nhà ở / Chung cư", "4", "283.000", "72,5%", "10 cổng / 4 bãi", "3.318 căn hộ, ~8.500 dân cư"],
    ["Giáo dục / Trường học", "4", "39.000", "10,0%", "8 cổng", "5.000 học sinh, 350 giáo viên"],
    ["Y tế / Bệnh viện", "1", "38.400", "9,8%", "3 cổng / 2 bãi", "150 giường bệnh, cấp cứu 24/7"],
    ["Thương mại – dịch vụ & Chợ", "2", "33.130", "8,5%", "9 cổng / 6 bãi", "Co.opmart PVH, Chợ Lạc Quang"],
    ["TỔNG CỘNG KHU VỰC GA ST01", "11", "390.530", "100,0%", "30 cổng / 12 bãi", "34 điểm đón trả khách PUDO"]
]

for c_idx, h in enumerate(func_headers):
    cell = tbl_func.rows[0].cells[c_idx]
    cell.width = func_widths[c_idx]
    cell.text = h
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.runs[0]
    run.font.name = "Arial"
    run.font.size = Pt(8)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(cell, "2B547E")
    set_cell_margins(cell, top=45, bottom=45, left=45, right=45)

for r_idx, r_vals in enumerate(func_data):
    row = tbl_func.rows[r_idx + 1]
    is_total = (r_idx == len(func_data) - 1)
    bg = "EAEFF5" if is_total else ("F4F7FA" if r_idx % 2 == 1 else "FFFFFF")
    for c_idx, val in enumerate(r_vals):
        cell = row.cells[c_idx]
        cell.width = func_widths[c_idx]
        cell.text = val
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 3, 4] else (WD_ALIGN_PARAGRAPH.RIGHT if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT)
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(8)
        if is_total:
            run.font.bold = True
            if c_idx == 0:
                run.font.color.rgb = RGBColor(180, 40, 40)
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=40, bottom=40, left=45, right=45)

# 1.3. Phân nhóm mức độ phát sinh/thu hút nhu cầu
p_s13 = doc.add_paragraph()
p_s13.paragraph_format.space_before = Pt(8)
p_s13.paragraph_format.space_after = Pt(2)
r_s13 = p_s13.add_run("1.3. Phân nhóm mức độ phát sinh / thu hút nhu cầu (Mức A, B, C)")
r_s13.font.name = "Arial"
r_s13.font.size = Pt(11)
r_s13.font.bold = True
r_s13.font.color.rgb = RGBColor(20, 50, 100)

p_s13_desc = doc.add_paragraph()
p_s13_desc.paragraph_format.space_after = Pt(2)
r_s13_d = p_s13_desc.add_run(
    "Để phục vụ mô hình dự báo giao thông PTV VISUM, 11 công trình được phân bổ vào 3 cấp độ nhu cầu dựa trên quy mô sàn, công suất và khả năng tạo chuyến đi:"
)
r_s13_d.font.name = "Arial"
r_s13_d.font.size = Pt(8.5)

bullet_points = [
    ("Mức A – Nhu cầu rất lớn (Trọng tâm thu hút): ", "Chung cư Prosper Plaza (105.000 m², 1.552 căn), Chung cư Phú Cường Home (83.000 m², 776 căn), Bệnh viện Đa khoa Tâm Trí Sài Gòn (38.400 m², 150 giường), Siêu thị Co.opmart Phan Văn Hớn (30.130 m²). Đây là các nguồn tạo chuyến đi chủ đạo hai chiều (Inbound & Outbound) cho ga Metro."),
    ("Mức B – Nhu cầu lớn (GFA > 5.000 m²): ", "Chung cư Moscow Tower (55.000 m²), Chung cư Thái An (~40.000 m²), Trường THPT Phan Văn Hớn (15.000 m², 1.800 học sinh), Trường THCS Nguyễn Ảnh Thủ (10.000 m², 1.400 học sinh), Trường THCS Hà Huy Tập (8.000 m², 1.300 học sinh), Hệ thống giáo dục ATY (6.000 m²). Các trường học tạo xung lượng tập trung cực lớn vào giờ cao điểm sáng và chiều."),
    ("Mức C – Nhu cầu bổ trợ (Luồng khách địa phương): ", "Chợ Lạc Quang (3.000 m², 100-150 gian hàng), đóng vai trò luồng mua sắm thiết yếu ven trục Trường Chinh tiếp cận trực tiếp nhà ga.")
]

for b_head, b_body in bullet_points:
    p_b = doc.add_paragraph(style='List Bullet')
    p_b.paragraph_format.space_before = Pt(1)
    p_b.paragraph_format.space_after = Pt(1)
    r_bh = p_b.add_run(b_head)
    r_bh.font.name = "Arial"
    r_bh.font.size = Pt(8)
    r_bh.font.bold = True
    r_bh.font.color.rgb = RGBColor(30, 50, 90)
    r_bb = p_b.add_run(b_body)
    r_bb.font.name = "Arial"
    r_bb.font.size = Pt(8)

# 1.4. Hiện trạng tiếp cận, bãi đỗ xe và điểm PUDO
p_s14 = doc.add_paragraph()
p_s14.paragraph_format.space_before = Pt(6)
p_s14.paragraph_format.space_after = Pt(2)
r_s14 = p_s14.add_run("1.4. Hiện trạng hạ tầng tiếp cận, bãi đỗ xe và điểm đón trả khách (PUDO)")
r_s14.font.name = "Arial"
r_s14.font.size = Pt(11)
r_s14.font.bold = True
r_s14.font.color.rgb = RGBColor(20, 50, 100)

p_s14_desc = doc.add_paragraph()
p_s14_desc.paragraph_format.space_after = Pt(4)
r_s14_d = p_s14_desc.add_run(
    "Toàn bộ 11 công trình sở hữu tổng cộng 30 cổng giao thông kết nối trực tiếp ra mạng lưới đường chính (Trường Chinh, Phan Văn Hớn, Song Hành, Nguyễn Văn Quá, Tân Thới Nhất 14/17). "
    "Tổng số điểm đón trả khách chuyên dụng (PUDO) ghi nhận đạt 34 điểm. Hạ tầng bãi đỗ xe nội bộ có sức chứa ước tính khoảng 8.750 – 10.950 chỗ đỗ xe máy và 735 – 1.115 chỗ đỗ ô tô, "
    "tạo điều kiện thuận lợi để tổ chức các tuyến trung chuyển (Feeder bus) hoặc luồng đi bộ tiếp cận các sảnh ga ST01."
)
r_s14_d.font.name = "Arial"
r_s14_d.font.size = Pt(8.5)

# 2. KẾT LUẬN VÀ THÔNG SỐ ĐẦU VÀO CHO MÔ HÌNH
p_s2 = doc.add_paragraph()
p_s2.paragraph_format.space_before = Pt(8)
p_s2.paragraph_format.space_after = Pt(2)
r_s2 = p_s2.add_run("2. KẾT LUẬN VÀ THÔNG SỐ ĐẦU VÀO CHO MÔ HÌNH PTV VISUM")
r_s2.font.name = "Arial"
r_s2.font.size = Pt(13)
r_s2.font.bold = True
r_s2.font.color.rgb = RGBColor(180, 40, 40)

conclusion_items = [
    ("Đánh giá tiềm năng thu hút:", "Ga ST01 là một trong những ga trọng điểm đầu tuyến có mật độ dân số và nhu cầu dịch chuyển cao nhất hành lang Tuyến 2. Quy mô 4 cụm chung cư lớn (hơn 3.300 căn hộ) và 4 trường học (5.000 học sinh) bảo đảm nguồn khách thường xuyên, ổn định cả vào khung giờ cao điểm sáng và chiều."),
    ("Dữ liệu đầu vào bàn giao mô hình:", "Toàn bộ bảng thuộc tính chi tiết (Mục 03.1) và Bảng tính toán Trip Rate (Mục 03.2) được chuẩn hóa theo định dạng dữ liệu GIS và Excel sẵn sàng tích hợp trực tiếp vào phần mềm PTV VISUM theo các biến số: Tọa độ nút (Node/Zone), Diện tích sàn GFA/GLA, Suất phát sinh chuyến đi cao điểm AM/PM, và Tỷ trọng lưu thông theo nhóm phương tiện."),
    ("Kiến nghị tổ chức giao thông kết nối:", "Cần ưu tiên phát triển dải bộ hành có mái che và làn xe đạp dọc trục Phan Văn Hớn và Trường Chinh nối từ cụm chung cư Prosper Plaza / Moscow Tower đến cửa sảnh ga; bố trí vị trí dừng xe buýt gom và điểm PUDO công cộng ngay trước khu vực quảng trường ga ST01.")
]

for c_head, c_body in conclusion_items:
    p_c = doc.add_paragraph(style='List Bullet')
    p_c.paragraph_format.space_before = Pt(1)
    p_c.paragraph_format.space_after = Pt(1)
    r_ch = p_c.add_run(c_head + " ")
    r_ch.font.name = "Arial"
    r_ch.font.size = Pt(8.5)
    r_ch.font.bold = True
    r_ch.font.color.rgb = RGBColor(30, 50, 90)
    r_cb = p_c.add_run(c_body)
    r_cb.font.name = "Arial"
    r_cb.font.size = Pt(8.5)

doc.add_page_break()

# ==============================================================================
# PHỤ LỤC MRT2S - KSGT - NV8 - 01. BIỂU MẪU
# ==============================================================================
p_pl1 = doc.add_paragraph()
p_pl1.paragraph_format.space_before = Pt(0)
p_pl1.paragraph_format.space_after = Pt(2)
r_pl1 = p_pl1.add_run("PHỤ LỤC MRT2S - KSGT - NV8 - 01. BIỂU MẪU")
r_pl1.font.name = "Arial"
r_pl1.font.size = Pt(13)
r_pl1.font.bold = True
r_pl1.font.color.rgb = RGBColor(180, 40, 40)

p_pl1_sub = doc.add_paragraph()
p_pl1_sub.paragraph_format.space_after = Pt(4)
r_pl1_s = p_pl1_sub.add_run("Tập hợp 11 Phiếu khảo sát đặc trưng công trình phát sinh – thu hút chuyến đi (Biểu mẫu TG-00):")
r_pl1_s.font.name = "Arial"
r_pl1_s.font.size = Pt(8.5)

for idx, fac in enumerate(facility_data):
    f_num = fac["id"]
    f_name = fac["name"]
    f_type = fac["type"]
    
    p_fh = doc.add_paragraph()
    p_fh.paragraph_format.space_before = Pt(4)
    p_fh.paragraph_format.space_after = Pt(2)
    r_fh = p_fh.add_run(f"PHIẾU TG-00 #{f_num:02d}: {f_name.upper()} [{f_type.upper()}]")
    r_fh.font.name = "Arial"
    r_fh.font.size = Pt(9.5)
    r_fh.font.bold = True
    r_fh.font.color.rgb = RGBColor(20, 50, 100)
    
    # Bảng hành chính
    t_info = doc.add_table(rows=len(fac["info_rows"]), cols=4)
    t_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_info, color="CCCCCC", sz="4")
    col_w_info = [Inches(1.4), Inches(2.2), Inches(1.4), Inches(2.1)]
    for r_i, r_data in enumerate(fac["info_rows"]):
        row_obj = t_info.rows[r_i]
        for c_i in range(min(4, len(r_data))):
            cell = row_obj.cells[c_i]
            cell.width = col_w_info[c_i]
            cell.text = r_data[c_i]
            p = cell.paragraphs[0]
            run = p.runs[0]
            run.font.name = "Arial"
            run.font.size = Pt(7)
            set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
            if c_i in [0, 2]:
                set_cell_background(cell, "EAEFF5")
                run.font.bold = True
                run.font.color.rgb = RGBColor(30, 50, 80)
            else:
                set_cell_background(cell, "FFFFFF")
                
    # Bảng chỉ tiêu
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(1)
    r_sp = p_sp.add_run("Chỉ tiêu quy mô và đặc trưng kỹ thuật:")
    r_sp.font.name = "Arial"
    r_sp.font.size = Pt(8)
    r_sp.font.bold = True
    r_sp.font.color.rgb = RGBColor(40, 70, 120)
    
    t_spec = doc.add_table(rows=len(fac["spec_rows"]), cols=4)
    t_spec.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_spec, color="CCCCCC", sz="4")
    col_w_spec = [Inches(2.2), Inches(0.75), Inches(1.15), Inches(3.0)]
    for r_i, r_data in enumerate(fac["spec_rows"]):
        row_obj = t_spec.rows[r_i]
        is_hdr = (r_i == 0)
        for c_i in range(min(4, len(r_data))):
            cell = row_obj.cells[c_i]
            cell.width = col_w_spec[c_i]
            cell.text = r_data[c_i]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.runs[0]
            run.font.name = "Arial"
            run.font.size = Pt(7)
            set_cell_margins(cell, top=14, bottom=14, left=35, right=35)
            if is_hdr:
                set_cell_background(cell, "2B547E")
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if c_i == 0:
                    set_cell_background(cell, "F9FAFC")
                    run.font.bold = True
                else:
                    set_cell_background(cell, "FFFFFF")
                    
    # Ngắt trang giữa các phiếu
    if idx % 2 == 1 or idx == len(facility_data) - 1:
        doc.add_page_break()
    else:
        p_div = doc.add_paragraph()
        p_div.paragraph_format.space_before = Pt(6)
        p_div.paragraph_format.space_after = Pt(6)

# ==============================================================================
# PHỤ LỤC MRT2S - KSGT - NV8 - 02. HÌNH ẢNH THỰC TẾ
# ==============================================================================
p_pl2 = doc.add_paragraph()
p_pl2.paragraph_format.space_before = Pt(0)
p_pl2.paragraph_format.space_after = Pt(2)
r_pl2 = p_pl2.add_run("PHỤ LỤC MRT2S - KSGT - NV8 - 02. HÌNH ẢNH THỰC TẾ")
r_pl2.font.name = "Arial"
r_pl2.font.size = Pt(13)
r_pl2.font.bold = True
r_pl2.font.color.rgb = RGBColor(180, 40, 40)

p_pl2_sub = doc.add_paragraph()
p_pl2_sub.paragraph_format.space_after = Pt(4)
r_pl2_s = p_pl2_sub.add_run("Sơ đồ mặt bằng tiếp cận đón trả khách (PUDO) và hình ảnh khảo sát thực tế 11 công trình:")
r_pl2_s.font.name = "Arial"
r_pl2_s.font.size = Pt(8.5)

for idx, fac in enumerate(facility_data):
    f_num = fac["id"]
    f_name = fac["name"]
    
    p_ih = doc.add_paragraph()
    p_ih.paragraph_format.space_before = Pt(4)
    p_ih.paragraph_format.space_after = Pt(2)
    r_ih = p_ih.add_run(f"Công trình #{f_num:02d}: {f_name}")
    r_ih.font.name = "Arial"
    r_ih.font.size = Pt(9.5)
    r_ih.font.bold = True
    r_ih.font.color.rgb = RGBColor(20, 50, 100)
    
    tbl_img = doc.add_table(rows=2, cols=2)
    tbl_img.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_img, val="none")
    
    c_il = tbl_img.rows[0].cells[0]
    c_ir = tbl_img.rows[0].cells[1]
    c_cl = tbl_img.rows[1].cells[0]
    c_cr = tbl_img.rows[1].cells[1]
    
    c_il.width = Inches(3.5)
    c_ir.width = Inches(3.5)
    c_cl.width = Inches(3.5)
    c_cr.width = Inches(3.5)
    
    p_l = c_il.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_l.paragraph_format.space_after = Pt(0)
    if f_num in facade_images:
        add_scaled_picture(p_l, facade_images[f_num], max_w_in=3.4, max_h_in=2.4)
        
    p_cl = c_cl.paragraphs[0]
    p_cl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cl.paragraph_format.space_before = Pt(1)
    p_cl.paragraph_format.space_after = Pt(0)
    r_cl = p_cl.add_run(f"Ảnh {f_num}.1: Toàn cảnh mặt tiền {f_name}")
    r_cl.font.name = "Arial"
    r_cl.font.size = Pt(7.5)
    r_cl.font.italic = True
    
    p_r = c_ir.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_r.paragraph_format.space_after = Pt(0)
    pudo_path = pudo_map.get(f_num)
    if pudo_path and os.path.exists(pudo_path):
        add_scaled_picture(p_r, pudo_path, max_w_in=3.4, max_h_in=2.4)
        
    p_cr = c_cr.paragraphs[0]
    p_cr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cr.paragraph_format.space_before = Pt(1)
    p_cr.paragraph_format.space_after = Pt(0)
    r_cr = p_cr.add_run(f"Ảnh {f_num}.2: Sơ đồ mặt bằng tiếp cận & điểm PUDO")
    r_cr.font.name = "Arial"
    r_cr.font.size = Pt(7.5)
    r_cr.font.italic = True
    
    if idx % 2 == 1 or idx == len(facility_data) - 1:
        doc.add_page_break()
    else:
        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_before = Pt(6)
        p_sep.paragraph_format.space_after = Pt(6)

# Mục minh chứng ảnh Timemark đại diện theo khu vực
p_tm_h = doc.add_paragraph()
p_tm_h.paragraph_format.space_before = Pt(0)
p_tm_h.paragraph_format.space_after = Pt(2)
r_tm = p_tm_h.add_run("HÌNH ẢNH KHẢO SÁT HIỆN TRƯỜNG ĐÓNG DẤU ĐỊNH VỊ TIMEMARK GPS")
r_tm.font.name = "Arial"
r_tm.font.size = Pt(11)
r_tm.font.bold = True
r_tm.font.color.rgb = RGBColor(20, 50, 100)

p_tm_desc = doc.add_paragraph()
p_tm_desc.paragraph_format.space_after = Pt(4)
r_tmd = p_tm_desc.add_run(
    "Ảnh khảo sát thực địa hiện trường đại diện các khu vực xung quanh nhà ga ST01, "
    "ghi nhận mã số phân loại khảo sát (MS1 - Thương mại, SS1 - Giáo dục, RS1 - Nhà ở), địa chỉ số nhà, ngày giờ và tọa độ GPS WGS-84:"
)
r_tmd.font.name = "Arial"
r_tmd.font.size = Pt(8.5)

st01_dir = os.path.join(base_dir, "ST01")
all_st01_imgs = sorted([os.path.join(st01_dir, f) for f in os.listdir(st01_dir) if f.lower().endswith('.jpg')])

# Chọn 6 ảnh đại diện rõ nét các vị trí quanh ga
sample_indices = [0, 5, 12, 16, 25, 45]
sample_tm_imgs = [all_st01_imgs[i] for i in sample_indices if i < len(all_st01_imgs)]
sample_caps = [
    "Minh chứng 01: Khảo sát trục đường Trường Chinh & Chợ Lạc Quang (Điểm MS1 - 10.8354°N, 106.6195°E)",
    "Minh chứng 02: Khảo sát trục đường Trường Chinh hướng về Ga ST01 (Điểm MS1 - 10.8346°N, 106.6200°E)",
    "Minh chứng 03: Khảo sát khu vực ngã ba Phan Văn Hớn - Tân Thới Nhất (Điểm MS1 - 10.8235°N, 106.6203°E)",
    "Minh chứng 04: Khảo sát khu vực các khu dân cư & chung cư cao tầng (Điểm RS1 - 10.8282°N, 106.6285°E)",
    "Minh chứng 05: Khảo sát tuyến tiếp cận cụm trường học Đông Hưng Thuận (Điểm SS1 - 10.8237°N, 106.6246°E)",
    "Minh chứng 06: Khảo sát tuyến đường Tân Thới Nhất 14 kết nối nhà ga (Điểm SS1 - 10.8263°N, 106.6167°E)"
]

tbl_tm = doc.add_table(rows=6, cols=2)
tbl_tm.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_tm, val="none")

for i in range(0, len(sample_tm_imgs), 2):
    row_img = tbl_tm.rows[i]
    row_cap = tbl_tm.rows[i+1]
    
    # Cột trái
    c_il = row_img.cells[0]
    c_cl = row_cap.cells[0]
    c_il.width = Inches(3.5)
    c_cl.width = Inches(3.5)
    p = c_il.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    add_scaled_picture(p, sample_tm_imgs[i], max_w_in=3.4, max_h_in=2.5)
    pc = c_cl.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_before = Pt(1)
    pc.paragraph_format.space_after = Pt(4)
    rc = pc.add_run(sample_caps[i] if i < len(sample_caps) else f"Minh chứng #{i+1}: Ảnh khảo sát thực địa Timemark")
    rc.font.name = "Arial"
    rc.font.size = Pt(7.5)
    rc.font.italic = True
    
    # Cột phải
    if i + 1 < len(sample_tm_imgs):
        c_ir = row_img.cells[1]
        c_cr = row_cap.cells[1]
        c_ir.width = Inches(3.5)
        c_cr.width = Inches(3.5)
        p2 = c_ir.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(0)
        add_scaled_picture(p2, sample_tm_imgs[i+1], max_w_in=3.4, max_h_in=2.5)
        pc2 = c_cr.paragraphs[0]
        pc2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pc2.paragraph_format.space_before = Pt(1)
        pc2.paragraph_format.space_after = Pt(4)
        rc2 = pc2.add_run(sample_caps[i+1] if i+1 < len(sample_caps) else f"Minh chứng #{i+2}: Ảnh khảo sát thực địa Timemark")
        rc2.font.name = "Arial"
        rc2.font.size = Pt(7.5)
        rc2.font.italic = True

p_note_album = doc.add_paragraph()
p_note_album.paragraph_format.space_before = Pt(4)
r_na = p_note_album.add_run(
    "(Ghi chú: Toàn bộ album chi tiết 84 hình ảnh hiện trường được lưu trữ đầy đủ trong tập hồ sơ kỹ thuật riêng: "
    "MRT2S_KSGT_NV8_02_Phu_Luc_Hinh_Anh_Hien_Truong_ST01.docx)"
)
r_na.font.name = "Arial"
r_na.font.size = Pt(8)
r_na.font.italic = True
r_na.font.color.rgb = RGBColor(90, 90, 90)

doc.add_page_break()

# ==============================================================================
# PHỤ LỤC MRT2S - KSGT - NV8 - 03. KẾT QUẢ CHI TIẾT
# ==============================================================================
p_pl3 = doc.add_paragraph()
p_pl3.paragraph_format.space_before = Pt(0)
p_pl3.paragraph_format.space_after = Pt(2)
r_pl3 = p_pl3.add_run("PHỤ LỤC MRT2S - KSGT - NV8 - 03. KẾT QUẢ CHI TIẾT")
r_pl3.font.name = "Arial"
r_pl3.font.size = Pt(13)
r_pl3.font.bold = True
r_pl3.font.color.rgb = RGBColor(180, 40, 40)

# Mục 03.1: Bảng dữ liệu thuộc tính chi tiết
p_031 = doc.add_paragraph()
p_031.paragraph_format.space_before = Pt(4)
p_031.paragraph_format.space_after = Pt(2)
r_031 = p_031.add_run("Mục 03.1: Bảng dữ liệu thuộc tính chi tiết 11 công trình khảo sát Ga ST01")
r_031.font.name = "Arial"
r_031.font.size = Pt(10.5)
r_031.font.bold = True
r_031.font.color.rgb = RGBColor(20, 50, 100)

tbl_attr = doc.add_table(rows=12, cols=7)
tbl_attr.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_attr, color="999999", sz="4")

attr_headers = ["STT", "Tên công trình", "Chức năng", "GFA (m²)", "Quy mô chính", "Bãi xe (xe máy/ô tô)", "Điểm PUDO"]
attr_widths = [Inches(0.4), Inches(2.2), Inches(0.9), Inches(0.9), Inches(1.5), Inches(1.3), Inches(0.6)]

attr_data = [
    ["1", "Trường THCS Nguyễn Ảnh Thủ", "School", "10.000", "1.400 HS, 90 GV", "500-700 / 15", "2"],
    ["2", "Trường THPT Phan Văn Hớn", "School", "15.000", "1.800 HS, 110 GV", "800-1.000 / 20", "2"],
    ["3", "Trường THCS Hà Huy Tập", "School", "8.000", "1.300 HS, 90 GV", "400-600 / 10", "2"],
    ["4", "Hệ thống GD ATY – CS Q12", "School", "6.000", "500 HS, 60 GV", "200-300 / 10", "2"],
    ["5", "BV Đa khoa Tâm Trí Sài Gòn", "Hospital", "38.400", "150 giường bệnh", "500-700 / 50-80", "5"],
    ["6", "Chung cư Phú Cường Home", "Residential", "83.000", "776 căn, 2.075 dân", "1.400-1.600 / 100-150", "2"],
    ["7", "Khu chung cư Thái An", "Residential", "~40.000", "390 căn, 1.200 dân", "700-900 / 80-120", "2"],
    ["8", "Chung cư Moscow Tower", "Residential", "55.000", "600 căn, 1.650 dân", "1.800-2.200 / 250-350", "2"],
    ["9", "Chung cư Prosper Plaza", "Residential", "~105.000", "1.552 căn, 3.800 dân", "800-1.000 / 100-150", "3"],
    ["10", "Co.opmart Phan Văn Hớn", "Mall", "30.130", "30 gian hàng", "1.500-1.800 / 150-250", "8"],
    ["11", "Chợ Lạc Quang", "Market", "3.000", "120 sạp chợ", "150-250 / 5-15", "4"]
]

for c_idx, h in enumerate(attr_headers):
    cell = tbl_attr.rows[0].cells[c_idx]
    cell.width = attr_widths[c_idx]
    cell.text = h
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.runs[0]
    run.font.name = "Arial"
    run.font.size = Pt(7.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(cell, "2B547E")
    set_cell_margins(cell, top=35, bottom=35, left=35, right=35)

for r_idx, r_vals in enumerate(attr_data):
    row = tbl_attr.rows[r_idx + 1]
    bg = "F4F7FA" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(r_vals):
        cell = row.cells[c_idx]
        cell.width = attr_widths[c_idx]
        cell.text = val
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 6] else (WD_ALIGN_PARAGRAPH.RIGHT if c_idx == 3 else WD_ALIGN_PARAGRAPH.LEFT)
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(7.5)
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=30, bottom=30, left=35, right=35)

# Mục 03.2: Bảng tính toán Trip Rate phục vụ PTV VISUM
p_032 = doc.add_paragraph()
p_032.paragraph_format.space_before = Pt(8)
p_032.paragraph_format.space_after = Pt(2)
r_032 = p_032.add_run("Mục 03.2: Bảng tính toán Trip Rate và ước tính lưu lượng chuyến đi phục vụ mô hình PTV VISUM")
r_032.font.name = "Arial"
r_032.font.size = Pt(10.5)
r_032.font.bold = True
r_032.font.color.rgb = RGBColor(20, 50, 100)

p_032_desc = doc.add_paragraph()
p_032_desc.paragraph_format.space_after = Pt(4)
r_032_d = p_032_desc.add_run(
    "Căn cứ vào đặc trưng quy mô và hệ số suất phát sinh chuyến đi (Trip Rate) tiêu chuẩn theo từng loại hình sử dụng đất, "
    "bảng dưới đây tổng hợp kết quả tính toán lưu lượng chuyến đi ngày (Daily Trips) và lưu lượng giờ cao điểm sáng (AM Peak) / chiều (PM Peak) "
    "của 11 công trình phục vụ nạp số liệu ma trận OD cho mô hình PTV VISUM:"
)
r_032_d.font.name = "Arial"
r_032_d.font.size = Pt(8)

tbl_trip = doc.add_table(rows=12, cols=6)
tbl_trip.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_trip, color="999999", sz="4")

trip_headers = ["Công trình", "Đơn vị tính Trip Rate", "Hệ số Trip Rate chuẩn", "Tổng chuyến đi ngày (Trips/day)", "Cao điểm sáng (AM Trips/h)", "Cao điểm chiều (PM Trips/h)"]
trip_widths = [Inches(2.2), Inches(1.5), Inches(1.3), Inches(1.1), Inches(0.9), Inches(0.9)]

trip_data = [
    ["THCS Nguyễn Ảnh Thủ", "chuyến / 100 học sinh", "45 chuyến / 100 HS", "630", "280 (Inbound)", "260 (Outbound)"],
    ["THPT Phan Văn Hớn", "chuyến / 100 học sinh", "45 chuyến / 100 HS", "810", "360 (Inbound)", "340 (Outbound)"],
    ["THCS Hà Huy Tập", "chuyến / 100 học sinh", "45 chuyến / 100 HS", "585", "260 (Inbound)", "240 (Outbound)"],
    ["Hệ thống GD ATY", "chuyến / 100 học sinh", "45 chuyến / 100 HS", "225", "100 (Inbound)", "90 (Outbound)"],
    ["BV Đa khoa Tâm Trí", "chuyến / 100 giường", "450 chuyến / 100 giường", "675", "90 (Inbound)", "80 (Outbound)"],
    ["CC Phú Cường Home", "chuyến / 100 căn hộ", "40 chuyến / 100 căn/h", "3.100", "310 (Outbound)", "290 (Inbound)"],
    ["Khu CC Thái An", "chuyến / 100 căn hộ", "40 chuyến / 100 căn/h", "1.560", "155 (Outbound)", "145 (Inbound)"],
    ["CC Moscow Tower", "chuyến / 100 căn hộ", "40 chuyến / 100 căn/h", "2.400", "240 (Outbound)", "220 (Inbound)"],
    ["CC Prosper Plaza", "chuyến / 100 căn hộ", "40 chuyến / 100 căn/h", "6.200", "620 (Outbound)", "580 (Inbound)"],
    ["Co.opmart Phan Văn Hớn", "chuyến / 1.000 m² GFA", "50 chuyến / 1.000 m²", "1.500", "120 (Inbound)", "280 (Inbound)"],
    ["Chợ Lạc Quang", "chuyến / 1.000 m² GFA", "80 chuyến / 1.000 m²", "240", "70 (Inbound)", "40 (Inbound)"]
]

for c_idx, h in enumerate(trip_headers):
    cell = tbl_trip.rows[0].cells[c_idx]
    cell.width = trip_widths[c_idx]
    cell.text = h
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.runs[0]
    run.font.name = "Arial"
    run.font.size = Pt(7.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(cell, "2B547E")
    set_cell_margins(cell, top=35, bottom=35, left=35, right=35)

for r_idx, r_vals in enumerate(trip_data):
    row = tbl_trip.rows[r_idx + 1]
    bg = "F4F7FA" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(r_vals):
        cell = row.cells[c_idx]
        cell.width = trip_widths[c_idx]
        cell.text = val
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2, 3, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(7.5)
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=30, bottom=30, left=35, right=35)

p_trip_sum = doc.add_paragraph()
p_trip_sum.paragraph_format.space_before = Pt(6)
r_ts = p_trip_sum.add_run(
    "Ghi chú: Toàn bộ thông số Trip Rate và ma trận lưu lượng phát sinh trên là cơ sở trực tiếp để nạp vào ma trận OD (Origin - Destination) "
    "phục vụ mô phỏng phân bố luồng hành khách tiếp cận nhà ga ST01 trong mô hình giao thông PTV VISUM."
)
r_ts.font.name = "Arial"
r_ts.font.size = Pt(8)
r_ts.font.italic = True
r_ts.font.color.rgb = RGBColor(80, 80, 80)

# Lưu file kết quả
doc.save(output_docx)
print(f"\n>>> ĐÃ TẠO THÀNH CÔNG BÁO CÁO: {output_docx}")
print(f"    Kích thước file: {os.path.getsize(output_docx):,} bytes")
