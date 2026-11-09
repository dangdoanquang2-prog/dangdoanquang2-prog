import sys
import os
import zipfile
import io
import openpyxl
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
output_docx = os.path.join(base_dir, "BC_KhaoSat_PhatSinhThuHut_Ga_ST01_Chuan.docx")

print("=== BẮT ĐẦU TỰ ĐỘNG HÓA BÁO CÁO PHÁT SINH - THU HÚT GA ST01 (BẢN CHUẨN 1 TRANG/CÔNG TRÌNH) ===")

# 1. Trích xuất ảnh mặt tiền từ docx gốc
raw_docx_path = os.path.join(base_dir, "ST01_Số liệu.docx")
facade_images = {}
with zipfile.ZipFile(raw_docx_path, 'r') as z:
    for i in range(1, 12):
        name = f"word/media/image{i}.png"
        try:
            b = z.read(name)
            facade_images[i] = b
            print(f"  Đã nạp ảnh mặt tiền công trình #{i} ({len(b):,} bytes)")
        except KeyError:
            print(f"  Không tìm thấy image{i}.png")

# 2. Ánh xạ sơ đồ mặt bằng PUDO từ ST01 MÔ TẢ
mota_dir = os.path.join(base_dir, "ST01 MÔ TẢ")
pudo_map = {
    1: os.path.join(mota_dir, "Screenshot 2026-09-16 162834.png"), # THCS Nguyễn Ảnh Thủ
    2: os.path.join(mota_dir, "Screenshot 2026-09-16 163024.png"), # THPT Phan Văn Hớn / TTN14
    3: os.path.join(mota_dir, "Screenshot 2026-09-16 162440.png"), # THCS Hà Huy Tập
    4: os.path.join(mota_dir, "Screenshot 2026-09-16 163323.png"), # ATY CS Q12
    5: os.path.join(mota_dir, "Screenshot 2026-09-16 163527.png"), # BV Đa khoa Tâm Trí
    6: os.path.join(mota_dir, "Screenshot 2026-09-16 164027.png"), # CC Phú Cường Home
    7: os.path.join(mota_dir, "Screenshot 2026-09-18 115140.png"), # Khu CC Thái An
    8: os.path.join(mota_dir, "Screenshot 2026-09-16 164817.png"), # CC Moscow Tower
    9: os.path.join(mota_dir, "Screenshot 2026-09-16 161626.png"), # CC Prosper Plaza
    10: os.path.join(mota_dir, "Screenshot 2026-09-16 162010.png"),# Co.opmart Phan Văn Hớn
    11: os.path.join(mota_dir, "Screenshot 2026-09-16 165231.png"),# Chợ Lạc Quang
}

overview_map_path = os.path.join(mota_dir, "Screenshot 2026-09-18 122910.png")

# 3. Nạp số liệu 11 công trình từ raw docx
raw_doc = Document(raw_docx_path)
facility_data = []

for idx in range(1, 12):
    t_info_idx = (idx - 1) * 2 + 1
    t_spec_idx = (idx - 1) * 2 + 2
    tbl_info = raw_doc.tables[t_info_idx]
    tbl_spec = raw_doc.tables[t_spec_idx]
    
    # Extract info table rows
    info_rows = []
    for r in tbl_info.rows:
        cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
        dedup = []
        for ct in cells:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        info_rows.append(dedup)
        
    # Extract spec table rows
    spec_rows = []
    for r in tbl_spec.rows:
        cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
        dedup = []
        for ct in cells:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        spec_rows.append(dedup)
        
    facility_data.append({
        "id": idx,
        "info_rows": info_rows,
        "spec_rows": spec_rows,
        "name": info_rows[0][1] if len(info_rows[0]) > 1 else f"Công trình {idx}",
        "type": info_rows[0][3] if len(info_rows[0]) > 3 else "N/A",
        "addr": info_rows[1][1] if len(info_rows[1]) > 1 else "N/A"
    })

print(f"Đã trích xuất số liệu thành công cho {len(facility_data)} công trình.")

# Helper format docx
def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=50, bottom=50, left=100, right=100):
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

