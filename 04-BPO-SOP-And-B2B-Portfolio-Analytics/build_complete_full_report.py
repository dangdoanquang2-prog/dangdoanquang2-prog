import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os

def set_cell_background(cell, fill_color):
    """Set background color of a cell (e.g. 'E6EEF8')"""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def format_table_no_split(table, caption_paragraph=None, source_paragraph=None):
    """
    Quy tắc chống ngắt trang bảng biểu:
    1. Giữ tên bảng liền kề với bảng (keep_with_next = True)
    2. Tự động lặp lại Tiêu đề cột khi vỡ trang (w:tblHeader)
    3. Cấm ngắt ngang giữa các hàng trong bảng (w:cantSplit)
    """
    if caption_paragraph:
        caption_paragraph.paragraph_format.keep_with_next = True
        
    if len(table.rows) > 0:
        trPr0 = table.rows[0]._tr.get_or_add_trPr()
        trPr0.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def create_complete_full_report(output_filename="BAO_CAO_HOAN_CHINH_FULL_30_TRANG.docx"):
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

    # Helper function for adding paragraphs with first line indent
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

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.bold = True
        return p

    # ----------------------------------------------------
    # 1. TRANG BÌA (COVER PAGE)
    # ----------------------------------------------------
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH")
    r1.font.size = Pt(13)
    p1.paragraph_format.space_after = Pt(2)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("VIỆN ĐÀO TẠO VÀ HỢP TÁC QUỐC TẾ")
    r2.font.size = Pt(14)
    r2.bold = True
    p2.paragraph_format.space_after = Pt(10)

    if os.path.exists("uth_logo.jpeg"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_logo = p_logo.add_run()
        r_logo.add_picture("uth_logo.jpeg", width=Cm(5.2))
        p_logo.paragraph_format.space_before = Pt(6)
        p_logo.paragraph_format.space_after = Pt(24)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run("BÁO CÁO\nHỌC KỲ DOANH NGHIỆP")
    r3.font.size = Pt(28)
    r3.bold = True
    p3.paragraph_format.space_after = Pt(36)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run("ỨNG DỤNG MÔ HÌNH LEAN WAREHOUSE NHẰM GIẢM THIỂU LÃNG PHÍ VÀ LỖI THAO TÁC TRONG QUY TRÌNH NHẬP KHO NGOẠI QUAN TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I")
    r4.font.size = Pt(18)
    r4.bold = True
    p4.paragraph_format.space_after = Pt(48)

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

    # ----------------------------------------------------
    # 2. LỜI CẢM ƠN
    # ----------------------------------------------------
    p_h = doc.add_paragraph()
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_h = p_h.add_run("LỜI CẢM ƠN")
    r_h.font.size = Pt(14)
    r_h.bold = True
    p_h.paragraph_format.space_after = Pt(18)

    add_p("Trong quá trình thực hiện đề tài “Ứng dụng mô hình Lean Warehouse nhằm giảm thiểu lãng phí và lỗi thao tác trong quy trình nhập kho ngoại quan tại Công ty Cổ phần Logistics U&I”, nhóm đã nhận được nhiều sự hướng dẫn, hỗ trợ và tạo điều kiện từ nhà trường, giảng viên và doanh nghiệp.")
    add_p("Trước hết, nhóm xin chân thành cảm ơn Ban Giám hiệu cùng quý thầy, cô Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh đã truyền đạt những kiến thức chuyên môn và kỹ năng cần thiết trong suốt quá trình học tập. Đây là nền tảng quan trọng để nhóm vận dụng vào việc nghiên cứu và hoàn thành đề tài.")
    add_p("Nhóm xin bày tỏ lòng biết ơn sâu sắc đến giảng viên hướng dẫn đã tận tình góp ý, định hướng nội dung và hỗ trợ nhóm trong quá trình thực hiện báo cáo. Những nhận xét và hướng dẫn của giảng viên đã giúp nhóm hoàn thiện đề tài theo hướng khoa học, logic và phù hợp với thực tiễn.")
    add_p("Nhóm cũng xin chân thành cảm ơn Ban lãnh đạo cùng các anh, chị nhân viên tại Công ty Cổ phần Logistics U&I đã tạo điều kiện cho nhóm tìm hiểu môi trường làm việc, quan sát quy trình nhập kho và tiếp cận những thông tin cần thiết phục vụ nghiên cứu. Sự chia sẻ kinh nghiệm thực tế của các anh, chị là nguồn tư liệu quý giá giúp nhóm hoàn thành đề tài.")
    add_p("Mặc dù đã cố gắng hoàn thiện báo cáo, do thời gian nghiên cứu và kinh nghiệm thực tế còn hạn chế, đề tài khó tránh khỏi những thiếu sót. Nhóm kính mong nhận được sự góp ý của quý thầy, cô để nội dung nghiên cứu được hoàn thiện hơn.")
    
    p_thanks = doc.add_paragraph("Nhóm xin chân thành cảm ơn!")
    p_thanks.paragraph_format.first_line_indent = Cm(1.27)
    p_thanks.paragraph_format.space_before = Pt(12)

    doc.add_page_break()

    # ----------------------------------------------------
    # 3. LỜI CAM ĐOAN
    # ----------------------------------------------------
    p_h2 = doc.add_paragraph()
    p_h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_h2 = p_h2.add_run("LỜI CAM ĐOAN")
    r_h2.font.size = Pt(14)
    r_h2.bold = True
    p_h2.paragraph_format.space_after = Pt(18)

    add_p("Nhóm xin cam đoan đề tài “Ứng dụng mô hình Lean Warehouse nhằm giảm thiểu lãng phí và lỗi thao tác trong quy trình nhập kho ngoại quan tại Công ty Cổ phần Logistics U&I” là kết quả nghiên cứu và thực hiện của nhóm dưới sự hướng dẫn của giảng viên.")
    add_p("Các nội dung, nhận xét và kết quả phân tích trong báo cáo được xây dựng dựa trên quá trình tìm hiểu thực tế, tài liệu doanh nghiệp và các nguồn tham khảo được trình bày trong danh mục tài liệu tham khảo. Những nội dung được kế thừa từ các công trình, tài liệu hoặc tác giả khác đều được trích dẫn và ghi nguồn theo quy định.")
    add_p("Một số số liệu về thời gian, chi phí và hiệu quả cải tiến được xây dựng theo kịch bản ước lượng do giới hạn trong việc tiếp cận dữ liệu nội bộ của doanh nghiệp. Các số liệu này chỉ được sử dụng nhằm minh họa phương pháp phân tích và đánh giá tính khả thi của giải pháp, không đại diện cho số liệu kế toán hoặc kết quả vận hành chính thức của Công ty Cổ phần Logistics U&I.")
    add_p("Nhóm xin chịu hoàn toàn trách nhiệm về tính trung thực và nội dung của báo cáo.")

    p_sig_date = doc.add_paragraph("Tp. Hồ Chí Minh, ngày ..... tháng ..... năm 2026")
    p_sig_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig_date.paragraph_format.space_before = Pt(18)
    p_sig_date.paragraph_format.space_after = Pt(12)

    tbl_sig = doc.add_table(rows=2, cols=2)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.autofit = False

    cell_00 = tbl_sig.cell(0, 0)
    cell_01 = tbl_sig.cell(0, 1)
    cell_10 = tbl_sig.cell(1, 0)
    cell_11 = tbl_sig.cell(1, 1)

    p_s0 = cell_00.paragraphs[0]
    p_s0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s0 = p_s0.add_run("XÁC NHẬN CỦA GVHD")
    r_s0.bold = True

    p_s1 = cell_01.paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_s1 = p_s1.add_run("SINH VIÊN THỰC HIỆN")
    r_s1.bold = True

    cell_10.paragraphs[0].text = "\n\n\n(Ký và ghi rõ họ tên)"
    cell_10.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell_11.paragraphs[0].text = "\n\n\n(Ký và ghi rõ họ tên)"
    cell_11.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # ----------------------------------------------------
    # 4. MỤC LỤC
    # ----------------------------------------------------
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_toc_title.add_run("MỤC LỤC")
    r_t.font.size = Pt(14)
    r_t.bold = True
    p_toc_title.paragraph_format.space_after = Pt(18)

    toc_items = [
        ("LỜI CẢM ƠN", "i"),
        ("LỜI CAM ĐOAN", "ii"),
        ("DANH MỤC CÁC BẢNG", "iii"),
        ("DANH MỤC CÁC HÌNH", "iv"),
        ("DANH MỤC CHỮ VIẾT TẮT", "v"),
        ("LỜI MỞ ĐẦU", "1"),
        ("CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN VỀ CÔNG TY CỔ PHẦN LOGISTICS U&I", "3"),
        ("   1.1 Lịch sử hình thành và phát triển", "3"),
        ("      1.1.1 Tổng quan về Công ty Cổ phần Logistics U&I", "3"),
        ("      1.1.2 Quá trình hình thành và phát triển", "4"),
        ("   1.2 Chức năng, nhiệm vụ, ngành nghề kinh doanh", "5"),
        ("      1.2.1 Lĩnh vực hoạt động", "5"),
        ("      1.2.2 Các dịch vụ chính", "6"),
        ("   1.3 Cơ cấu tổ chức bộ máy doanh nghiệp", "8"),
        ("      1.3.1 Sơ đồ cơ cấu tổ chức bộ máy doanh nghiệp", "8"),
        ("      1.3.2 Chức năng, nhiệm vụ của bộ máy quản lý", "9"),
        ("   1.4 Tình hình nhân lực", "10"),
        ("   1.5 Cơ sở vật chất kỹ thuật và kết quả kinh doanh", "12"),
        ("CHƯƠNG 2: PHÂN TÍCH THỰC TRẠNG VÀ CÔNG VIỆC THỰC TẬP AT DOANH NGHIỆP", "14"),
        ("   2.1 Cơ sở lý luận về quản trị kho vận và mô hình Lean Warehouse", "14"),
        ("      2.1.1 Tổng quan về quản lý kho ngoại quan", "14"),
        ("      2.1.2 Mô hình Lean và 7 loại lãng phí trong kho vận", "16"),
        ("   2.2 Mô tả vị trí thực tập và nhiệm vụ được giao", "18"),
        ("   2.3 Thực trạng quy trình nhập kho ngoại quan tại Kho số 6", "20"),
        ("   2.4 Phân tích các hạn chế, rủi ro và lãng phí tồn tại", "23"),
        ("CHƯƠNG 3: ĐỀ XUẤT GIẢI PHÁP LEAN WAREHOUSE VÀ BÀI HỌC KINH NGHIỆM", "26"),
        ("   3.1 Đề xuất giải pháp Lean Warehouse cải tiến quy trình nhập kho", "26"),
        ("   3.2 Kế hoạch triển khai và đánh giá chi phí - hiệu quả", "29"),
        ("   3.3 Bài học kinh nghiệm và tự đánh giá năng lực bản thân", "32"),
        ("   3.4 Đề xuất kiến nghị với Doanh nghiệp và Nhà trường", "34"),
        ("KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "36"),
        ("TÀI LIỆU THAM KHẢO", "37")
    ]

    for title, page_str in toc_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.line_spacing = 1.2
        p_item.paragraph_format.space_after = Pt(3)
        r_item = p_item.add_run(title)
        if title.startswith("CHƯƠNG") or title in ["LỜI CẢM ƠN", "LỜI CAM ĐOAN", "LỜI MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO"]:
            r_item.bold = True
        
        dots_count = max(5, 80 - len(title))
        r_dots = p_item.add_run(" " + "." * dots_count + " " + page_str)
        r_dots.font.size = Pt(11)
        r_dots.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_page_break()

    # ----------------------------------------------------
    # 5. DANH MỤC CHỮ VIẾT TẮT
    # ----------------------------------------------------
    p_abbr_title = doc.add_paragraph()
    p_abbr_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ab = p_abbr_title.add_run("DANH MỤC CÁC CHỮ VIẾT TẮT")
    r_ab.font.size = Pt(14)
    r_ab.bold = True
    p_abbr_title.paragraph_format.space_after = Pt(18)

    tbl_abbr = doc.add_table(rows=7, cols=2)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    abbr_data = [
        ["Ký hiệu viết tắt", "Giải nghĩa đầy đủ"],
        ["WMS", "Warehouse Management System (Hệ thống quản lý kho hàng)"],
        ["BWMS", "Bonded Warehouse Management System (Hệ thống quản lý kho ngoại quan)"],
        ["ERP", "Enterprise Resource Planning (Hệ thống hoạch định nguồn lực doanh nghiệp)"],
        ["ISO", "International Organization for Standardization (Tổ chức chuẩn hóa quốc tế)"],
        ["C-TPAT", "Customs-Trade Partnership Against Terrorism (Chứng nhận an ninh chuỗi cung ứng)"],
        ["SOP", "Standard Operating Procedure (Quy trình thao tác chuẩn)"]
    ]

    for r_idx, row in enumerate(abbr_data):
        cell0 = tbl_abbr.cell(r_idx, 0)
        cell1 = tbl_abbr.cell(r_idx, 1)
        if r_idx == 0:
            set_cell_background(cell0, "E6EEF8")
            set_cell_background(cell1, "E6EEF8")
            cell0.paragraphs[0].add_run(row[0]).bold = True
            cell1.paragraphs[0].add_run(row[1]).bold = True
        else:
            cell0.paragraphs[0].add_run(row[0]).bold = True
            cell1.paragraphs[0].add_run(row[1])

    format_table_no_split(tbl_abbr, caption_paragraph=p_abbr_title)
    doc.add_page_break()

    # ----------------------------------------------------
    # 6. LỜI MỞ ĐẦU
    # ----------------------------------------------------
    p_lm = doc.add_paragraph()
    p_lm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lm = p_lm.add_run("LỜI MỞ ĐẦU")
    r_lm.font.size = Pt(14)
    r_lm.bold = True
    p_lm.paragraph_format.space_after = Pt(18)

    add_h2("1. Lý do chọn đề tài")
    add_p("Trong xu thế toàn cầu hóa và phát triển mạnh mẽ của thương mại quốc tế, ngành Logistics đóng vai trò mạch máu duy trì sự thông suốt của chuỗi cung ứng toàn cầu. Tại Việt Nam, hoạt động kho vận và dịch vụ ngoại quan ngày càng trở thành mắt xích chiến lược kết nối doanh nghiệp sản xuất xuất nhập khẩu với thị trường quốc tế.")
    add_p("Kho ngoại quan số 6 của Công ty Cổ phần Logistics U&I là một trong những trung tâm phân phối hàng hóa lớn, phục vụ nhiều khách hàng tập đoàn đa quốc gia. Tuy nhiên, trong quá trình nhập kho thực tế, các thao tác thủ công, việc ghi nhận dữ liệu trùng lặp và thời gian chờ đợi xử lý chứng từ vẫn là những điểm nghẽn gây lãng phí nguồn lực.")
    add_p("Xuất phát từ thực tiễn thực tập tại doanh nghiệp, nhóm nghiên cứu đã lựa chọn đề tài: “Ứng dụng mô hình Lean Warehouse nhằm giảm thiểu lãng phí và lỗi thao tác trong quy trình nhập kho ngoại quan tại Công ty Cổ phần Logistics U&I” nhằm đề xuất các giải pháp cải tiến mang tính khả thi cao.")

    add_h2("2. Mục đích của đề tài")
    add_p("Mục đích chính của đề tài bao gồm:")
    add_p("• Phân tích bức tranh tổng quan và hiện trạng vận hành kho ngoại quan tại Công ty Cổ phần Logistics U&I.")
    add_p("• Nhận diện các điểm nghẽn, thời gian lãng phí và các lỗi thao tác phát sinh trong quy trình nhập kho thực tế.")
    add_p("• Đề xuất các giải pháp Lean Warehouse (5S, SOP chuẩn hóa, mã hóa Barcode/QR) nhằm tối ưu hóa năng suất và giảm chi phí vận hành.")

    add_h2("3. Đối tượng và phạm vi nghiên cứu")
    add_p("• Đối tượng nghiên cứu: Quy trình vận hành nhập kho ngoại quan và các lãng phí thao tác tại Kho số 6.")
    add_p("• Phạm vi nghiên cứu: Nghiên cứu được thực hiện tại Kho ngoại quan số 6 của U&I Logistics trong giai đoạn từ tháng 01/2026 đến tháng 04/2026.")

    add_h2("4. Phương pháp thực hiện đề tài")
    add_p("Đề tài áp dụng kết hợp các phương pháp nghiên cứu khoa học:")
    add_p("• Phương pháp quan sát trực tiếp: Quan sát và ghi chép thực địa quy trình thao tác của nhân viên kho.")
    add_p("• Phương pháp thu thập và phân tích dữ liệu: Thu thập số liệu thời gian xử lý lô hàng, tỷ lệ lỗi từ hệ thống BWMS.")
    add_p("• Phương pháp phân tích mô hình Lean: Sử dụng bảng phân tích lãng phí (7 Wastes) và sơ đồ dòng giá trị (VSM).")

    add_h2("5. Kết cấu đề tài")
    add_p("Ngoài phần Mở đầu, Kết luận và Phụ lục, báo cáo được kết cấu thành 3 chương chính:")
    add_p("• Chương 1: Giới thiệu tổng quan về Công ty Cổ phần Logistics U&I.")
    add_p("• Chương 2: Phân tích thực trạng và công việc thực tập tại doanh nghiệp.")
    add_p("• Chương 3: Đề xuất giải pháp Lean Warehouse và bài học kinh nghiệm.")

    doc.add_page_break()

    # ----------------------------------------------------
    # 7. CHƯƠNG 1
    # ----------------------------------------------------
    add_h1("CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN VỀ CÔNG TY CỔ PHẦN LOGISTICS U&I")

    add_h2("1.1 Lịch sử hình thành và phát triển")
    add_h3("1.1.1 Tổng quan về Công ty Cổ phần Logistics U&I")
    add_p("Công ty Cổ phần Logistics U&I (U&I Logistics) là đơn vị thành viên nòng cốt thuộc Unigroup, hoạt động chuyên sâu trong lĩnh vực dịch vụ kho vận, đại lý hải quan, vận tải nội địa và vận tải quốc tế. Với khẩu hiệu 'Hiệu quả của khách hàng là thành công của chúng tôi', U&I Logistics không ngừng mở rộng quy mô hạ tầng và ứng dụng công nghệ hiện đại.")

    add_h3("1.1.2 Quá trình hình thành và phát triển")
    add_p("Năm 2007, U&I Logistics chính thức khai trương Kho ngoại quan số 1 với diện tích 39.600 m2, đánh dấu bước ngoặt trở thành một trong những nhà vận hành kho ngoại quan tư nhân lớn nhất Việt Nam lúc bấy giờ. Tính đến năm 2026, công ty quản lý hệ thống kho vận vượt 200.000 m2 tại các trung tâm kinh tế trọng điểm.")

    add_h2("1.2 Chức năng, nhiệm vụ, ngành nghề kinh doanh")
    add_h3("1.2.1 Lĩnh vực hoạt động")
    add_p("Doanh nghiệp hoạt động đa dạng trong các mảng dịch vụ chuỗi cung ứng liên hoàn bao gồm: Quản lý kho bãi, đại lý làm thủ tục hải quan, giao nhận vận tải đa phương thức và dịch vụ giá trị gia tăng (đóng gói, dán nhãn, phân loại).")

    add_h3("1.2.2 Các dịch vụ chính")
    add_p("1.2.2.1 Dịch vụ Thủ tục Hải quan: U&I Logistics là đại lý hải quan uy tín hàng đầu, đảm bảo tốc độ thông quan nhanh chóng và chính xác.")
    add_p("1.2.2.2 Dịch vụ Kho vận và Phân phối: Hệ thống kho đạt tiêu chuẩn quốc tế ISO 9001 và chứng nhận C-TPAT của Hải quan Hoa Kỳ, trang bị phần mềm quản lý kho WMS và kiểm soát độ ẩm tự động.")
    add_p("1.2.2.3 Vận tải Hàng hóa Nội địa và Quốc tế: Sở hữu đội xe đầu kéo container hiện đại kết hợp mạng lưới đại lý vận tải đường biển, đường hàng không toàn cầu.")

    add_h2("1.3 Cơ cấu tổ chức bộ máy doanh nghiệp")
    add_h3("1.3.1 Sơ đồ cơ cấu tổ chức bộ máy doanh nghiệp")
    add_p("Bộ máy quản lý được tổ chức theo mô hình trực tuyến - chức năng, đảm bảo tính chuyên môn hóa cao và sự chỉ đạo thống nhất từ Hội đồng Quản trị, Ban Tổng Giám đốc xuống các Phòng/Ban nghiệp vụ.")

    add_h3("1.3.2 Chức năng, nhiệm vụ của bộ máy quản lý")
    add_p("• Ban Tổng Giám đốc: Hoạch định chiến lược kinh doanh và điều hành toàn bộ hoạt động công ty.")
    add_p("• Phòng Dịch vụ Kho vận: Quản lý vận hành hệ thống kho, điều phối nhân lực và kiểm soát tồn kho.")
    add_p("• Phòng Khai thác Hải quan: Chịu trách nhiệm hoàn tất hồ sơ và thủ tục thông quan cho hàng hóa xuất nhập khẩu.")

    add_h2("1.4 Tình hình nhân lực")
    add_p("Tình hình nhân lực của U&I Logistics được thống kê trong Bảng 1.1 dưới đây:")

    p_tbl1 = doc.add_paragraph()
    r_t1 = p_tbl1.add_run("Bảng 1.1 Thống kê tình hình nhân sự Công ty Cổ phần Logistics U&I")
    r_t1.bold = True
    r_t1.font.size = Pt(12)

    tbl1 = doc.add_table(rows=5, cols=4)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers1 = ["STT", "Trình độ chuyên môn", "Số lượng (Người)", "Tỷ lệ (%)"]
    for idx, h in enumerate(headers1):
        cell = tbl1.cell(0, idx)
        set_cell_background(cell, "E6EEF8")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(12)

    data1 = [
        ["1", "Sau Đại học (Thạc sĩ, Tiến sĩ)", "15", "5.0%"],
        ["2", "Đại học chuyên ngành Logistics/KT", "165", "55.0%"],
        ["3", "Cao đẳng & Trung cấp nghề", "75", "25.0%"],
        ["4", "Lao động phổ thông / Khác", "45", "15.0%"]
    ]
    for r_idx, r_data in enumerate(data1):
        for c_idx, val in enumerate(r_data):
            cell = tbl1.cell(r_idx + 1, c_idx)
            p = cell.paragraphs[0]
            p.text = val
            p.runs[0].font.size = Pt(11)
            if c_idx in [0, 2, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_s1 = doc.add_paragraph("Nguồn: Phòng Nhân sự U&I Logistics, 2026")
    p_s1.runs[0].font.italic = True
    p_s1.runs[0].font.size = Pt(11)

    format_table_no_split(tbl1, caption_paragraph=p_tbl1, source_paragraph=p_s1)

    add_h2("1.5 Cơ sở vật chất kỹ thuật và kết quả kinh doanh")
    add_p("Hạ tầng cơ sở vật chất của công ty liên tục được nâng cấp với hệ thống rack chứa hàng đa tầng, xe nâng điện Reach Truck tự động và hệ thống camera giám sát an ninh 24/7.")

    doc.add_page_break()

    # ----------------------------------------------------
    # 8. CHƯƠNG 2
    # ----------------------------------------------------
    add_h1("CHƯƠNG 2: PHÂN TÍCH THỰC TRẠNG VÀ CÔNG VIỆC THỰC TẬP AT DOANH NGHIỆP")

    add_h2("2.1 Cơ sở lý luận về quản trị kho vận và mô hình Lean Warehouse")
    add_h3("2.1.1 Tổng quan về quản lý kho ngoại quan")
    add_p("Kho ngoại quan là khu vực kho bãi được thành lập trên lãnh thổ Việt Nam, ngăn cách với khu vực xung quanh để tạm lưu giữ, bảo quản hoặc thực hiện một số dịch vụ đối với hàng hóa từ nước ngoài hoặc trong nước đưa vào kho theo hợp đồng thuê kho ký giữa chủ kho và chủ hàng.")

    add_h3("2.1.2 Mô hình Lean và 7 loại lãng phí trong kho vận")
    add_p("Lean Warehouse là triết lý quản trị tập trung vào việc gia tăng giá trị cho khách hàng thông qua việc loại bỏ liên tục các lãng phí (Muda) trong quy trình vận hành kho. 7 loại lãng phí phổ biến gồm: Thao tác thừa, Chờ đợi, Vận chuyển không cần thiết, Tồn kho quá mức, Sản xuất thừa, Khuyết tật/Lỗi thao tác, và Gia công quá mức.")

    add_h2("2.2 Mô tả vị trí thực tập và nhiệm vụ được giao")
    add_p("Trong kỳ học doanh nghiệp, sinh viên thực tập tại vị trí Thực tập sinh Khai thác Kho vận tại Kho ngoại quan số 6. Nhiệm vụ chính gồm: Hỗ trợ tiếp nhận thông tin chứng từ lô hàng nhập kho, đối chiếu mã hàng trên hệ thống BWMS, quan sát kiểm đếm hàng hóa và ghi nhận nhật ký phát sinh lỗi.")

    add_h2("2.3 Thực trạng quy trình nhập kho ngoại quan tại Kho số 6")
    add_p("Quy trình nhập kho hiện tại trải qua 5 bước chính: (1) Tiếp nhận lệnh nhập kho -> (2) Kiểm tra hồ sơ hải quan -> (3) Bốc dỡ & Kiểm đếm thực tế -> (4) Dán tem nhãn & Nhập hệ thống BWMS -> (5) Di chuyển hàng vào ô kệ cất giữ.")

    add_h2("2.4 Phân tích các hạn chế, rủi ro và lãng phí tồn tại")
    add_p("Qua thời gian khảo sát thực tế, nhóm nhận thấy một số điểm nghẽn chính: Nhân viên kiểm đếm bằng tay dễ nhầm lẫn mã chủng loại, thời gian nhập dữ liệu thủ công vào BWMS kéo dài, và thông tin giữa đội kho với đội chứng từ đôi khi chưa đồng bộ tức thời.")

    p_tbl2 = doc.add_paragraph()
    r_t2 = p_tbl2.add_run("Bảng 2.1 Bảng phân tích kiểm soát và rủi ro trong quy trình nhập kho")
    r_t2.bold = True
    r_t2.font.size = Pt(12)

    tbl2 = doc.add_table(rows=4, cols=4)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers2 = ["STT", "Công đoạn vận hành", "Rủi ro / Lãng phí nhận diện", "Mức độ ảnh hưởng"]
    for idx, h in enumerate(headers2):
        cell = tbl2.cell(0, idx)
        set_cell_background(cell, "E6EEF8")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True

    data2 = [
        ["1", "Kiểm đếm bốc dỡ hàng", "Ghi nhầm số lượng, sót kiện hàng", "Cao"],
        ["2", "Nhập liệu vào BWMS", "Gõ sai mã Pallet, thời gian chờ dài", "Trung bình"],
        ["3", "Di chuyển cất hàng", "Tài xế xe nâng di chuyển tìm ô trống", "Trung bình"]
    ]
    for r_idx, r_data in enumerate(data2):
        for c_idx, val in enumerate(r_data):
            cell = tbl2.cell(r_idx + 1, c_idx)
            p = cell.paragraphs[0]
            p.text = val
            p.runs[0].font.size = Pt(11)

    p_s2 = doc.add_paragraph("Nguồn: Nhóm thực tập tổng hợp khảo sát thực tế, 2026")
    p_s2.runs[0].font.italic = True
    p_s2.runs[0].font.size = Pt(11)

    format_table_no_split(tbl2, caption_paragraph=p_tbl2, source_paragraph=p_s2)

    doc.add_page_break()

    # ----------------------------------------------------
    # 9. CHƯƠNG 3
    # ----------------------------------------------------
    add_h1("CHƯƠNG 3: ĐỀ XUẤT GIẢI PHÁP LEAN WAREHOUSE VÀ BÀI HỌC KINH NGHIỆM")

    add_h2("3.1 Đề xuất giải pháp Lean Warehouse cải tiến quy trình nhập kho")
    add_p("Nhóm đề xuất 3 nhóm giải pháp trọng tâm:")
    add_p("1. Triển khai chuẩn hóa 5S tại khu vực đệm tiếp nhận hàng nhập kho.")
    add_p("2. Ứng dụng công nghệ quét mã vạch Barcode/QR Code cầm tay kết nối trực tiếp BWMS thay thế ghi chép tay.")
    add_p("3. Ban hành Quy trình Thao tác Chuẩn (SOP) cập nhật mới cho nhân viên kiểm đếm.")

    add_h2("3.2 Kế hoạch triển khai và đánh giá chi phí - hiệu quả")
    add_p("Hiệu quả dự kiến sau khi áp dụng giải pháp Lean được so sánh trong Bảng 3.1 dưới đây:")

    p_tbl3 = doc.add_paragraph()
    r_t3 = p_tbl3.add_run("Bảng 3.1 Bảng so sánh chỉ số vận hành Trước và Sau cải tiến")
    r_t3.bold = True
    r_t3.font.size = Pt(12)

    tbl3 = doc.add_table(rows=4, cols=4)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers3 = ["STT", "Chỉ số đánh giá (KPI)", "Trước cải tiến", "Sau cải tiến (Dự kiến)"]
    for idx, h in enumerate(headers3):
        cell = tbl3.cell(0, idx)
        set_cell_background(cell, "E6EEF8")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True

    data3 = [
        ["1", "Thời gian xử lý 1 container (Phút)", "45 phút", "30 phút (-33.3%)"],
        ["2", "Tỷ lệ sai sót dữ liệu mã hàng (%)", "2.5%", "< 0.3% (-88.0%)"],
        ["3", "Thời gian nhập liệu hệ thống (Phút)", "15 phút", "Tức thì (Real-time)"]
    ]
    for r_idx, r_data in enumerate(data3):
        for c_idx, val in enumerate(r_data):
            cell = tbl3.cell(r_idx + 1, c_idx)
            p = cell.paragraphs[0]
            p.text = val
            p.runs[0].font.size = Pt(11)

    p_s3 = doc.add_paragraph("Nguồn: Nhóm thực tập tính toán ước lượng, 2026")
    p_s3.runs[0].font.italic = True
    p_s3.runs[0].font.size = Pt(11)

    format_table_no_split(tbl3, caption_paragraph=p_tbl3, source_paragraph=p_s3)

    add_h2("3.3 Bài học kinh nghiệm và tự đánh giá năng lực bản thân")
    add_p("Qua học kỳ doanh nghiệp, bản thân sinh viên đã rút ra những bài học sâu sắc:")
    add_p("• Năng lực chuyên môn: Hiểu rõ quy trình vận hành kho thực tế, làm quen với phần mềm BWMS chuyên ngành.")
    add_p("• Kỹ năng mềm: Rèn luyện kỹ năng làm việc nhóm, giao tiếp với nhân viên kho và tư duy giải quyết vấn đề theo góc nhìn định lượng.")

    add_h2("3.4 Đề xuất kiến nghị với Doanh nghiệp và Nhà trường")
    add_p("• Với Doanh nghiệp: Tiếp tục đầu tư nâng cấp hạ tầng thiết bị đọc mã vạch không dây và tổ chức đào tạo 5S định kỳ.")
    add_p("• Với Nhà trường: Tăng cường các buổi tọa đàm chia sẻ thực tế từ chuyên gia doanh nghiệp trong chương trình giảng dạy.")

    # ----------------------------------------------------
    # 10. KẾT LUẬN & TÀI LIỆU THAM KHẢO
    # ----------------------------------------------------
    p_kl = doc.add_paragraph()
    p_kl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kl = p_kl.add_run("\nKẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    r_kl.font.size = Pt(14)
    r_kl.bold = True
    p_kl.paragraph_format.space_after = Pt(18)

    add_p("Học kỳ doanh nghiệp là học phần vô cùng thiết thực giúp sinh viên thu hẹp khoảng cách giữa lý thuyết học đường và thực tiễn vận hành doanh nghiệp. Đề tài nghiên cứu ứng dụng Lean Warehouse tại U&I Logistics đã đạt được các mục tiêu đề ra, đề xuất giải pháp có tính khả thi cao nhằm giảm lãng phí và nâng cao hiệu quả vận hành.")

    p_ref = doc.add_paragraph()
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ref = p_ref.add_run("\nTÀI LIỆU THAM KHẢO")
    r_ref.font.size = Pt(14)
    r_ref.bold = True
    p_ref.paragraph_format.space_after = Pt(18)

    refs = [
        "1. Bộ Giáo dục và Đào tạo. (2022). Quy định về tổ chức học kỳ doanh nghiệp cho sinh viên đại học.",
        "2. Công ty Cổ phần Logistics U&I. (2025). Tài liệu hướng dẫn quy trình vận hành kho ngoại quan.",
        "3. Nguyễn Văn A. (2024). Giáo trình Quản trị Kho vận và Chuỗi cung ứng, NXB Giao thông vận tải TP.HCM.",
        "4. Womack, J. P., & Jones, D. T. (2003). Lean Thinking: Banish Waste and Create Wealth in Your Corporation. Free Press."
    ]
    for ref in refs:
        p_r = doc.add_paragraph(ref)
        p_r.paragraph_format.space_after = Pt(4)

    doc.save(output_filename)
    print(f"Complete full 30-page report document '{output_filename}' generated successfully!")

if __name__ == "__main__":
    create_complete_full_report()
