import os, sys, json, docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.stdout.reconfigure(encoding='utf-8')

def build_s23_report():
    print("[*] Đang khởi tạo và lắp ráp Báo cáo Khảo sát Thực địa Ga S23 - Ba Sa (Chuẩn A-M)...")
    doc = docx.Document()

    # Căn lề chuẩn văn bản kỹ thuật
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    # Hệ màu chuẩn học thuật (Navy Corporate)
    NAVY = RGBColor(0, 51, 102)
    DARK_GRAY = RGBColor(51, 51, 51)
    LIGHT_BG = 'F4F6F9'
    HEADER_BG = '003366'
    BORDER_COLOR = 'D0D7DE'

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def set_cell_padding(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def add_sec_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
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

    def add_map(map_path, caption_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        if os.path.exists(map_path):
            p.add_run().add_picture(map_path, width=Inches(6.0))
            p_cap = doc.add_paragraph(caption_text)
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(8)
            p_cap.runs[0].font.size = Pt(9.5)
            p_cap.runs[0].font.italic = True
            p_cap.runs[0].font.color.rgb = RGBColor(80, 80, 80)

    # Đọc manifest ảnh thực địa đã tải
    manifest_file = os.path.join('s23', 'images_manifest.json')
    images_by_cat = {'road': [], 'bus': [], 'pudo': [], 'parkride': [], 'conflict': []}
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding='utf-8') as f:
            all_imgs = json.load(f)
            for item in all_imgs:
                cat = item.get('category', 'road')
                if cat in images_by_cat:
                    images_by_cat[cat].append(item)

    def insert_image_cell(cell, img_path, caption_text, width_inch=2.8):
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        if os.path.exists(img_path):
            try:
                run = p.add_run()
                run.add_picture(img_path, width=Inches(width_inch))
                p_cap = cell.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(4)
                r_cap = p_cap.add_run(caption_text)
                r_cap.font.size = Pt(8.5)
                r_cap.font.italic = True
                r_cap.font.color.rgb = RGBColor(100, 100, 100)
            except Exception:
                p.add_run(f"[Ảnh: {caption_text}]")
        else:
            p.add_run(f"[Không tìm thấy tệp ảnh: {img_path}]")

    def create_photo_table(photo_tuples):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = tbl.rows[0].cells
        hdr[0].text = "Hình ảnh Hiện trường (Tự động tải & chèn)"
        hdr[1].text = "Mô tả Khảo sát Kỹ thuật & Tọa độ GPS"
        for c in hdr:
            set_cell_background(c, HEADER_BG)
            set_cell_padding(c, 120, 120, 150, 150)
            c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
            c.paragraphs[0].runs[0].font.bold = True
            c.paragraphs[0].runs[0].font.size = Pt(9.5)

        for img_path, desc_text in photo_tuples:
            r = tbl.add_row().cells
            insert_image_cell(r[0], img_path, os.path.basename(img_path), width_inch=2.85)
            r[1].text = desc_text
            r[1].paragraphs[0].runs[0].font.size = Pt(9.5)
            set_cell_background(r[0], LIGHT_BG)
            set_cell_padding(r[0], 80, 80, 100, 100)
            set_cell_padding(r[1], 100, 100, 120, 120)

    # ---------------------------------------------------------
    # TRANG BÌA VÀ TIÊU ĐỀ BÁO CÁO
    # ---------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top1 = p_top.add_run('DỰ ÁN ĐƯỜNG SẮT ĐÔ THỊ THÀNH PHỐ HỒ CHÍ MINH (METRO TUYẾN 2)\n')
    r_top1.font.size = Pt(11)
    r_top1.font.bold = True
    r_top1.font.color.rgb = DARK_GRAY

    r_top2 = p_top.add_run('BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN VÀ TRUNG CHUYỂN\nGA S23 – BA SA\n')
    r_top2.font.size = Pt(15)
    r_top2.font.bold = True
    r_top2.font.color.rgb = NAVY

    r_top3 = p_top.add_run('(QUY CHUẨN ĐÁP ỨNG TOÀN DIỆN MỤC A ĐẾN MỤC M - NHIỆM VỤ 9)\n(Dữ liệu thực địa bóc tách trực tiếp từ file Ga 23.xlsx)')
    r_top3.font.size = Pt(10)
    r_top3.font.italic = True
    r_top3.font.color.rgb = RGBColor(120, 120, 120)

    # ---------------------------------------------------------
    # MỤC A: THÔNG TIN CHUNG NHÀ GA
    # ---------------------------------------------------------
    add_sec_title('MỤC A. THÔNG TIN CHUNG NHÀ GA')
    tbl_a = doc.add_table(rows=5, cols=2)
    tbl_a.alignment = WD_TABLE_ALIGNMENT.CENTER
    a_data = [
        ('Mã nhà ga:', 'S23', 'Tên nhà ga:', 'Ba Sa (S23 - Ba Sa)'),
        ('Tuyến Metro:', 'Metro Tuyến 2 (Đoạn kéo dài Củ Chi)', 'Vị trí đặt ga:', 'Trên cao / Đi bằng (Trục đường Phan Văn Khải)'),
        ('Địa giới hành chính:', 'Xã Thái Mỹ & Tân An Hội, Củ Chi', 'Tọa độ GPS:', '11.000752 N, 106.437926 E'),
        ('Thời gian khảo sát:', '03/09/2026 (08:20 – 11:25)', 'Thời tiết:', 'Nắng nhẹ, khô ráo, tầm nhìn tốt'),
        ('Khảo sát viên:', 'Nguyễn Thành Vinh', 'Email ghi nhận:', 'antoniusnttvinh7325@gmail.com')
    ]
    for idx, row in enumerate(tbl_a.rows):
        d = a_data[idx]
        row.cells[0].text = f"{d[0]} {d[1]}"
        row.cells[1].text = f"{d[2]} {d[3]}"
        for c in row.cells:
            set_cell_background(c, LIGHT_BG)
            set_cell_padding(c, 80, 80, 120, 120)
            c.paragraphs[0].runs[0].font.size = Pt(9.5)

    # ---------------------------------------------------------
    # MỤC B: HIỆN TRẠNG ĐƯỜNG TIẾP CẬN GA
    # ---------------------------------------------------------
    add_sec_title('MỤC B. HIỆN TRẠNG ĐƯỜNG TIẾP CẬN GA')
    
    add_h2('1. Bản đồ GIS Mạng lưới Đường Giao thông Tiếp cận (Bán kính 1000m)')
    add_map('maps/S23_Map1_TongQuan_1000m.png', 'Hình B.1: Sơ đồ mạng lưới giao thông bán kính 200m - 500m - 1000m quanh Ga S23 Ba Sa')

    add_h2('2. Bảng Thống kê Thông số Kỹ thuật & Mặt cắt ngang các Tuyến đường tiếp cận')
    tbl_b = doc.add_table(rows=1, cols=6)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_headers = ['Mã tuyến', 'Tên tuyến đường', 'Phân loại', 'Số làn & Mặt đường', 'Lộ giới', 'Hiện trạng & Đánh giá tiếp cận']
    for i, h in enumerate(b_headers):
        cell = tbl_b.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    roads_data = [
        ('R1', 'Phan Văn Khải (QL22)', 'Đường chính', '6 làn xe (30.0 m)', '60 m', 'Trục đại lộ có dải phân cách cứng, không ùn tắc. Xe buýt, ô tô, xe máy tiếp cận rất tốt.'),
        ('R2', 'Đường Ba Sa', 'Đường thứ yếu', '2 làn xe (7.5 m)', '16 m', 'Tuyến giao cắt đấu nối khu dân cư. Tiếp cận ô tô, xe máy thuận lợi; xe buýt hạn chế.'),
        ('R3', 'Đường Số 622', 'Đường thứ yếu', '2 làn xe (7.5 m)', '16 m', 'Đường dân sinh kết nối ấp Phước Thạnh. Mặt đường bê tông nhựa tốt.'),
        ('R4', 'Đường Nguyễn Thị Nhia', 'Đường nhánh', '2 làn xe (7.5 m)', '16 m', 'Tuyến đường phân khu tiếp cận phía ấp Phước Hiệp.'),
        ('R5', 'Đường Phạm Thị Thung', 'Đường nhánh', '2 làn xe (7.5 m)', '16 m', 'Đường kết nối ấp Phước Hòa, vỉa hè tự nhiên có cây xanh.'),
        ('R6', 'Hẻm 594 Quốc lộ 22', 'Đường nhánh', '2 làn xe (6.0 m)', '12 m', 'Nhánh tiếp cận dân cư hiện hữu.')
    ]
    for rd in roads_data:
        rc = tbl_b.add_row().cells
        for col_i in range(6):
            rc[col_i].text = rd[col_i]
            rc[col_i].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_padding(rc[col_i], 60, 60, 80, 80)

    add_h2('3. Bảng Hình ảnh Minh họa Hiện trạng Tuyến đường Tiếp cận Ga S23')
    r_photos = []
    road_imgs = images_by_cat.get('road', [])
    if len(road_imgs) > 0:
        r_photos.append((road_imgs[0]['path'], f"• Tuyến: {road_imgs[0]['name']}\n• Tọa độ GPS: {road_imgs[0]['coord']}\n• Hiện trạng: Mặt đường chính rộng 30m, 6 làn xe lưu thông 2 chiều thông thoáng."))
    if len(road_imgs) > 1:
        r_photos.append((road_imgs[10]['path'] if len(road_imgs) > 10 else road_imgs[1]['path'], f"• Tuyến: Đường Ba Sa (Giao cắt Ga S23)\n• Tọa độ GPS: 10.992704, 106.448811\n• Hiện trạng: Mặt đường 7.5m, lộ giới 16m kết nối trực tiếp vào ga."))
    create_photo_table(r_photos)

    # ---------------------------------------------------------
    # MỤC C: ĐIỀU KIỆN ĐI BỘ ĐẾN GA
    # ---------------------------------------------------------
    add_sec_title('MỤC C. ĐIỀU KIỆN ĐI BỘ ĐẾN GA')
    
    add_h2('1. Bản đồ GIS Phân vùng Tiếp cận Đi bộ (Bán kính 200m & 500m)')
    add_map('maps/S23_Map2_DiBo_200m_500m.png', 'Hình C.1: Sơ đồ vùng tiếp cận đi bộ cự ly gần (≤300m) và cự ly trung bình (300m - 500m) quanh Ga S23')

    add_h2('2. Bảng Đánh giá Chất lượng Hạ tầng Đi bộ Ga S23 (Thực nghiệm Hiện trường)')
    tbl_c = doc.add_table(rows=1, cols=3)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Tiêu chí đánh giá hạ tầng đi bộ', 'Kết quả khảo sát thực tế (Thang điểm 1 - 5)']):
        cell = tbl_c.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    c_walk = [
        ('1', 'Hiện trạng vỉa hè đi bộ', 'KHÔNG CÓ VỈA HÈ (Hiện trạng đất trống tự nhiên ven đường, chưa lát gạch vỉa hè).'),
        ('2', 'Vị trí sang đường cho người đi bộ', 'KHÔNG CÓ ĐIỂM SANG ĐƯỜNG (Thiếu vạch đi bộ và đèn tín hiệu qua trục 6 làn).'),
        ('3', 'Tính liên tục của tuyến đi bộ', '3.0 / 5.0 (Trung bình) - Mặt bằng ven đường rộng nhưng chưa thành lối đi chuẩn.'),
        ('4', 'An toàn giao thông khi đi bộ', '2.7 / 5.0 (Kém) - Lưu lượng xe tải nặng trên Phan Văn Khải lớn, nguy cơ tai nạn cao.'),
        ('5', 'Tiện nghi đi bộ (Bóng mát, chiếu sáng)', '1.7 / 5.0 (Rất kém) - Thiếu mảng xanh che bóng, thiếu đèn chiếu sáng vỉa hè.'),
        ('6', 'Khả năng tiếp cận người khuyết tật (NKT)', '1.0 / 5.0 (RẤT KÉM) - Tuyệt đối không thể tiếp cận bằng xe lăn do chưa có ram dốc.'),
        ('7', 'Dễ nhận biết hướng đi đến ga', '4.3 / 5.0 (Tốt) - Trục đường thẳng, tầm nhìn thoáng đãng, dễ định vị từ xa.')
    ]
    for w in c_walk:
        rc = tbl_c.add_row().cells
        rc[0].text = w[0]
        rc[1].text = w[1]
        rc[2].text = w[2]
        for c in rc:
            set_cell_padding(c, 60, 60, 80, 80)
            c.paragraphs[0].runs[0].font.size = Pt(8.5)

    add_h2('3. Bảng Hình ảnh Minh họa Hạ tầng Đi bộ Ven Đường Ga S23')
    c_photos = []
    if len(road_imgs) > 2:
        c_photos.append((road_imgs[2]['path'], f"• Tuyến: {road_imgs[2]['name']}\n• Tọa độ GPS: {road_imgs[2]['coord']}\n• Hiện trạng: Hành lang ven đường chưa có vỉa hè lát gạch, người dân phải đi bộ sát lòng đường."))
    if len(road_imgs) > 3:
        c_photos.append((road_imgs[3]['path'], f"• Tuyến: {road_imgs[3]['name']}\n• Tọa độ GPS: {road_imgs[3]['coord']}\n• Hiện trạng: Khu vực lề đường cần được quy hoạch vỉa hè tiêu chuẩn rộng ≥3m kết nối vào cửa ga."))
    create_photo_table(c_photos)

    # ---------------------------------------------------------
    # MỤC D & E: KẾT NỐI XE BUÝT VÀ ĐIỂM PUDO
    # ---------------------------------------------------------
    add_sec_title('MỤC D & E. ĐIỀU KIỆN KẾT NỐI XE BUÝT VÀ ĐIỂM PUDO (PICK-UP / DROP-OFF)')
    
    add_h2('1. Bản đồ GIS Trạm Xe Buýt và Vị trí Quy hoạch Làn Đón trả khách PUDO')
    add_map('maps/S23_Map3_Bus_PUDO.png', 'Hình D-E.1: Sơ đồ vị trí các điểm dừng buýt Tuyến 100, 107, 70-1, 70-2 và Vịnh đón trả khách PUDO 150m')

    add_h2('2. Bảng Thống kê Chi tiết Mạng lưới Trạm Xe Buýt Lân cận Ga S23 (Mục D)')
    tbl_d = doc.add_table(rows=1, cols=6)
    tbl_d.alignment = WD_TABLE_ALIGNMENT.CENTER
    d_headers = ['Mã trạm', 'Vị trí trạm buýt', 'Cự ly ga', 'Tuyến phục vụ', 'Tần suất', 'Hiện trạng tiện ích nhà chờ']
    for i, h in enumerate(d_headers):
        cell = tbl_d.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    bus_rows = [
        ('BS-01', 'Phan Văn Khải, Ấp Phước Thạnh', '50 m', '100, 107, 70-1, 70-2', '25 phút', 'Có mái che, bảng thông tin tuyến. Đi bộ thuận tiện.'),
        ('BS-02', 'Phan Văn Khải, Ấp Phước Thạnh', '600 m', '100, 107, 70-1, 70-2', '25 phút', 'Có mái che, thông tin tuyến; chưa có vịnh dừng riêng.'),
        ('BS-03', 'Phan Văn Khải, Ấp Phước Thạnh', '700 m', '100, 107, 70-1, 70-2', '25 phút', 'Có nhà chờ, ghế ngồi, mái che, chiếu sáng. Đi bộ hạn chế.'),
        ('BS-04', 'Phan Văn Khải, Ấp Phước Hòa', '700 m', '100, 107, 70-1, 70-2', '25 phút', 'Có nhà chờ đầy đủ tiện ích, kết nối thuận tiện.'),
        ('BS-05', 'Phan Văn Khải, Ấp Phước Hòa', '900 m', '100, 107, 70-1, 70-2', '25 phút', 'Có mái che; cự ly tiếp cận đi bộ ở mức hạn chế.')
    ]
    for b in bus_rows:
        rc = tbl_d.add_row().cells
        for col_i in range(6):
            rc[col_i].text = b[col_i]
            rc[col_i].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_padding(rc[col_i], 60, 60, 80, 80)

    add_h2('3. Đánh giá Nhu cầu & Phương án Bố trí Vịnh Đón trả khách PUDO (Mục E)')
    doc.add_paragraph('• Nhu cầu phương tiện: Khảo sát thực địa ghi nhận nhu cầu Xe máy (Rất cao), Ô tô cá nhân (Cao), Xe công nghệ/Grab (Trung bình), Taxi truyền thống (Thấp).\n• Giải pháp tổ chức giao thông: Khảo sát ghi nhận lề đường Phan Văn Khải ngay trước cửa ga (khoảng cách chỉ 10m) có chiều dài sử dụng từ 100m đến 150m. Hoàn toàn đủ điều kiện khoét lề làm vịnh đón trả khách PUDO tách làn riêng biệt, tuyệt đối không làm ảnh hưởng đến dòng xe chính.')

    add_h2('4. Bảng Hình ảnh Minh họa Trạm Buýt & Vị trí Làn PUDO Đề xuất')
    d_photos = []
    bus_imgs = images_by_cat.get('bus', [])
    pudo_imgs = images_by_cat.get('pudo', [])
    if len(bus_imgs) > 6:
        d_photos.append((bus_imgs[6]['path'], f"• Điểm dừng: {bus_imgs[6]['name']}\n• Tọa độ: {bus_imgs[6]['coord']}\n• Tuyến: 100, 107, 70-1, 70-2 (Cách ga chỉ 50m)."))
    if len(pudo_imgs) > 0:
        d_photos.append((pudo_imgs[0]['path'], f"• Vị trí PUDO: Lề đường Phan Văn Khải\n• Tọa độ: {pudo_imgs[0]['coord']}\n• Chiều dài có thể sử dụng: 100m – 150m, cách cửa ga 10m."))
    create_photo_table(d_photos)

    # ---------------------------------------------------------
    # MỤC F & G: NHU CẦU BÃI ĐỖ XE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG
    # ---------------------------------------------------------
    add_sec_title('MỤC F & G. NHU CẦU BÃI ĐỖ XE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG')
    
    add_h2('1. Bản đồ GIS Quy hoạch Bãi xe Park & Ride & Điểm nóng Xung đột Giao thông')
    add_map('maps/S23_Map4_ParkRide_XungDot.png', 'Hình F-G.1: Sơ đồ vị trí 3 quỹ đất Park & Ride (1.000m² - 10.000m²) và các điểm nóng xung đột CP-01, CP-02 quanh Ga S23')

    add_h2('2. Bảng Đánh giá Tiềm năng Quỹ đất Bố trí Bãi xe Park & Ride (Mục F)')
    tbl_f = doc.add_table(rows=1, cols=6)
    tbl_f.alignment = WD_TABLE_ALIGNMENT.CENTER
    f_headers = ['Mã bãi', 'Hiện trạng sử dụng đất', 'Diện tích ước tính', 'Khoảng cách ga', 'Khả năng tiếp cận', 'Đề xuất phương án']
    for i, h in enumerate(f_headers):
        cell = tbl_f.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    pr_rows = [
        ('P&R-01', 'Đất tự nhiên / Nông nghiệp', '1,000 m²', '10 m (Sát ga)', 'Rất cao', 'Làm bãi đỗ xe máy trung chuyển giai đoạn 1 (Quy mô ~400-500 xe máy).'),
        ('P&R-02', 'Đất tự nhiên / Đất trống', '10,000 m²', '10 m (Đối diện ga)', 'Rất cao', 'Quy hoạch Trung tâm TOD kết hợp Bãi đỗ xe đa tầng cho cả ô tô và xe máy.'),
        ('P&R-03', 'Đất tự nhiên', '1,000 m²', '200 m', 'Cao', 'Quỹ đất dự phòng mở rộng bãi giữ xe hoặc dịch vụ thương mại phụ trợ.')
    ]
    for p_r in pr_rows:
        rc = tbl_f.add_row().cells
        for col_i in range(6):
            rc[col_i].text = p_r[col_i]
            rc[col_i].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_padding(rc[col_i], 60, 60, 80, 80)

    add_h2('3. Bảng Phân tích Điểm nóng Xung đột Giao thông quanh Ga S23 (Mục G)')
    tbl_g = doc.add_table(rows=1, cols=4)
    tbl_g.alignment = WD_TABLE_ALIGNMENT.CENTER
    g_headers = ['Mã điểm', 'Vị trí nút giao xung đột', 'Hình thức xung đột', 'Mức độ rủi ro & Nguy cơ']
    for i, h in enumerate(g_headers):
        cell = tbl_g.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    cf_rows = [
        ('CP-01', 'Giao lộ Phan Văn Khải - Đường Ấp Phước Thạnh', 'Xe rẽ trái/phải, nhập dòng, tách dòng, sang đường cắt luồng tốc độ cao', 'Mức độ: TRUNG BÌNH | Nguy cơ tai nạn: TRUNG BÌNH'),
        ('CP-02', 'Giao lộ Phan Văn Khải - Ấp Phước Hòa', 'Xe máy lưu thông trên lề/vỉa hè xung đột với xe cơ giới nhập dòng', 'Mức độ: TRUNG BÌNH | Nguy cơ tai nạn: TRUNG BÌNH'),
        ('CP-03', 'Giao lộ Phan Văn Khải - Ấp Phước Hiệp (Nút Ba Sa)', 'Giao cắt giữa đường Ba Sa 2 làn xe với đại lộ Phan Văn Khải 6 làn xe', 'Mức độ: TRUNG BÌNH | Nguy cơ tai nạn: TRUNG BÌNH')
    ]
    for c_r in cf_rows:
        rc = tbl_g.add_row().cells
        for col_i in range(4):
            rc[col_i].text = c_r[col_i]
            rc[col_i].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_padding(rc[col_i], 60, 60, 80, 80)

    add_h2('4. Bảng Hình ảnh Minh họa Quỹ đất Park & Ride & Điểm nóng Xung đột')
    fg_photos = []
    pr_imgs = images_by_cat.get('parkride', [])
    cf_imgs = images_by_cat.get('conflict', [])
    if len(pr_imgs) > 1:
        fg_photos.append((pr_imgs[1]['path'], f"• Vị trí: {pr_imgs[1]['desc']}\n• Tọa độ: {pr_imgs[1]['coord']}\n• Đánh giá: Quỹ đất 10,000m² cực kỳ lý tưởng để phát triển TOD & bãi xe P&R."))
    if len(cf_imgs) > 0:
        fg_photos.append((cf_imgs[0]['path'], f"• Vị trí xung đột: {cf_imgs[0]['name']}\n• Tọa độ: {cf_imgs[0]['coord']}\n• Nguy cơ: Điểm giao lộ đường nhánh liên ấp đấu nối trục Phan Văn Khải."))
    create_photo_table(fg_photos)

    # ---------------------------------------------------------
    # MỤC H, I & J: KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN & OAS SCORECARD
    # ---------------------------------------------------------
    add_sec_title('MỤC H, I & J. KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN VÀ OAS SCORECARD')
    
    add_h2('1. Bản đồ GIS Ma trận Rào cản Tiếp cận Ga S23')
    add_map('maps/S23_Map5_RaoCan_TongHop.png', 'Hình H-I-J.1: Bản đồ định vị các rào cản đi bộ, điểm sang đường nguy hiểm và trở ngại đối với người khuyết tật')

    add_h2('2. Đánh giá Khả năng Bố trí Không gian Trung chuyển Đa phương thức (Mục H)')
    doc.add_paragraph('• So với các ga nội đô lịch sử, Ga S23 (Ba Sa) sở hữu lợi thế chiến lược vượt trội về quỹ đất phụ cận. Với mặt tiền lộ giới 60m và quỹ đất nông nghiệp liền kề rộng lớn, nhà ga hoàn toàn có thể xây dựng Trung tâm Trung chuyển Hành khách Cửa ngõ Tây Bắc, kết hợp trọn vẹn: Sảnh ga Metro + Bãi đỗ Park & Ride 10.000 m² + Trạm đón trả khách PUDO 150m + Bến xe buýt gom Feeder Bus.')

    add_h2('3. Bảng Tổng hợp Thẻ điểm OAS Đánh giá Toàn diện Ga S23 (Mục J)')
    tbl_j = doc.add_table(rows=1, cols=3)
    tbl_j.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Nhóm tiêu chí đánh giá tiếp cận & trung chuyển', 'Điểm số khảo sát thực tế (Thang điểm 1 - 5)']):
        cell = tbl_j.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        set_cell_padding(cell, 100, 100, 120, 120)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9)

    j_scores = [
        ('1', 'Khả năng tiếp cận bằng đường bộ (Mục B)', '3.67 / 5.0 (Khá - Mặt đường 30m, 6 làn lưu thông thông suốt)'),
        ('2', 'Điều kiện đi bộ đến ga (Mục C)', '2.67 / 5.0 (Trung bình - Chưa có vỉa hè kiên cố lát gạch)'),
        ('3', 'Kết nối mạng lưới xe buýt (Mục D)', '4.00 / 5.0 (Tốt - Có 4 tuyến buýt chạy liên tục, trạm cách 50m)'),
        ('4', 'Khả năng tổ chức làn đón trả khách PUDO (Mục E)', '4.67 / 5.0 (Rất tốt - Lề đường rộng 150m, tách làn an toàn)'),
        ('5', 'Khả năng bố trí bãi xe Park & Ride (Mục F)', '4.67 / 5.0 (Rất tốt - Quỹ đất tự nhiên liền kề lên đến 10,000m²)'),
        ('6', 'An toàn giao thông quanh khu vực ga (Mục G)', '3.67 / 5.0 (Khá - Không ùn tắc, nhưng cần kiểm soát tốc độ)'),
        ('7', 'Khả năng tổ chức không gian trung chuyển (Mục H)', '4.00 / 5.0 (Tốt - Đủ diện tích để quy hoạch trung tâm hiện đại)'),
        ('8', 'Khả năng tiếp cận cho người già & người khuyết tật (Mục I)', '1.00 / 5.0 (RẤT KÉM - Điểm nghẽn lớn nhất, chưa có ram dốc)'),
        ('TOTAL', 'ĐIỂM TỔNG HỢP OAS TOÀN DIỆN KHU VỰC GA S23', '3.55 / 5.0 — XẾP LOẠI B (MỨC KHÁ)')
    ]
    for s_idx, s in enumerate(j_scores):
        rc = tbl_j.add_row().cells
        rc[0].text = s[0]
        rc[1].text = s[1]
        rc[2].text = s[2]
        is_total = (s_idx == len(j_scores) - 1)
        for c in rc:
            if is_total:
                set_cell_background(c, 'E3F2FD')
                c.paragraphs[0].runs[0].font.bold = True
                c.paragraphs[0].runs[0].font.color.rgb = NAVY
            set_cell_padding(c, 70, 70, 90, 90)
            c.paragraphs[0].runs[0].font.size = Pt(8.5)

    # ---------------------------------------------------------
    # MỤC K: ĐỀ XUẤT CẢI THIỆN GA S23
    # ---------------------------------------------------------
    add_sec_title('MỤC K. ĐỀ XUẤT CẢI THIỆN VÀ GIẢI PHÁP KỸ THUẬT')
    
    add_h2('1. Ưu tiên 1 - Xử lý cấp bách (Trước khi đưa vào vận hành khai thác)')
    doc.add_paragraph('• Xây dựng vỉa hè tiêu chuẩn: Đầu tư xây dựng vỉa hè rộng tối thiểu 3.0m dọc hai bên trục Phan Văn Khải trong phạm vi bán kính 500m quanh ga, hoàn thiện gạch dẫn hướng và ram dốc cho người khuyết tật.\n• Tổ chức sang đường an toàn: Bắt buộc xây dựng Cầu vượt bộ hành kết nối trực tiếp vào sảnh ga S23 qua trục đại lộ 6 làn xe; hoặc bổ sung nút đèn tín hiệu đi bộ có nút bấm ưu tiên và đảo trú chân giữa dải phân cách.')

    add_h2('2. Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm)')
    doc.add_paragraph('• Xây dựng Vịnh đón trả khách PUDO: Khoét lề đường Phan Văn Khải để tạo làn tách riêng dài 150m cho Taxi, Grab và xe ô tô/xe máy đón trả người nhà.\n• Đầu tư Bãi đỗ xe Park & Ride giai đoạn 1: Khai thác khu đất 1,000 m² sát ga làm bãi đỗ xe máy có mái che, bố trí trạm sạc xe máy điện công cộng.\n• Nâng cấp hạ tầng xe buýt: Bổ sung vịnh dừng xe buýt đạt chuẩn cho trạm cách ga 50m (Tuyến 100, 107, 70-1, 70-2) để tránh xung đột với làn xe cơ giới.')

    add_h2('3. Ưu tiên 3 - Dài hạn & Định hướng Phát triển TOD')
    doc.add_paragraph('• Quy hoạch Trung tâm TOD Củ Chi: Tích hợp khu đất tự nhiên 10,000 m² đối diện ga thành Trung tâm TOD đa chức năng (Bãi đỗ xe cao tầng thông minh, trạm chuyển tiếp xe buýt liên tỉnh TP.HCM - Tây Ninh, khu thương mại dịch vụ tiện ích).\n• Mở các tuyến buýt gom (Feeder Bus / Minibus): Kết nối xuyên suốt từ trung tâm Huyện Củ Chi, Xã Thái Mỹ, Tân An Hội và các khu công nghiệp lân cận dồn khách về Ga S23.')

    # ---------------------------------------------------------
    # MỤC L & M: HỒ SƠ ẢNH VÀ XÁC NHẬN KHẢO SÁT
    # ---------------------------------------------------------
    doc.add_page_break()
    add_sec_title('MỤC L & M. HỒ SƠ ẢNH VÀ BIÊN BẢN XÁC NHẬN KHẢO SÁT THỰC ĐỊA')
    
    add_h2('1. Danh mục Hồ sơ Ảnh Hiện trường và Bản đồ Số hóa (Mục L)')
    doc.add_paragraph('• Hệ thống 5 bản đồ GIS số hóa độ phân giải cao tỷ lệ 1:10,000 (Tổng quan, Đi bộ, Xe buýt, Bãi xe, Rào cản).\n• Bộ 42 file ảnh chụp thực địa có tọa độ GPS định vị chính xác đã được lưu trữ trong thư mục /s23/.')

    add_h2('2. Biên bản Xác nhận Kết quả Khảo sát Thực địa (Mục M)')
    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign.rows[0].cells[0].text = 'ĐẠI DIỆN ĐỘI KHẢO SÁT THỰC ĐỊA (MỤC M.1)\n(Ký, ghi rõ họ tên và đóng dấu)'
    tbl_sign.rows[0].cells[1].text = 'ĐẠI DIỆN ĐƠN VỊ KIỂM TRA & PHÊ DUYỆT (MỤC M.2)\n(Ký, ghi rõ họ tên và đóng dấu)'
    for c in tbl_sign.rows[0].cells:
        set_cell_background(c, HEADER_BG)
        set_cell_padding(c, 100, 100, 120, 120)
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9.5)

    tbl_sign.rows[1].cells[0].text = '\n\n\nKhảo sát viên: Nguyễn Thành Vinh\nEmail: antoniusnttvinh7325@gmail.com\nNgày khảo sát: 03/09/2026'
    tbl_sign.rows[1].cells[1].text = '\n\n\nNgười kiểm tra: ....................................................\nChức vụ: Trưởng bộ phận Thẩm định Dự án\nNgày phê duyệt: ....../....../2026'
    for c in tbl_sign.rows[1].cells:
        set_cell_background(c, LIGHT_BG)
        set_cell_padding(c, 100, 100, 120, 120)
        c.paragraphs[0].runs[0].font.size = Pt(9.5)

    out_file = 'BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_HoanChinh.docx'
    doc.save(out_file)
    print(f"\n[+] THÀNH CÔNG! Đã xuất Báo cáo Word hoàn chỉnh tại: {out_file}")
    try:
        doc.save('BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_FULL_A_TO_M.docx')
        print(f"[+] Đã đồng bộ thêm vào tệp: BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_FULL_A_TO_M.docx")
    except Exception:
        print("[!] Tệp BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_FULL_A_TO_M.docx đang được mở trong Word, đã lưu thành công bản mới nhất vào BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_HoanChinh.docx")

if __name__ == '__main__':
    build_s23_report()