def add_scaled_picture(p, img_source, max_w_in=3.35, max_h_in=2.5):
    """Adds picture maintaining aspect ratio within box (max_w_in x max_h_in)"""
    if isinstance(img_source, (bytes, bytearray)):
        im = Image.open(io.BytesIO(img_source))
        stream = io.BytesIO(img_source)
    else:
        im = Image.open(img_source)
        stream = img_source
        
    w_px, h_px = im.size
    aspect = w_px / h_px
    
    # Target dimensions
    calc_w = max_w_in
    calc_h = calc_w / aspect
    if calc_h > max_h_in:
        calc_h = max_h_in
        calc_w = calc_h * aspect
        
    run = p.add_run()
    run.add_picture(stream, width=Inches(calc_w), height=Inches(calc_h))

# Khởi tạo Document mới
doc = Document()

# Lề A4 tối ưu (Top 0.5 in, Bottom 0.5 in, Left 0.6 in, Right 0.5 in)
section = doc.sections[0]
section.top_margin = Inches(0.5)
section.bottom_margin = Inches(0.5)
section.left_margin = Inches(0.6)
section.right_margin = Inches(0.5)
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)

# Header & Footer
header = section.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hrun = hp.add_run("BỘ PHIẾU KHẢO SÁT PHÁT SINH – THU HÚT CHUYẾN ĐI (FORM TG-00) | GA ST01")
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
# TRANG 1: TIÊU ĐỀ & KHUNG TRIP RATE CHUẨN HÓA
# ==============================================================================
p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_before = Pt(0)
p_sub.paragraph_format.space_after = Pt(2)
r_sub = p_sub.add_run("DỰ ÁN NGHIÊN CỨU TUYẾN SỐ 2 (ĐOẠN THAM LƯƠNG - AN HẠ)\nVÀ TUYẾN 2S (AN HẠ - KHU ĐÔ THỊ TÂY BẮC)")
r_sub.font.name = "Arial"
r_sub.font.size = Pt(11)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(40, 70, 120)

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(4)
p_title.paragraph_format.space_after = Pt(4)
r_title = p_title.add_run("BÁO CÁO KẾT QUẢ KHẢO SÁT\nPHÁT SINH – THU HÚT CHUYẾN ĐI TẠI CÁC CÔNG TRÌNH\nKHU VỰC NHÀ GA ST01 (TÂN SƠN NHẤT / PHAN VĂN HỚN)")
r_title.font.name = "Arial"
r_title.font.size = Pt(14)
r_title.font.bold = True
r_title.font.color.rgb = RGBColor(180, 40, 40)

p_note = doc.add_paragraph()
p_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_note.paragraph_format.space_after = Pt(6)
r_note = p_note.add_run("TG-00 – PHIẾU THÔNG TIN ĐẶC TRƯNG CÔNG TRÌNH (TRIP GENERATION / ATTRACTION SURVEY)\nPhục vụ phân tích nhu cầu đi lại và hiệu chỉnh mô hình PTV VISUM")
r_note.font.name = "Arial"
r_note.font.size = Pt(9.5)
r_note.font.italic = True
r_note.font.color.rgb = RGBColor(90, 90, 90)

# 1. Đơn vị Trip Rate khuyến nghị
p_sec1 = doc.add_paragraph()
p_sec1.paragraph_format.space_before = Pt(4)
p_sec1.paragraph_format.space_after = Pt(2)
r_sec1 = p_sec1.add_run("1. Đơn vị Trip Rate chuẩn hóa khuyến nghị theo nhóm công trình")
r_sec1.font.name = "Arial"
r_sec1.font.size = Pt(11)
r_sec1.font.bold = True
r_sec1.font.color.rgb = RGBColor(20, 50, 100)

tbl_rates = doc.add_table(rows=7, cols=3)
tbl_rates.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_rates, color="999999", sz="4")

rate_data = [
    ["Loại công trình", "Đơn vị chuẩn hóa chính", "Chỉ tiêu bổ sung cần thu thập"],
    ["Shopping Mall", "chuyến / 1.000 m² GLA", "GFA, số gian hàng, nhân viên, chỗ đỗ xe"],
    ["Hospital", "chuyến / 100 giường", "GFA, lượt khám/ngày, nhân viên"],
    ["Residential", "chuyến / 100 căn hộ", "Dân số cư trú, tỷ lệ lấp đầy, GFA"],
    ["Hotel", "chuyến / 100 phòng", "Tỷ lệ lấp đầy, nhân viên, GFA"],
    ["School", "chuyến / 100 học sinh", "Giáo viên/nhân viên, GFA"],
    ["Office", "chuyến / 1.000 m² GFA", "Số nhân viên, tỷ lệ lấp đầy, chỗ đỗ xe"]
]

