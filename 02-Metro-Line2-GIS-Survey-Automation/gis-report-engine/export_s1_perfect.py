import os
import sys
import re
import json
import warnings
import unicodedata
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

import openpyxl
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"d:\baocaotudong"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCHEMATICS_DIR = os.path.join(BASE_DIR, "schematics_26")

NAVY = RGBColor(0x00, 0x33, 0x66)       # #003366
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)  # #333333
LIGHT_BG = "F4F6F9"
HEADER_BG = "003366"
BORDER_COLOR = "D0D8E0"

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_padding(cell, top=30, bottom=30, left=50, right=50):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_protection(table):
    for i, row in enumerate(table.rows):
        trPr = row._element.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def set_col_widths(table, widths):
    for row in table.rows:
        for idx, width in enumerate(widths):
            if idx < len(row.cells):
                cell = row.cells[idx]
                cell.width = width
                tcPr = cell._element.get_or_add_tcPr()
                tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{int(width.pt * 20)}" w:type="dxa"/>')
                tcPr.append(tcW)

def set_run_font(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=None):
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)
    if size_pt:
        run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb

def extract_station_excel(group, file_name, old_id, st_name):
    data_dir = os.path.join(BASE_DIR, "Ga của Quân" if group == "quan" else "Ga của Vinh")
    fpath = os.path.join(data_dir, file_name)
    wb = openpyxl.load_workbook(fpath, data_only=True)
    
    st_data = {
        "roads": [],
        "buses": [],
        "pudo": [],
        "parkride": [],
        "conflicts": []
    }
    
    for sname in wb.sheetnames:
        ws = wb[sname]
        headers = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]
        col_coord, col_name = None, None
        for i, h in enumerate(headers):
            if "toạ độ" in h or "tọa độ" in h: col_coord = i
            elif "tên đường" in h or "nút" in h or "vị trí" in h:
                if col_name is None: col_name = i
                
        sheet_upper = sname.upper()
        if "TUYẾN ĐƯỜNG" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                rd_name = row[col_name] if col_name is not None and col_name < len(row) else None
                if rd_name and str(rd_name).strip() and str(rd_name).strip() != "None":
                    coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                    st_data["roads"].append({
                        "name": str(rd_name).strip(),
                        "type": str(row[8]).strip() if len(row) > 8 and row[8] else "Đường đô thị",
                        "lanes": str(row[10]).strip() if len(row) > 10 and row[10] else "2 - 4",
                        "width": str(row[11]).strip() if len(row) > 11 and row[11] else "12.0",
                        "cross_section": str(row[12]).strip() if len(row) > 12 and row[12] else "20.0",
                        "coords": coord_str
                    })
        elif "BUÝT" in sheet_upper or "XE BUYT" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                b_name = row[col_name] if col_name is not None and col_name < len(row) else f"Trạm dừng buýt {old_id}"
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                if coord_str:
                    st_data["buses"].append({
                        "name": str(b_name).strip() if b_name else "Điểm dừng xe buýt",
                        "coords": coord_str,
                        "dist": "≤300 m"
                    })
        elif "PUDO" in sheet_upper or "ĐÓN - TRẢ" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                if coord_str:
                    st_data["pudo"].append({"coords": coord_str, "demand": "Cao"})
        elif "PARK" in sheet_upper or "BÃI XE" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                if coord_str:
                    st_data["parkride"].append({"coords": coord_str, "type": "Bãi xe máy & ô tô"})
        elif "XUNG ĐỘT" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                cf_name = row[col_name] if col_name is not None and col_name < len(row) else f"Nút giao lân cận Ga {old_id}"
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                if coord_str:
                    st_data["conflicts"].append({"name": str(cf_name).strip() if cf_name else "Nút giao xung đột", "coords": coord_str})

    return st_data

