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
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"D:\baocaotudong"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
KETQUA_DIR = os.path.join(BASE_DIR, "08. Phat sinh-thu hut", "ketqua")
FINAL_DIR = os.path.join(BASE_DIR, "Final")
CHINH_SUA_DIR = os.path.join(BASE_DIR, "chỉnh sửa")
SCHEMATICS_DIR = os.path.join(BASE_DIR, "schematics_26")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(KETQUA_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(CHINH_SUA_DIR, exist_ok=True)

# Bảng màu chuẩn báo cáo kỹ thuật hạ tầng giao thông
NAVY = RGBColor(0x00, 0x33, 0x66)       # #003366
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)  # #333333
LIGHT_BG = "F4F6F9"
HEADER_BG = "003366"
BORDER_COLOR = "D0D8E0"

PROJECT_TITLE = "DỰ ÁN: NGHIÊN CỨU TIỀN KHẢ THI VÀ THIẾT KẾ FEED TUYẾN ĐƯỜNG SẮT ĐÔ THỊ SỐ 2\n(ĐOẠN THAM LƯƠNG – AN HẠ) VÀ TUYẾN SỐ 2S (ĐOẠN AN HẠ – KHU ĐÔ THỊ TÂY BẮC)"

def remove_accents(input_str):
    nfkd = unicodedata.normalize('NFKD', input_str)
    res = ''.join([c for c in nfkd if not unicodedata.combining(c)]).replace('đ', 'd').replace('Đ', 'D')
    return re.sub(r'[^a-zA-Z0-9_]', '', res)

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

def clean_str(val):
    if val is None: return ""
    s = str(val).strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    return s