col_widths_rate = [Inches(1.8), Inches(2.2), Inches(3.1)]
for r_idx, row in enumerate(tbl_rates.rows):
    for c_idx, cell in enumerate(row.cells):
        cell.width = col_widths_rate[c_idx]
        cell.text = rate_data[r_idx][c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 1 else (WD_ALIGN_PARAGRAPH.LEFT if c_idx == 2 else WD_ALIGN_PARAGRAPH.CENTER)
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(8.5)
        set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
        if r_idx == 0:
            set_cell_background(cell, "2B547E")
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
        else:
            if r_idx % 2 == 1:
                set_cell_background(cell, "F4F7FA")

# Khung thời gian khảo sát khuyến nghị
p_sec2 = doc.add_paragraph()
p_sec2.paragraph_format.space_before = Pt(6)
p_sec2.paragraph_format.space_after = Pt(2)
r_sec2 = p_sec2.add_run("2. Khung thời gian khảo sát khuyến nghị")
r_sec2.font.name = "Arial"
r_sec2.font.size = Pt(11)
r_sec2.font.bold = True
r_sec2.font.color.rgb = RGBColor(20, 50, 100)

tbl_time = doc.add_table(rows=7, cols=3)
tbl_time.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_time, color="999999", sz="4")

time_data = [
    ["Loại công trình", "Khung khảo sát chính", "Ghi chú phân tích lưu lượng"],
    ["Shopping Mall", "07:00–22:00, ưu tiên Thứ Bảy", "Theo dõi toàn ngày để bắt đúng profile mua sắm/giải trí."],
    ["Hospital", "07:00–09:00 và 16:30–18:30", "Bổ sung khung giữa ngày nếu bệnh viện có lưu lượng khám lớn."],
    ["Residential", "07:00–22:00, ngày thường", "Cần đủ dài để nhận dạng outbound AM và inbound PM."],
    ["Hotel", "07:00–09:00 và 16:30–18:30", "Nếu có đoàn khách/sự kiện nên ghi chú riêng."],
    ["School", "07:00–09:00 và 16:30–18:30, ngày học", "PUDO nên khảo sát chi tiết ở giờ đưa/đón học sinh."],
    ["Office", "07:00–20:00, ngày thường", "Tập trung AM inbound và PM outbound."]
]

col_widths_time = [Inches(1.8), Inches(2.2), Inches(3.1)]
for r_idx, row in enumerate(tbl_time.rows):
    for c_idx, cell in enumerate(row.cells):
        cell.width = col_widths_time[c_idx]
        cell.text = time_data[r_idx][c_idx]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 1 else (WD_ALIGN_PARAGRAPH.LEFT if c_idx == 2 else WD_ALIGN_PARAGRAPH.CENTER)
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(8.5)
        set_cell_margins(cell, top=45, bottom=45, left=70, right=70)
        if r_idx == 0:
            set_cell_background(cell, "2B547E")
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
        else:
            if r_idx % 2 == 1:
                set_cell_background(cell, "F4F7FA")

p_end1 = doc.add_paragraph()
p_end1.paragraph_format.space_before = Pt(8)
r_end1 = p_end1.add_run("Lưu ý nghiệp vụ: Khảo sát viên phải chụp ảnh có địa chỉ, tọa độ công trình khảo sát (Timemark Verified) để làm minh chứng. Lập 01 phiếu cho mỗi công trình.")
r_end1.font.name = "Arial"
r_end1.font.size = Pt(8.5)
r_end1.font.italic = True
r_end1.font.color.rgb = RGBColor(120, 40, 40)

# NGẮT TRANG SANG TRANG 2
doc.add_page_break()

# ==============================================================================
# TRANG 2: BẢN ĐỒ TỔNG THỂ MẠNG LƯỚI BÁN KÍNH 1KM
# ==============================================================================
p_s2_t = doc.add_paragraph()
p_s2_t.paragraph_format.space_before = Pt(0)
p_s2_t.paragraph_format.space_after = Pt(2)
r_s2_t = p_s2_t.add_run("PHẦN I: TỔNG QUAN VÀ BẢN ĐỒ MẠNG LƯỚI PHÁT SINH – THU HÚT GA ST01")
r_s2_t.font.name = "Arial"
r_s2_t.font.size = Pt(12)
r_s2_t.font.bold = True
r_s2_t.font.color.rgb = RGBColor(20, 50, 100)

