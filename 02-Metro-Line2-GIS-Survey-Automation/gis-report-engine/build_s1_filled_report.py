import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def generate_s1_report():
    doc = docx.Document()

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styling Colors
    NAVY = RGBColor(0, 51, 102)      # #003366 (Chủ đạo)
    DARK_GRAY = RGBColor(51, 51, 51)
    LIGHT_BG = 'F4F6F9'
    HEADER_BG = '003366'

    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def add_h1(text):
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

    def create_photo_table(photo_data):
        """Tạo bảng chứa hình ảnh minh họa cho từng mục"""
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        hdr = tbl.rows[0].cells
        hdr[0].text = "Khung Hình ảnh Thực địa (Ảnh đính kèm)"
        hdr[1].text = "Mô tả Chi tiết & Tọa độ GPS"
        set_cell_background(hdr[0], HEADER_BG)
        set_cell_background(hdr[1], HEADER_BG)
        hdr[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[0].paragraphs[0].runs[0].font.bold = True
        hdr[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[1].paragraphs[0].runs[0].font.bold = True

        for tag, desc in photo_data:
            r = tbl.add_row().cells
            r[0].text = f"[{tag}]\n(Hình ảnh thực địa)"
            r[1].text = desc
            set_cell_background(r[0], LIGHT_BG)

    # ---------------------------------------------------------
    # TRANG BÌA & THÔNG TIN CHUNG
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run('DỰ ÁN ĐƯỜNG SẮT ĐÔ THỊ THÀNH PHỐ HỒ CHÍ MINH (METRO TUYẾN 2)\n')
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = DARK_GRAY

    r_main = p_title.add_run('BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN VÀ TRUNG CHUYỂN\nGA S1 – PHAN VĂN HỚN')
    r_main.font.size = Pt(15)
    r_main.font.bold = True
    r_main.font.color.rgb = NAVY

    tbl_info = doc.add_table(rows=4, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ('Mã nhà ga:', 'S1', 'Tên nhà ga:', 'Phan Văn Hớn'),
        ('Vị trí nút giao:', 'Nút giao QL22 & Đường Phan Văn Hớn, Q.12', 'Tọa độ GPS:', '10.836068 N, 106.618255 E'),
        ('Ngày khảo sát:', '01/09/2026', 'Thời tiết:', 'Nắng nhẹ, khô ráo'),
        ('Khảo sát viên:', 'Nguyễn Văn A (Đội trưởng)', 'Đơn vị thực hiện:', 'Đội Khảo sát Kỹ thuật Metro 2')
    ]
    for idx, row in enumerate(tbl_info.rows):
        d = info_data[idx]
        row.cells[0].text = f'{d[0]} {d[1]}'
        row.cells[1].text = f'{d[2]} {d[3]}'
        set_cell_background(row.cells[0], LIGHT_BG)
        set_cell_background(row.cells[1], LIGHT_BG)

    # ---------------------------------------------------------
    # CHƯƠNG 1: TỔNG QUAN VỊ TRÍ & MẠNG LƯỚI ĐƯỜNG TIẾP CẬN
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 1: TỔNG QUAN VỊ TRÍ & MẠNG LƯỚI ĐƯỜNG TIẾP CẬN')
    
    add_h2('1. Bản đồ Phân vùng Khảo sát Ga S1 (Bán kính 200m & 1000m)')
    p_map1 = doc.add_paragraph()
    p_map1.add_run('[BẢN ĐỒ GIS VỆ TINH GA S1 - KHOANH VÙNG LÕI 200M VÀ HÀNH LANG 1000M]').bold = True
    
    add_h2('2. Bảng Tổng hợp Thông số Mặt cắt ngang Đường tiếp cận')
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
    create_photo_table([
        ('IMG_S1_ROAD_MAIN', 'Ảnh mặt cắt ngang lòng đường QL22 & vỉa hè rộng 4.5m trước vị trí ga S1 (GPS: 10.8361 N, 106.6183 E)'),
        ('IMG_S1_EXIT_LOCATION', 'Khu vực vỉa hè dự kiến đặt Cửa lên xuống Exit A (Phía QL22 hướng đi An Sương)')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 2: HIỆN TRẠNG ĐIỀU KIỆN ĐI BỘ VÀ CỬA GA
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 2: HIỆN TRẠNG ĐIỀU KIỆN ĐI BỘ VÀ CỬA GA')
    
    add_h2('1. Bản đồ Phân vùng Đi bộ Ga S1 (Lõi 200m & Hành lang 1000m)')
    doc.add_paragraph('[BẢN ĐỒ GIS PHÂN VÙNG TIẾP CẬN ĐI BỘ 200M VÀ KẾT NỐI KHU DÂN CƯ 1000M]')
    
    add_h2('2. Bảng Đánh giá Chất lượng Đi bộ Ga S1')
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
    create_photo_table([
        ('IMG_S1_SIDEWALK', 'Hiện trạng vỉa hè đường Phan Văn Hớn bị lấn chiếm buôn bán (GPS: 10.8359 N, 106.6181 E)'),
        ('IMG_S1_CROSSING', 'Vạch sang đường cho người đi bộ tại nút giao QL22 - Phan Văn Hớn')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 3: KẾT NỐI XE BUÝT VÀ ĐÓ N TRẢ KHÁCH (PUDO)
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 3: KẾT NỐI XE BUÝT VÀ ĐÓ N TRẢ KHÁCH (PUDO)')
    
    add_h2('1. Bản đồ Mạng lưới Trạm Buýt & Làn PUDO (Bán kính 200m & 1000m)')
    doc.add_paragraph('[BẢN ĐỒ ĐỊNH VỊ CÁC TRẠM BUÝT VÀ ĐIỂM ĐÓN TRẢ KHÁCH PUDO GA S1]')
    
    add_h2('2. Bảng Tổng hợp Mạng lưới Trạm Xe buýt Trung chuyển')
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

    add_h2('3. Bảng Hình ảnh Minh họa Trạm Buýt & Vị trí Làn PUDO')
    create_photo_table([
        ('IMG_S1_BUS_STOP', 'Trạm buýt BS-01 trên QL22 cách cửa ga S1 60m đi bộ (GPS: 10.8362 N, 106.6184 E)'),
        ('IMG_S1_PUDO', 'Khu vực đường Song Hành QL22 đề xuất bố trí làn đón trả khách Kiss & Ride (dài 45m)')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 4: NGUYÊN TẮC BÃI GIỮ XE VÀ XUNG ĐỘT GIAO THÔNG
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 4: NGUYÊN TẮC BÃI GIỮ XE VÀ XUNG ĐỘT GIAO THÔNG')
    
    add_h2('1. Bản đồ Bãi giữ xe Park & Ride & Điểm xung đột (Bán kính 200m & 1000m)')
    doc.add_paragraph('[BẢN ĐỒ ĐỊNH VỊ BÃI XE PARK & RIDE VÀ CÁC ĐIỂM NÓNG ÙN TẮC GIAO THÔNG]')
    
    add_h2('2. Bảng Đánh giá Điểm nóng Xung đột Giao thông Ga S1')
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

    add_h2('3. Bảng Hình ảnh Minh họa Bãi xe Park & Ride & Kẹt xe')
    create_photo_table([
        ('IMG_S1_PARK_RIDE', 'Khu đất trống 1,200m2 tại góc Phan Văn Hớn - Tân Thới Nhất 17 đề xuất làm bãi xe Park & Ride'),
        ('IMG_S1_TRAFFIC_JAM', 'Ùn tắc giao thông cục bộ tại nút giao QL22 - Phan Văn Hớn giờ cao điểm chiều')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 5: RÀO CẢN TIẾP CẬN VÀ ĐÁNH GIÁ TỔNG HỢP KHU VỰC
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 5: RÀO CẢN TIẾP CẬN VÀ ĐÁNH GIÁ TỔNG HỢP KHU VỰC')
    
    add_h2('1. Bản đồ Tổng hợp Rào cản Tiếp cận Ga S1 (Bán kính 200m & 1000m)')
    doc.add_paragraph('[BẢN ĐỒ TỔNG HỢP MA TRẬN 16 RÀO CẢN TIẾP CẬN QUANH GA S1]')
    
    add_h2('2. Bảng Tổng hợp Điểm Đánh giá Khả năng Tiếp cận Ga (OAS Scorecard)')
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
        ('1', 'Khả năng tiếp cận bằng đường bộ', '3.5 / 5 - Khá'),
        ('2', 'Điều kiện đi bộ đến ga', '2.0 / 5 - Kém'),
        ('3', 'Kết nối mạng lưới xe buýt', '3.5 / 5 - Khá'),
        ('4', 'Tổ chức điểm đón trả khách (PUDO)', '3.0 / 5 - Trung bình'),
        ('5', 'Bố trí bãi xe trung chuyển (Park & Ride)', '3.0 / 5 - Trung bình'),
        ('6', 'An toàn giao thông quanh ga', '2.0 / 5 - Kém'),
        ('7', 'Tổ chức không gian trung chuyển tổng hợp', '3.0 / 5 - Trung bình'),
        ('8', 'Khả năng tiếp cận cho người khuyết tật (NKT)', '1.5 / 5 - Rất kém'),
        ('TOTAL', 'TỔNG THỂ KHẢ NĂNG TIẾP CẬN GA (OAS)', '2.81 / 5.0 - TRUNG BÌNH (LOẠI C)')
    ]
    for o_row in oas_data:
        rc = tbl_oas.add_row().cells
        rc[0].text = o_row[0]
        rc[1].text = o_row[1]
        rc[2].text = o_row[2]

    add_h2('3. Bảng Hình ảnh Minh họa Top Rào cản Trọng yếu Ga S1')
    create_photo_table([
        ('IMG_S1_BARRIER_1', 'Rào cản 1: Hàng rong, chợ tự phát lấn chiếm hoàn toàn vỉa hè đường Phan Văn Hớn'),
        ('IMG_S1_BARRIER_2', 'Rào cản 2: Mạng lưới dây điện & cáp viễn thông treo thấp sà xuống lối đi bộ'),
        ('IMG_S1_BARRIER_3', 'Rào cản 3: Vỉa hè chênh cao, thiếu dốc ram gây rào cản lớn cho người khuyết tật')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 6: KHUNG ĐỀ XUẤT VÀ GIẢI PHÁP CẢI THIỆN
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 6: KHUNG ĐỀ XUẤT VÀ GIẢI PHÁP CẢI THIỆN GA S1')
    
    add_h2('1. Ưu tiên 1 - Xử lý ngay (Giai đoạn chuẩn bị vận hành)')
    doc.add_paragraph('• Giải tỏa buôn bán lấn chiếm trên đường Phan Văn Hớn (đoạn 150m từ QL22).\n• Điều chỉnh thời gian đèn xanh đi bộ tại nút QL22 từ 15s lên 25s; xây đảo trú chân giữa dải phân cách.')

    add_h2('2. Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm)')
    doc.add_paragraph('• Xây cầu vượt đi bộ nối Cửa ga S1 qua QL22 đến trạm xe buýt BS-02.\n• Cải tạo đường Song Hành QL22 thành làn 1 chiều kết hợp vịnh đón trả khách PUDO dài 45m.')

    add_h2('3. Ưu tiên 3 - Dài hạn & Quy hoạch TOD (Bán kính 1000m)')
    doc.add_paragraph('• Thu hồi/thuê khu đất 1,200m2 tại góc Phan Văn Hớn - Tân Thới Nhất 17 làm bãi xe Park & Ride.\n• Mở mới tuyến buýt gom Minibus kết nối khu dân cư Bà Điểm / Hóc Môn trực tiếp về Ga S1.')

    # ---------------------------------------------------------
    # PHỤ LỤC & NGHIỆM THU
    # ---------------------------------------------------------
    doc.add_page_break()
    add_h1('PHỤ LỤC: XÁC NHẬN KHẢO SÁT THỰC ĐỊA GA S1')
    
    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign.rows[0].cells[0].text = 'ĐẠI DIỆN ĐỘI KHẢO SÁT\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[0].cells[1].text = 'NGƯỜI KIỂM TRA & DUYỆT BÁO CÁO\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[1].cells[0].text = '\n\nHọ tên: Nguyễn Văn A\nNgày: 01/09/2026'
    tbl_sign.rows[1].cells[1].text = '\n\nHọ tên: Trần Văn B\nNgày: 02/09/2026'

    output_path = 'BaoCao_KhaoSat_ThucDia_Ga_S1_PhanVanHon.docx'
    doc.save(output_path)

if __name__ == '__main__':
    generate_s1_report()
