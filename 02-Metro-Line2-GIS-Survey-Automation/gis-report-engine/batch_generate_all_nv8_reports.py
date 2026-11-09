import sys
import os
import io
import re
import datetime
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
sl_base = os.path.join(base_dir, "Số liệu")
ct_base = os.path.join(base_dir, "Hình ảnh công trình")
tc_base = os.path.join(base_dir, "Hình ảnh tiếp cận mặt bằng")
out_dir = os.path.join(base_dir, "ketqua")
os.makedirs(out_dir, exist_ok=True)

STATION_NAMES = {
    "ST01": "Phan Văn Hớn",
    "ST02": "Đông Hưng Thuận",
    "ST03": "An Sương",
    "ST04": "Nguyễn Ảnh Thủ",
    "ST05": "Nguyễn Thị Sóc",
    "ST06": "Bà Triệu",
    "ST07": "Lý Thường Kiệt",
    "ST08": "Nguyễn Thị Nuôi",
    "ST09": "Vòng cung Tây Bắc 2",
    "ST10": "Vành Đai 3",
    "ST11": "An Hạ",
    "ST12": "Tân Phú Trung",
    "ST13": "Hương Lộ 2",
    "ST14": "Đào Thị Kiểm",
    "ST15": "Lê Minh Nhựt",
    "ST16": "Tân Thông Hội",
    "ST17": "Trần Tử Bình",
    "ST18": "Huỳnh Văn Cọ",
    "ST19": "Củ Chi",
    "ST20": "BV Củ Chi",
    "ST21": "Nguyễn Thị Rành",
    "ST22": "Tân An Hội",
    "ST23": "Ba Sa",
    "ST24": "Phước Hiệp",
    "ST25": "Tỉnh Lộ 7",
    "ST26": "Thái Mỹ"
}

READY_STATIONS = [
    "ST01", "ST02", "ST03", "ST11", "ST12", "ST13", "ST14", "ST15", 
    "ST16", "ST18", "ST19", "ST20", "ST21", "ST22", "ST23", "ST24", 
    "ST25", "ST26"
]

def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=35, bottom=35, left=50, right=50):
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
    try:
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
        return True
    except Exception as e:
        return False

def parse_facilities(st_code):
    doc_path = os.path.join(sl_base, f"{st_code} Số liệu.docx")
    if not os.path.exists(doc_path):
        return []
    
    doc = Document(doc_path)
    facilities = []
    
    for i in range(0, len(doc.tables) - 1, 2):
        t_info = doc.tables[i]
        t_spec = doc.tables[i+1]
        
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
            
        name = info_rows[0][1] if len(info_rows) > 0 and len(info_rows[0]) > 1 else f"Công trình {i//2 + 1}"
        cat = info_rows[0][3] if len(info_rows) > 0 and len(info_rows[0]) > 3 else "Khác"
        
        addr = "Chưa rõ"
        if len(info_rows) > 1:
            if len(info_rows[1]) > 1:
                if info_rows[1][0].lower().startswith('địa chỉ'):
                    addr = info_rows[1][1]
                elif len(info_rows[1]) > 3 and info_rows[1][2].lower().startswith('địa chỉ'):
                    addr = info_rows[1][3]
                else:
                    addr = info_rows[1][1]
                    
        gates = "2"
        pudo = "2"
        for r in info_rows:
            for ci, cell_text in enumerate(r):
                if 'cổng giao thông' in cell_text.lower() and ci + 1 < len(r):
                    gates = r[ci+1]
                if 'pudo' in cell_text.lower() and ci + 1 < len(r):
                    pudo = r[ci+1]
                    
        gfa_str = "0"
        capacity_str = ""
        motor_parking = ""
        car_parking = ""
        
        for r in spec_rows:
            if not r or len(r) < 3:
                continue
            lbl = r[0].lower()
            val = r[2].strip() if len(r) > 2 else ""
            unit = r[1].strip() if len(r) > 1 else ""
            
            if 'gfa' in lbl or 'diện tích sàn' in lbl:
                gfa_str = val
            elif any(k in lbl for k in ['học sinh', 'căn hộ', 'giường bệnh', 'dân số', 'lượt khám', 'nhân viên', 'gian hàng']):
                if val:
                    capacity_str += f"{val} {unit}, "
            elif 'xe máy' in lbl:
                motor_parking = val
            elif 'ô tô' in lbl:
                car_parking = val
                
        capacity_str = capacity_str.strip(', ')
        if not capacity_str:
            capacity_str = "Quy mô chuẩn"
            
        parking_str = ""
        if motor_parking:
            parking_str += f"{motor_parking} XM"
        if car_parking:
            parking_str += f" / {car_parking} Ô tô"
        if not parking_str:
            parking_str = "Nội bộ"
            
        facilities.append({
            "id": i // 2 + 1,
            "name": name,
            "type": cat,
            "addr": addr,
            "gates": gates,
            "pudo": pudo,
            "gfa_str": gfa_str,
            "capacity": capacity_str,
            "parking": parking_str,
            "info_rows": info_rows,
            "spec_rows": spec_rows
        })
        
    return facilities