p_s2_desc = doc.add_paragraph()
p_s2_desc.paragraph_format.space_after = Pt(4)
r_s2_desc = p_s2_desc.add_run(
    "Ga ST01 (Tân Sơn Nhất / Phan Văn Hớn) nằm tại nút giao Trường Chinh và Phan Văn Hớn. "
    "Phạm vi khảo sát được xác lập trong vùng đệm bán kính R ≈ 1.000m bao quanh nhà ga, bao gồm 11 công trình trọng điểm phát sinh – thu hút chuyến đi lớn nhất trong khu vực."
)
r_s2_desc.font.name = "Arial"
r_s2_desc.font.size = Pt(9)

# Chèn ảnh bản đồ tổng thể chiếm trọn trang 2 sắc nét
if os.path.exists(overview_map_path):
    p_map = doc.add_paragraph()
    p_map.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_map.paragraph_format.space_before = Pt(2)
    p_map.paragraph_format.space_after = Pt(2)
    run_map = p_map.add_run()
    # Chiều cao khoảng 6.8 inches để trọn vẹn và cực kỳ sắc nét trên trang 2
    run_map.add_picture(overview_map_path, width=Inches(6.8), height=Inches(6.6))
    
    p_map_cap = doc.add_paragraph()
    p_map_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_map_cap.paragraph_format.space_after = Pt(0)
    r_mc = p_map_cap.add_run("Hình 1.1: Sơ đồ phân bố 11 công trình phát sinh – thu hút chuyến đi trong bán kính 1km quanh Ga ST01\n(M: Thương mại/Chợ, H: Bệnh viện, R: Khu dân cư/Chung cư, S: Trường học; Tuyến Metro số 2 hiển thị màu xanh lá)")
    r_mc.font.name = "Arial"
    r_mc.font.size = Pt(8.5)
    r_mc.font.italic = True
    r_mc.font.color.rgb = RGBColor(80, 80, 80)

# NGẮT TRANG SANG TRANG 3: BẢNG MA TRẬN TỔNG HỢP 11 CÔNG TRÌNH
doc.add_page_break()

p_m_head = doc.add_paragraph()
p_m_head.paragraph_format.space_before = Pt(0)
p_m_head.paragraph_format.space_after = Pt(4)
r_mh = p_m_head.add_run("DANH MỤC TỔNG HỢP 11 CÔNG TRÌNH PHÁT SINH – THU HÚT KHU VỰC GA ST01")
r_mh.font.name = "Arial"
r_mh.font.size = Pt(12)
r_mh.font.bold = True
r_mh.font.color.rgb = RGBColor(20, 50, 100)

p_m_sub = doc.add_paragraph()
p_m_sub.paragraph_format.space_after = Pt(6)
r_ms = p_m_sub.add_run("Bảng ma trận tổng hợp thông tin định vị, phân loại chức năng và hạ tầng tiếp cận của 11 công trình khảo sát chi tiết:")
r_ms.font.name = "Arial"
r_ms.font.size = Pt(9)

tbl_matrix = doc.add_table(rows=12, cols=6)
tbl_matrix.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_matrix, color="999999", sz="4")

matrix_headers = ["STT", "Tên công trình", "Phân loại", "Địa chỉ", "Số cổng", "Điểm PUDO"]
col_widths_m = [Inches(0.45), Inches(2.2), Inches(0.9), Inches(2.35), Inches(0.6), Inches(0.6)]

matrix_rows = [
    [str(d["id"]), d["name"], d["type"], d["addr"], 
     d["info_rows"][4][1] if len(d["info_rows"][4]) > 1 else "2",
     d["info_rows"][5][1] if len(d["info_rows"]) > 5 and len(d["info_rows"][5]) > 1 else "2"]
    for d in facility_data
]