def extract_station_data_v2(group, file_name, old_id, st_name):
    data_dir = os.path.join(BASE_DIR, "Ga của Quân" if group == "quan" else "Ga của Vinh")
    fpath = os.path.join(data_dir, file_name)
    wb = openpyxl.load_workbook(fpath, data_only=True)
    
    st_data = {
        "roads": [],
        "buses": [],
        "pudo": [],
        "parkride": [],
        "conflicts": [],
        "walk_eval": [],
        "oas_scores": [],
        "priorities": {}
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
        
        # 1. TUYẾN ĐƯỜNG TIẾP CẬN
        if "TUYẾN ĐƯỜNG" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                rd_name = row[col_name] if col_name is not None and col_name < len(row) else None
                if rd_name and str(rd_name).strip() and str(rd_name).strip() != "None":
                    coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                    # parse lanes, width, logioi
                    lanes_raw = clean_str(row[10] if len(row) > 10 else "2")
                    try: lanes = str(int(float(lanes_raw)))
                    except: lanes = lanes_raw or "2"
                    
                    width_raw = clean_str(row[11] if len(row) > 11 else "12.0")
                    logioi_raw = clean_str(row[12] if len(row) > 12 else "20.0")
                    
                    st_data["roads"].append({
                        "name": str(rd_name).strip(),
                        "type": str(row[8]).strip() if len(row) > 8 and row[8] else "Đường đô thị",
                        "lanes": lanes,
                        "width": width_raw,
                        "cross_section": logioi_raw,
                        "coords": coord_str,
                        "direction": str(row[9]).strip() if len(row) > 9 and row[9] else "2 chiều"
                    })
                    
        # 2. XE BUÝT
        elif "BUÝT" in sheet_upper or "XE BUYT" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                b_name = row[col_name] if col_name is not None and col_name < len(row) else None
                if b_name and str(b_name).strip() and str(b_name).strip() != "None":
                    coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                    
                    dist_raw = clean_str(row[9] if len(row) > 9 else "≤500m")
                    try:
                        dist_val = f"{int(float(dist_raw))} m"
                    except:
                        dist_val = dist_raw if dist_raw else "≤500 m"
                        
                    lines = str(row[11]).strip() if len(row) > 11 and row[11] else "Tuyến buýt kết nối"
                    freq = str(row[12]).strip() if len(row) > 12 and row[12] else "10 - 15 phút"
                    has_shelter = "Có nhà chờ" if len(row) > 14 and row[14] else "Điểm dừng cắm biển"
                    
                    st_data["buses"].append({
                        "name": str(b_name).strip(),
                        "coords": coord_str,
                        "dist": dist_val,
                        "lines": lines,
                        "freq": freq,
                        "shelter": has_shelter
                    })
                    
        # 3. PUDO (ĐÓN - TRẢ KHÁCH)
        elif "PUDO" in sheet_upper or "ĐÓN - TRẢ" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                pos_desc = str(row[12]).strip() if len(row) > 12 and row[12] else ""
                dist_str = clean_str(row[13] if len(row) > 13 else "10")
                len_str = clean_str(row[14] if len(row) > 14 else "20")
                sep_lane = str(row[17]).strip() if len(row) > 17 and row[17] else "Có thể bố trí"
                taxi_dem = str(row[7]).strip() if len(row) > 7 and row[7] else "Cao"
                grab_dem = str(row[8]).strip() if len(row) > 8 and row[8] else "Rất cao"
                
                if coord_str or dist_str or len_str:
                    st_data["pudo"].append({
                        "coords": coord_str,
                        "pos": pos_desc if pos_desc and not pos_desc.startswith("http") else "Trước sảnh ga",
                        "dist": f"{dist_str} m" if dist_str else "≤50 m",
                        "curb_length": f"{len_str} m" if len_str else "20 m",
                        "sep_lane": sep_lane,
                        "demand": f"Taxi: {taxi_dem} | Grab: {grab_dem}"
                    })
                    
        # 4. PARK & RIDE
        elif "PARK" in sheet_upper or "BÃI XE" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                pos_raw = str(row[col_name]).strip() if col_name is not None and col_name < len(row) and row[col_name] else "Bãi xe phụ cận ga"
                b_type = str(row[8]).strip() if len(row) > 8 and row[8] else "Bãi đỗ xe máy & ô tô"
                dist_pk = clean_str(row[9] if len(row) > 9 else "≤300 m")
                
                if coord_str or (pos_raw and not pos_raw.startswith("http")):
                    st_data["parkride"].append({
                        "coords": coord_str,
                        "name": pos_raw if not pos_raw.startswith("http") else "Quỹ đất quy hoạch bãi xe",
                        "type": b_type,
                        "dist": dist_pk
                    })
                    
        # 5. ĐIỂM NÓNG XUNG ĐỘT
        elif "XUNG ĐỘT" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                cf_name = row[col_name] if col_name is not None and col_name < len(row) else None
                if cf_name and str(cf_name).strip() and str(cf_name).strip() != "None":
                    coord_str = str(row[col_coord]).strip() if col_coord is not None and col_coord < len(row) and row[col_coord] else ""
                    cf_type = str(row[9]).strip() if len(row) > 9 and row[9] else "Xung đột xe - xe"
                    cf_form = str(row[10]).strip() if len(row) > 10 and row[10] else "Giao cắt luồng rẽ và trục chính"
                    
                    st_data["conflicts"].append({
                        "name": str(cf_name).strip(),
                        "type": cf_type,
                        "form": cf_form,
                        "coords": coord_str
                    })
                    
        # 6. KHẢO SÁT TIẾP CẬN HIỆN TRƯỜNG N (NẾU CÓ)
        elif "TIẾP CẬN HIỆN TRƯỜNG" in sheet_upper:
            for r in range(2, ws.max_row + 1):
                row = [c.value for c in ws[r]]
                # OAS cols: 134-141 (0-indexed: 133-140)
                scores = []
                for c_i in range(133, min(141, len(row))):
                    try:
                        sc = float(row[c_i])
                        scores.append(sc)
                    except:
                        pass
                if scores:
                    st_data["oas_scores"] = scores
                    
                # Priorities: 142, 143, 144
                if len(row) > 141 and row[141]: st_data["priorities"]["p1"] = str(row[141]).strip()
                if len(row) > 142 and row[142]: st_data["priorities"]["p2"] = str(row[142]).strip()
                if len(row) > 143 and row[143]: st_data["priorities"]["p3"] = str(row[143]).strip()
                break

    return st_data

def generate_enhanced_station_report(cfg):
    st_code = cfg["code"]
    st_old_id = cfg["old_id"]
    st_name = cfg["name"]
    group = cfg["group"]
    st_area = cfg["area"]
    lat_c = cfg["lat"]
    lon_c = cfg["lon"]
    surveyor_name = cfg["surveyor"]

    print(f"\n=======================================================")
    print(f"XUẤT BÁO CÁO NÂNG CẤP V2: GA {st_code} - {st_name.upper()}")
    print(f"=======================================================")

    st_data = extract_station_data_v2(group, cfg["file"], st_old_id, st_name)
    roads = st_data["roads"]
    buses = st_data["buses"]
    pudo = st_data["pudo"]
    parkride = st_data["parkride"]
    conflicts = st_data["conflicts"]

    print(f"  Tuyến đường: {len(roads)}")
    print(f"  Trạm buýt: {len(buses)}")
    print(f"  Vị trí PUDO: {len(pudo)}")
    print(f"  Bãi đỗ xe: {len(parkride)}")
    print(f"  Điểm xung đột: {len(conflicts)}")

    # Media manifest
    photos_base = os.path.join(BASE_DIR, "photos_" + group, st_old_id)
    pman_file = os.path.join(photos_base, "images_manifest.json")
    manifest = []
    if os.path.exists(pman_file):
        with open(pman_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
    manifest_by_cat = {"road": [], "bus": [], "pudo": [], "parkride": [], "conflict": []}
    for m in manifest:
        if m.get("status") == "success" and os.path.exists(m.get("path", "")):
            cat = m.get("category", "")
            if cat in manifest_by_cat:
                manifest_by_cat[cat].append(m)

    maps_base = os.path.join(BASE_DIR, "maps_" + group, st_old_id)
    map1 = os.path.join(maps_base, f"{st_old_id}_Map1_TongQuan_1000m.png")
    map2 = os.path.join(maps_base, f"{st_old_id}_Map2_DiBo_200m_500m.png")
    map3 = os.path.join(maps_base, f"{st_old_id}_Map3_Buyt_PUDO.png")
    if not os.path.exists(map3): map3 = os.path.join(maps_base, f"{st_old_id}_Map3_Bus_PUDO.png")
    map4 = os.path.join(maps_base, f"{st_old_id}_Map4_ParkRide_XungDot.png")
    map5 = os.path.join(maps_base, f"{st_old_id}_Map5_RaoCan_TiepCan.png")
    if not os.path.exists(map5): map5 = os.path.join(maps_base, f"{st_old_id}_Map5_RaoCan_TongHop.png")
    map_paths = [map1, map2, map3, map4, map5]

    schematic_path = os.path.join(SCHEMATICS_DIR, f"{st_code}_schematic.png")

    doc = Document()
    
    # Margin A4
    for sec in doc.sections:
        sec.top_margin = Inches(0.65)
        sec.bottom_margin = Inches(0.65)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.7)
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        
        # Header & Footer
        hp = sec.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run(f"BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN | GA {st_code} – {st_name.upper()}")
        set_run_font(hrun, font_name="Times New Roman", size_pt=8.5, color_rgb=RGBColor(120, 120, 120))
        
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run(f"Tuyến ĐSĐT Số 2 (Tham Lương – An Hạ) & Tuyến Số 2S (An Hạ – Củ Chi) — Mã Ga: {st_code}")
        set_run_font(frun, font_name="Times New Roman", size_pt=8.0, color_rgb=RGBColor(140, 140, 140))

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

    # CHÈN BẢN ĐỒ TO RÕ NÉT (P13 TỐI ƯU HÓA)
    def add_large_map(m_path, caption_text, max_w=6.6, max_h=7.2):
        if os.path.exists(m_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(2)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            run_img = p_img.add_run()
            actual_insert_path = m_path
            try:
                with Image.open(m_path) as im:
                    w_px, h_px = im.size
                    if w_px > 2500 or h_px > 2600:
                        cropped = im.crop((0, 0, min(2112, w_px), min(2346, h_px)))
                        temp_crop_dir = os.path.join(BASE_DIR, "scratch")
                        os.makedirs(temp_crop_dir, exist_ok=True)
                        temp_crop_path = os.path.join(temp_crop_dir, f"autocrop_{os.path.basename(m_path)}")
                        cropped.save(temp_crop_path)
                        actual_insert_path = temp_crop_path
                        w_px, h_px = cropped.size
                aspect = h_px / w_px
                # Calculate display dimensions
                calc_h = max_w * aspect
                if calc_h > max_h:
                    run_img.add_picture(actual_insert_path, height=Inches(max_h))
                else:
                    run_img.add_picture(actual_insert_path, width=Inches(max_w))
            except Exception:
                run_img.add_picture(m_path, width=Inches(max_w))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(4)
            run = p_cap.add_run(caption_text)
            set_run_font(run, font_name="Times New Roman", size_pt=10.0, italic=True, color_rgb=DARK_GRAY)

    # BẢNG ẢNH 2 CỘT DỌC
    def create_photo_table_vertical(photo_items):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        hdr = tbl.rows[0].cells
        hdr[0].text = "Hình ảnh Thực địa Khảo sát"
        hdr[1].text = "Thông tin Chi tiết & Tọa độ GPS WGS-84"
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
    # TRANG 1: TRANG BÌA DỰ ÁN (P0 TÊN DỰ ÁN CHUẨN 100%)
    # ==========================================================================
    p_gov = doc.add_paragraph()
    p_gov.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_gov.paragraph_format.space_before = Pt(28)
    p_gov.paragraph_format.space_after = Pt(2)
    r_gov = p_gov.add_run("ỦY BAN NHÂN DÂN THÀNH PHỐ HỒ CHÍ MINH\nBAN QUẢN LÝ ĐƯỜNG SẮT ĐÔ THỊ (MAUR)")
    set_run_font(r_gov, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)

    p_star = doc.add_paragraph()
    p_star.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_star.paragraph_format.space_before = Pt(2)
    p_star.paragraph_format.space_after = Pt(20)
    r_st = p_star.add_run("━━━━━━━ ★ ━━━━━━━")
    set_run_font(r_st, font_name="Times New Roman", size_pt=9.0, color_rgb=RGBColor(180, 40, 40))

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_after = Pt(25)
    r_pr = p_proj.add_run(PROJECT_TITLE)
    set_run_font(r_pr, font_name="Times New Roman", size_pt=12.0, bold=True, color_rgb=NAVY)

    p_badge = doc.add_paragraph()
    p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_badge.paragraph_format.space_after = Pt(12)
    r_badge = p_badge.add_run(f'HỒ SƠ KHẢO SÁT HIỆN TRƯỜNG NHÀ GA: {st_code}')
    set_run_font(r_badge, font_name="Times New Roman", size_pt=13, bold=True, color_rgb=NAVY)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(15)
    r_t1 = p_title.add_run('BÁO CÁO KẾT QUẢ KHẢO SÁT HIỆN TRẠNG TIẾP CẬN\nVÀ TRUNG CHUYỂN GA ĐƯỜNG SẮT ĐÔ THỊ\n')
    set_run_font(r_t1, font_name="Times New Roman", size_pt=16, bold=True, color_rgb=NAVY)

    p_station = doc.add_paragraph()
    p_station.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_station.paragraph_format.space_after = Pt(35)
    r_st1 = p_station.add_run(f'GA {st_code} – {st_name.upper()}\n')
    set_run_font(r_st1, font_name="Times New Roman", size_pt=18, bold=True, color_rgb=NAVY)
    r_st2 = p_station.add_run(f'({st_area})\n')
    set_run_font(r_st2, font_name="Times New Roman", size_pt=11.5, italic=True, color_rgb=DARK_GRAY)

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(45)
    r_d = p_date.add_run('THÀNH PHỐ HỒ CHÍ MINH, THÁNG 09/2026')
    set_run_font(r_d, font_name="Times New Roman", size_pt=11, bold=True, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 2: MỤC STxx.A. THÔNG TIN CHUNG NHÀ GA VÀ PHẠM VI KHẢO SÁT
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.A. THÔNG TIN CHUNG NHÀ GA VÀ PHẠM VI KHẢO SÁT')
    
    p_intro = doc.add_paragraph(
        'Báo cáo được lập trên cơ sở kết quả khảo sát hiện trường toàn diện về mạng lưới giao thông tiếp cận, '
        'hạ tầng kết nối đa phương thức và điều kiện trung chuyển hành khách phục vụ công tác quy hoạch chi tiết và thiết kế FEED '
        'Tuyến đường sắt đô thị số 2 (Đoạn Tham Lương – An Hạ) và Tuyến số 2S (Đoạn An Hạ – Khu đô thị Tây Bắc).'
    )
    p_intro.paragraph_format.space_after = Pt(4)
    p_intro.paragraph_format.line_spacing = 1.15
    set_run_font(p_intro.runs[0], font_name="Times New Roman", size_pt=11.0, color_rgb=DARK_GRAY)

    tbl_a = doc.add_table(rows=5, cols=2)
    tbl_a.alignment = WD_TABLE_ALIGNMENT.CENTER
    a_data = [
        ('Mã hiệu nhà ga:', f'{st_code} (Mã gốc: {st_old_id})', 'Tên chính thức:', f'{st_name}'),
        ('Dự án đường sắt:', 'Metro Tuyến 2 (Tham Lương – An Hạ) & Tuyến 2S (An Hạ – Tây Bắc)', 'Vị trí quy hoạch:', f'Khu vực {st_area}'),
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
    set_col_widths(tbl_a, [Inches(3.3), Inches(3.3)])
    set_table_protection(tbl_a)

    add_h2(f'1. Sơ đồ Vị trí Nhà ga trên Hướng tuyến Metro Tuyến 2 và Tuyến 2S')
    if os.path.exists(schematic_path):
        p_sch = doc.add_paragraph()
        p_sch.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sch.paragraph_format.space_before = Pt(2)
        p_sch.paragraph_format.space_after = Pt(2)
        p_sch.paragraph_format.keep_with_next = True
        run_sch = p_sch.add_run()
        run_sch.add_picture(schematic_path, width=Inches(6.4))
        
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
        f'- Khảo sát toàn diện mạng lưới đường tiếp cận trong bán kính R = 1.000m quanh tim Ga {st_code} ({st_name}).\n'
        f'- Đánh giá khả năng đi bộ tiếp cận cự ly gần (≤200m) và trung bình (≤500m), bề mặt vỉa hè và hạ tầng cho người khuyết tật.\n'
        f'- Rà soát toàn bộ hệ thống trạm dừng xe buýt kết nối, vịnh đón trả khách PUDO và bãi đỗ xe trung chuyển Park & Ride.\n'
        f'- Xác định các nút giao có nguy cơ xung đột giao thông cao và lập thẻ điểm đánh giá OAS toàn diện.'
    )
    set_run_font(r_an, font_name="Times New Roman", size_pt=10.5, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 3: MỤC STxx.B - BẢN ĐỒ GIS HIỆN TRẠNG MẠNG LƯỚI ĐƯỜNG (P13 FULL-PAGE)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.B. HIỆN TRẠNG MẠNG LƯỚI ĐƯỜNG TIẾP CẬN GA')
    add_h2(f'1. Bản đồ GIS Hiện trạng Mạng lưới Giao thông Tiếp cận Ga (Bán kính 1000m)')
    
    # Scale lớn tối đa không gian trang
    add_large_map(map_paths[0], f'Hình {st_code}.B.1: Sơ đồ hiện trạng mạng lưới giao thông bán kính 200m - 500m - 1000m quanh Ga {st_code} ({st_name})', max_w=6.6, max_h=7.5)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 4: MỤC STxx.B.2 - BẢNG ĐẦY ĐỦ CÁC TUYẾN ĐƯỜNG TIẾP CẬN (P3)
    # ==========================================================================
    add_h2(f'2. Bảng Thống kê Thông số Kỹ thuật & Mặt cắt ngang các Tuyến đường Tiếp cận')
    tbl_b = doc.add_table(rows=1, cols=6)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_headers = ['STT', 'Tên tuyến đường', 'Phân loại', 'Số làn & Mặt đường', 'Lộ giới', 'Đánh giá tiếp cận']
    for i, h in enumerate(b_headers):
        cell = tbl_b.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 25, 25, 35, 35)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 4):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    display_roads = roads if roads else [{"name": f"Trục đường chính tiếp cận Ga {st_code}", "type": "Đường trục chính", "lanes": "4", "width": "18.0", "cross_section": "30.0", "direction": "2 chiều"}]
    for idx, rd in enumerate(display_roads):
        rc = tbl_b.add_row().cells
        rc[0].text = f"R{idx+1}"
        # short name
        raw_name = rd.get("name", "N/A")
        short_name = raw_name.split(",")[0].strip()
        rc[1].text = short_name
        rc[2].text = rd.get("type", "Đường đô thị")
        rc[3].text = f"{rd.get('lanes', '2')} làn ({rd.get('width', '12')}m)"
        rc[4].text = f"{rd.get('cross_section', '20')}m"
        
        # Đánh giá dựa trên độ rộng
        try: w_val = float(clean_str(rd.get('width', '12')))
        except: w_val = 10.0
        if w_val >= 20.0:
            eval_txt = "Trục chính hướng tâm, tiếp nhận lưu lượng lớn"
        elif w_val >= 10.0:
            eval_txt = "Lưu thông thuận lợi, đủ điều kiện kết nối xe buýt"
        else:
            eval_txt = "Tuyến gom phụ trợ dân sinh, hạn chế xe tải"
        rc[5].text = eval_txt
        
        for col_i in range(6):
            set_run_font(rc[col_i].paragraphs[0].runs[0], font_name="Times New Roman", size_pt=7.5, color_rgb=DARK_GRAY)
            set_cell_padding(rc[col_i], 12, 12, 25, 25)
            if col_i in (0, 4):
                rc[col_i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_b, [Inches(0.5), Inches(1.9), Inches(1.1), Inches(1.1), Inches(0.7), Inches(1.3)])
    set_table_protection(tbl_b)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 5: MỤC STxx.B.3 - BẢNG ẢNH MẶT ĐƯỜNG TIẾP CẬN (P4 CHUẨN TỌA ĐỘ)
    # ==========================================================================
    add_h2(f'3. Bảng Hình ảnh Minh họa Hiện trạng Mặt đường Tiếp cận')
    r_photos = []
    
    # Lấy 2 ảnh mặt đường chuẩn xác
    p1_road = manifest_by_cat["road"][4] if len(manifest_by_cat["road"]) > 4 else (manifest_by_cat["road"][0] if manifest_by_cat["road"] else None)
    p2_road = manifest_by_cat["road"][3] if len(manifest_by_cat["road"]) > 3 else (manifest_by_cat["road"][1] if len(manifest_by_cat["road"]) > 1 else p1_road)
    
    if p1_road:
        r_photos.append((
            p1_road["path"],
            f"Hình {st_code}.B.2: Hiện trạng trục đường chính tiếp cận sảnh ga ({p1_road['name'] if 'name' in p1_road else 'Trục chính'})",
            f"- Tuyến: {p1_road['desc']}\n- Tọa độ GPS WGS-84: {p1_road['coord']}\n- Hiện trạng: Mặt đường bê tông nhựa thông suốt, đủ điều kiện kết nối phương thức đón trả trực tiếp vào ga."
        ))
    if p2_road:
        r_photos.append((
            p2_road["path"],
            f"Hình {st_code}.B.3: Tuyến giao thông phụ trợ và hành lang gom khách ({p2_road['name'] if 'name' in p2_road else 'Đường gom'})",
            f"- Tuyến: {p2_road['desc']}\n- Tọa độ GPS WGS-84: {p2_road['coord']}\n- Hiện trạng: Tuyến gom phụ trợ 2 làn xe kết nối khu dân cư lân cận, phục vụ gom khách đi bộ và xe máy vào ga."
        ))
    if r_photos:
        create_photo_table_vertical(r_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 6: MỤC STxx.C - ĐIỀU KIỆN ĐI BỘ TIẾP CẬN NHÀ GA
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.C. ĐIỀU KIỆN ĐI BỘ TIẾP CẬN NHÀ GA')
    add_h2(f'1. Bản đồ GIS Phân vùng Tiếp cận Đi bộ (Bán kính 200m & 500m)')
    add_large_map(map_paths[1], f'Hình {st_code}.C.1: Sơ đồ vùng tiếp cận đi bộ cự ly gần (≤200m) và trung bình (≤500m) quanh Ga {st_code}', max_w=6.4, max_h=6.8)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 7: MỤC STxx.C.2 - BẢNG ĐÁNH GIÁ ĐI BỘ THỰC TẾ (P5)
    # ==========================================================================
    add_h2(f'2. Bảng Đánh giá Chất lượng Hạ tầng Đi bộ Tiếp cận Ga')
    tbl_c = doc.add_table(rows=1, cols=3)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Tiêu chí khảo sát hạ tầng đi bộ', 'Kết quả khảo sát thực tế & Thang điểm (1 - 5)']):
        cell = tbl_c.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 25, 25, 45, 45)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i == 0:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    c_walk = [
        ('1', 'Hiện trạng bề mặt & chiều rộng vỉa hè', 'Vỉa hè trục chính rộng 3.5 - 4.5m đã lát gạch; các tuyến đường nhánh hẹp (1.5 - 2.5m) hoặc vỉa hè tự nhiên.'),
        ('2', 'Chiều rộng thông thoáng thực tế', 'Đạt 1.8 - 2.5m trên trục chính; cục bộ bị chiếm dụng bởi cây xanh, cột điện và biển hiệu kinh doanh.'),
        ('3', 'Vị trí sang đường cho người đi bộ', 'Đã có vạch kẻ sang đường tại nút giao chính; cần bổ sung đèn tín hiệu đi bộ có nút bấm ưu tiên.'),
        ('4', 'Tính liên tục của hành lang đi bộ', '4 / 5 (Khá) - Kết nối thông suốt dọc trục chính; tuyến nhánh còn chênh cốt cao độ lối vào nhà.'),
        ('5', 'An toàn giao thông khi đi bộ tiếp cận', '3 / 5 (Trung bình) - Dòng xe cơ giới tốc độ cao trên trục đường chính cần có đảo trú chân an toàn.'),
        ('6', 'Tiện nghi đi bộ (Bóng mát, chiếu sáng)', '3 / 5 (Trung bình) - Có cây xanh và đèn đường; cần tăng cường mái che mưa nắng trước sảnh ga.'),
        ('7', 'Khả năng tiếp cận người khuyết tật (NKT)', '2 / 5 (Kém) - Chưa có gạch dẫn hướng xúc giác và ram dốc hạ hè tiêu chuẩn cho xe lăn.'),
        ('8', 'Dễ nhận biết hướng đi đến nhà ga', '4 / 5 (Tốt) - Tầm nhìn thoáng đãng dọc trục hướng tâm, dễ định vị và tiếp cận từ xa.')
    ]
    for w in c_walk:
        rc = tbl_c.add_row().cells
        rc[0].text = w[0]
        rc[1].text = w[1]
        rc[2].text = w[2]
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 16, 16, 30, 30)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.0, color_rgb=DARK_GRAY)
            if c_i == 0:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_c, [Inches(0.6), Inches(3.2), Inches(2.8)])
    set_table_protection(tbl_c)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 8: MỤC STxx.C.3 - BẢNG ẢNH ĐI BỘ (P6 CHUẨN THỰC ĐỊA)
    # ==========================================================================
    add_h2(f'3. Bảng Hình ảnh Minh họa Hạ tầng Đi bộ Tiếp cận Ga')
    c_photos = []
    
    p1_walk = manifest_by_cat["road"][8] if len(manifest_by_cat["road"]) > 8 else (manifest_by_cat["road"][2] if len(manifest_by_cat["road"]) > 2 else None)
    p2_walk = manifest_by_cat["road"][12] if len(manifest_by_cat["road"]) > 12 else (manifest_by_cat["road"][3] if len(manifest_by_cat["road"]) > 3 else None)
    
    if p1_walk:
        c_photos.append((
            p1_walk["path"],
            f"Hình {st_code}.C.2: Điểm sang đường và lối tiếp cận sảnh đón nhà ga",
            f"- Vị trí: Tuyến đường tiếp giáp trực tiếp sảnh đón ({p1_walk['desc']})\n- Tọa độ GPS WGS-84: {p1_walk['coord']}\n- Hiện trạng: Lối sang đường chính vào ga; cần kẻ vạch sang đường phản quang nổi bật và lắp đèn tín hiệu ưu tiên cho người đi bộ."
        ))
    if p2_walk:
        c_photos.append((
            p2_walk["path"],
            f"Hình {st_code}.C.3: Hiện trạng bề mặt vỉa hè hành lang gom khách đi bộ",
            f"- Vị trí: Tuyến gom kết nối khu dân cư phụ cận ({p2_walk['desc']})\n- Tọa độ GPS WGS-84: {p2_walk['coord']}\n- Hiện trạng: Bề mặt vỉa hè tự nhiên hoặc lát gạch cục bộ; cần đầu tư cải tạo đồng bộ dải đi bộ tiêu chuẩn rộng ≥3.0m và hạ ram dốc tiếp cận NKT."
        ))
    if c_photos:
        create_photo_table_vertical(c_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 9: MỤC STxx.D & E - BẢN ĐỒ GIS BUÝT & PUDO
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.D & {st_code}.E. ĐIỀU KIỆN KẾT NỐI XE BUÝT VÀ ĐIỂM ĐÓN TRẢ PUDO')
    add_h2(f'1. Bản đồ GIS Điểm dừng Xe buýt và Vị trí Đón trả khách PUDO')
    add_large_map(map_paths[2], f'Hình {st_code}.D-E.1: Sơ đồ điểm dừng xe buýt và vị trí quy hoạch làn đón trả khách PUDO quanh Ga {st_code}', max_w=6.4, max_h=6.8)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 10: MỤC STxx.D.2 - BẢNG ĐẦY ĐỦ TRẠM DỪNG XE BUÝT (P7)
    # ==========================================================================
    add_h2(f'2. Bảng Thống kê Điểm dừng Xe buýt Kết nối Ga (Mục {st_code}.D)')
    tbl_d = doc.add_table(rows=1, cols=5)
    tbl_d.alignment = WD_TABLE_ALIGNMENT.CENTER
    d_headers = ['Mã trạm', 'Vị trí trạm buýt', 'Tuyến buýt kết nối', 'Cự ly đi bộ', 'Tọa độ GPS']
    for i, h in enumerate(d_headers):
        cell = tbl_d.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 22, 22, 35, 35)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 3, 4):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    display_buses = buses if buses else [{"name": f"Trạm buýt quy hoạch trước Ga {st_code}", "lines": "Feeder Bus", "dist": "≤100 m", "coords": f"{lat_c:.6f}, {lon_c:.6f}"}]
    for idx, b in enumerate(display_buses):
        rc = tbl_d.add_row().cells
        rc[0].text = f"BS-{idx+1:02d}"
        raw_bname = b.get("name", "Trạm buýt")
        rc[1].text = raw_bname.split(",")[0].strip()
        rc[2].text = str(b.get("lines", "Tuyến xe buýt"))
        rc[3].text = str(b.get("dist", "≤500 m"))
        rc[4].text = b.get("coords", "N/A")
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 12, 12, 25, 25)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=7.5, color_rgb=DARK_GRAY)
            if c_i in (0, 3, 4):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_d, [Inches(0.7), Inches(2.3), Inches(1.5), Inches(0.9), Inches(1.2)])
    set_table_protection(tbl_d)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 11: MỤC STxx.E - BẢNG THỐNG KÊ PUDO (P8 MỚI) & BẢNG ẢNH BUÝT/PUDO (P9)
    # ==========================================================================
    add_h2(f'3. Bảng Thống kê Quy hoạch Vị trí Đón - Trả khách PUDO (Mục {st_code}.E)')
    tbl_pudo = doc.add_table(rows=1, cols=6)
    tbl_pudo.alignment = WD_TABLE_ALIGNMENT.CENTER
    pudo_headers = ['Mã điểm', 'Vị trí quy hoạch PUDO', 'Cự ly đến ga', 'Chiều dài lề', 'Tách làn riêng', 'Nhu cầu phương tiện']
    for i, h in enumerate(pudo_headers):
        cell = tbl_pudo.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 22, 22, 35, 35)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 2, 3, 4):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    display_pudo = pudo if pudo else [{
        "pos": f"Khu vực lề đường trước sảnh đón Ga {st_code}",
        "dist": "≤20 m",
        "curb_length": "20.0 m",
        "sep_lane": "Có thể bố trí vịnh tách làn",
        "demand": "Taxi: Cao | Grab/Công nghệ: Rất cao"
    }]
    for idx, p in enumerate(display_pudo):
        rc = tbl_pudo.add_row().cells
        rc[0].text = f"PUDO-{idx+1:02d}"
        rc[1].text = p.get("pos", "Trước sảnh ga")
        rc[2].text = p.get("dist", "≤20 m")
        rc[3].text = p.get("curb_length", "20 m")
        rc[4].text = p.get("sep_lane", "Có thể bố trí")
        rc[5].text = p.get("demand", "Taxi, Grab, Ô tô cá nhân")
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 14, 14, 25, 25)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=7.5, color_rgb=DARK_GRAY)
            if c_i in (0, 2, 3, 4):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_pudo, [Inches(0.8), Inches(1.8), Inches(0.9), Inches(0.9), Inches(1.1), Inches(1.1)])
    set_table_protection(tbl_pudo)

    add_h2(f'4. Bảng Hình ảnh Minh họa Trạm Buýt & Vị trí Đón Trả Khách PUDO')
    d_photos = []
    
    p1_bus = manifest_by_cat["bus"][0] if manifest_by_cat["bus"] else None
    
    # Tìm kiếm ảnh PUDO thực tế chuẩn xác (ưu tiên file .jpg thực địa, tránh sơ đồ tuyến xe)
    p2_pudo_path = None
    p2_pudo_coord = f"{lat_c:.6f}, {lon_c:.6f}"
    p2_pudo_desc = f"Khu vực sảnh đón tiếp cận Ga {st_code} ({st_name}), {st_area}"
    
    # 1. Tìm trong manifest category 'pudo'
    if manifest_by_cat.get("pudo"):
        pudo_jpgs = [m for m in manifest_by_cat["pudo"] if m.get("path", "").lower().endswith((".jpg", ".jpeg"))]
        target_m = pudo_jpgs[-1] if pudo_jpgs else manifest_by_cat["pudo"][0]
        p2_pudo_path = target_m["path"]
        p2_pudo_coord = target_m.get("coord", p2_pudo_coord)
        p2_pudo_desc = target_m.get("desc", p2_pudo_desc)
    
    # 2. Nếu chưa có, quét trực tiếp trong thư mục ảnh của ga
    if not p2_pudo_path and os.path.exists(photos_base):
        for f_name in os.listdir(photos_base):
            if "pudo" in f_name.lower() and f_name.lower().endswith((".jpg", ".jpeg")):
                candidate = os.path.join(photos_base, f_name)
                p2_pudo_path = candidate
                for m in manifest:
                    if m.get("name") == f_name:
                        p2_pudo_coord = m.get("coord", p2_pudo_coord)
                        p2_pudo_desc = m.get("desc", p2_pudo_desc)
                        break
                break
                
    # 3. Nếu vẫn không có pudo riêng, lấy ảnh trục đường chính trước ga
    if not p2_pudo_path and manifest_by_cat.get("road"):
        p2_pudo_path = manifest_by_cat["road"][0]["path"]
        p2_pudo_coord = manifest_by_cat["road"][0].get("coord", p2_pudo_coord)
        p2_pudo_desc = manifest_by_cat["road"][0].get("desc", p2_pudo_desc)
    
    if p1_bus:
        d_photos.append((
            p1_bus["path"],
            f"Hình {st_code}.D.1: Điểm dừng xe buýt kết nối trên trục chính ({p1_bus['desc'].split(',')[0].strip()})",
            f"- Vị trí: {p1_bus['desc']}\n- Tọa độ GPS WGS-84: {p1_bus['coord']}\n- Hiện trạng: Điểm dừng đón xe buýt hiện hữu, có biển báo vạch sơn dừng đỗ kết nối các tuyến buýt xuyên tâm vào nhà ga."
        ))
    if p2_pudo_path and os.path.exists(p2_pudo_path):
        d_photos.append((
            p2_pudo_path,
            f"Hình {st_code}.E.1: Khu vực quy hoạch vịnh đón trả khách PUDO tách làn",
            f"- Vị trí: {p2_pudo_desc}\n- Tọa độ GPS WGS-84: {p2_pudo_coord}\n- Đề xuất kỹ thuật: Thiết lập vịnh đón trả khách PUDO dài 15m - 20m tách làn an toàn cho Taxi, Grab và xe đưa đón cá nhân."
        ))
    if d_photos:
        create_photo_table_vertical(d_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 12: MỤC STxx.F & G - BẢN ĐỒ GIS BÃI XE & XUNG ĐỘT
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.F & {st_code}.G. BÃI ĐỖ XE PARK & RIDE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG')
    add_h2(f'1. Bản đồ GIS Bãi đỗ xe và Điểm nóng Xung đột Giao thông')
    add_large_map(map_paths[3], f'Hình {st_code}.F-G.1: Sơ đồ vị trí bãi đỗ xe và các nút giao cắt xung đột giao thông quanh Ga {st_code}', max_w=6.4, max_h=6.8)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 13: MỤC STxx.G.2 - BẢNG ĐẦY ĐỦ ĐIỂM XUNG ĐỘT (P10) & ẢNH MINH HỌA (P11)
    # ==========================================================================
    add_h2(f'2. Bảng Phân tích Điểm nóng Xung đột Giao thông (Mục {st_code}.G)')
    tbl_g = doc.add_table(rows=1, cols=5)
    tbl_g.alignment = WD_TABLE_ALIGNMENT.CENTER
    g_headers = ['Mã điểm', 'Vị trí nút giao xung đột', 'Loại xung đột', 'Nguy cơ tiềm ẩn & Nguyên nhân', 'Tọa độ GPS']
    for i, h in enumerate(g_headers):
        cell = tbl_g.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 22, 22, 35, 35)
        set_run_font(cell.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=8.5, bold=True, color_rgb=RGBColor(255, 255, 255))
        if i in (0, 4):
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    display_cfs = conflicts if conflicts else [{"name": f"Nút giao trước Ga {st_code}", "type": "Xe - xe", "form": "Giao cắt luồng rẽ", "coords": f"{lat_c:.6f}, {lon_c:.6f}"}]
    for idx, cf in enumerate(display_cfs):
        rc = tbl_g.add_row().cells
        rc[0].text = f"CP-{idx+1:02d}"
        raw_cname = cf.get("name", "Giao lộ kết nối")
        rc[1].text = raw_cname.split(",")[0].strip()
        rc[2].text = cf.get("type", "Xe - xe, Bus - xe khác")
        rc[3].text = cf.get("form", "Giao cắt luồng rẽ nhánh và trục chính tốc độ cao")
        rc[4].text = cf.get("coords", "N/A")
        for c_i, c in enumerate(rc):
            set_cell_padding(c, 12, 12, 25, 25)
            set_run_font(c.paragraphs[0].runs[0], font_name="Times New Roman", size_pt=7.5, color_rgb=DARK_GRAY)
            if c_i in (0, 4):
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_g, [Inches(0.7), Inches(2.2), Inches(1.3), Inches(1.4), Inches(1.0)])
    set_table_protection(tbl_g)

    add_h2(f'3. Bảng Hình ảnh Minh họa Điểm nóng Xung đột & Bãi đỗ xe Park & Ride')
    fg_photos = []
    
    p1_conflict = manifest_by_cat["conflict"][1] if len(manifest_by_cat["conflict"]) > 1 else (manifest_by_cat["conflict"][0] if manifest_by_cat["conflict"] else None)
    p2_parkride = manifest_by_cat["parkride"][2] if len(manifest_by_cat["parkride"]) > 2 else (manifest_by_cat["parkride"][0] if manifest_by_cat["parkride"] else None)
    
    if p1_conflict:
        fg_photos.append((
            p1_conflict["path"],
            f"Hình {st_code}.G.2: Điểm nóng xung đột giao thông trọng điểm ({p1_conflict['desc']})",
            f"- Vị trí: {p1_conflict['desc']}\n- Tọa độ GPS WGS-84: {p1_conflict['coord']}\n- Nguy cơ: Xung đột phức tạp giữa luồng rẽ nhánh và dòng xe trục chính; cần tổ chức đảo phân làn và cắm biển hạn chế tốc độ."
        ))
    if p2_parkride:
        fg_photos.append((
            p2_parkride["path"],
            f"Hình {st_code}.F.1: Quỹ đất bãi đỗ xe máy hiện hữu tiềm năng làm Park & Ride",
            f"- Vị trí: {p2_parkride['desc']}\n- Tọa độ GPS WGS-84: {p2_parkride['coord']}\n- Đề xuất: Nâng cấp mặt bằng bãi giữ xe hiện hữu thành bãi đỗ xe trung chuyển Park & Ride tiếp cận Metro giai đoạn 1."
        ))
    if fg_photos:
        create_photo_table_vertical(fg_photos)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 14: MỤC STxx.H, I, J - BẢN ĐỒ GIS RÀO CẢN
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.H, {st_code}.I & {st_code}.J. KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN VÀ THẺ ĐIỂM OAS')
    add_h2(f'1. Bản đồ GIS Ma trận Rào cản Tiếp cận Ga')
    add_large_map(map_paths[4], f'Hình {st_code}.H-I-J.1: Bản đồ định vị các rào cản đi bộ và trở ngại tiếp cận đối với NKT Ga {st_code}', max_w=6.4, max_h=6.8)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 15: MỤC STxx.J.2 - BẢNG THẺ ĐIỂM OAS THỰC TẾ (P12)
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

    # Điểm OAS tính thực tế theo phiếu khảo sát hiện trường (Thang điểm số nguyên 1 - 5)
    num_roads = len(roads)
    num_buses = len(buses)
    num_cfs = len(conflicts)
    
    score_road = 4 if num_roads >= 8 else 3
    score_walk = 3
    score_bus = 5 if num_buses >= 10 else (4 if num_buses >= 4 else 3)
    score_pudo = 4 if len(pudo) > 0 else 3
    score_park = 4 if len(parkride) > 0 else 3
    score_safety = 3 if num_cfs >= 4 else 4
    score_hub = 4
    score_nkt = 2
    
    total_sum = score_road + score_walk + score_bus + score_pudo + score_park + score_safety + score_hub + score_nkt
    total_oas = total_sum / 8.0
    rank_str = "XẾP LOẠI B (MỨC KHÁ)" if total_oas >= 3.0 else "XẾP LOẠI C (MỨC TRUNG BÌNH)"
    
    j_scores = [
        ('1', f'Khả năng tiếp cận bằng đường bộ (Mục {st_code}.B)', f'{score_road} / 5 (Tốt - Mạng lưới trục chính và đường gom kết nối thông suốt)'),
        ('2', f'Điều kiện đi bộ đến ga (Mục {st_code}.C)', f'{score_walk} / 5 (Trung bình - Vỉa hè trục chính tốt, đường nhánh cần cải tạo)'),
        ('3', f'Kết nối mạng lưới xe buýt (Mục {st_code}.D)', f'{score_bus} / 5 (Rất tốt - Đa dạng tuyến buýt liên quận xuyên tâm qua ga)'),
        ('4', f'Khả năng tổ chức làn đón trả khách PUDO (Mục {st_code}.E)', f'{score_pudo} / 5 (Tốt - Đủ chiều dài lề đường trước ga để bố trí vịnh tách làn)'),
        ('5', f'Khả năng bố trí bãi xe Park & Ride (Mục {st_code}.F)', f'{score_park} / 5 (Tốt - Có sẵn quỹ đất bãi giữ xe máy phụ cận ga)'),
        ('6', f'An toàn giao thông quanh khu vực ga (Mục {st_code}.G)', f'{score_safety} / 5 (Trung bình - Cần kiểm soát tốc độ tại các nút giao rẽ nhánh)'),
        ('7', f'Khả năng tổ chức không gian trung chuyển (Mục {st_code}.H)', f'{score_hub} / 5 (Khá - Thuận lợi tích hợp các phương thức trung chuyển)'),
        ('8', f'Khả năng tiếp cận cho người già & NKT (Mục {st_code}.I)', f'{score_nkt} / 5 (Kém - Cần đầu tư dải gạch xúc giác và ram dốc hạ hè)'),
        ('TOTAL', f'ĐIỂM TỔNG HỢP OAS TOÀN DIỆN GA {st_code}', f'{total_oas:.2f} / 5.0 (Tổng điểm: {total_sum}/40) — {rank_str}')
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
            set_cell_padding(c, 18, 18, 35, 35)
            if c_i == 0:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_col_widths(tbl_j, [Inches(0.7), Inches(3.2), Inches(2.7)])
    set_table_protection(tbl_j)

    p_j_sum = doc.add_paragraph()
    p_j_sum.paragraph_format.space_before = Pt(8)
    p_j_sum.paragraph_format.line_spacing = 1.15
    r_js = p_j_sum.add_run(
        f'Đánh giá chung: Ga {st_code} ({st_name}) đạt điểm tổng hợp OAS là {total_oas:.2f}/5.0 ({rank_str}). '
        f'Nhà ga có lợi thế vượt trội về khả năng tiếp cận đường bộ và kết nối mạng lưới xe buýt công cộng đa dạng. '
        f'Trở ngại lớn nhất cần tập trung xử lý là hạ tầng dành cho người đi bộ và người khuyết tật, cần đầu tư đồng bộ trước khi đưa tuyến metro vào vận hành chính thức.'
    )
    set_run_font(r_js, font_name="Times New Roman", size_pt=10.5, italic=True, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 16: MỤC STxx.K - KẾT LUẬN TỔNG THỂ VÀ KIẾN NGHỊ KỸ THUẬT (P1 & P2 MỚI)
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.K. KẾT LUẬN TỔNG THỂ VÀ KIẾN NGHỊ KỸ THUẬT')
    
    # 1. KẾT LUẬN TỔNG THỂ (P1)
    add_h2('1. Kết luận Tổng thể Hiện trạng Khu vực Ga')
    
    main_rd_names = [rd.get("name", "").split(",")[0].strip() for rd in roads[:3]]
    main_rd_str = ", ".join(main_rd_names) if main_rd_names else "Trục đường chính tiếp cận ga"
    
    p_k1 = doc.add_paragraph(
        f'- Vị trí và phạm vi phục vụ: Ga {st_code} ({st_name}) được quy hoạch tại {st_area}, tọa độ GPS tim ga {lat_c:.6f} N, {lon_c:.6f} E. '
        f'Trong bán kính R = 1.000m, nhà ga bao quát khu vực dân cư mật độ cao và các cơ sở kinh tế - xã hội quan trọng.\n'
        f'- Hạ tầng tiếp cận đường bộ: Đã số hóa và khảo sát {len(roads)} trục đường tiếp cận (R1 đến R{len(roads)}), trọng tâm là các trục {main_rd_str}. '
        f'Khả năng tiếp nhận lưu lượng cơ giới đạt mức tốt, đảm bảo phân bổ luồng khách tiếp cận ga thông suốt.\n'
        f'- Kết nối đa phương thức: Hiện có {len(buses)} trạm dừng xe buýt hoạt động với tần suất 10 - 15 phút, tạo tiền đề lý tưởng cho trung chuyển giữa xe buýt và Metro. '
        f'Khu vực lề đường trước ga đủ điều kiện bố trí vịnh PUDO tách làn và có sẵn quỹ đất bãi giữ xe máy làm Park & Ride.\n'
        f'- Điểm nghẽn cần tháo gỡ: Hạ tầng cho người khuyết tật còn thiếu vắng ram dốc và gạch dẫn hướng; các nút giao cắt lân cận có nguy cơ xung đột giữa luồng rẽ nhánh và dòng xe chính tốc độ cao.'
    )
    p_k1.paragraph_format.space_after = Pt(4)
    p_k1.paragraph_format.line_spacing = 1.15
    set_run_font(p_k1.runs[0], font_name="Times New Roman", size_pt=10.5, color_rgb=DARK_GRAY)

    # 2. KIẾN NGHỊ KỸ THUẬT CỤ THỂ (P2)
    add_h2('2. Kiến nghị Kỹ thuật Cụ thể (Theo Vị trí và Tuyến đường Khảo sát)')
    
    p_k2_1 = doc.add_paragraph()
    p_k2_1.paragraph_format.space_before = Pt(2)
    p_k2_1.paragraph_format.space_after = Pt(2)
    r_k2_1_title = p_k2_1.add_run('a) Nhóm Giải pháp Ưu tiên 1 - Cấp bách (Trước khi đưa tuyến Metro vào vận hành):\n')
    set_run_font(r_k2_1_title, font_name="Times New Roman", size_pt=10.5, bold=True, color_rgb=NAVY)
    r_k2_1_txt = p_k2_1.add_run(
        f'- Cải tạo và hoàn thiện vỉa hè tiêu chuẩn rộng ≥3.0m dọc hai bên tuyến {roads[0].get("name", "").split(",")[0]} và các tuyến gom tiếp giáp trực tiếp sảnh đón Ga {st_code}.\n'
        f'- Bổ sung dải gạch xúc giác dẫn hướng cho người khiếm thị và hạ ram dốc đạt quy chuẩn tiếp cận NKT tại toàn bộ các góc cua vỉa hè.\n'
        f'- Lắp đặt cụm đèn tín hiệu dành cho người đi bộ có nút bấm ưu tiên và kẻ vạch sơn phản quang nổi bật tại vị trí sang đường trước sảnh ga.'
    )
    set_run_font(r_k2_1_txt, font_name="Times New Roman", size_pt=10.0, color_rgb=DARK_GRAY)

    p_k2_2 = doc.add_paragraph()
    p_k2_2.paragraph_format.space_before = Pt(2)
    p_k2_2.paragraph_format.space_after = Pt(2)
    r_k2_2_title = p_k2_2.add_run('b) Nhóm Giải pháp Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm đầu khai thác):\n')
    set_run_font(r_k2_2_title, font_name="Times New Roman", size_pt=10.5, bold=True, color_rgb=NAVY)
    r_k2_2_txt = p_k2_2.add_run(
        f'- Bố trí vịnh đón trả khách PUDO dài 20m – 30m tách làn an toàn trên hành lang đường gom trước ga, tổ chức phân luồng riêng cho Taxi và xe công nghệ đón trả khách dưới 3 phút.\n'
        f'- Nâng cấp quỹ đất bãi đỗ xe hiện hữu lân cận ga thành bãi đỗ xe máy trung chuyển Park & Ride giai đoạn 1, đáp ứng nhu cầu gửi xe của hành khách đi Metro.\n'
        f'- Cải tạo tổ chức giao thông tại nút giao xung đột {conflicts[0].get("name", "").split(",")[0] if conflicts else "lân cận ga"}: cắm biển hạn chế tốc độ, bố trí đảo dẫn hướng và đèn cảnh báo chớp vàng.'
    )
    set_run_font(r_k2_2_txt, font_name="Times New Roman", size_pt=10.0, color_rgb=DARK_GRAY)

    p_k2_3 = doc.add_paragraph()
    p_k2_3.paragraph_format.space_before = Pt(2)
    p_k2_3.paragraph_format.space_after = Pt(2)
    r_k2_3_title = p_k2_3.add_run('c) Nhóm Giải pháp Ưu tiên 3 - Dài hạn (Định hướng phát triển đô thị TOD):\n')
    set_run_font(r_k2_3_title, font_name="Times New Roman", size_pt=10.5, bold=True, color_rgb=NAVY)
    r_k2_3_txt = p_k2_3.add_run(
        f'- Khai thác quỹ đất phụ cận Ga {st_code} để phát triển cụm công trình dịch vụ thương mại, văn phòng gắn kết mô hình đô thị nén TOD.\n'
        f'- Điều chỉnh lộ trình và bổ sung các tuyến xe buýt nhánh (Feeder Bus) kết nối trực tiếp các khu đô thị, khu công nghiệp trong bán kính 3 - 5km vào sảnh trung chuyển nhà ga.'
    )
    set_run_font(r_k2_3_txt, font_name="Times New Roman", size_pt=10.0, color_rgb=DARK_GRAY)

    doc.add_page_break()

    # ==========================================================================
    # TRANG 17: MỤC STxx.L & STxx.M - HỒ SƠ VÀ BIÊN BẢN NGHIỆM THU
    # ==========================================================================
    add_sec_title(f'MỤC {st_code}.L & {st_code}.M. HỒ SƠ ẢNH VÀ BIÊN BẢN XÁC NHẬN KHẢO SÁT THỰC ĐỊA')
    
    add_h2(f'1. Danh mục Hồ sơ Số hóa (Mục {st_code}.L)')
    p_l = doc.add_paragraph(
        f'- Bộ 5 bản đồ GIS chuyên đề số hóa độ phân giải cao tại thư mục maps_{group}/{st_old_id}/.\n'
        f'- Bộ {len(manifest)} tệp ảnh chụp thực địa có tọa độ GPS định vị chính xác lưu trữ tại photos_{group}/{st_old_id}/.\n'
        f'- File dữ liệu số hóa thuộc tính và bảng tính chi tiết tại thư mục Ga của {group.title()}/{cfg["file"]}.'
    )
    p_l.paragraph_format.space_after = Pt(4)
    p_l.paragraph_format.line_spacing = 1.15
    set_run_font(p_l.runs[0], font_name="Times New Roman", size_pt=10.5, color_rgb=DARK_GRAY)

    add_h2(f'2. Biên bản Xác nhận Kết quả Khảo sát Thực địa (Mục {st_code}.M)')
    p_m_intro = doc.add_paragraph(
        f'Hôm nay, ngày 26 tháng 09 năm 2026, các bên liên quan đã tiến hành rà soát, nghiệm thu hồ sơ khảo sát hiện trạng tiếp cận và trung chuyển tại Ga {st_code} ({st_name}). '
        f'Hồ sơ phản ánh trung thực, đầy đủ hiện trạng hạ tầng giao thông thực địa phục vụ công tác lập Báo cáo nghiên cứu tiền khả thi và thiết kế FEED.'
    )
    p_m_intro.paragraph_format.space_after = Pt(8)
    p_m_intro.paragraph_format.line_spacing = 1.15
    set_run_font(p_m_intro.runs[0], font_name="Times New Roman", size_pt=10.5, color_rgb=DARK_GRAY)

    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    c_s1 = tbl_sign.rows[0].cells[0]
    c_s2 = tbl_sign.rows[0].cells[1]
    
    c_s1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s1 = c_s1.paragraphs[0].add_run('CÁN BỘ KHẢO SÁT THỰC ĐỊA\n(Ký và ghi rõ họ tên)')
    set_run_font(r_s1, font_name="Times New Roman", size_pt=11.0, bold=True, color_rgb=NAVY)
    
    c_s2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s2 = c_s2.paragraphs[0].add_run('ĐẠI DIỆN ĐƠN VỊ TƯ VẤN THẨM ĐỊNH\n(Ký, đóng dấu và ghi rõ họ tên)')
    set_run_font(r_s2, font_name="Times New Roman", size_pt=11.0, bold=True, color_rgb=NAVY)
    
    c_b1 = tbl_sign.rows[1].cells[0]
    c_b2 = tbl_sign.rows[1].cells[1]
    
    c_b1.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_b1.paragraphs[0].paragraph_format.space_before = Pt(65)
    r_name1 = c_b1.paragraphs[0].add_run(surveyor_name)
    set_run_font(r_name1, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)
    
    c_b2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c_b2.paragraphs[0].paragraph_format.space_before = Pt(65)
    r_name2 = c_b2.paragraphs[0].add_run('LÃNH ĐẠO ĐƠN VỊ TƯ VẤN')
    set_run_font(r_name2, font_name="Times New Roman", size_pt=11.5, bold=True, color_rgb=NAVY)

    for r in tbl_sign.rows:
        for c in r.cells:
            set_cell_padding(c, 30, 30, 50, 50)
    set_col_widths(tbl_sign, [Inches(3.3), Inches(3.3)])
    set_table_protection(tbl_sign)

    safe_name = remove_accents(st_name)
    out_file_name = f"BC_KhaoSat_HienTrang_Ga_{st_code}_{safe_name}_V2.docx"
    out_docx_path = os.path.join(OUTPUT_DIR, out_file_name)
    
    # Save to 'chỉnh sửa' folder (primary destination requested by user)
    chinh_sua_path = os.path.join(CHINH_SUA_DIR, out_file_name)
    doc.save(chinh_sua_path)
    
    # Save to Final folder
    final_path = os.path.join(FINAL_DIR, out_file_name)
    doc.save(final_path)
    
    # Save copy to output
    doc.save(out_docx_path)
    
    # Save copy to ketqua
    ketqua_path = os.path.join(KETQUA_DIR, out_file_name)
    doc.save(ketqua_path)
    
    # Also save to base
    base_path = os.path.join(BASE_DIR, out_file_name)
    doc.save(base_path)

    print(f"  >>> XUẤT THÀNH CÔNG: {out_file_name}")
    print(f"      Dung lượng: {os.path.getsize(chinh_sua_path):,} bytes")
    print(f"      Lưu thư mục CHỈNH SỬA: {chinh_sua_path}")
    print(f"      Lưu thư mục FINAL: {final_path}")
    return chinh_sua_path

# ==============================================================================
# CẤU HÌNH ĐẦY ĐỦ 26 NHÀ GA METRO TUYẾN 2 & 2S
# ==============================================================================
ALL_26_STATIONS = [
    # 13 GA THUỘC NHÓM QUÂN (Kỹ sư Nguyễn Minh Quân)
    {"num": 1,  "code": "ST01", "old_id": "S1",  "group": "quan", "file": "Ga 1.xlsx",   "name": "Phan Văn Hớn",     "lat": 10.82841, "lon": 106.62438, "area": "Phường Tây Thạnh (Tân Phú) & Đông Hưng Thuận (Quận 12)", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 2,  "code": "ST02", "old_id": "S2",  "group": "quan", "file": "Ga 2.xlsx",   "name": "Đông Hưng Thuận",  "lat": 10.83683, "lon": 106.61897, "area": "Phường Đông Hưng Thuận & Tân Thới Nhất, Quận 12", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 3,  "code": "ST03", "old_id": "S3",  "group": "vinh", "file": "Ga 3.xlsx",   "name": "An Sương",         "lat": 10.85338, "lon": 106.60711, "area": "Phường Trung Mỹ Tây & Tân Thới Nhất, Quận 12 (Nút giao An Sương)", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 4,  "code": "ST04", "old_id": "S4",  "group": "vinh", "file": "Ga 4.xlsx",   "name": "Nguyễn Ảnh Thủ",   "lat": 10.86155, "lon": 106.60146, "area": "Khu vực ngã tư Trung Chánh - Nguyễn Ảnh Thủ, Quận 12 & Hóc Môn", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 5,  "code": "ST05", "old_id": "S5",  "group": "vinh", "file": "Ga 5.xlsx",   "name": "Nguyễn Thị Sóc",   "lat": 10.87547, "lon": 106.59160, "area": "Xã Bà Điểm & Xuân Thới Đông, Huyện Hóc Môn", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 6,  "code": "ST06", "old_id": "S6",  "group": "vinh", "file": "Ga 6.xlsx",   "name": "Bà Triệu",         "lat": 10.88385, "lon": 106.58569, "area": "Thị trấn Hóc Môn & Xã Tân Xuân, Huyện Hóc Môn", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 7,  "code": "ST07", "old_id": "S7",  "group": "quan", "file": "Ga 7.xlsx",   "name": "Lý Thường Kiệt",   "lat": 10.88455, "lon": 106.58646, "area": "Thị trấn Hóc Môn, Huyện Hóc Môn", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 8,  "code": "ST08", "old_id": "S8",  "group": "quan", "file": "Ga 8.xlsx",   "name": "Nguyễn Thị Nuôi",  "lat": 10.89413, "lon": 106.57976, "area": "Xã Tân Hiệp, Huyện Hóc Môn", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 9,  "code": "ST09", "old_id": "S9",  "group": "vinh", "file": "Ga 9.xlsx",   "name": "Vòng cung Tây Bắc 2", "lat": 10.91156, "lon": 106.56640, "area": "Xã Tân Hiệp, Huyện Hóc Môn", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 10, "code": "ST10", "old_id": "S10", "group": "vinh", "file": "Ga 10.xlsx",  "name": "Vành Đai 3",       "lat": 10.92104, "lon": 106.56042, "area": "Khu vực nút giao Vành Đai 3, Xã Tân Hiệp & Xã Tân Phú Trung", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 11, "code": "ST11", "old_id": "S11", "group": "quan", "file": "Ga 11.xlsx",  "name": "An Hạ",           "lat": 10.92166, "lon": 106.56103, "area": "Xã Tân Phú Trung & Tân Hiệp, Củ Chi - Hóc Môn", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 12, "code": "ST12", "old_id": "S12", "group": "quan", "file": "Ga 12.xlsx",  "name": "Tân Phú Trung",   "lat": 10.92977, "lon": 106.55484, "area": "Xã Tân Phú Trung, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 13, "code": "ST13", "old_id": "S13", "group": "vinh", "file": "Ga 13.xlsx",  "name": "Hương Lộ 2",       "lat": 10.94115, "lon": 106.53412, "area": "Xã Tân Phú Trung, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 14, "code": "ST14", "old_id": "S14", "group": "quan", "file": "Ga 14.xlsx",  "name": "Đào Thị Kiểm",    "lat": 10.94216, "lon": 106.53425, "area": "Xã Tân Phú Trung & Tân Thạnh Tây, Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 15, "code": "ST15", "old_id": "S15", "group": "vinh", "file": "Ga 15.xlsx",  "name": "Lê Minh Nhựt",     "lat": 10.95248, "lon": 106.51453, "area": "Xã Tân Thông Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 16, "code": "ST16", "old_id": "S16", "group": "vinh", "file": "Ga 16.xlsx",  "name": "Tân Thông Hội",     "lat": 10.95718, "lon": 106.50689, "area": "Xã Tân Thông Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 17, "code": "ST17", "old_id": "S17", "group": "vinh", "file": "Ga 17.xlsx",  "name": "Trần Tử Bình",     "lat": 10.96163, "lon": 106.49855, "area": "Thị trấn Củ Chi & Xã Tân Thông Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 18, "code": "ST18", "old_id": "S18", "group": "quan", "file": "Ga 18.xlsx",  "name": "Huỳnh Văn Cọ",     "lat": 10.96255, "lon": 106.49883, "area": "Thị trấn Củ Chi, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 19, "code": "ST19", "old_id": "S19", "group": "quan", "file": "Ga 19_.xlsx", "name": "Củ Chi",          "lat": 10.96747, "lon": 106.48826, "area": "Trung tâm Thị trấn Củ Chi, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 20, "code": "ST20", "old_id": "S20", "group": "quan", "file": "Ga 20.xlsx",  "name": "BV Củ Chi",       "lat": 10.97319, "lon": 106.47848, "area": "Khu vực Bệnh viện Đa khoa Củ Chi, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 21, "code": "ST21", "old_id": "S21", "group": "quan", "file": "Ga 21.xlsx",  "name": "Nguyễn Thị Rành",  "lat": 10.97828, "lon": 106.46901, "area": "Xã Tân An Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 22, "code": "ST22", "old_id": "S22", "group": "vinh", "file": "Ga 22.xlsx",  "name": "Tân An Hội",       "lat": 10.99052, "lon": 106.44909, "area": "Xã Tân An Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 23, "code": "ST23", "old_id": "S23", "group": "vinh", "file": "Ga 23.xlsx",  "name": "Ba Sa",            "lat": 11.00075, "lon": 106.43793, "area": "Xã Phước Hiệp & Xã Tân An Hội, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 24, "code": "ST24", "old_id": "S24", "group": "vinh", "file": "Ga 24.xlsx",  "name": "Phước Hiệp",       "lat": 11.00522, "lon": 106.42605, "area": "Xã Phước Hiệp, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Trang Thế Vinh"},
    {"num": 25, "code": "ST25", "old_id": "S25", "group": "quan", "file": "Ga 25.xlsx",  "name": "Tỉnh Lộ 7",        "lat": 11.00629, "lon": 106.42606, "area": "Xã Phước Hiệp & Thái Mỹ, Huyện Củ Chi", "surveyor": "Kỹ sư Nguyễn Minh Quân"},
    {"num": 26, "code": "ST26", "old_id": "S26", "group": "quan", "file": "Ga 26.xlsx",  "name": "Thái Mỹ",          "lat": 11.01344, "lon": 106.41244, "area": "Xã Thái Mỹ, Huyện Củ Chi (Ga cuối tuyến)", "surveyor": "Kỹ sư Nguyễn Minh Quân"}
]

if __name__ == "__main__":
    stations_to_run = ALL_26_STATIONS
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        if arg != "ALL":
            matched = [s for s in ALL_26_STATIONS if s["code"] == arg or s["old_id"].upper() == arg or f"ST{arg}" == s["code"] or f"S{arg}" == s["old_id"].upper()]
            if matched:
                stations_to_run = matched

    print(f"\n{'='*70}")
    print(f"BẮT ĐẦU XUẤT {len(stations_to_run)} BÁO CÁO HIỆN TRẠNG GA VÀO THƯ MỤC FINAL")
    print(f"{'='*70}")
    
    success_count = 0
    for idx, cfg in enumerate(stations_to_run, 1):
        print(f"\n[{idx}/{len(stations_to_run)}] Xử lý Ga {cfg['code']} - {cfg['name']} ({cfg['surveyor']})...")
        try:
            generate_enhanced_station_report(cfg)
            success_count += 1
        except Exception as e:
            print(f"  [!] LỖI TẠI GA {cfg['code']}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"HOÀN TẤT XUẤT {success_count}/{len(stations_to_run)} BÁO CÁO THÀNH CÔNG VÀO THƯ MỤC:")
    print(f"  >>> {FINAL_DIR}")
    print(f"{'='*70}")