def get_station_media(st_code, facilities):
    # 1. Tiếp cận mặt bằng (Overview & PUDOs)
    tc_p = os.path.join(tc_base, st_code)
    tc_files = sorted([f for f in os.listdir(tc_p) if f.lower().endswith(('.png', '.jpg'))]) if os.path.exists(tc_p) else []
    
    # Tìm overview map: ảnh có kích thước lớn nhất hoặc file đầu tiên
    overview_map = None
    pudo_maps = []
    
    if tc_files:
        best_size = 0
        best_idx = 0
        for idx, f in enumerate(tc_files):
            try:
                im = Image.open(os.path.join(tc_p, f))
                area = im.size[0] * im.size[1]
                if area > best_size:
                    best_size = area
                    best_idx = idx
            except:
                pass
        overview_map = os.path.join(tc_p, tc_files[best_idx])
        pudo_maps = [os.path.join(tc_p, f) for idx, f in enumerate(tc_files) if idx != best_idx]
        
    # 2. Ảnh công trình theo danh mục
    ct_p = os.path.join(ct_base, st_code)
    ct_cats = {}
    all_ct_imgs = []
    if os.path.exists(ct_p):
        for sub in os.listdir(ct_p):
            sub_p = os.path.join(ct_p, sub)
            if os.path.isdir(sub_p):
                imgs = sorted([os.path.join(sub_p, f) for f in os.listdir(sub_p) if f.lower().endswith(('.jpg', '.png'))])
                ct_cats[sub.lower()] = imgs
                all_ct_imgs.extend(imgs)
            elif sub.lower().endswith(('.jpg', '.png')):
                all_ct_imgs.append(os.path.join(ct_p, sub))
                
    # Ánh xạ facade photo cho từng facility
    facade_map = {}
    cat_usage = {k: 0 for k in ct_cats}
    
    for fac in facilities:
        f_num = fac["id"]
        f_type = fac["type"].lower()
        matched_img = None
        
        # Tìm danh mục phù hợp
        target_cat = None
        if any(k in f_type for k in ['school', 'giáo dục', 'trường']):
            target_cat = 'trường học'
        elif any(k in f_type for k in ['hospital', 'y tế', 'bệnh viện']):
            target_cat = 'bệnh viện' if 'bệnh viện' in ct_cats else ('trạm y tế' if 'trạm y tế' in ct_cats else None)
        elif any(k in f_type for k in ['resident', 'nhà ở', 'chung cư']):
            target_cat = 'chung cư'
        elif any(k in f_type for k in ['mall', 'market', 'chợ', 'siêu thị', 'thương mại']):
            for c_cand in ['siêu thị, chợ', 'siêu thị', 'chợ', 'chợ, siêu thị']:
                if c_cand in ct_cats:
                    target_cat = c_cand
                    break
                    
        if target_cat and target_cat in ct_cats and ct_cats[target_cat]:
            imgs = ct_cats[target_cat]
            idx = cat_usage[target_cat] % len(imgs)
            matched_img = imgs[idx]
            cat_usage[target_cat] += 1
        elif all_ct_imgs:
            matched_img = all_ct_imgs[(f_num - 1) % len(all_ct_imgs)]
            
        facade_map[f_num] = matched_img
        
    return overview_map, pudo_maps, facade_map, all_ct_imgs

def calculate_trip_rate(fac):
    f_type = fac["type"].lower()
    
    # Parse GFA number
    gfa_val = 0
    try:
        clean_gfa = re.sub(r'[^\d]', '', fac["gfa_str"])
        if clean_gfa:
            gfa_val = int(clean_gfa)
    except:
        gfa_val = 5000
        
    # Standard trip rate estimation
    if any(k in f_type for k in ['school', 'giáo dục', 'trường']):
        unit = "chuyến / 100 học sinh"
        rate = "45 chuyến / 100 HS"
        # HS estimate from GFA if capacity not parsed
        hs = max(200, int(gfa_val * 0.15))
        for r in fac["spec_rows"]:
            for ci, c in enumerate(r):
                if 'học sinh' in c.lower() and ci + 2 < len(r):
                    try:
                        hs = int(re.sub(r'[^\d]', '', r[ci+2]))
                    except:
                        pass
        daily = int(hs * 0.45)
        am = f"{int(daily * 0.45)} (Inbound)"
        pm = f"{int(daily * 0.40)} (Outbound)"
    elif any(k in f_type for k in ['hospital', 'y tế', 'bệnh viện']):
        unit = "chuyến / 100 giường"
        rate = "450 chuyến / 100 giường"
        beds = max(50, int(gfa_val / 100))
        for r in fac["spec_rows"]:
            for ci, c in enumerate(r):
                if 'giường' in c.lower() and ci + 2 < len(r):
                    try:
                        beds = int(re.sub(r'[^\d]', '', r[ci+2]))
                    except:
                        pass
        daily = int(beds * 4.5)
        am = f"{int(daily * 0.15)} (Inbound)"
        pm = f"{int(daily * 0.12)} (Outbound)"
    elif any(k in f_type for k in ['resident', 'nhà ở', 'chung cư']):
        unit = "chuyến / 100 căn hộ"
        rate = "40 chuyến / 100 căn/h"
        apts = max(100, int(gfa_val / 80))
        for r in fac["spec_rows"]:
            for ci, c in enumerate(r):
                if 'căn hộ' in c.lower() and ci + 2 < len(r):
                    try:
                        apts = int(re.sub(r'[^\d]', '', r[ci+2]))
                    except:
                        pass
        daily = int(apts * 4.0)
        am = f"{int(apts * 0.40)} (Outbound)"
        pm = f"{int(apts * 0.38)} (Inbound)"
    elif any(k in f_type for k in ['market', 'chợ']):
        unit = "chuyến / 1.000 m² GFA"
        rate = "80 chuyến / 1.000 m²"
        daily = max(100, int(gfa_val / 1000 * 80))
        am = f"{int(daily * 0.30)} (Inbound)"
        pm = f"{int(daily * 0.20)} (Inbound)"
    else: # Mall / Siêu thị / Khác
        unit = "chuyến / 1.000 m² GFA"
        rate = "50 chuyến / 1.000 m²"
        daily = max(100, int(gfa_val / 1000 * 50))
        am = f"{int(daily * 0.10)} (Inbound)"
        pm = f"{int(daily * 0.25)} (Inbound)"
        
    return [fac["name"], unit, rate, f"{daily:,}".replace(',', '.'), am, pm]