for c_idx, h in enumerate(matrix_headers):
    cell = tbl_matrix.rows[0].cells[c_idx]
    cell.width = col_widths_m[c_idx]
    cell.text = h
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.runs[0]
    run.font.name = "Arial"
    run.font.size = Pt(8.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    set_cell_background(cell, "2B547E")
    set_cell_margins(cell, top=50, bottom=50, left=50, right=50)

for r_idx, r_vals in enumerate(matrix_rows):
    row = tbl_matrix.rows[r_idx + 1]
    bg = "F4F7FA" if r_idx % 2 == 1 else "FFFFFF"
    for c_idx, val in enumerate(r_vals):
        cell = row.cells[c_idx]
        cell.width = col_widths_m[c_idx]
        cell.text = val
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 4, 5] else WD_ALIGN_PARAGRAPH.LEFT
        run = p.runs[0]
        run.font.name = "Arial"
        run.font.size = Pt(8.5)
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=40, bottom=40, left=50, right=50)

p_m_exp = doc.add_paragraph()
p_m_exp.paragraph_format.space_before = Pt(8)
r_me = p_m_exp.add_run(
    "Ghi chú: Điểm PUDO (Pick-up / Drop-off) thể hiện số vị trí đón trả khách chuyên dụng hoặc mặt tiền tiếp cận trực tiếp luồng hành khách. "
    "Toàn bộ 11 công trình trên đều đã được khảo sát thực địa, thu thập số liệu đặc trưng quy mô và lập phiếu chi tiết theo chuẩn Form TG-00 ở các trang sau."
)
r_me.font.name = "Arial"
r_me.font.size = Pt(8.5)
r_me.font.italic = True
r_me.font.color.rgb = RGBColor(80, 80, 80)

# NGẮT TRANG SANG PHẦN CHI TIẾT
doc.add_page_break()

# ==============================================================================
# PHẦN II: CHI TIẾT 11 CÔNG TRÌNH KHẢO SÁT (MỖI CÔNG TRÌNH ĐÚNG 1 TRANG CHUẨN ĐẸP)
# ==============================================================================

