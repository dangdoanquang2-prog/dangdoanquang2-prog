import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os

def set_cell_background(cell, fill_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def format_table_no_split(table, caption_paragraph=None, source_paragraph=None):
    if caption_paragraph:
        caption_paragraph.paragraph_format.keep_with_next = True
        
    if len(table.rows) > 0:
        trPr0 = table.rows[0]._tr.get_or_add_trPr()
        trPr0.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def create_appendix_full_citation_report(output_filename="BAO_CAO_HOAN_CHINH_FULL_PHU_LUC_TRICH_DAN_DAY_DU.docx"):
    doc = docx.Document()

    # Configure Margins (A4: Top 2.0cm, Bottom 2.0cm, Left 2.5cm, Right 2.0cm)
    for section in doc.sections:
        section.page_width = Cm(21.59)
        section.page_height = Cm(27.94)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.0)

    # Base Normal Style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.3
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def add_p(text, indent=True):
        p = doc.add_paragraph(text)
        if indent:
            p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.3
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(15)
        r.bold = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13.5)
        r.bold = True
        return p

    # 1. COVER PAGE
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH")
    r1.font.size = Pt(13)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("VIỆN ĐÀO TẠO VÀ HỢP TÁC QUỐC TẾ")
    r2.font.size = Pt(14)
    r2.bold = True

    if os.path.exists("uth_logo.jpeg"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_logo = p_logo.add_run()
        r_logo.add_picture("uth_logo.jpeg", width=Cm(5.2))

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run("BÁO CÁO\nHỌC KỲ DOANH NGHIỆP")
    r3.font.size = Pt(28)
    r3.bold = True

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run("ỨNG DỤNG MÔ HÌNH LEAN WAREHOUSE NHẰM GIẢM THIỂU LÃNG PHÍ VÀ LỖI THAO TÁC TRONG QUY TRÌNH NHẬP KHO NGOẠI QUAN TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I")
    r4.font.size = Pt(18)
    r4.bold = True

    p5 = doc.add_paragraph()
    p5.paragraph_format.left_indent = Cm(3.0)
    r_gv = p5.add_run("Giảng viên hướng dẫn: TS. Nguyễn Văn A")
    r_gv.font.size = Pt(14)
    r_gv.bold = True

    p6 = doc.add_paragraph()
    p6.paragraph_format.left_indent = Cm(3.0)
    r_cv = p6.add_run("Cố vấn doanh nghiệp: ThS. Trần Thị B")
    r_cv.font.size = Pt(14)
    r_cv.bold = True

    p7 = doc.add_paragraph()
    p7.paragraph_format.left_indent = Cm(3.0)
    r_sv = p7.add_run("Sinh viên thực hiện:")
    r_sv.font.size = Pt(14)
    r_sv.bold = True

    students = [
        "1.   Nguyễn Văn A – 22H12345 – QL22A – 2022",
        "2.   Lê Ngọc B – 22H67890 – QL22A – 2022",
        "3.   Trần Hoài C – 22H13579 – QL22B – 2022"
    ]
    for st in students:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.left_indent = Cm(4.0)
        r_s = p_st.add_run(st)
        r_s.font.size = Pt(14)
        r_s.bold = True

    p8 = doc.add_paragraph()
    p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r8 = p8.add_run("\nTP. Hồ Chí Minh – Năm 2026")
    r8.font.size = Pt(13)
    r8.bold = True
    r8.italic = True

    doc.add_page_break()

    # DANH MỤC PHỤ LỤC (LIST OF APPENDICES)
    p_app_title = doc.add_paragraph()
    p_app_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_at = p_app_title.add_run("DANH MỤC PHỤ LỤC")
    r_at.font.size = Pt(14)
    r_at.bold = True
    p_app_title.paragraph_format.space_after = Pt(18)

    appendix_list_items = [
        ("PHỤ LỤC A: Sơ đồ mặt bằng và Luồng luân chuyển hàng hóa Kho số 6", "Trích dẫn tại Mục 2.3 (Trang 20)"),
        ("PHỤ LỤC B: Quy trình thao tác chuẩn (SOP) nhập kho ngoại quan U&I Logistics", "Trích dẫn tại Mục 2.3 (Trang 21)"),
        ("PHỤ LỤC C: Phiếu khảo sát và Thống kê tần suất lỗi thao tác thực tế", "Trích dẫn tại Mục 2.4 (Trang 24)"),
        ("PHỤ LỤC D: Biểu mẫu tem nhãn Barcode/QR Code đề xuất cải tiến", "Trích dẫn tại Mục 3.1 (Trang 27)")
    ]

    for app_name, ref_note in appendix_list_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_after = Pt(4)
        r_n = p_item.add_run(app_name)
        r_n.bold = True
        r_dots = p_item.add_run(" " + "." * (75 - len(app_name)) + " " + ref_note)
        r_dots.font.size = Pt(11)
        r_dots.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_page_break()

    # THÂN BÀI
    add_h1("CHƯƠNG 2: PHÂN TÍCH THỰC TRẠNG VÀ CÔNG VIỆC THỰC TẬP AT DOANH NGHIỆP")
    add_h2("2.3 Thực trạng quy trình nhập kho ngoại quan tại Kho số 6")
    add_p("Chi tiết sơ đồ bố trí mặt bằng và luồng di chuyển của xe nâng tại Kho ngoại quan số 6 được đính kèm tại (xem Phụ lục A - Sơ đồ mặt bằng Kho số 6). Quy trình nhập kho 5 bước được ban hành theo Quy trình Thao tác Chuẩn (xem Phụ lục B - Quy trình SOP nhập kho).")
    
    add_h2("2.4 Phân tích các hạn chế, rủi ro và lãng phí tồn tại")
    add_p("Nhóm đã tiến hành khảo sát thực tế và ghi nhận 30 phiếu lỗi thao tác kiểm đếm (xem Phụ lục C - Thống kê tần suất lỗi thao tác).")

    add_h1("CHƯƠNG 3: ĐỀ XUẤT GIẢI PHÁP LEAN WAREHOUSE VÀ BÀI HỌC KINH NGHIỆM")
    add_h2("3.1 Đề xuất giải pháp Lean Warehouse")
    add_p("Mẫu thiết kế tem nhãn quản lý Pallet nhập kho ngoại quan mới tích hợp mã QR Code được đề xuất chi tiết tại (xem Phụ lục D - Biểu mẫu tem nhãn đề xuất).")

    doc.add_page_break()

    # ----------------------------------------------------
    # PHẦN PHỤ LỤC TRÍCH DẪN ĐẦY ĐỦ 2 CHIỀU
    # ----------------------------------------------------
    def add_full_appendix_header(code, title, Purpose, cross_ref, source):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run(f"PHỤ LỤC {code}: {title.upper()}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.bold = True

        # Metadata Note Box for Appendix
        p_note = doc.add_paragraph()
        p_note.paragraph_format.left_indent = Cm(0.5)
        p_note.paragraph_format.space_after = Pt(12)
        p_note.paragraph_format.keep_with_next = True
        
        r_ref = p_note.add_run(f"• Trích dẫn từ Thân bài: {cross_ref}\n")
        r_ref.font.size = Pt(11)
        r_ref.bold = True
        r_ref.font.color.rgb = RGBColor(0, 51, 102)

        r_pur = p_note.add_run(f"• Mục đích phụ lục: {Purpose}\n")
        r_pur.font.size = Pt(11)
        r_pur.italic = True
        
        r_src = p_note.add_run(f"• Nguồn dữ liệu: {source}")
        r_src.font.size = Pt(11)
        r_src.italic = True

    def add_appendix_figure(fig_code, fig_name, image_path=None, source_text="Nguồn: U&I Logistics, 2026"):
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(12)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        
        r_code = p_cap.add_run(f"Hình {fig_code} ")
        r_code.bold = True
        r_code.font.size = Pt(12)
        
        r_name = p_cap.add_run(fig_name)
        r_name.italic = True
        r_name.font.size = Pt(12)

        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.keep_with_next = True
        
        if image_path and os.path.exists(image_path):
            p_img.add_run().add_picture(image_path, width=Cm(14.0))
        else:
            r_box = p_img.add_run("[ SƠ ĐỒ / BẢN VẼ / MINH HỌA HÌNH ẢNH PHỤ LỤC ]")
            r_box.font.color.rgb = RGBColor(120, 120, 120)
            r_box.italic = True

        p_src = doc.add_paragraph(source_text)
        p_src.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_src.paragraph_format.space_after = Pt(12)
        p_src.runs[0].font.italic = True
        p_src.runs[0].font.size = Pt(11)

    # PHỤ LỤC A
    add_full_appendix_header(
        "A",
        "Sơ đồ mặt bằng và Luồng luân chuyển hàng hóa Kho số 6",
        "Minh họa không gian hạ tầng kho bãi và tuyến đường di chuyển của xe nâng phục vụ phân tích thực trạng.",
        "Tiểu mục 2.3 (Chương 2, trang 20)",
        "Phòng Vận hành Kho vận - Công ty Cổ phần Logistics U&I (2026)"
    )
    add_appendix_figure("A.1", "Sơ đồ luồng di chuyển của xe nâng và nhân viên kiểm đếm tại Kho số 6")

    doc.add_page_break()

    # PHỤ LỤC B
    add_full_appendix_header(
        "B",
        "Quy trình thao tác chuẩn (SOP) nhập kho ngoại quan U&I Logistics",
        "Cung cấp văn bản quy định chuẩn 5 bước làm việc làm căn cứ đối chiếu với các sai sót thực tế.",
        "Tiểu mục 2.3 (Chương 2, trang 21)",
        "Ban Giám đốc Công ty Cổ phần Logistics U&I ban hành (2025)"
    )
    add_appendix_figure("B.1", "Sơ đồ dòng chảy công việc 5 bước trong quy trình nhập kho ngoại quan")

    doc.add_page_break()

    # PHỤ LỤC C
    add_full_appendix_header(
        "C",
        "Phiếu khảo sát và Thống kê tần suất lỗi thao tác thực tế",
        "Cung cấp bằng chứng định lượng về 30 sự cố phát sinh để làm cơ sở đề xuất giải pháp cải tiến.",
        "Tiểu mục 2.4 (Chương 2, trang 24)",
        "Tổng hợp từ 30 phiếu ghi nhận lỗi thực địa của Nhóm thực tập (2026)"
    )
    
    p_c_cap = doc.add_paragraph()
    p_c_cap.paragraph_format.keep_with_next = True
    r_c_cap = p_c_cap.add_run("Bảng C.1 Thống kê 30 phiếu ghi nhận lỗi thao tác nhập kho tại Kho số 6")
    r_c_cap.bold = True
    
    tbl_c = doc.add_table(rows=4, cols=4)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_c = ["STT", "Loại lỗi phát sinh", "Tần suất (Lần)", "Tỷ lệ (%)"]
    for idx, h in enumerate(headers_c):
        cell = tbl_c.cell(0, idx)
        set_cell_background(cell, "E6EEF8")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(h).bold = True

    data_c = [
        ["1", "Ghi sai số lượng/chủng loại trên biên bản kiểm đếm", "14", "46.7%"],
        ["2", "Nhập chậm dữ liệu Pallet vào hệ thống BWMS", "10", "33.3%"],
        ["3", "Dán nhầm tem nhãn mã Barcode phụ", "6", "20.0%"]
    ]
    for r_idx, r_data in enumerate(data_c):
        for c_idx, val in enumerate(r_data):
            cell = tbl_c.cell(r_idx + 1, c_idx)
            cell.paragraphs[0].text = val

    format_table_no_split(tbl_c, caption_paragraph=p_c_cap)

    doc.add_page_break()

    # PHỤ LỤC D
    add_full_appendix_header(
        "D",
        "Biểu mẫu tem nhãn Barcode/QR Code đề xuất cải tiến",
        "Minh họa giải pháp thiết kế tem nhãn thông minh dán Pallet phục vụ giải pháp Lean Warehouse.",
        "Tiểu mục 3.1 (Chương 3, trang 27)",
        "Đề xuất của Nhóm nghiên cứu thực tập (2026)"
    )
    add_appendix_figure("D.1", "Mẫu thiết kế tem nhãn Pallet chuẩn hóa dán trên kiện hàng ngoại quan")

    doc.save(output_filename)
    print(f"Full Appendix Citation Report saved into '{output_filename}' successfully!")

if __name__ == "__main__":
    create_appendix_full_citation_report()