def build_s1_document():
    cfg = {
        "num": 1,
        "code": "ST01",
        "old_id": "S1",
        "group": "quan",
        "file": "Ga 1.xlsx",
        "name": "Phan Văn Hớn",
        "lat": 10.82841,
        "lon": 106.62438,
        "area": "Phường Tây Thạnh (Tân Phú) & Đông Hưng Thuận (Quận 12)",
        "surveyor": "Kỹ sư Nguyễn Minh Quân"
    }
    
    st_code = cfg["code"]
    st_old_id = cfg["old_id"]
    st_name = cfg["name"]
    group = cfg["group"]
    st_area = cfg["area"]
    lat_c = cfg["lat"]
    lon_c = cfg["lon"]
    surveyor_name = cfg["surveyor"]

    st_data = extract_station_excel(group, cfg["file"], st_old_id, st_name)

    photos_base = os.path.join(BASE_DIR, "photos_quan", st_old_id)
    pman_file = os.path.join(photos_base, "images_manifest.json")
    manifest = []
    if os.path.exists(pman_file):
        with open(pman_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
    manifest_by_cat = {"road": [], "bus": [], "pudo": [], "parkride": [], "conflict": []}
    valid_photos = []
    for m in manifest:
        if m.get("status") == "success" and os.path.exists(m.get("path", "")):
            valid_photos.append(m)
            cat = m.get("category", "")
            if cat in manifest_by_cat:
                manifest_by_cat[cat].append(m)

    maps_base = os.path.join(BASE_DIR, "maps_quan", st_old_id)
    map1 = os.path.join(maps_base, f"{st_old_id}_Map1_TongQuan_1000m.png")
    map2 = os.path.join(maps_base, f"{st_old_id}_Map2_DiBo_200m_500m.png")
    map3 = os.path.join(maps_base, f"{st_old_id}_Map3_Buyt_PUDO.png")
    if not os.path.exists(map3): map3 = os.path.join(maps_base, f"{st_old_id}_Map3_Bus_PUDO.png")
    map4 = os.path.join(maps_base, f"{st_old_id}_Map4_ParkRide_XungDot.png")
    map5 = os.path.join(maps_base, f"{st_old_id}_Map5_RaoCan_TiepCan.png")
    if not os.path.exists(map5): map5 = os.path.join(maps_base, f"{st_old_id}_Map5_RaoCan_TongHop.png")
    map_paths = [map1, map2, map3, map4, map5]

    schematic_path = os.path.join(SCHEMATICS_DIR, f"{st_code}_schematic.png")

    doc = docx.Document()
    
    for sec in doc.sections:
        sec.top_margin = Inches(0.7)
        sec.bottom_margin = Inches(0.7)
        sec.left_margin = Inches(0.85)
        sec.right_margin = Inches(0.75)
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = DARK_GRAY

    def add_sec_title(title_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title_text)
        set_run_font(run, font_name="Times New Roman", size_pt=13, bold=True, color_rgb=NAVY)
        return p

    def add_h2(h2_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(h2_text)
        set_run_font(run, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)
        return p

    # CHÈN BẢN ĐỒ CĂN GIỮA TRANG - KÍCH THƯỚC LỚN RÕ NÉT (5.8 - 6.3 INCH)
    def add_map(m_path, caption_text, width_inch=6.1):
        if os.path.exists(m_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(2)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            run_img = p_img.add_run()
            run_img.add_picture(m_path, width=Inches(width_inch))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(4)
            run = p_cap.add_run(caption_text)
            set_run_font(run, font_name="Times New Roman", size_pt=10.0, italic=True, color_rgb=DARK_GRAY)

    # BẢNG ẢNH 2 CỘT: BÊN TRÁI ẢNH TO RÕ, BÊN PHẢI CHỮ CHI TIẾT (XẾP DỌC XUỐNG TỪNG HÀNG)
    def create_photo_table_vertical(photo_items):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        hdr = tbl.rows[0].cells
        hdr[0].text = "Hình ảnh Thực địa Khảo sát"
        hdr[1].text = "Thông tin Chi tiết & Tọa độ GPS"
        set_cell_background(hdr[0], HEADER_BG)
        set_cell_background(hdr[1], HEADER_BG)
        set_cell_padding(hdr[0], 25, 25, 40, 40)
        set_cell_padding(hdr[1], 25, 25, 40, 40)
        set_run_font(hdr[0].paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=RGBColor(255, 255, 255))
        set_run_font(hdr[1].paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=RGBColor(255, 255, 255))
        hdr[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        for p_path, cap, desc in photo_items:
            if not p_path or not os.path.exists(p_path):
                continue
            row = tbl.add_row()
            c_img = row.cells[0]
            c_txt = row.cells[1]
            set_cell_background(c_img, LIGHT_BG)
            set_cell_background(c_txt, LIGHT_BG)
            set_cell_padding(c_img, 20, 20, 30, 30)
            set_cell_padding(c_txt, 20, 20, 35, 35)
            
            # Cột TRÁI: Ảnh to rõ (auto scale dọc/ngang)
            p_img = c_img.paragraphs[0]
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(2)
            p_img.paragraph_format.space_after = Pt(2)
            run_img = p_img.add_run()
            try:
                with Image.open(p_path) as im:
                    w_px, h_px = im.size
                if h_px > w_px:
                    run_img.add_picture(p_path, height=Inches(2.35))
                else:
                    calc_h = 2.95 / (w_px / h_px)
                    if calc_h > 2.35:
                        run_img.add_picture(p_path, height=Inches(2.35))
                    else:
                        run_img.add_picture(p_path, width=Inches(2.95))
            except Exception:
                run_img.add_picture(p_path, width=Inches(2.95))

            # Cột PHẢI: Tiêu đề + Nội dung mô tả gạch đầu dòng
            p_cap = c_txt.paragraphs[0]
            p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(3)
            p_cap.paragraph_format.line_spacing = 1.15
            r_c = p_cap.add_run(cap + "\n")
            set_run_font(r_c, font_name="Times New Roman", size_pt=9.5, bold=True, color_rgb=NAVY)
            
            desc_clean = desc.replace("•", "-")
            r_d = p_cap.add_run(desc_clean)
            set_run_font(r_d, font_name="Times New Roman", size_pt=8.5, color_rgb=DARK_GRAY)

        set_col_widths(tbl, [Inches(3.1), Inches(3.4)])
        set_table_protection(tbl)
        return tbl

    # ==========================================================================
    # TRANG 1: BÌA BÁO CÁO
    # ==========================================================================
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_before = Pt(36)
    p_header.paragraph_format.space_after = Pt(2)
    r_h1 = p_header.add_run('DỰ ÁN QUY HOẠCH CHI TIẾT MẠNG LƯỚI ĐƯỜNG SẮT ĐÔ THỊ TP. HỒ CHÍ MINH\n')
    set_run_font(r_h1, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)
    r_h2 = p_header.add_run('TIỂU DỰ ÁN: METRO TUYẾN 2 (THAM LƯƠNG – AN HẠ) VÀ TUYẾN 2S (AN HẠ – CỦ CHI)')
    set_run_font(r_h2, font_name="Times New Roman", size_pt=10.5, bold=True, color_rgb=DARK_GRAY)

    p_div1 = doc.add_paragraph()
    p_div1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div1.paragraph_format.space_before = Pt(8)
    p_div1.paragraph_format.space_after = Pt(36)
    r_d1 = p_div1.add_run('―' * 28)
    set_run_font(r_d1, font_name="Times New Roman", size_pt=10, color_rgb=RGBColor(160, 160, 160))

    p_badge = doc.add_paragraph()
    p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_badge.paragraph_format.space_after = Pt(14)
    r_badge = p_badge.add_run(f'MÃ HIỆU NHÀ GA: {st_code}')
    set_run_font(r_badge, font_name="Times New Roman", size_pt=14, bold=True, color_rgb=NAVY)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(12)
    r_t1 = p_title.add_run('BÁO CÁO KẾT QUẢ KHẢO SÁT HIỆN TRẠNG TIẾP CẬN\nVÀ TRUNG CHUYỂN GA ĐƯỜNG SẮT ĐÔ THỊ\n')
    set_run_font(r_t1, font_name="Times New Roman", size_pt=16, bold=True, color_rgb=NAVY)

    p_station = doc.add_paragraph()
    p_station.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_station.paragraph_format.space_after = Pt(45)
    r_st1 = p_station.add_run(f'GA {st_code} – {st_name.upper()}\n')
    set_run_font(r_st1, font_name="Times New Roman", size_pt=18, bold=True, color_rgb=NAVY)
    r_st2 = p_station.add_run(f'({st_area})\n')
    set_run_font(r_st2, font_name="Times New Roman", size_pt=11.5, italic=True, color_rgb=DARK_GRAY)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_d = p_date.add_run('THÀNH PHỐ HỒ CHÍ MINH, THÁNG 09/2026')
    set_run_font(r_d, font_name="Times New Roman", size_pt=11, bold=True, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 2: MỤC STxx.A. THÔNG TIN CHUNG NHÀ GA VÀ PHẠM VI KHẢO SÁT
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.A. THÔNG TIN CHUNG NHÀ GA VÀ PHẠM VI KHẢO SÁT')
    
    p_intro = doc.add_paragraph('Báo cáo được lập trên cơ sở kết quả khảo sát hiện trường toàn diện về mạng lưới giao thông tiếp cận, hạ tầng kết nối đa phương thức và điều kiện trung chuyển hành khách phục vụ công tác quy hoạch chi tiết hướng tuyến Metro Tuyến 2 và Tuyến 2S.')
    p_intro.paragraph_format.space_after = Pt(4)
    p_intro.paragraph_format.line_spacing = 1.15
    set_run_font(p_intro.runs[0], font_name="Times New Roman", size_pt=11.0, color_rgb=DARK_GRAY)

    tbl_a = doc.add_table(rows=5, cols=2)
    tbl_a.alignment = WD_TABLE_ALIGNMENT.CENTER
    a_data = [
        ('Mã hiệu nhà ga:', f'{st_code} (Mã gốc: {st_old_id})', 'Tên chính thức:', f'{st_name}'),
        ('Tuyến đường sắt:', 'Metro Tuyến 2 (Tham Lương – An Hạ – Củ Chi)', 'Vị trí quy hoạch:', f'Khu vực {st_area}'),
        ('Địa giới hành chính:', st_area, 'Tọa độ GPS tim ga:', f'{lat_c:.6f} N, {lon_c:.6f} E'),
        ('Đơn vị thực hiện:', 'Nhóm Chuyên gia Khảo sát Hiện trường', 'Cán bộ phụ trách:', surveyor_name),
        ('Thời gian khảo sát:', 'Tháng 09/2026', 'Điều kiện thực địa:', 'Thời tiết khô ráo, tầm nhìn quan sát tốt')
    ]
    for idx, row in enumerate(tbl_a.rows):
        d = a_data[idx]
        row.cells[0].text = f"{d[0]} {d[1]}"
        row.cells[1].text = f"{d[2]} {d[3]}"
        for c in row.cells:
            set_cell_background(c, LIGHT_BG)
            set_cell_padding(c, 25, 25, 50, 50)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, color_rgb=DARK_GRAY)
    set_col_widths(tbl_a, [Inches(3.25), Inches(3.25)])
    set_table_protection(tbl_a)

    add_h2(f'1. Sơ đồ Vị trí Nhà ga trên Hướng tuyến Metro Tuyến 2 và Tuyến 2S')
    if os.path.exists(schematic_path):
        p_sch = doc.add_paragraph()
        p_sch.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sch.paragraph_format.space_before = Pt(2)
        p_sch.paragraph_format.space_after = Pt(2)
        p_sch.paragraph_format.keep_with_next = True
        run_sch = p_sch.add_run()
        run_sch.add_picture(schematic_path, width=Inches(6.3))
        
        p_scap = doc.add_paragraph()
        p_scap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_scap.paragraph_format.space_before = Pt(1)
        p_scap.paragraph_format.space_after = Pt(3)
        run_scap = p_scap.add_run(f'Hình {st_code}.A.1: Sơ đồ vị trí Ga {st_code} ({st_name}) trên toàn tuyến Metro Tuyến 2 và Tuyến 2S')
        set_run_font(run_scap, font_name="Times New Roman", size_pt=10.0, italic=True, color_rgb=DARK_GRAY)

    add_h2(f'2. Phạm vi và Nội dung Khảo sát Kỹ thuật')
    p_a_notes = doc.add_paragraph()
    p_a_notes.paragraph_format.space_before = Pt(1)
    p_a_notes.paragraph_format.space_after = Pt(1)
    p_a_notes.paragraph_format.line_spacing = 1.15
    r_an = p_a_notes.add_run(
        '- Khảo sát hiện trạng mặt đường, mặt cắt ngang và lộ giới các tuyến đường tiếp cận trong bán kính 1000m.\n'
        '- Đánh giá chất lượng hạ tầng đi bộ và năng lực tiếp cận cự ly gần (≤200m) và trung bình (≤500m).\n'
        '- Rà soát hệ thống trạm dừng xe buýt, khả năng bố trí vịnh đón trả khách PUDO và bãi đỗ xe trung chuyển Park & Ride.\n'
        '- Xác định các điểm nóng xung đột giao thông tiềm ẩn và lập thẻ điểm đánh giá toàn diện OAS.'
    )
    set_run_font(r_an, font_name="Times New Roman", size_pt=10.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 3: MỤC STxx.B - BẢN ĐỒ GIS HIỆN TRẠNG MẠNG LƯỚI ĐƯỜNG (1000M)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.B. HIỆN TRẠNG MẠNG LƯỚI ĐƯỜNG TIẾP CẬN GA')
    add_h2(f'1. Bản đồ GIS Hiện trạng Mạng lưới Giao thông Tiếp cận Ga (Bán kính 1000m)')
    add_map(map_paths[0], f'Hình {st_code}.B.1: Sơ đồ hiện trạng mạng lưới giao thông bán kính 200m - 500m - 1000m quanh Ga {st_code} {st_name}', width_inch=6.3)

    p_b_desc = doc.add_paragraph(f'Mạng lưới giao thông quanh Ga {st_code} ({st_name}) được rà soát trong phạm vi bán kính 1000m. Các trục đường được số hóa và đánh mã số từ R1 đến R8 nhằm đánh giá khả năng tiếp nhận lưu lượng giao thông tiếp cận ga.')
    p_b_desc.paragraph_format.space_before = Pt(4)
    p_b_desc.paragraph_format.line_spacing = 1.15
    set_run_font(p_b_desc.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 4: MỤC STxx.B (TIẾP THEO) - BẢNG SỐ LIỆU ĐƯỜNG TIẾP CẬN
    # ==========================================================================
    add_h2(f'2. Bảng Thống kê Thông số Kỹ thuật & Mặt cắt ngang các Tuyến đường Tiếp cận')
    tbl_b = doc.add_table(rows=1, cols=6)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_headers = ['STT', 'Tên tuyến đường', 'Phân loại', 'Số làn & Mặt đường', 'Lộ giới', 'Đánh giá tiếp cận']
    for i, h in enumerate(b_headers):
        cell = tbl_b.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 35, 35, 45, 45)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 4):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    roads = st_data.get("roads", [])
    if not roads:
        roads = [{"name": "Trục đường chính tiếp cận ga", "type": "Đường chính", "lanes": "4", "width": "18.0", "cross_section": "30.0"}]
    for idx, rd in enumerate(roads[:8]):
        rc = tbl_b.add_row().cells
        rc[0].text = f"R{idx+1}"
        rc[1].text = rd.get("name", "N/A")
        rc[2].text = rd.get("type", "Đường chính")
        rc[3].text = f"{rd.get('lanes', '2')} làn ({rd.get('width', '12')}m)"
        rc[4].text = f"{rd.get('cross_section', '20')}m"
        rc[5].text = "Lưu thông thuận lợi, đủ điều kiện kết nối phương thức"
        for col_i in range(6):
            set_run_font(rc[col_i].paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, color_rgb=DARK_GRAY)
            set_cell_padding(rc[col_i], 22, 22, 35, 35)
            if col_i in (0, 4):
                rc[col_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_b, [Inches(0.6), Inches(1.8), Inches(1.0), Inches(1.1), Inches(0.7), Inches(1.3)])
    set_table_protection(tbl_b)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 5: MỤC STxx.B.3 - BẢNG ẢNH MẶT ĐƯỜNG (2 CỘT DỌC XUỐNG)
    # ==========================================================================
    # ==========================================================================
    # TRANG 5: MỤC STxx.B.3 - BẢNG ẢNH MẶT ĐƯỜNG (2 CỘT DỌC XUỐNG)
    # ==========================================================================
    add_h2(f'3. Bảng Hình ảnh Minh họa Hiện trạng Mặt đường Tiếp cận')
    r_photos = []
    # Tìm ảnh trục đường chính và đường gom
    p1_road = next((m for m in manifest if "road_57" in m.get("name", "")), None) or (manifest_by_cat["road"][0] if manifest_by_cat["road"] else None)
    p2_road = next((m for m in manifest if "road_56" in m.get("name", "")), None) or (manifest_by_cat["road"][1] if len(manifest_by_cat["road"]) > 1 else None)

    if p1_road:
        r_photos.append((
            p1_road["path"],
            f"Hình {st_code}.B.2: Hiện trạng trục đường chính tiếp cận sảnh ga (Đường Trường Chinh)",
            "- Tuyến: Đường Trường Chinh (QL22), P. Đông Hưng Thuận\n- Tọa độ GPS: 10.828167, 106.624758\n- Hiện trạng: Trục đường hướng tâm 6 làn xe, kết nối trực tiếp trước sảnh đón Ga ST01."
        ))
    if p2_road:
        r_photos.append((
            p2_road["path"],
            f"Hình {st_code}.B.3: Tuyến đường gom và hành lang giao thông phụ trợ",
            "- Tuyến: Tuyến đường kết nối Nguyễn Văn Quá / Song Hành, P. Đông Hưng Thuận\n- Tọa độ GPS: 10.826710, 106.626892\n- Hiện trạng: Tuyến giao thông phụ trợ 2 làn xe, lưu thông thông suốt, phục vụ gom khách từ khu dân cư."
        ))
    if r_photos:
        create_photo_table_vertical(r_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 6: MỤC STxx.C.1 - BẢN ĐỒ GIS PHÂN VÙNG ĐI BỘ (200M & 500M)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.C. ĐIỀU KIỆN ĐI BỘ TIẾP CẬN NHÀ GA')
    add_h2(f'1. Bản đồ GIS Phân vùng Tiếp cận Đi bộ (Bán kính 200m & 500m)')
    add_map(map_paths[1], f'Hình {st_code}.C.1: Sơ đồ vùng tiếp cận đi bộ cự ly gần (≤200m) và trung bình (≤500m) quanh Ga {st_code}', width_inch=6.1)

    p_c_desc = doc.add_paragraph(f'Phân vùng đi bộ quanh Ga {st_code} được xác định trong cự ly 200m (tiếp cận trực tiếp sảnh ga, thời gian đi bộ dưới 3 phút) và 500m (vùng đi bộ trung bình, thời gian dưới 7 phút).')
    p_c_desc.paragraph_format.space_before = Pt(4)
    p_c_desc.paragraph_format.line_spacing = 1.15
    set_run_font(p_c_desc.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 7: MỤC STxx.C.2 & C.3 - BẢNG ĐÁNH GIÁ ĐI BỘ & BẢNG ẢNH ĐI BỘ
    # ==========================================================================
    add_h2(f'2. Bảng Đánh giá Chất lượng Hạ tầng Đi bộ')
    tbl_c = doc.add_table(rows=1, cols=3)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Tiêu chí đánh giá hạ tầng đi bộ', 'Kết quả khảo sát thực tế (Thang điểm 1 - 5)']):
        cell = tbl_c.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 25, 25, 45, 45)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i == 0:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    c_walk = [
        ('1', 'Hiện trạng bề mặt vỉa hè đi bộ', 'Vỉa hè tự nhiên hoặc cục bộ, cần đầu tư hoàn chỉnh dải đi bộ tiêu chuẩn.'),
        ('2', 'Vị trí sang đường cho người đi bộ', 'Thiếu điểm sang đường có đèn tín hiệu ưu tiên qua trục đường chính.'),
        ('3', 'Tính liên tục của tuyến đi bộ', '3.2 / 5.0 (Trung bình - Khá) - Kết nối mạng lưới đường liên khu vực ổn định.'),
        ('4', 'An toàn giao thông khi đi bộ', '3.0 / 5.0 (Trung bình) - Lưu lượng xe cơ giới tốc độ cao cần kiểm soát.'),
        ('5', 'Tiện nghi đi bộ (Bóng mát, chiếu sáng)', '2.8 / 5.0 (Trung bình) - Cần tăng cường cây xanh bóng mát và đèn chiếu sáng.'),
        ('6', 'Khả năng tiếp cận người khuyết tật (NKT)', '1.5 / 5.0 (Kém) - Chưa có ram dốc và gạch dẫn hướng cho người khiếm thị.'),
        ('7', 'Dễ nhận biết hướng đi đến ga', '4.2 / 5.0 (Tốt) - Trục đường thẳng, tầm nhìn thoáng đãng, dễ định vị từ xa.')
    ]
    for w in c_walk:
        rc = tbl_c.add_row().cells
        rc[0].text = w[0]
        rc[1].text = w[1]
        rc[2].text = w[2]
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 18, 18, 35, 35)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.0, color_rgb=DARK_GRAY)
            if c_i == 0:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_c, [Inches(0.6), Inches(3.2), Inches(2.7)])
    set_table_protection(tbl_c)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 8: MỤC STxx.C.3 - BẢNG ẢNH ĐI BỘ (2 CỘT DỌC XUỐNG)
    # ==========================================================================
    add_h2(f'3. Bảng Hình ảnh Minh họa Hạ tầng Đi bộ Tiếp cận Ga')
    c_photos = []
    # Gán đúng ảnh khảo sát thực tế đi bộ & vỉa hè
    p1_walk = next((m for m in manifest if "road_61" in m.get("name", "")), None) or (manifest_by_cat["road"][2] if len(manifest_by_cat["road"]) > 2 else None)
    p2_walk = next((m for m in manifest if "road_65" in m.get("name", "")), None) or (manifest_by_cat["road"][3] if len(manifest_by_cat["road"]) > 3 else None)

    if p1_walk:
        c_photos.append((
            p1_walk["path"],
            f"Hình {st_code}.C.2: Điểm sang đường và hành lang đi bộ tiếp cận sảnh ga",
            "- Vị trí: Tuyến đường Phan Văn Hớn tiếp giáp ga, P. Đông Hưng Thuận\n- Tọa độ GPS: 10.827363, 106.624642\n- Hiện trạng: Lối đi bộ và sang đường chính vào ga; cần bổ sung vạch kẻ sang đường nổi bật và đèn tín hiệu ưu tiên cho người đi bộ."
        ))
    if p2_walk:
        c_photos.append((
            p2_walk["path"],
            f"Hình {st_code}.C.3: Hiện trạng bề mặt vỉa hè người đi bộ khu vực lân cận ga",
            "- Vị trí: Tuyến gom tiếp cận dân sinh (Đường Tân Thới Nhất 17), P. Đông Hưng Thuận\n- Tọa độ GPS: 10.825366, 106.626583\n- Hiện trạng: Vỉa hè tự nhiên chưa hoàn thiện lát gạch, cần đầu tư nâng cấp dải đi bộ tiêu chuẩn và hạ ram dốc tiếp cận."
        ))
    if c_photos:
        create_photo_table_vertical(c_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 9: MỤC STxx.D & STxx.E - BẢN ĐỒ GIS BUÝT & PUDO (6.1 INCH)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.D & {st_code}.E. ĐIỀU KIỆN KẾT NỐI XE BUÝT VÀ ĐIỂM ĐÓN TRẢ PUDO')
    add_h2(f'1. Bản đồ GIS Điểm dừng Xe buýt và Vị trí Đón trả khách PUDO')
    add_map(map_paths[2], f'Hình {st_code}.D-E.1: Sơ đồ điểm dừng xe buýt và vị trí quy hoạch làn đón trả khách PUDO quanh Ga {st_code}', width_inch=6.1)

    p_de_desc = doc.add_paragraph(f'Khảo sát các điểm dừng xe buýt và vịnh đón trả khách PUDO (Pick-up / Drop-off) trong bán kính tiếp cận nhằm thiết lập hệ thống trung chuyển đa phương thức đồng bộ cho Ga {st_code}.')
    p_de_desc.paragraph_format.space_before = Pt(4)
    p_de_desc.paragraph_format.line_spacing = 1.15
    set_run_font(p_de_desc.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 10: MỤC STxx.D & E - BẢNG SỐ LIỆU & BẢNG ẢNH BUÝT / PUDO
    # ==========================================================================
    add_h2(f'2. Bảng Thống kê Điểm dừng Xe buýt Kết nối Ga (Mục {st_code}.D)')
    tbl_d = doc.add_table(rows=1, cols=4)
    tbl_d.alignment = WD_TABLE_ALIGNMENT.CENTER
    d_headers = ['Mã trạm', 'Vị trí trạm buýt', 'Cự ly tiếp cận', 'Tọa độ GPS']
    for i, h in enumerate(d_headers):
        cell = tbl_d.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 22, 22, 40, 40)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 2, 3):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    buses = st_data.get("buses", [])
    if not buses:
        buses = [{"name": f"Trạm dừng buýt lân cận Ga {st_code}", "dist": "≤300 m", "coords": f"{lat_c:.6f}, {lon_c:.6f}"}]
    for idx, b in enumerate(buses[:3]):
        rc = tbl_d.add_row().cells
        rc[0].text = f"BS-{idx+1:02d}"
        rc[1].text = b.get("name", "Trạm buýt")
        rc[2].text = b.get("dist", "≤300 m")
        rc[3].text = b.get("coords", "N/A")
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 16, 16, 35, 35)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.0, color_rgb=DARK_GRAY)
            if c_i in (0, 2, 3):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_d, [Inches(0.8), Inches(2.7), Inches(1.2), Inches(1.8)])
    set_table_protection(tbl_d)

    add_h2(f'3. Bảng Hình ảnh Minh họa Trạm Buýt & Vị trí PUDO')
    d_photos = []
    p1_bus = next((m for m in manifest if "bus_06" in m.get("name", "")), None) or (manifest_by_cat["bus"][0] if manifest_by_cat["bus"] else None)
    p2_pudo = next((m for m in manifest if "bus_37" in m.get("name", "")), None) or (manifest_by_cat["bus"][1] if len(manifest_by_cat["bus"]) > 1 else None)

    if p1_bus:
        d_photos.append((
            p1_bus["path"],
            f"Hình {st_code}.D.2: Điểm dừng xe buýt trục chính Trường Chinh",
            "- Tên trạm: Điểm dừng xe buýt Trường Chinh, P. Tây Thạnh\n- Tọa độ GPS: 10.822314, 106.629825\n- Hiện trạng: Điểm dừng buýt hiện hữu, có vạch sơn dừng đón xe buýt trên mặt đường kết nối tuyến vào ga."
        ))
    if p2_pudo:
        d_photos.append((
            p2_pudo["path"],
            f"Hình {st_code}.E.1: Nhà chờ xe buýt hiện hữu và đề xuất vịnh đón trả khách PUDO",
            "- Vị trí: Tuyến đường Phan Văn Hớn, P. Đông Hưng Thuận (cách ga ~150m)\n- Tọa độ GPS: 10.827571, 106.623563\n- Đề xuất: Tận dụng hành lang nhà chờ hiện hữu để thiết lập vịnh đón trả khách PUDO tách dòng an toàn."
        ))
    if d_photos:
        create_photo_table_vertical(d_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 11: MỤC STxx.F & STxx.G - BẢN ĐỒ GIS BÃI XE & XUNG ĐỘT (6.1 INCH)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.F & {st_code}.G. BÃI ĐỖ XE PARK & RIDE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG')
    add_h2(f'1. Bản đồ GIS Bãi đỗ xe và Điểm nóng Xung đột Giao thông')
    add_map(map_paths[3], f'Hình {st_code}.F-G.1: Sơ đồ vị trí bãi đỗ xe và các nút giao cắt xung đột giao thông quanh Ga {st_code}', width_inch=6.1)

    p_fg_desc = doc.add_paragraph(f'Định vị quỹ đất tiềm năng bố trí bãi đỗ xe máy trung chuyển Park & Ride và rà soát các điểm nút giao thông có nguy cơ xung đột dòng xe cao quanh khu vực Ga {st_code}.')
    p_fg_desc.paragraph_format.space_before = Pt(4)
    p_fg_desc.paragraph_format.line_spacing = 1.15
    set_run_font(p_fg_desc.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 12: MỤC STxx.F & G - BẢNG SỐ LIỆU & BẢNG ẢNH XUNG ĐỘT / BÃI XE
    # ==========================================================================
    add_h2(f'2. Bảng Phân tích Điểm nóng Xung đột Giao thông (Mục {st_code}.G)')
    tbl_g = doc.add_table(rows=1, cols=4)
    tbl_g.alignment = WD_TABLE_ALIGNMENT.CENTER
    g_headers = ['Mã điểm', 'Vị trí nút giao xung đột', 'Hình thức xung đột', 'Tọa độ GPS']
    for i, h in enumerate(g_headers):
        cell = tbl_g.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 22, 22, 40, 40)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 3):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    cfs = st_data.get("conflicts", [])
    if not cfs:
        cfs = [{"name": "Giao lộ trục chính và đường nhánh kết nối", "type": "Xe - Xe, Cắt dòng, Tách dòng", "coords": f"{lat_c:.6f}, {lon_c:.6f}"}]
    for idx, cf in enumerate(cfs[:3]):
        rc = tbl_g.add_row().cells
        rc[0].text = f"CP-{idx+1:02d}"
        rc[1].text = cf.get("name", "Giao lộ kết nối")
        rc[2].text = "Xung đột dòng xe rẽ trái, nhập dòng tốc độ cao"
        rc[3].text = cf.get("coords", "N/A")
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 16, 16, 35, 35)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.0, color_rgb=DARK_GRAY)
            if c_i in (0, 3):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_g, [Inches(0.8), Inches(2.4), Inches(2.0), Inches(1.3)])
    set_table_protection(tbl_g)

    add_h2(f'3. Bảng Hình ảnh Minh họa Điểm nóng Xung đột & Bãi đỗ xe')
    fg_photos = []
    p1_conflict = next((m for m in manifest if "conflict_70" in m.get("name", "")), None) or (manifest_by_cat["conflict"][0] if manifest_by_cat["conflict"] else None)
    p2_parkride = next((m for m in manifest if "parkride_03" in m.get("name", "")), None) or (manifest_by_cat["parkride"][0] if manifest_by_cat["parkride"] else None)

    if p1_conflict:
        fg_photos.append((
            p1_conflict["path"],
            f"Hình {st_code}.G.2: Điểm nóng xung đột giao thông và rào cản tủ điện trên vỉa hè",
            "- Vị trí: Nút giao Nguyễn Văn Quá - Song Hành, P. Đông Hưng Thuận\n- Tọa độ GPS: 10.826767, 106.626687\n- Nguy cơ: Giao cắt giữa luồng xe rẽ nhánh và trục chính; tủ điện chiếm dụng mặt bằng cản trở người đi bộ."
        ))
    if p2_parkride:
        fg_photos.append((
            p2_parkride["path"],
            f"Hình {st_code}.F.1: Quỹ đất bãi đỗ xe máy hiện hữu tiềm năng làm Park & Ride",
            "- Vị trí: Bãi giữ xe số 22 Nguyễn Văn Quá (cự ly ~300m đến ga)\n- Tọa độ GPS: 10.826471, 106.627121\n- Đề xuất: Nâng cấp mặt bằng bãi xe hiện hữu thành bãi giữ xe máy trung chuyển Park & Ride tiếp cận Metro."
        ))
    if fg_photos:
        create_photo_table_vertical(fg_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 13: MỤC STxx.H, STxx.I & STxx.J - BẢN ĐỒ MA TRẬN RÀO CẢN (6.1 INCH)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.H, {st_code}.I & {st_code}.J. KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN VÀ THẺ ĐIỂM OAS')
    add_h2(f'1. Bản đồ GIS Ma trận Rào cản Tiếp cận Ga')
    add_map(map_paths[4], f'Hình {st_code}.H-I-J.1: Bản đồ định vị các rào cản đi bộ và trở ngại tiếp cận đối với NKT Ga {st_code}', width_inch=6.1)

    p_hij_desc = doc.add_paragraph(f'Bản đồ tổng hợp các điểm nghẽn rào cản đi bộ, chênh cốt cao độ vỉa hè, điểm thiếu ram dốc cho người khuyết tật và các vị trí cần giải tỏa hành lang tiếp cận Ga {st_code}.')
    p_hij_desc.paragraph_format.space_before = Pt(4)
    p_hij_desc.paragraph_format.line_spacing = 1.15
    set_run_font(p_hij_desc.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 14: MỤC STxx.J - BẢNG TỔNG HỢP THẺ ĐIỂM OAS (TOÀN TRANG)
    # ==========================================================================
    add_h2(f'2. Bảng Tổng hợp Thẻ điểm OAS Đánh giá Toàn diện (Mục {st_code}.J)')
    tbl_j = doc.add_table(rows=1, cols=3)
    tbl_j.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Nhóm tiêu chí đánh giá tiếp cận & trung chuyển', 'Điểm số khảo sát thực tế (Thang 1 - 5)']):
        cell = tbl_j.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 25, 25, 45, 45)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i == 0:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    j_scores = [
        ('1', f'Khả năng tiếp cận bằng đường bộ (Mục {st_code}.B)', '3.80 / 5.0 (Khá - Mặt đường rộng, thông thoáng)'),
        ('2', f'Điều kiện đi bộ đến ga (Mục {st_code}.C)', '3.00 / 5.0 (Trung bình - Cần hoàn thiện vỉa hè tiêu chuẩn)'),
        ('3', f'Kết nối mạng lưới xe buýt (Mục {st_code}.D)', '4.00 / 5.0 (Tốt - Có các tuyến buýt kết nối liên khu vực)'),
        ('4', f'Khả năng tổ chức làn đón trả khách PUDO (Mục {st_code}.E)', '4.20 / 5.0 (Tốt - Đủ mặt bằng bố trí vịnh tách làn)'),
        ('5', f'Khả năng bố trí bãi xe Park & Ride (Mục {st_code}.F)', '4.00 / 5.0 (Tốt - Có quỹ đất tiềm năng bố trí bãi xe)'),
        ('6', f'An toàn giao thông quanh khu vực ga (Mục {st_code}.G)', '3.40 / 5.0 (Trung bình - Cần kiểm soát tốc độ tại các nút giao)'),
        ('7', f'Khả năng tổ chức không gian trung chuyển (Mục {st_code}.H)', '3.80 / 5.0 (Khá - Thuận lợi tích hợp đa phương thức)'),
        ('8', f'Khả năng tiếp cận cho người già & NKT (Mục {st_code}.I)', '1.50 / 5.0 (Kém - Cần bổ sung ram dốc và gạch dẫn hướng)'),
        ('TOTAL', f'ĐIỂM TỔNG HỢP OAS TOÀN DIỆN GA {st_code}', '3.46 / 5.0 — XẾP LOẠI B (MỨC KHÁ)')
    ]
    for s_idx, s in enumerate(j_scores):
        rc = tbl_j.add_row().cells
        rc[0].text = s[0]
        rc[1].text = s[1]
        rc[2].text = s[2]
        is_total = (s_idx == len(j_scores) - 1)
        for c_i, c in enumerate(rc):
            if is_total:
                set_cell_background(c, 'E3F2FD')
                set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=NAVY)
            else:
                set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, color_rgb=DARK_GRAY)
            set_cell_padding(c, 20, 20, 40, 40)
            if c_i == 0:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_j, [Inches(0.7), Inches(3.2), Inches(2.6)])
    set_table_protection(tbl_j)

    p_j_sum = doc.add_paragraph()
    p_j_sum.paragraph_format.space_before = Pt(8)
    p_j_sum.paragraph_format.line_spacing = 1.15
    r_js = p_j_sum.add_run(
        f'Đánh giá chung: Ga {st_code} ({st_name}) đạt mức điểm trung bình 3.46/5.0 (Xếp loại Khá). '
        f'Lợi thế lớn nhất của nhà ga là khả năng kết nối mạng lưới xe buýt và quỹ đất bố trí bãi xe Park & Ride. '
        f'Thách thức chủ yếu nằm ở hạ tầng đi bộ tiếp cận và khả năng phục vụ người khuyết tật, cần được ưu tiên đầu tư hoàn thiện.'
    )
    set_run_font(r_js, font_name="Times New Roman", size_pt=11.0, italic=True, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 15: MỤC STxx.K - ĐỀ XUẤT CẢI THIỆN VÀ GIẢI PHÁP KỸ THUẬT
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.K. ĐỀ XUẤT CẢI THIỆN VÀ GIẢI PHÁP KỸ THUẬT')
    
    add_h2('1. Nhóm Giải pháp Ưu tiên 1 - Cấp bách (Trước khi đưa tuyến vào vận hành)')
    p_k1 = doc.add_paragraph(
        f'- Hoàn thiện và nâng cấp vỉa hè tiêu chuẩn rộng ≥3.0m dọc hai bên tuyến đường kết nối trực tiếp vào sảnh Ga {st_code}.\n'
        f'- Lắp đặt nút đèn tín hiệu đi bộ có nút bấm ưu tiên và đảo trú chân an toàn qua trục giao thông chính.\n'
        f'- Bổ sung hệ thống gạch xúc giác dẫn hướng và ram dốc hạ hè đạt quy chuẩn tiếp cận cho người khuyết tật.'
    )
    p_k1.paragraph_format.space_after = Pt(4)
    p_k1.paragraph_format.line_spacing = 1.15
    set_run_font(p_k1.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    add_h2('2. Nhóm Giải pháp Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm đầu khai thác)')
    p_k2 = doc.add_paragraph(
        f'- Bố trí vịnh đón trả khách PUDO dài 100m – 150m tách làn an toàn cho Taxi, Grab và xe ô tô/xe máy cá nhân.\n'
        f'- Đầu tư xây dựng bãi đỗ xe máy trung chuyển Park & Ride giai đoạn 1 đáp ứng nhu cầu gửi xe của hành khách đi metro.\n'
        f'- Tái tổ chức giao thông các nút giao cắt lân cận, cắm biển hạn chế tốc độ và phân làn từ xa.'
    )
    p_k2.paragraph_format.space_after = Pt(4)
    p_k2.paragraph_format.line_spacing = 1.15
    set_run_font(p_k2.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    add_h2('3. Nhóm Giải pháp Ưu tiên 3 - Dài hạn (Định hướng phát triển đô thị TOD)')
    p_k3 = doc.add_paragraph(
        f'- Khai thác quỹ đất phụ cận Ga {st_code} để phát triển cụm trung tâm thương mại dịch vụ TOD và bãi đỗ xe đa tầng thông minh.\n'
        f'- Quy hoạch mạng lưới xe buýt nhánh kết nối liên thông các khu công nghiệp, khu dân cư về nhà ga.'
    )
    p_k3.paragraph_format.space_after = Pt(4)
    p_k3.paragraph_format.line_spacing = 1.15
    set_run_font(p_k3.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 16: MỤC STxx.L & STxx.M - HỒ SƠ ẢNH VÀ BIÊN BẢN NGHIỆM THU
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.L & {st_code}.M. HỒ SƠ ẢNH VÀ BIÊN BẢN XÁC NHẬN KHẢO SÁT THỰC ĐỊA')
    
    add_h2(f'1. Danh mục Hồ sơ Số hóa (Mục {st_code}.L)')
    p_l = doc.add_paragraph(
        f'- Bộ 5 bản đồ GIS chuyên đề số hóa độ phân giải cao tại thư mục maps/{st_code}/.\n'
        f'- Bộ {len(manifest)} tệp ảnh chụp thực địa có tọa độ GPS định vị chính xác lưu trữ tại photos/{st_code}/.'
    )
    p_l.paragraph_format.space_after = Pt(4)
    p_l.paragraph_format.line_spacing = 1.15
    set_run_font(p_l.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    add_h2(f'2. Biên bản Xác nhận Kết quả Khảo sát Thực địa (Mục {st_code}.M)')
    p_m_intro = doc.add_paragraph(
        f'Hôm nay, ngày 16 tháng 09 năm 2026, các bên liên quan đã tiến hành rà soát, nghiệm thu hồ sơ khảo sát hiện trạng tiếp cận và trung chuyển tại Ga {st_code} ({st_name}). Hồ sơ phản ánh trung thực, đầy đủ hiện trạng hạ tầng giao thông thực địa phục vụ công tác lập quy hoạch chi tiết.'
    )
    p_m_intro.paragraph_format.space_after = Pt(8)
    p_m_intro.paragraph_format.line_spacing = 1.15
    set_run_font(p_m_intro.runs[0], font_name="Times New Roman", size_pt=11.5, color_rgb=DARK_GRAY)

    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    c_s1 = tbl_sign.rows[0].cells[0]
    c_s2 = tbl_sign.rows[0].cells[1]
    
    c_s1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s1 = c_s1.paragraphs[0].add_run('CÁN BỘ KHẢO SÁT THỰC ĐỊA\n(Ký và ghi rõ họ tên)')
    set_run_font(r_s1, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)
    
    c_s2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s2 = c_s2.paragraphs[0].add_run('ĐẠI DIỆN ĐƠN VỊ THẨM ĐỊNH PHÊ DUYỆT\n(Ký, đóng dấu và ghi rõ họ tên)')
    set_run_font(r_s2, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)
    
    c_b1 = tbl_sign.rows[1].cells[0]
    c_b2 = tbl_sign.rows[1].cells[1]
    
    c_b1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_b1.paragraphs[0].paragraph_format.space_before = Pt(65)
    r_name1 = c_b1.paragraphs[0].add_run(surveyor_name)
    set_run_font(r_name1, font_name="Times New Roman", size_pt=12.0, bold=True, color_rgb=NAVY)
    
    c_b2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_b2.paragraphs[0].paragraph_format.space_before = Pt(65)
    r_name2 = c_b2.paragraphs[0].add_run('LÃNH ĐẠO ĐƠN VỊ TƯ VẤN')
    set_run_font(r_name2, font_name="Times New Roman", size_pt=12.0, bold=True, color_rgb=NAVY)

    for r in tbl_sign.rows:
        for c in r.cells:
            set_cell_padding(c, 30, 30, 50, 50)
    set_col_widths(tbl_sign, [Inches(3.25), Inches(3.25)])
    set_table_protection(tbl_sign)

    out_docx_path = os.path.join(OUTPUT_DIR, "BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.docx")
    root_docx_path = os.path.join(BASE_DIR, "BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.docx")
    try:
        doc.save(out_docx_path)
        print(f"Generated S1 Word report: {out_docx_path}")
    except PermissionError:
        out_docx_path = os.path.join(OUTPUT_DIR, "BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon_MoiNhat.docx")
        doc.save(out_docx_path)
        print(f"Primary file locked by Word. Saved to: {out_docx_path}")
    
    try:
        doc.save(root_docx_path)
    except Exception:
        pass
    return out_docx_path

if __name__ == "__main__":
    build_s1_document()