for idx, fac in enumerate(facility_data):
    f_num = fac["id"]
    f_name = fac["name"]
    f_type = fac["type"]
    
    # Tiêu đề công trình
    p_head = doc.add_paragraph()
    p_head.paragraph_format.space_before = Pt(0)
    p_head.paragraph_format.space_after = Pt(2)
    r_h = p_head.add_run(f"CÔNG TRÌNH {f_num:02d}: {f_name.upper()} [{f_type.upper()}]")
    r_h.font.name = "Arial"
    r_h.font.size = Pt(10.5)
    r_h.font.bold = True
    r_h.font.color.rgb = RGBColor(180, 40, 40)
    
    # Section A: Thông tin hành chính
    p_sec_a = doc.add_paragraph()
    p_sec_a.paragraph_format.space_before = Pt(0)
    p_sec_a.paragraph_format.space_after = Pt(1)
    r_sa = p_sec_a.add_run("A. Thông tin hành chính & Hạ tầng tiếp cận:")
    r_sa.font.name = "Arial"
    r_sa.font.size = Pt(9)
    r_sa.font.bold = True
    r_sa.font.color.rgb = RGBColor(20, 50, 100)
    
    raw_info = fac["info_rows"]
    t_info = doc.add_table(rows=len(raw_info), cols=4)
    t_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_info, color="CCCCCC", sz="4")
    col_w_info = [Inches(1.4), Inches(2.2), Inches(1.4), Inches(2.1)]
    
    for r_i, row_data in enumerate(raw_info):
        row_obj = t_info.rows[r_i]
        for c_i in range(min(4, len(row_data))):
            cell = row_obj.cells[c_i]
            cell.width = col_w_info[c_i]
            cell.text = row_data[c_i]
            p = cell.paragraphs[0]
            run = p.runs[0]
            run.font.name = "Arial"
            run.font.size = Pt(7.5)
            set_cell_margins(cell, top=18, bottom=18, left=40, right=40)
            if c_i in [0, 2]:
                set_cell_background(cell, "EAEFF5")
                run.font.bold = True
                run.font.color.rgb = RGBColor(30, 50, 80)
            else:
                set_cell_background(cell, "FFFFFF")
                
    # Section B: Chỉ tiêu kỹ thuật
    p_sec_b = doc.add_paragraph()
    p_sec_b.paragraph_format.space_before = Pt(2)
    p_sec_b.paragraph_format.space_after = Pt(1)
    r_sb = p_sec_b.add_run("B. Quy mô và chỉ tiêu kỹ thuật công trình:")
    r_sb.font.name = "Arial"
    r_sb.font.size = Pt(9)
    r_sb.font.bold = True
    r_sb.font.color.rgb = RGBColor(20, 50, 100)
    
    raw_spec = fac["spec_rows"]
    t_spec = doc.add_table(rows=len(raw_spec), cols=4)
    t_spec.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_spec, color="CCCCCC", sz="4")
    col_w_spec = [Inches(2.2), Inches(0.75), Inches(1.15), Inches(3.0)]
    
    for r_i, row_data in enumerate(raw_spec):
        row_obj = t_spec.rows[r_i]
        is_header = (r_i == 0)
        for c_i in range(min(4, len(row_data))):
            cell = row_obj.cells[c_i]
            cell.width = col_w_spec[c_i]
            cell.text = row_data[c_i]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            run = p.runs[0]
            run.font.name = "Arial"
            run.font.size = Pt(7.5)
            set_cell_margins(cell, top=18, bottom=18, left=40, right=40)
            if is_header:
                set_cell_background(cell, "2B547E")
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if c_i == 0:
                    set_cell_background(cell, "F9FAFC")
                    run.font.bold = True
                else:
                    set_cell_background(cell, "FFFFFF")
                    
    # Section C: Hình ảnh trực quan (Mặt tiền + Sơ đồ PUDO)
    p_sec_c = doc.add_paragraph()
    p_sec_c.paragraph_format.space_before = Pt(2)
    p_sec_c.paragraph_format.space_after = Pt(1)
    r_sc = p_sec_c.add_run("C. Hình ảnh thực tế & Sơ đồ mặt bằng tiếp cận PUDO:")
    r_sc.font.name = "Arial"
    r_sc.font.size = Pt(9)
    r_sc.font.bold = True
    r_sc.font.color.rgb = RGBColor(20, 50, 100)
    
    # Tạo bảng 1 hàng 2 cột chứa 2 ảnh song song với chiều cao tối đa 2.4 inches
    tbl_img = doc.add_table(rows=2, cols=2)
    tbl_img.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_img, val="none")
    
    cell_img_left = tbl_img.rows[0].cells[0]
    cell_img_right = tbl_img.rows[0].cells[1]
    cell_cap_left = tbl_img.rows[1].cells[0]
    cell_cap_right = tbl_img.rows[1].cells[1]
    
    cell_img_left.width = Inches(3.5)
    cell_img_right.width = Inches(3.5)
    cell_cap_left.width = Inches(3.5)
    cell_cap_right.width = Inches(3.5)
    
    # 1. Ảnh mặt tiền bên trái
    p_il = cell_img_left.paragraphs[0]
    p_il.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_il.paragraph_format.space_after = Pt(0)
    if f_num in facade_images:
        add_scaled_picture(p_il, facade_images[f_num], max_w_in=3.4, max_h_in=2.35)
        
    p_cl = cell_cap_left.paragraphs[0]
    p_cl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cl.paragraph_format.space_before = Pt(1)
    p_cl.paragraph_format.space_after = Pt(0)
    r_cl = p_cl.add_run(f"Hình {f_num}.1: Toàn cảnh mặt tiền {f_name}")
    r_cl.font.name = "Arial"
    r_cl.font.size = Pt(7.5)
    r_cl.font.italic = True
    r_cl.font.color.rgb = RGBColor(80, 80, 80)
    
    # 2. Sơ đồ PUDO bên phải
    p_ir = cell_img_right.paragraphs[0]
    p_ir.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ir.paragraph_format.space_after = Pt(0)
    pudo_path = pudo_map.get(f_num)
    if pudo_path and os.path.exists(pudo_path):
        add_scaled_picture(p_ir, pudo_path, max_w_in=3.4, max_h_in=2.35)
    else:
        p_ir.add_run("(Đang cập nhật sơ đồ mặt bằng)")
        
    p_cr = cell_cap_right.paragraphs[0]
    p_cr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cr.paragraph_format.space_before = Pt(1)
    p_cr.paragraph_format.space_after = Pt(0)
    r_cr = p_cr.add_run(f"Hình {f_num}.2: Sơ đồ mặt bằng tiếp cận & điểm PUDO")
    r_cr.font.name = "Arial"
    r_cr.font.size = Pt(7.5)
    r_cr.font.italic = True
    r_cr.font.color.rgb = RGBColor(80, 80, 80)
    
    # Ngắt trang giữa các công trình
    doc.add_page_break()

