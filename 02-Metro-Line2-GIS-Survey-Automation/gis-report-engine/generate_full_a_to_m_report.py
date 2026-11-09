import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def generate_full_a_to_m_report():
    print("[*] Generating Full A-M Master Report for Ga S1...")
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Colors
    NAVY = RGBColor(0, 51, 102)
    DARK_GRAY = RGBColor(51, 51, 51)
    LIGHT_BG = 'F4F6F9'
    HEADER_BG = '003366'

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def add_sec_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = NAVY

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = DARK_GRAY

    # Images & Maps
    s1_dir = 's1'
    s1_images = []
    if os.path.exists(s1_dir):
        s1_images = [os.path.join(s1_dir, f) for f in sorted(os.listdir(s1_dir)) if f.lower().endswith(('.jpg', '.png'))]

    map1 = os.path.join('maps', 'S1_Map1_TongQuan_1000m.png')
    map2 = os.path.join('maps', 'S1_Map2_DiBo_200m_500m.png')
    map3 = os.path.join('maps', 'S1_Map3_Bus_PUDO.png')
    map4 = os.path.join('maps', 'S1_Map4_ParkRide_XungDot.png')
    map5 = os.path.join('maps', 'S1_Map5_RaoCan_TongHop.png')

    def add_chapter_map(map_path, caption_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(map_path):
            p.add_run().add_picture(map_path, width=Inches(5.8))
            p_cap = doc.add_paragraph(caption_text)
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.runs[0].font.size = Pt(9.5)
            p_cap.runs[0].font.italic = True

    def insert_image_cell(cell, img_path, caption_text, width_inch=2.8):
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(img_path):
            try:
                run = p.add_run()
                run.add_picture(img_path, width=Inches(width_inch))
                p_cap = cell.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r_cap = p_cap.add_run(caption_text)
                r_cap.font.size = Pt(9)
                r_cap.font.italic = True
            except Exception as e:
                p.add_run(f"[Hình ảnh: {caption_text}]")

    def create_photo_table(photo_list):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        hdr = tbl.rows[0].cells
        hdr[0].text = "Hình ảnh Thực địa (Chèn tự động)"
        hdr[1].text = "Mô tả Chi tiết & Tọa độ GPS"
        set_cell_background(hdr[0], HEADER_BG)
        set_cell_background(hdr[1], HEADER_BG)
        hdr[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[0].paragraphs[0].runs[0].font.bold = True
        hdr[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[1].paragraphs[0].runs[0].font.bold = True

        for img_path, desc in photo_list:
            r = tbl.add_row().cells
            insert_image_cell(r[0], img_path, os.path.basename(img_path), width_inch=2.8)
            r[1].text = desc
            set_cell_background(r[0], LIGHT_BG)

    # ---------------------------------------------------------
    # TRANG BÌA & MỤC A: THÔNG TIN CHUNG
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run('DỰ ÁN ĐƯỜNG SẮT ĐÔ THỊ THÀNH PHỐ HỒ CHÍ MINH (METRO TUYẾN 2)\n')
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = DARK_GRAY

    r_main = p_title.add_run('BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN VÀ TRUNG CHUYỂN\nGA S1 – PHAN VĂN HỚN\n(CHUẨN ĐẮP ỨNG TOÀN BỘ MỤC A ĐẾN MỤC M - NHIỆM VỤ 9)')
    r_main.font.size = Pt(14)
    r_main.font.bold = True
    r_main.font.color.rgb = NAVY

    add_sec_title('MỤC A. THÔNG TIN CHUNG NHÀ GA')
    tbl_info = doc.add_table(rows=5, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ('Mã nhà ga:', 'S1', 'Tên nhà ga:', 'Phan Văn Hớn'),
        ('Tuyến Metro:', 'Tuyến 2 (Bến Thành - Tham Lương)', 'Vị trí đặt ga:', 'Ga ngầm (Nút giao QL22 & Phan Văn Hớn)'),
        ('Địa giới hành chính:', 'Phường Tân Thới Nhất, Quận 12', 'Tọa độ GPS:', '10.836068 N, 106.618255 E'),
        ('Ngày khảo sát:', '01/09/2026', 'Thời tiết:', 'Nắng nhẹ, khô ráo'),
        ('Khảo sát viên:', 'Nguyễn Văn A (Đội trưởng)', 'Đơn vị kiểm tra:', 'Đội Khảo sát Kỹ thuật Metro 2')
    ]
    for idx, row in enumerate(tbl_info.rows):
        d = info_data[idx]
        row.cells[0].text = f'{d[0]} {d[1]}'
        row.cells[1].text = f'{d[2]} {d[3]}'
        set_cell_background(row.cells[0], LIGHT_BG)
        set_cell_background(row.cells[1], LIGHT_BG)

    # ---------------------------------------------------------
    # MỤC B: HIỆN TRẠNG ĐƯỜNG TIẾP CẬN GA
    # ---------------------------------------------------------
    add_sec_title('MỤC B. HIỆN TRẠNG ĐƯỜNG TIẾP CẬN GA')
    
    add_h2('1. Bản đồ GIS Tổng quan Mạng lưới Đường tiếp cận (200m & 1000m)')
    add_chapter_map(map1, 'Hình B.1: Sơ đồ mạng lưới giao thông bán kính 200m & 1000m - Ga S1 Phan Văn Hớn')

    add_h2('2. Bảng Thông số Mặt cắt ngang các Tuyến đường tiếp cận')
    tbl_r = doc.add_table(rows=1, cols=6)
    tbl_r.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ['Mã tuyến', 'Tên đường', 'Lòng đường (m)', 'Vỉa hè trái (m)', 'Vỉa hè phải (m)', 'Ghi chú hiện trạng']
    for i, h in enumerate(headers):
        cell = tbl_r.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    road_rows = [
        ('R1', 'Quốc lộ 22 (Trường Chinh)', '28.0 m', '4.5 m', '4.0 m', 'Trục chính 6 làn xe, dải phân cách cứng'),
        ('R2', 'Đường Phan Văn Hớn', '10.5 m', '1.5 m', '1.2 m', 'Trục cắt ngang thu gom, vỉa hè bị lấn chiếm'),
        ('R3', 'Đường Song Hành QL22', '7.0 m', '2.0 m', '1.5 m', 'Đường gom tiếp cận phụ, đề xuất làn PUDO'),
        ('R4', 'Đường Tân Thới Nhất 17', '6.0 m', '1.0 m', '1.0 m', 'Hẻm dân sinh kết nối bãi xe Park & Ride')
    ]
    for r_data in road_rows:
        rc = tbl_r.add_row().cells
        for col_idx in range(6):
            rc[col_idx].text = r_data[col_idx]

    add_h2('3. Bảng Hình ảnh Minh họa Đường tiếp cận & Cửa ga S1')
    img1 = s1_images[0] if len(s1_images) > 0 else ""
    img2 = s1_images[1] if len(s1_images) > 1 else ""
    create_photo_table([
        (img1, 'Ảnh mặt cắt ngang lòng đường QL22 & vỉa hè rộng 4.5m trước vị trí ga S1'),
        (img2, 'Khu vực vỉa hè dự kiến đặt Cửa lên xuống Exit A (Phía QL22 hướng đi An Sương)')
    ])

    # ---------------------------------------------------------
    # MỤC C: ĐIỀU KIỆN ĐI BỘ ĐẾN GA
    # ---------------------------------------------------------
    add_sec_title('MỤC C. ĐIỀU KIỆN ĐI BỘ ĐẾN GA')
    
    add_h2('1. Bản đồ GIS Phân vùng Tiếp cận Đi bộ (Bán kính 200m & 500m)')
    add_chapter_map(map2, 'Hình C.1: Sơ đồ phân vùng hành lang đi bộ 200m & 500m quanh cửa ga S1')

    add_h2('2. Bảng Đánh giá Chất lượng Đi bộ Ga S1 (6 Tiêu chí)')
    tbl_walk = doc.add_table(rows=1, cols=3)
    tbl_walk.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Tiêu chí đánh giá đi bộ', 'Điểm (1-5) & Ghi nhận thực địa']):
        cell = tbl_walk.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    walk_data = [
        ('1', 'Tính liên tục của tuyến đi bộ', '2/5 - Vỉa hè Phan Văn Hớn bị lấn chiếm, đứt đoạn tại các hẻm nhánh.'),
        ('2', 'An toàn giao thông đi bộ', '2/5 - Mật độ xe cơ giới QL22 lớn, thiếu đảo trú chân khi sang đường.'),
        ('3', 'Tiện nghi & Mảng xanh', '3/5 - QL22 thông thoáng nhưng đường Phan Văn Hớn thiếu cây xanh bóng mát.'),
        ('4', 'Mức độ chiếu sáng ban đêm', '3/5 - Trục QL22 chiếu sáng tốt; chiếu sáng vỉa hè đường phụ còn yếu.'),
        ('5', 'Khả năng tiếp cận NKT', '1/5 - Rất kém, vỉa hè chênh cao, vướng bậc tam cấp, chưa có dốc ram.'),
        ('6', 'Biển chỉ dẫn đi bộ đến ga', '1/5 - Chưa có hệ thống biển chỉ dẫn đi bộ chuyên dùng.')
    ]
    for w_row in walk_data:
        rc = tbl_walk.add_row().cells
        rc[0].text = w_row[0]
        rc[1].text = w_row[1]
        rc[2].text = w_row[2]

    add_h2('3. Bảng Hình ảnh Minh họa Hạ tầng Đi bộ & Nút Sang đường')
    img3 = s1_images[2] if len(s1_images) > 2 else ""
    img4 = s1_images[3] if len(s1_images) > 3 else ""
    create_photo_table([
        (img3, 'Hiện trạng vỉa hè đường Phan Văn Hớn bị lấn chiếm buôn bán'),
        (img4, 'Vạch sang đường cho người đi bộ tại nút giao QL22 - Phan Văn Hớn')
    ])

    # ---------------------------------------------------------
    # MỤC D & E: KẾT NỐI XE BUÝT VÀ PUDO ĐÓ N TRẢ KHÁCH
    # ---------------------------------------------------------
    add_sec_title('MỤC D & E. ĐIỀU KIỆN KẾT NỐI XE BUÝT VÀ ĐIỂM PUDO (PICK-UP / DROP-OFF)')
    
    add_h2('1. Bản đồ GIS Trạm Buýt & Làn Đón trả khách PUDO')
    add_chapter_map(map3, 'Hình D-E.1: Sơ đồ trạm dừng xe buýt & vị trí làn PUDO / Kiss & Ride quanh Ga S1')

    add_h2('2. Bảng Tổng hợp Mạng lưới Trạm Xe buýt (Mục D)')
    tbl_bus = doc.add_table(rows=1, cols=5)
    tbl_bus.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_headers = ['Mã trạm', 'Vị trí trạm buýt', 'Khoảng cách ga', 'Tuyến buýt đi qua', 'Hiện trạng hạ tầng']
    for i, h in enumerate(b_headers):
        cell = tbl_bus.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    bus_data = [
        ('BS-01', 'QL22 (Chiều đi An Sương)', '60 m', 'Tuyến 04, 13, 27, 65, 94', 'Có nhà chờ, mái che, biển báo'),
        ('BS-02', 'QL22 (Chiều đi Bến Thành)', '85 m', 'Tuyến 04, 13, 27, 65, 94', 'Chỉ có cột mốc trạm, thiếu mái che'),
        ('BS-03', 'Phan Văn Hớn (2 chiều)', '180 m', 'Tuyến 23', 'Cắm biển dừng, vỉa hè hẹp')
    ]
    for b_row in bus_data:
        rc = tbl_bus.add_row().cells
        for c_idx in range(5):
            rc[c_idx].text = b_row[c_idx]

    add_h2('3. Đánh giá Nhu cầu & Phương án Bố trí Làn PUDO Taxi/Grab (Mục E)')
    doc.add_paragraph('• Nhu cầu PUDO hiện tại: Taxi (Trung bình), Grab/Xe công nghệ (Cao), Xe cá nhân đón trả (Cao).\n• Đề xuất giải pháp: Khoét lề bố trí vịnh đón trả khách PUDO dài 45m trên đường Song Hành QL22 (cách Exit A 40m).')

    add_h2('4. Bảng Hình ảnh Trạm Buýt & Vị trí Làn PUDO')
    img5 = s1_images[4] if len(s1_images) > 4 else ""
    img6 = s1_images[5] if len(s1_images) > 5 else ""
    create_photo_table([
        (img5, 'Trạm buýt BS-01 trên QL22 cách cửa ga S1 60m đi bộ'),
        (img6, 'Khu vực đường Song Hành QL22 đề xuất bố trí làn đón trả khách Kiss & Ride (dài 45m)')
    ])

    # ---------------------------------------------------------
    # MỤC F & G: NHU CẦU BÃI ĐỖ XE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG
    # ---------------------------------------------------------
    add_sec_title('MỤC F & G. NHU CẦU BÃI ĐỖ XE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG')
    
    add_h2('1. Bản đồ GIS Quy hoạch Bãi xe Park & Ride & Điểm nóng Xung đột')
    add_chapter_map(map4, 'Hình F-G.1: Sơ đồ vị trí quy hoạch Bãi xe Park & Ride & Điểm nóng ùn tắc CP-01, CP-02')

    add_h2('2. Đánh giá Nhu cầu Bãi đỗ xe Trung chuyển Park & Ride (Mục F)')
    doc.add_paragraph('• Nhu cầu dự kiến: Xe máy (Rất cao - trên 800 xe/ngày), Xe đạp (Thấp), Ô tô cá nhân (Trung bình).\n• Vị trí quy hoạch: Đề xuất thu hồi/thuê khu đất trống 1,200m2 tại góc đường Phan Văn Hớn - Tân Thới Nhất 17.')

    add_h2('3. Bảng Điểm nóng Xung đột Giao thông quanh Ga S1 (Mục G)')
    tbl_conf = doc.add_table(rows=1, cols=4)
    tbl_conf.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_headers = ['Mã điểm', 'Vị trí xung đột', 'Loại hình xung đột', 'Mức độ rủi ro & Khung giờ']
    for i, h in enumerate(c_headers):
        cell = tbl_conf.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    conf_data = [
        ('CP-01', 'Ngã 3 QL22 - Phan Văn Hớn', 'Xe rẽ trái cắt ngang dòng xe đi thẳng + Xe buýt ra vào trạm', 'Rủi ro CAO (06:30-08:30 & 16:30-19:00)'),
        ('CP-02', 'Mũi tàu Song Hành QL22', 'Nhập dòng giữa xe máy và xe tải lớn từ QL22 đổ về', 'Rủi ro TRUNG BÌNH (Cả ngày)')
    ]
    for c_row in conf_data:
        rc = tbl_conf.add_row().cells
        for c_idx in range(4):
            rc[c_idx].text = c_row[c_idx]

    add_h2('4. Bảng Hình ảnh Minh họa Bãi xe Park & Ride & Kẹt xe')
    img7 = s1_images[6] if len(s1_images) > 6 else ""
    img8 = s1_images[7] if len(s1_images) > 7 else ""
    create_photo_table([
        (img7, 'Khu đất trống 1,200m2 tại góc Phan Văn Hớn - Tân Thới Nhất 17 đề xuất làm bãi xe Park & Ride'),
        (img8, 'Ùn tắc giao thông cục bộ tại nút giao QL22 - Phan Văn Hớn giờ cao điểm chiều')
    ])

    # ---------------------------------------------------------
    # MỤC H, I & J: TRUNG CHUYỂN, RÀO CẢN & OAS SCORECARD
    # ---------------------------------------------------------
    add_sec_title('MỤC H, I & J. KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN VÀ OAS SCORECARD')
    
    add_h2('1. Bản đồ GIS Ma trận Rào cản Tiếp cận Ga S1')
    add_chapter_map(map5, 'Hình H-I-J.1: Sơ đồ ma trận 16 rào cản tiếp cận & vị trí Top 3 rào cản nghiêm trọng quanh Ga S1')

    add_h2('2. Khả năng Bố trí Không gian Trung chuyển Tổng hợp (Mục H)')
    doc.add_paragraph('• Đánh giá không gian: Khu vực cửa ga S1 có mặt tiền QL22 rộng, thuận lợi tổ chức quảng trường nhỏ đón trả khách kết hợp lối thoát hiểm ngầm.')

    add_h2('3. Bảng Tổng hợp Thẻ điểm OAS Đánh giá Tiếp cận Ga S1 (Mục J)')
    tbl_oas = doc.add_table(rows=1, cols=3)
    tbl_oas.alignment = WD_TABLE_ALIGNMENT.CENTER
    o_headers = ['STT', 'Nhóm chỉ tiêu tiếp cận', 'Điểm đánh giá (1 - 5) & Xếp loại']
    for i, h in enumerate(o_headers):
        cell = tbl_oas.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    oas_data = [
        ('1', 'Khả năng tiếp cận bằng đường bộ (Mục B)', '3.5 / 5 - Khá'),
        ('2', 'Điều kiện đi bộ đến ga (Mục C)', '2.0 / 5 - Kém'),
        ('3', 'Kết nối mạng lưới xe buýt (Mục D)', '3.5 / 5 - Khá'),
        ('4', 'Tổ chức điểm đón trả khách PUDO (Mục E)', '3.0 / 5 - Trung bình'),
        ('5', 'Bố trí bãi xe trung chuyển Park & Ride (Mục F)', '3.0 / 5 - Trung bình'),
        ('6', 'An toàn giao thông quanh ga (Mục G)', '2.0 / 5 - Kém'),
        ('7', 'Tổ chức không gian trung chuyển (Mục H)', '3.0 / 5 - Trung bình'),
        ('8', 'Khả năng tiếp cận cho NKT (Mục I)', '1.5 / 5 - Rất kém'),
        ('TOTAL', 'TỔNG THỂ KHẢ NĂNG TIẾP CẬN GA (OAS SCORE)', '2.81 / 5.0 - TRUNG BÌNH (LOẠI C)')
    ]
    for o_row in oas_data:
        rc = tbl_oas.add_row().cells
        rc[0].text = o_row[0]
        rc[1].text = o_row[1]
        rc[2].text = o_row[2]

    add_h2('4. Bảng Hình ảnh Minh họa Top Rào cản Trọng yếu Ga S1 (Mục I)')
    img9 = s1_images[8] if len(s1_images) > 8 else ""
    img10 = s1_images[9] if len(s1_images) > 9 else ""
    img11 = s1_images[10] if len(s1_images) > 10 else ""
    create_photo_table([
        (img9, 'Rào cản 1: Hàng rong, chợ tự phát lấn chiếm hoàn toàn vỉa hè đường Phan Văn Hớn'),
        (img10, 'Rào cản 2: Mạng lưới dây điện & cáp viễn thông treo thấp sà xuống lối đi bộ'),
        (img11, 'Rào cản 3: Vỉa hè chênh cao, thiếu dốc ram gây rào cản lớn cho người khuyết tật')
    ])

    # ---------------------------------------------------------
    # MỤC K: ĐỀ XUẤT CẢI THIỆN
    # ---------------------------------------------------------
    add_sec_title('MỤC K. ĐỀ XUẤT CẢI THIỆN GA S1')
    
    add_h2('1. Ưu tiên 1 - Xử lý ngay (Chuẩn bị vận hành)')
    doc.add_paragraph('• Giải tỏa buôn bán lấn chiếm trên đường Phan Văn Hớn (đoạn 150m từ QL22).\n• Điều chỉnh thời gian đèn xanh đi bộ tại nút QL22 từ 15s lên 25s; xây đảo trú chân giữa dải phân cách.')

    add_h2('2. Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm)')
    doc.add_paragraph('• Xây cầu vượt đi bộ nối Cửa ga S1 qua QL22 đến trạm xe buýt BS-02.\n• Cải tạo đường Song Hành QL22 thành làn 1 chiều kết hợp vịnh đón trả khách PUDO dài 45m.')

    add_h2('3. Ưu tiên 3 - Dài hạn & Quy hoạch TOD (Bán kính 1000m)')
    doc.add_paragraph('• Thu hồi/thuê khu đất 1,200m2 tại góc Phan Văn Hớn - Tân Thới Nhất 17 làm bãi xe Park & Ride.\n• Mở mới tuyến buýt gom Minibus kết nối khu dân cư Bà Điểm / Hóc Môn trực tiếp về Ga S1.')

    # ---------------------------------------------------------
    # MỤC L & M: HỒ SƠ ẢNH VÀ XÁC NHẬN KHẢO SÁT
    # ---------------------------------------------------------
    doc.add_page_break()
    add_sec_title('MỤC L & M. HỒ SƠ ẢNH VÀ BIÊN BẢN XÁC NHẬN KHẢO SÁT THỰC ĐỊA')
    
    add_h2('1. Danh mục Hồ sơ Ảnh & Bản đồ số hóa (Mục L)')
    doc.add_paragraph('• Bản đồ GIS 1: Sơ đồ mạng lưới đường bán kính 1000m.\n• Bản đồ GIS 2: Phân vùng đi bộ 200m/500m.\n• Bản đồ GIS 3: Mạng lưới xe buýt & PUDO.\n• Bản đồ GIS 4: Bãi xe Park & Ride & Điểm xung đột.\n• Bản đồ GIS 5: Ma trận rào cản tiếp cận.\n• Bộ 11 ảnh chụp thực địa có tọa độ GPS định vị công trường.')

    add_h2('2. Biên bản Xác nhận Khảo sát Thực địa (Mục M)')
    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign.rows[0].cells[0].text = 'ĐẠI DIỆN ĐỘI KHẢO SÁT (MỤC M.1)\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[0].cells[1].text = 'NGƯỜI KIỂM TRA & DUYỆT BÁO CÁO (MỤC M.2)\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[1].cells[0].text = '\n\nHọ tên: Nguyễn Văn A\nNgày khảo sát: 01/09/2026'
    tbl_sign.rows[1].cells[1].text = '\n\nHọ tên: Trần Văn B\nNgày duyệt: 02/09/2026'

    output_path = 'BaoCao_KhaoSat_ThucDia_Ga_S1_PhanVanHon_NO_BLUE_LINES.docx'
    doc.save(output_path)
    print(f"[+] Done! Saved full A-M report to: {output_path}")

if __name__ == '__main__':
    generate_full_a_to_m_report()
