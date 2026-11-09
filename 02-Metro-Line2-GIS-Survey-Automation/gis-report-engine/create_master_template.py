import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_master_template():
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
    BORDER_COLOR = 'D3D3D3'

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

    def create_photo_table(rows_count, photo_tags):
        """Tạo bảng chứa hình ảnh minh họa cho riêng từng mục"""
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header
        hdr = tbl.rows[0].cells
        hdr[0].text = "Khung Hình ảnh Thực địa (Tag Placeholder)"
        hdr[1].text = "Mô tả Chi tiết & Tọa độ GPS"
        set_cell_background(hdr[0], HEADER_BG)
        set_cell_background(hdr[1], HEADER_BG)
        hdr[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[0].paragraphs[0].runs[0].font.bold = True
        hdr[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        hdr[1].paragraphs[0].runs[0].font.bold = True

        for tag, desc in photo_tags:
            r = tbl.add_row().cells
            r[0].text = tag
            r[1].text = desc
            set_cell_background(r[0], LIGHT_BG)

    # ---------------------------------------------------------
    # TRANG BÌA & THÔNG TIN CHUNG
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run('DỰ ÁN ĐƯỜNG SẮT ĐÔ THỊ THÀNH PHỐ HỒ CHÍ MINH\n')
    r_sub.font.size = Pt(11)
    r_sub.font.bold = True
    r_sub.font.color.rgb = DARK_GRAY

    r_main = p_title.add_run('BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN VÀ TRUNG CHUYỂN\nGA {{ MA_GA }} – {{ TEN_GA_UPPER }}')
    r_main.font.size = Pt(15)
    r_main.font.bold = True
    r_main.font.color.rgb = NAVY

    tbl_info = doc.add_table(rows=4, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ('Mã nhà ga:', '{{ MA_GA }}', 'Tên nhà ga:', '{{ TEN_GA }}'),
        ('Vị trí nút giao:', '{{ VI_TRI_NUT_GIAO }}', 'Tọa độ GPS:', '{{ TOA_DO_GPS }}'),
        ('Ngày khảo sát:', '{{ NGAY_KHAO_SAT }}', 'Thời tiết:', '{{ THOI_TIET }}'),
        ('Khảo sát viên:', '{{ KHAO_SAT_VIEN }}', 'Đơn vị thực hiện:', '{{ DON_VI_THUC_HIEN }}')
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
    
    add_h2('1. Bản đồ Tổng Phân vùng (Bán kính 200m & Bán kính 1000m)')
    p_map1 = doc.add_paragraph()
    p_map1.add_run('{{ BANDO_TONG_CHIPHI_200M_1000M }}').bold = True
    
    add_h2('2. Phiếu / Bảng Tổng hợp Thông số Mặt cắt ngang Đường tiếp cận')
    tbl_r = doc.add_table(rows=1, cols=6)
    tbl_r.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ['Mã tuyến', 'Tên đường', 'Lòng đường (m)', 'Vỉa hè trái (m)', 'Vỉa hè phải (m)', 'Ghi chú hiện trạng']
    for i, h in enumerate(headers):
        cell = tbl_r.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    for r_idx in range(4):
        rc = tbl_r.add_row().cells
        rc[0].text = f'{{{{ MA_DUONG_{r_idx+1} }}}}'
        rc[1].text = f'{{{{ TEN_DUONG_{r_idx+1} }}}}'
        rc[2].text = f'{{{{ LONG_DUONG_{r_idx+1} }}}}'
        rc[3].text = f'{{{{ VIA_HE_TRAI_{r_idx+1} }}}}'
        rc[4].text = f'{{{{ VIA_HE_PHAI_{r_idx+1} }}}}'
        rc[5].text = f'{{{{ GHI_CHU_DUONG_{r_idx+1} }}}}'

    add_h2('3. Bảng Hình ảnh Minh họa Đường tiếp cận & Cửa ga')
    create_photo_table(2, [
        ('{{ IMG_ROAD_MAIN }}', 'Ảnh mặt cắt lòng đường & vỉa hè trục chính (Bán kính 200m)'),
        ('{{ IMG_EXIT_LOCATION }}', 'Vị trí dự kiến đặt Cửa lên xuống nhà ga Exit A / Exit B')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 2: HIỆN TRẠNG ĐIỀU KIỆN ĐI BỘ VÀ CỬA GA
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 2: HIỆN TRẠNG ĐIỀU KIỆN ĐI BỘ VÀ CỬA GA')
    
    add_h2('1. Bản đồ Phân vùng Đi bộ (Lõi 200m & Hành lang 1000m)')
    doc.add_paragraph('{{ BANDO_DIBO_200M_1000M }}')
    
    add_h2('2. Phiếu / Bảng Tổng hợp Đánh giá Chất lượng Đi bộ')
    tbl_walk = doc.add_table(rows=1, cols=3)
    tbl_walk.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['STT', 'Tiêu chí đánh giá đi bộ', 'Điểm (1-5) & Ghi nhận thực địa']):
        cell = tbl_walk.rows[0].cells[i]
        cell.text = h
        set_cell_background(cell, HEADER_BG)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.bold = True

    for w_idx in range(6):
        rc = tbl_walk.add_row().cells
        rc[0].text = str(w_idx+1)
        rc[1].text = f'{{{{ TIEU_CHI_WALK_{w_idx+1} }}}}'
        rc[2].text = f'{{{{ DIEM_WALK_{w_idx+1} }}}}'

    add_h2('3. Bảng Hình ảnh Minh họa Hạ tầng Đi bộ & Lối sang đường')
    create_photo_table(2, [
        ('{{ IMG_SIDEWALK_STATUS }}', 'Hiện trạng chất lượng vỉa hè & chướng ngại vật đi bộ'),
        ('{{ IMG_CROSSING_POINT }}', 'Vị trí vạch sơn sang đường & nút đèn tín hiệu đi bộ')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 3: KẾT NỐI XE BUÝT VÀ ĐÓN TRẢ KHÁCH (PUDO)
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 3: KẾT NỐI XE BUÝT VÀ ĐÓ N TRẢ KHÁCH (PUDO)')
    
    add_h2('1. Bản đồ Mạng lưới Trạm Buýt & Tuyến Gom (Bán kính 200m & 1000m)')
    doc.add_paragraph('{{ BANDO_BUS_PUDO_200M_1000M }}')
    
    add_h2('2. Phiếu / Bảng Tổng hợp Hiện trạng Trạm Buýt & Điểm PUDO')
    doc.add_paragraph('{{ BANG_TONG_HOP_BUS_VA_PUDO }}')

    add_h2('3. Bảng Hình ảnh Minh họa Trạm Buýt & Vị trí Làn PUDO')
    create_photo_table(2, [
        ('{{ IMG_BUS_STOP }}', 'Hiện trạng trạm dừng xe buýt gần cửa ga'),
        ('{{ IMG_PUDO_LOCATION }}', 'Vị trí lề đường/đường gom đề xuất bố trí làn PUDO / Kiss & Ride')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 4: NGUYÊN TẮC BÃI GIỮ XE VÀ XUNG ĐỘT GIAO THÔNG
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 4: NGUYÊN TẮC BÃI GIỮ XE VÀ XUNG ĐỘT GIAO THÔNG')
    
    add_h2('1. Bản đồ Bãi giữ xe & Điểm nóng Xung đột (Bán kính 200m & 1000m)')
    doc.add_paragraph('{{ BANDO_PARK_CONFLICT_200M_1000M }}')
    
    add_h2('2. Phiếu / Bảng Tổng hợp Đánh giá Bãi xe & Điểm Xung đột')
    doc.add_paragraph('{{ BANG_TONG_HOP_PARK_VA_XUNG_DOT }}')

    add_h2('3. Bảng Hình ảnh Minh họa Bãi xe Park & Ride & Kẹt xe')
    create_photo_table(2, [
        ('{{ IMG_PARK_RIDE }}', 'Vị trí đất trống / bãi đỗ xe trung chuyển Park & Ride'),
        ('{{ IMG_TRAFFIC_CONFLICT }}', 'Ảnh điểm nóng xung đột & ùn tắc giao thông giờ cao điểm')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 5: RÀO CẢN TIẾP CẬN VÀ ĐÁNH GIÁ TỔNG HỢP KHU VỰC
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 5: RÀO CẢN TIẾP CẬN VÀ ĐÁNH GIÁ TỔNG HỢP KHU VỰC')
    
    add_h2('1. Bản đồ Tổng hợp Rào cản Tiếp cận (Bán kính 200m & 1000m)')
    doc.add_paragraph('{{ BANDO_RAOCAN_TONGHOP_200M_1000M }}')
    
    add_h2('2. Phiếu / Bảng Ma trận 16 Rào cản & Scorecard Điểm OAS')
    doc.add_paragraph('{{ BANG_MA_TRAN_16_RAO_CAN_VA_DIEM_OAS }}')

    add_h2('3. Bảng Hình ảnh Minh họa Top Rào cản Trọng yếu')
    create_photo_table(3, [
        ('{{ IMG_BARRIER_1 }}', 'Rào cản 1: Hàng rong / Chợ tự phát lấn chiếm vỉa hè'),
        ('{{ IMG_BARRIER_2 }}', 'Rào cản 2: Dây điện / cáp viễn thông treo thấp sà xuống đường'),
        ('{{ IMG_BARRIER_3 }}', 'Rào cản 3: Vỉa hè bị đứt đoạn / Cản trở tiếp cận cho người khuyết tật')
    ])

    # ---------------------------------------------------------
    # CHƯƠNG 6: KHUNG ĐỀ XUẤT VÀ GIẢI PHÁP CẢI THIỆN
    # ---------------------------------------------------------
    add_h1('CHƯƠNG 6: KHUNG ĐỀ XUẤT VÀ GIẢI PHÁP CẢI THIỆN')
    add_h2('1. Ưu tiên 1 - Xử lý ngay')
    doc.add_paragraph('{{ DE_XUAT_UU_TIEN_1 }}')

    add_h2('2. Ưu tiên 2 - Ngắn hạn (1 - 2 năm)')
    doc.add_paragraph('{{ DE_XUAT_UU_TIEN_2 }}')

    add_h2('3. Ưu tiên 3 - Dài hạn & Quy hoạch TOD (Bán kính 1000m)')
    doc.add_paragraph('{{ DE_XUAT_UU_TIEN_3 }}')

    # ---------------------------------------------------------
    # PHỤ LỤC & NGHIỆM THU
    # ---------------------------------------------------------
    doc.add_page_break()
    add_h1('PHỤ LỤC: XÁC NHẬN KHẢO SÁT THỰC ĐỊA')
    
    tbl_sign = doc.add_table(rows=2, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign.rows[0].cells[0].text = 'ĐẠI DIỆN ĐỘI KHẢO SÁT\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[0].cells[1].text = 'NGƯỜI KIỂM TRA & DUYỆT BÁO CÁO\n(Ký và ghi rõ họ tên)'
    tbl_sign.rows[1].cells[0].text = '\n\nHọ tên: {{ KHAO_SAT_VIEN }}\nNgày: {{ NGAY_LAP }}'
    tbl_sign.rows[1].cells[1].text = '\n\nHọ tên: {{ NGUOI_DUYET }}\nNgày: {{ NGAY_DUYET }}'

    output_path = 'Template_BaoCao_KhaoSat_Metro.docx'
    doc.save(output_path)

if __name__ == '__main__':
    create_master_template()