# ==============================================================================
# PHẦN III: PHỤ LỤC ẢNH MINH CHỨNG KHẢO SÁT HIỆN TRƯỜNG (TIMEMARK VERIFIED)
# ==============================================================================
p_app_h = doc.add_paragraph()
p_app_h.paragraph_format.space_before = Pt(0)
p_app_h.paragraph_format.space_after = Pt(2)
r_ah = p_app_h.add_run("PHỤ LỤC: HÌNH ẢNH MINH CHỨNG KHẢO SÁT HIỆN TRƯỜNG (TIMEMARK VERIFIED)")
r_ah.font.name = "Arial"
r_ah.font.size = Pt(12)
r_ah.font.bold = True
r_ah.font.color.rgb = RGBColor(20, 50, 100)

p_app_desc = doc.add_paragraph()
p_app_desc.paragraph_format.space_after = Pt(4)
r_ad = p_app_desc.add_run(
    "Toàn bộ hình ảnh dưới đây được khảo sát viên chụp trực tiếp tại hiện trường bằng ứng dụng chuyên dụng Timemark, "
    "tự động đóng dấu watermark kỹ thuật số không thể chỉnh sửa gồm: Ký hiệu điểm khảo sát, Thời gian khảo sát thực tế, Địa chỉ số nhà và Tọa độ GPS chính xác (WGS-84). "
    "Dữ liệu hình ảnh này là minh chứng bắt buộc phục vụ nghiệm thu số liệu và tính toán Trip Rate chuẩn hóa."
)
r_ad.font.name = "Arial"
r_ad.font.size = Pt(8.5)

# Chọn lọc 6 ảnh hiện trường đại diện tiêu biểu từ thư mục ST01
st01_dir = os.path.join(base_dir, "ST01")
all_st01_imgs = sorted([os.path.join(st01_dir, f) for f in os.listdir(st01_dir) if f.lower().endswith('.jpg')])

sample_appendix_imgs = [all_st01_imgs[i] for i in [0, 5, 20, 30, 50, 65] if i < len(all_st01_imgs)]

tbl_app = doc.add_table(rows=len(sample_appendix_imgs)//2 * 2, cols=2)
tbl_app.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_app, val="none")

for i in range(0, len(sample_appendix_imgs), 2):
    row_img = tbl_app.rows[i]
    row_cap = tbl_app.rows[i+1]
    
    # Left
    c_il = row_img.cells[0]
    c_cl = row_cap.cells[0]
    c_il.width = Inches(3.5)
    c_cl.width = Inches(3.5)
    p = c_il.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    add_scaled_picture(p, sample_appendix_imgs[i], max_w_in=3.4, max_h_in=2.6)
    pc = c_cl.paragraphs[0]
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_before = Pt(1)
    pc.paragraph_format.space_after = Pt(4)
    rc = pc.add_run(f"Minh chứng #{i+1}: Ảnh khảo sát thực địa Timemark (có GPS & thời gian)")
    rc.font.name = "Arial"
    rc.font.size = Pt(7.5)
    rc.font.italic = True
    
    # Right
    if i + 1 < len(sample_appendix_imgs):
        c_ir = row_img.cells[1]
        c_cr = row_cap.cells[1]
        c_ir.width = Inches(3.5)
        c_cr.width = Inches(3.5)
        p2 = c_ir.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(0)
        add_scaled_picture(p2, sample_appendix_imgs[i+1], max_w_in=3.4, max_h_in=2.6)
        pc2 = c_cr.paragraphs[0]
        pc2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pc2.paragraph_format.space_before = Pt(1)
        pc2.paragraph_format.space_after = Pt(4)
        rc2 = pc2.add_run(f"Minh chứng #{i+2}: Ảnh khảo sát thực địa Timemark (có GPS & thời gian)")
        rc2.font.name = "Arial"
        rc2.font.size = Pt(7.5)
        rc2.font.italic = True

# Lưu file kết quả
doc.save(output_docx)
print(f"\n>>> ĐÃ TẠO THÀNH CÔNG BÁO CÁO: {output_docx}")
print(f"    Kích thước file: {os.path.getsize(output_docx):,} bytes")