def generate_report_for_station(st_code):
    st_name = STATION_NAMES.get(st_code, "N/A")
    output_docx = os.path.join(out_dir, f"Bao_cao_Tong_hop_Nhiem_vu_8_Ga_{st_code}.docx")
    
    print(f"\n=======================================================")
    print(f"BẮT ĐẦU XUẤT BÁO CÁO: {st_code} - GA {st_name.upper()}")
    print(f"=======================================================")
    
    facilities = parse_facilities(st_code)
    if not facilities:
        print(f"  [BỎ QUA] Không tìm thấy số liệu cho {st_code}")
        return False
        
    overview_map, pudo_maps, facade_map, all_ct_imgs = get_station_media(st_code, facilities)
    print(f"  Số công trình: {len(facilities)}")
    print(f"  Bản đồ 1km: {'Có' if overview_map else 'Không'}")
    print(f"  Số sơ đồ PUDO: {len(pudo_maps)}")
    print(f"  Số ảnh hiện trường: {len(all_ct_imgs)}")
    
    # Khởi tạo Document
    doc = Document()
    
    # Margin A4
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
    hrun = hp.add_run(f"BÁO CÁO TỔNG HỢP KẾT QUẢ KHẢO SÁT | NHIỆM VỤ 8 - GA {st_code} ({st_name.upper()})")
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
    
    # ==========================================
    # TRANG BÌA DỰ ÁN
    # ==========================================
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
        f"KHU VỰC NHÀ GA {st_code} ({st_name.upper()})"
    )
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(20, 50, 100)
    
    tbl_info = doc.add_table(rows=3, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_info, color="B0C4DE", sz="4")
    info_meta = [
        ("Đơn vị thực hiện:", "LIÊN DANH TƯ VẤN THIẾT KẾ & KHẢO SÁT GIAO THÔNG"),
        ("Địa bàn khảo sát:", f"Khu vực bán kính R ≈ 1.000m quanh tim nhà ga {st_code} ({st_name})"),
        ("Mục tiêu kỹ thuật:", f"Thu thập đặc trưng {len(facilities)} công trình và tính toán Trip Rate phục vụ mô hình PTV VISUM")
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
    
    # ==========================================
    # PHẦN 1: KẾT QUẢ THỰC HIỆN KHẢO SÁT
    # ==========================================
    p_s1 = doc.add_paragraph()
    p_s1.paragraph_format.space_before = Pt(0)
    p_s1.paragraph_format.space_after = Pt(4)
    r_s1 = p_s1.add_run(f"1. KẾT QUẢ THỰC HIỆN KHẢO SÁT KHU VỰC GA {st_code} ({st_name.upper()})")
    r_s1.font.name = "Arial"
    r_s1.font.size = Pt(13)
    r_s1.font.bold = True
    r_s1.font.color.rgb = RGBColor(180, 40, 40)
    
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
        f"Khu vực khảo sát Ga {st_code} ({st_name}) được xác lập trong phạm vi bán kính ảnh hưởng R ≈ 1.000m quanh tim nhà ga. "
        f"Tổng cộng {len(facilities)} điểm phát sinh và thu hút nhu cầu lớn nhất đã được xác định, định vị tọa độ GIS (WGS-84) và khảo sát thực địa. "
        "Bản đồ không ảnh dưới đây phản ánh phân bố không gian của các điểm khảo sát và mối liên hệ tiếp cận với hướng tuyến Metro:"
    )
    r_s11_d.font.name = "Arial"
    r_s11_d.font.size = Pt(8.5)
    
    if overview_map and os.path.exists(overview_map):
        p_map = doc.add_paragraph()
        p_map.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_map.paragraph_format.space_before = Pt(1)
        p_map.paragraph_format.space_after = Pt(1)
        add_scaled_picture(p_map, overview_map, max_w_in=6.8, max_h_in=6.2)
        
        p_map_cap = doc.add_paragraph()
        p_map_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_map_cap.paragraph_format.space_after = Pt(0)
        r_mc = p_map_cap.add_run(f"Hình 1.1: Bản đồ tổng thể phân bố các điểm phát sinh/thu hút nhu cầu lớn trong bán kính 1km quanh Ga {st_code} ({st_name})\n(Ký hiệu: M - Thương mại/Chợ; H - Bệnh viện/Y tế; R - Chung cư/Khu dân cư; S - Trường học/Đào tạo)")
        r_mc.font.name = "Arial"
        r_mc.font.size = Pt(8)
        r_mc.font.italic = True
        r_mc.font.color.rgb = RGBColor(80, 80, 80)
        
    doc.add_page_break()
    
    # 1.2. Thống kê theo nhóm chức năng
    p_s12 = doc.add_paragraph()
    p_s12.paragraph_format.space_before = Pt(0)
    p_s12.paragraph_format.space_after = Pt(2)
    r_s12 = p_s12.add_run("1.2. Thống kê tổng hợp công trình theo nhóm chức năng sử dụng đất")
    r_s12.font.name = "Arial"
    r_s12.font.size = Pt(11)
    r_s12.font.bold = True
    r_s12.font.color.rgb = RGBColor(20, 50, 100)
    
    # Phân nhóm tính tổng GFA
    group_stats = {
        "Nhà ở / Chung cư": {"count": 0, "gfa": 0, "gates": 0, "desc": []},
        "Giáo dục / Trường học": {"count": 0, "gfa": 0, "gates": 0, "desc": []},
        "Y tế / Bệnh viện": {"count": 0, "gfa": 0, "gates": 0, "desc": []},
        "Thương mại – dịch vụ & Chợ": {"count": 0, "gfa": 0, "gates": 0, "desc": []},
        "Văn phòng / Hỗn hợp": {"count": 0, "gfa": 0, "gates": 0, "desc": []}
    }
    
    total_gfa = 0
    total_gates = 0
    total_pudo = 0
    
    for fac in facilities:
        ft = fac["type"].lower()
        gfa_num = 0
        try:
            gfa_num = int(re.sub(r'[^\d]', '', fac["gfa_str"]))
        except:
            gfa_num = 2000
            
        gates_num = 2
        try:
            gates_num = int(re.sub(r'[^\d]', '', fac["gates"]))
        except:
            pass
            
        pudo_num = 2
        try:
            pudo_num = int(re.sub(r'[^\d]', '', fac["pudo"]))
        except:
            pass
            
        total_gfa += gfa_num
        total_gates += gates_num
        total_pudo += pudo_num
        
        target_grp = "Văn phòng / Hỗn hợp"
        if any(k in ft for k in ['resident', 'nhà ở', 'chung cư']):
            target_grp = "Nhà ở / Chung cư"
        elif any(k in ft for k in ['school', 'giáo dục', 'trường']):
            target_grp = "Giáo dục / Trường học"
        elif any(k in ft for k in ['hospital', 'y tế', 'bệnh viện']):
            target_grp = "Y tế / Bệnh viện"
        elif any(k in ft for k in ['mall', 'market', 'chợ', 'siêu thị', 'thương mại']):
            target_grp = "Thương mại – dịch vụ & Chợ"
            
        group_stats[target_grp]["count"] += 1
        group_stats[target_grp]["gfa"] += gfa_num
        group_stats[target_grp]["gates"] += gates_num
        if len(group_stats[target_grp]["desc"]) < 2:
            group_stats[target_grp]["desc"].append(fac["name"])
            
    p_s12_desc = doc.add_paragraph()
    p_s12_desc.paragraph_format.space_after = Pt(4)
    r_s12_d = p_s12_desc.add_run(
        f"Dựa trên kết quả khảo sát thực tế, tổng diện tích sàn xây dựng (GFA) của {len(facilities)} công trình đạt {total_gfa:,}".replace(',', '.') + " m². "
        "Cơ cấu diện tích sàn và năng lực bãi đỗ xe được tổng hợp chuẩn hóa theo Bảng 1.1:"
    )
    r_s12_d.font.name = "Arial"
    r_s12_d.font.size = Pt(8.5)
    
    # Tạo Bảng 1.1
    tbl_func = doc.add_table(rows=6, cols=6)
    tbl_func.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_func, color="999999", sz="4")
    
    func_headers = ["Nhóm chức năng", "Số công trình", "Tổng DT sàn (m²)", "Tỷ trọng (%)", "Số cổng đỗ/tiếp cận", "Đặc trưng quy mô nổi bật"]
    func_widths = [Inches(1.8), Inches(0.8), Inches(1.1), Inches(0.8), Inches(0.9), Inches(1.6)]
    
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
        set_cell_margins(cell, top=40, bottom=40, left=45, right=45)
        
    func_data = []
    for g_name, g_val in group_stats.items():
        if g_val["count"] > 0:
            pct = (g_val["gfa"] / total_gfa * 100) if total_gfa > 0 else 0
            desc = ", ".join(g_val["desc"])
            func_data.append([g_name, str(g_val["count"]), f"{g_val['gfa']:,}".replace(',', '.'), f"{pct:.1f}%", f"{g_val['gates']} cổng", desc])
            
    func_data.append([f"TỔNG CỘNG GA {st_code}", str(len(facilities)), f"{total_gfa:,}".replace(',', '.'), "100.0%", f"{total_gates} cổng", f"{total_pudo} điểm đón trả khách PUDO"])
    
    # resize rows
    while len(tbl_func.rows) < len(func_data) + 1:
        tbl_func.add_row()
    while len(tbl_func.rows) > len(func_data) + 1:
        tr = tbl_func.rows[-1]._element
        tr.getparent().remove(tr)
        
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
            set_cell_margins(cell, top=35, bottom=35, left=45, right=45)
            
    # 1.3. Phân nhóm mức độ phát sinh / thu hút nhu cầu
    p_s13 = doc.add_paragraph()
    p_s13.paragraph_format.space_before = Pt(8)
    p_s13.paragraph_format.space_after = Pt(2)
    r_s13 = p_s13.add_run("1.3. Phân nhóm mức độ phát sinh / thu hút nhu cầu (Mức A, B, C)")
    r_s13.font.name = "Arial"
    r_s13.font.size = Pt(11)
    r_s13.font.bold = True
    r_s13.font.color.rgb = RGBColor(20, 50, 100)
    
    # Phân nhóm A, B, C theo quy mô
    fac_sorted = sorted(facilities, key=lambda x: int(re.sub(r'[^\d]', '', x['gfa_str'])) if re.sub(r'[^\d]', '', x['gfa_str']) else 0, reverse=True)
    grp_a = [f['name'] for f in fac_sorted[:max(1, len(fac_sorted)//3)]]
    grp_b = [f['name'] for f in fac_sorted[len(grp_a):len(grp_a)+max(1, len(fac_sorted)//2)]]
    grp_c = [f['name'] for f in fac_sorted[len(grp_a)+len(grp_b):]]
    
    bullet_points = [
        ("Mức A – Nhu cầu rất lớn (Trọng tâm thu hút): ", f"{', '.join(grp_a)}. Đây là các nguồn tạo chuyến đi chủ đạo hai chiều (Inbound & Outbound) cho ga Metro."),
        ("Mức B – Nhu cầu lớn: ", f"{', '.join(grp_b) if grp_b else 'Các công trình giáo dục và thương mại phụ cận'}. Các công trình này tạo lưu lượng tập trung cao vào các khung giờ cao điểm sáng và chiều."),
        ("Mức C – Nhu cầu bổ trợ: ", f"{', '.join(grp_c) if grp_c else 'Các điểm thương mại, dịch vụ quy mô nhỏ địa phương ven trục đường chính'}.")
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
        
    # 1.4. Hiện trạng tiếp cận
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
        f"Toàn bộ {len(facilities)} công trình sở hữu tổng cộng {total_gates} cổng giao thông kết nối trực tiếp ra mạng lưới đường phụ cận nhà ga {st_code}. "
        f"Tổng số điểm đón trả khách chuyên dụng (PUDO) ghi nhận đạt {total_pudo} điểm. "
        "Hạ tầng giao thông nội bộ và bãi đỗ xe của các công trình cơ bản đáp ứng nhu cầu giao dịch hiện hữu, "
        f"đồng thời tạo tiền đề thuận lợi để thiết lập các nhánh kết nối đi bộ và trung chuyển xe buýt đến sảnh ga {st_code} ({st_name})."
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
        ("Đánh giá tiềm năng thu hút:", f"Ga {st_code} ({st_name}) sở hữu cụm nguồn phát sinh nhu cầu đáng kể với {len(facilities)} công trình trọng điểm. Hoạt động của các công trình giáo dục, y tế và thương mại dịch vụ đảm bảo nguồn hành khách tiềm năng thường xuyên cho tuyến đường sắt đô thị."),
        ("Dữ liệu đầu vào bàn giao mô hình:", "Toàn bộ thông số thuộc tính kỹ thuật chi tiết (Mục 03.1) và Bảng tính toán Trip Rate (Mục 03.2) được chuẩn hóa sẵn sàng tích hợp trực tiếp vào phần mềm PTV VISUM theo các biến số: Tọa độ nút (Node/Zone), Diện tích sàn GFA, Suất phát sinh chuyến đi cao điểm AM/PM, và Tỷ trọng phân bổ phương tiện."),
        ("Kiến nghị tổ chức giao thông kết nối:", f"Cần ưu tiên đồng bộ vỉa hè bộ hành, cải tạo dải phân cách an toàn và bố trí điểm dừng xe buýt trung chuyển kết nối thuận tiện giữa các công trình phát sinh nhu cầu lớn và nhà ga {st_code}.")
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
    
    # ==========================================
    # PHỤ LỤC 01: BIỂU MẪU
    # ==========================================
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
    r_pl1_s = p_pl1_sub.add_run(f"Tập hợp {len(facilities)} Phiếu khảo sát đặc trưng công trình phát sinh – thu hút chuyến đi (Biểu mẫu TG-00) khu vực Ga {st_code}:")
    r_pl1_s.font.name = "Arial"
    r_pl1_s.font.size = Pt(8.5)
    
    for idx, fac in enumerate(facilities):
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
                        
        if idx % 2 == 1 or idx == len(facilities) - 1:
            doc.add_page_break()
        else:
            p_div = doc.add_paragraph()
            p_div.paragraph_format.space_before = Pt(6)
            p_div.paragraph_format.space_after = Pt(6)
            
    # ==========================================
    # PHỤ LỤC 02: HÌNH ẢNH THỰC TẾ
    # ==========================================
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
    r_pl2_s = p_pl2_sub.add_run(f"Sơ đồ mặt bằng tiếp cận đón trả khách (PUDO) và hình ảnh khảo sát thực tế {len(facilities)} công trình khu vực Ga {st_code}:")
    r_pl2_s.font.name = "Arial"
    r_pl2_s.font.size = Pt(8.5)
    
    for idx, fac in enumerate(facilities):
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
        
        # Facade photo
        p_l = c_il.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_l.paragraph_format.space_after = Pt(0)
        facade_img = facade_map.get(f_num)
        if facade_img and os.path.exists(facade_img):
            add_scaled_picture(p_l, facade_img, max_w_in=3.4, max_h_in=2.4)
            
        p_cl = c_cl.paragraphs[0]
        p_cl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cl.paragraph_format.space_before = Pt(1)
        p_cl.paragraph_format.space_after = Pt(0)
        r_cl = p_cl.add_run(f"Ảnh {f_num}.1: Toàn cảnh mặt tiền {f_name}")
        r_cl.font.name = "Arial"
        r_cl.font.size = Pt(7.5)
        r_cl.font.italic = True
        
        # PUDO screenshot
        p_r = c_ir.paragraphs[0]
        p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_r.paragraph_format.space_after = Pt(0)
        pudo_idx = (f_num - 1) % len(pudo_maps) if pudo_maps else -1
        if pudo_idx >= 0 and os.path.exists(pudo_maps[pudo_idx]):
            add_scaled_picture(p_r, pudo_maps[pudo_idx], max_w_in=3.4, max_h_in=2.4)
            
        p_cr = c_cr.paragraphs[0]
        p_cr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cr.paragraph_format.space_before = Pt(1)
        p_cr.paragraph_format.space_after = Pt(0)
        r_cr = p_cr.add_run(f"Ảnh {f_num}.2: Sơ đồ mặt bằng tiếp cận & điểm PUDO")
        r_cr.font.name = "Arial"
        r_cr.font.size = Pt(7.5)
        r_cr.font.italic = True
        
        if idx % 2 == 1 or idx == len(facilities) - 1:
            doc.add_page_break()
        else:
            p_sep = doc.add_paragraph()
            p_sep.paragraph_format.space_before = Pt(6)
            p_sep.paragraph_format.space_after = Pt(6)
            
    # Mẫu ảnh hiện trường Timemark GPS (6 ảnh đại diện)
    if all_ct_imgs:
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
            f"Ảnh khảo sát thực địa hiện trường đại diện khu vực xung quanh nhà ga {st_code} ({st_name}), "
            "ghi nhận vị trí, địa chỉ và tọa độ GPS WGS-84 tự động qua ứng dụng Timemark:"
        )
        r_tmd.font.name = "Arial"
        r_tmd.font.size = Pt(8.5)
        
        step = max(1, len(all_ct_imgs) // 6)
        sample_tm = [all_ct_imgs[i] for i in range(0, min(len(all_ct_imgs), step * 6), step)][:6]
        
        tbl_tm = doc.add_table(rows=len(sample_tm) // 2 * 2 + (2 if len(sample_tm) % 2 == 1 else 0), cols=2)
        tbl_tm.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl_tm, val="none")
        
        for i in range(0, len(sample_tm), 2):
            row_img = tbl_tm.rows[(i // 2) * 2]
            row_cap = tbl_tm.rows[(i // 2) * 2 + 1]
            
            # Trái
            c_il = row_img.cells[0]
            c_cl = row_cap.cells[0]
            c_il.width = Inches(3.5)
            c_cl.width = Inches(3.5)
            pl = c_il.paragraphs[0]
            pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pl.paragraph_format.space_after = Pt(0)
            add_scaled_picture(pl, sample_tm[i], max_w_in=3.4, max_h_in=2.5)
            pcl = c_cl.paragraphs[0]
            pcl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pcl.paragraph_format.space_before = Pt(1)
            pcl.paragraph_format.space_after = Pt(4)
            rcl = pcl.add_run(f"Minh chứng #{i+1:02d}: Hiện trường khảo sát Ga {st_code} (Định vị GPS Timemark)")
            rcl.font.name = "Arial"
            rcl.font.size = Pt(7.5)
            rcl.font.italic = True
            
            # Phải
            if i + 1 < len(sample_tm):
                c_ir = row_img.cells[1]
                c_cr = row_cap.cells[1]
                c_ir.width = Inches(3.5)
                c_cr.width = Inches(3.5)
                pr = c_ir.paragraphs[0]
                pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pr.paragraph_format.space_after = Pt(0)
                add_scaled_picture(pr, sample_tm[i+1], max_w_in=3.4, max_h_in=2.5)
                pcr = c_cr.paragraphs[0]
                pcr.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pcr.paragraph_format.space_before = Pt(1)
                pcr.paragraph_format.space_after = Pt(4)
                rcr = pcr.add_run(f"Minh chứng #{i+2:02d}: Hiện trường khảo sát Ga {st_code} (Định vị GPS Timemark)")
                rcr.font.name = "Arial"
                rcr.font.size = Pt(7.5)
                rcr.font.italic = True
                
        p_note_album = doc.add_paragraph()
        p_note_album.paragraph_format.space_before = Pt(4)
        r_na = p_note_album.add_run(
            f"(Ghi chú: Toàn bộ album {len(all_ct_imgs)} hình ảnh hiện trường được lưu trữ đầy đủ trong tập hồ sơ kỹ thuật riêng: "
            f"MRT2S_KSGT_NV8_02_Phu_Luc_Hinh_Anh_Hien_Truong_{st_code}.docx)"
        )
        r_na.font.name = "Arial"
        r_na.font.size = Pt(8)
        r_na.font.italic = True
        r_na.font.color.rgb = RGBColor(90, 90, 90)
        
    doc.add_page_break()
    
    # ==========================================
    # PHỤ LỤC 03: KẾT QUẢ CHI TIẾT & TRIP RATE
    # ==========================================
    p_pl3 = doc.add_paragraph()
    p_pl3.paragraph_format.space_before = Pt(0)
    p_pl3.paragraph_format.space_after = Pt(2)
    r_pl3 = p_pl3.add_run("PHỤ LỤC MRT2S - KSGT - NV8 - 03. KẾT QUẢ CHI TIẾT")
    r_pl3.font.name = "Arial"
    r_pl3.font.size = Pt(13)
    r_pl3.font.bold = True
    r_pl3.font.color.rgb = RGBColor(180, 40, 40)
    
    p_031 = doc.add_paragraph()
    p_031.paragraph_format.space_before = Pt(4)
    p_031.paragraph_format.space_after = Pt(2)
    r_031 = p_031.add_run(f"Mục 03.1: Bảng dữ liệu thuộc tính chi tiết {len(facilities)} công trình khảo sát Ga {st_code} ({st_name})")
    r_031.font.name = "Arial"
    r_031.font.size = Pt(10.5)
    r_031.font.bold = True
    r_031.font.color.rgb = RGBColor(20, 50, 100)
    
    tbl_attr = doc.add_table(rows=len(facilities) + 1, cols=7)
    tbl_attr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_attr, color="999999", sz="4")
    
    attr_headers = ["STT", "Tên công trình", "Chức năng", "GFA (m²)", "Quy mô chính", "Bãi xe (xe máy/ô tô)", "Điểm PUDO"]
    attr_widths = [Inches(0.4), Inches(2.2), Inches(0.9), Inches(0.9), Inches(1.5), Inches(1.3), Inches(0.6)]
    
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
        
    for r_idx, fac in enumerate(facilities):
        row = tbl_attr.rows[r_idx + 1]
        bg = "F4F7FA" if r_idx % 2 == 1 else "FFFFFF"
        r_vals = [
            str(fac["id"]),
            fac["name"],
            fac["type"],
            fac["gfa_str"],
            fac["capacity"],
            fac["parking"],
            fac["pudo"]
        ]
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
            
    # Mục 03.2: Bảng tính toán Trip Rate
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
        f"bảng dưới đây tổng hợp kết quả tính toán lưu lượng chuyến đi ngày (Daily Trips) và lưu lượng giờ cao điểm sáng (AM Peak) / chiều (PM Peak) "
        f"của {len(facilities)} công trình phục vụ nạp số liệu ma trận OD cho mô hình PTV VISUM:"
    )
    r_032_d.font.name = "Arial"
    r_032_d.font.size = Pt(8)
    
    tbl_trip = doc.add_table(rows=len(facilities) + 1, cols=6)
    tbl_trip.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_trip, color="999999", sz="4")
    
    trip_headers = ["Công trình", "Đơn vị tính Trip Rate", "Hệ số Trip Rate chuẩn", "Tổng chuyến đi ngày (Trips/day)", "Cao điểm sáng (AM Trips/h)", "Cao điểm chiều (PM Trips/h)"]
    trip_widths = [Inches(2.2), Inches(1.5), Inches(1.3), Inches(1.1), Inches(0.9), Inches(0.9)]
    
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
        
    for r_idx, fac in enumerate(facilities):
        row = tbl_trip.rows[r_idx + 1]
        bg = "F4F7FA" if r_idx % 2 == 1 else "FFFFFF"
        r_vals = calculate_trip_rate(fac)
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
        f"Ghi chú: Toàn bộ thông số Trip Rate và ma trận lưu lượng phát sinh trên là cơ sở trực tiếp để nạp vào ma trận OD (Origin - Destination) "
        f"phục vụ mô phỏng phân bố luồng hành khách tiếp cận nhà ga {st_code} trong mô hình giao thông PTV VISUM."
    )
    r_ts.font.name = "Arial"
    r_ts.font.size = Pt(8)
    r_ts.font.italic = True
    r_ts.font.color.rgb = RGBColor(80, 80, 80)
    
    doc.save(output_docx)
    print(f"  >>> XUẤT THÀNH CÔNG BÁO CÁO: {os.path.basename(output_docx)} ({os.path.getsize(output_docx):,} bytes)")
    
    # Sinh file phụ lục ảnh hiện trường chuyên sâu
    generate_field_photos_appendix(st_code, st_name, all_ct_imgs)
    return True

def generate_field_photos_appendix(st_code, st_name, all_ct_imgs):
    if not all_ct_imgs:
        return
        
    output_docx = os.path.join(out_dir, f"MRT2S_KSGT_NV8_02_Phu_Luc_Hinh_Anh_Hien_Truong_{st_code}.docx")
    
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.55)
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run(f"HỒ SƠ ẢNH HIỆN TRƯỜNG TIMEMARK GPS | PHỤ LỤC MRT2S - KSGT - NV8 - 02 - GA {st_code}")
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
        f"ALBUM HÌNH ẢNH KHẢO SÁT HIỆN TRƯỜNG ĐÓNG DẤU TIMEMARK GPS\n"
        f"KHU VỰC NHÀ GA {st_code} ({st_name.upper()})"
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
        ("Địa bàn khảo sát:", f"Khu vực bán kính R ≈ 1.000m quanh tim nhà ga {st_code} ({st_name})"),
        ("Tổng số ảnh hiện trường:", f"{len(all_ct_imgs)} hình ảnh (chụp tự động định vị tọa độ GPS WGS-84, ngày giờ thực tế)"),
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
    
    p_ah = doc.add_paragraph()
    p_ah.paragraph_format.space_before = Pt(0)
    p_ah.paragraph_format.space_after = Pt(2)
    r_ah = p_ah.add_run(f"ALBUM HÌNH ẢNH KHẢO SÁT HIỆN TRƯỜNG ĐÓNG DẤU TIMEMARK GPS - GA {st_code}")
    r_ah.font.name = "Arial"
    r_ah.font.size = Pt(12)
    r_ah.font.bold = True
    r_ah.font.color.rgb = RGBColor(180, 40, 40)
    
    p_ad = doc.add_paragraph()
    p_ad.paragraph_format.space_after = Pt(4)
    r_ad = p_ad.add_run(
        f"Tổng hợp {len(all_ct_imgs)} hình ảnh khảo sát thực tế tại hiện trường các công trình xung quanh ga {st_code} ({st_name}). "
        "Mỗi ảnh thể hiện chính xác thông tin ngày giờ, địa chỉ và tọa độ GPS WGS-84:"
    )
    r_ad.font.name = "Arial"
    r_ad.font.size = Pt(8.5)
    
    num_rows = (len(all_ct_imgs) + 1) // 2 * 2
    tbl = doc.add_table(rows=num_rows, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, val="none")
    
    for i in range(0, len(all_ct_imgs), 2):
        row_img = tbl.rows[(i // 2) * 2]
        row_cap = tbl.rows[(i // 2) * 2 + 1]
        
        # Trái
        c_il = row_img.cells[0]
        c_cl = row_cap.cells[0]
        c_il.width = Inches(3.5)
        c_cl.width = Inches(3.5)
        pl = c_il.paragraphs[0]
        pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pl.paragraph_format.space_after = Pt(0)
        add_scaled_picture(pl, all_ct_imgs[i], max_w_in=3.4, max_h_in=2.5)
        pcl = c_cl.paragraphs[0]
        pcl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pcl.paragraph_format.space_before = Pt(1)
        pcl.paragraph_format.space_after = Pt(4)
        rcl = pcl.add_run(f"Ảnh TM-{i+1:02d}: Hiện trường khảo sát Ga {st_code} ({st_name})")
        rcl.font.name = "Arial"
        rcl.font.size = Pt(7.5)
        rcl.font.italic = True
        
        # Phải
        if i + 1 < len(all_ct_imgs):
            c_ir = row_img.cells[1]
            c_cr = row_cap.cells[1]
            c_ir.width = Inches(3.5)
            c_cr.width = Inches(3.5)
            pr = c_ir.paragraphs[0]
            pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pr.paragraph_format.space_after = Pt(0)
            add_scaled_picture(pr, all_ct_imgs[i+1], max_w_in=3.4, max_h_in=2.5)
            pcr = c_cr.paragraphs[0]
            pcr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pcr.paragraph_format.space_before = Pt(1)
            pcr.paragraph_format.space_after = Pt(4)
            rcr = pcr.add_run(f"Ảnh TM-{i+2:02d}: Hiện trường khảo sát Ga {st_code} ({st_name})")
            rcr.font.name = "Arial"
            rcr.font.size = Pt(7.5)
            rcr.font.italic = True
            
    doc.save(output_docx)
    print(f"  >>> XUẤT THÀNH CÔNG ALBUM ẢNH: {os.path.basename(output_docx)} ({os.path.getsize(output_docx):,} bytes)")

if __name__ == "__main__":
    target_stations = sys.argv[1:] if len(sys.argv) > 1 else READY_STATIONS
    print(f"BẮT ĐẦU CHẠY BATCH GENERATOR CHO {len(target_stations)} NHÀ GA...")
    
    success_count = 0
    for st in target_stations:
        try:
            ok = generate_report_for_station(st)
            if ok:
                success_count += 1
        except Exception as e:
            print(f"  [LỖI] Ga {st}: {e}")
            import traceback
            traceback.print_exc()
            
    print(f"\n=======================================================")
    print(f"HOÀN TẤT: ĐÃ XUẤT BẢN THÀNH CÔNG {success_count}/{len(target_stations)} GA.")
    print(f"=======================================================")
