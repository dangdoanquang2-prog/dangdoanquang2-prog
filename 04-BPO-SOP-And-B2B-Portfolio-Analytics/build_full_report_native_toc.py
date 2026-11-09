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

def add_native_word_toc_field(doc):
    """Chèn mã Field XML Mục lục tự động chuẩn Microsoft Word (Update Field / Ctrl+A -> F9)"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run()
    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>')
    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    fldChar3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_native_toc_report(output_filename="BAO_CAO_HOAN_CHINH_MUC_LUC_TU_DONG_WORD.docx"):
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

    # Configure Heading Styles for Native Word TOC Field Detection
    style_h1 = doc.styles['Heading 1']
    style_h1.font.name = 'Times New Roman'
    style_h1.font.size = Pt(15)
    style_h1.font.bold = True
    style_h1.font.color.rgb = RGBColor(0, 0, 0)
    style_h1.paragraph_format.space_before = Pt(18)
    style_h1.paragraph_format.space_after = Pt(12)
    style_h1.paragraph_format.keep_with_next = True

    style_h2 = doc.styles['Heading 2']
    style_h2.font.name = 'Times New Roman'
    style_h2.font.size = Pt(13.5)
    style_h2.font.bold = True
    style_h2.font.color.rgb = RGBColor(0, 0, 0)
    style_h2.paragraph_format.space_before = Pt(12)
    style_h2.paragraph_format.space_after = Pt(6)
    style_h2.paragraph_format.keep_with_next = True

    style_h3 = doc.styles['Heading 3']
    style_h3.font.name = 'Times New Roman'
    style_h3.font.size = Pt(13)
    style_h3.font.bold = True
    style_h3.font.color.rgb = RGBColor(0, 0, 0)
    style_h3.paragraph_format.space_before = Pt(8)
    style_h3.paragraph_format.space_after = Pt(4)
    style_h3.paragraph_format.keep_with_next = True

    def add_p(text, indent=True):
        p = doc.add_paragraph(text)
        if indent:
            p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.3
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

    # ----------------------------------------------------
    # MỤC LỤC TỰ ĐỘNG CHUẨN WORD (FIELD XML & PRE-RENDERED)
    # ----------------------------------------------------
    p_toc_title = doc.add_paragraph()
    p_toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_toc_title.add_run("MỤC LỤC")
    r_t.font.size = Pt(14)
    r_t.bold = True
    p_toc_title.paragraph_format.space_after = Pt(12)

    # Add Native Word TOC Field (Update Field / F9)
    add_native_word_toc_field(doc)

    # Pre-rendered Visual TOC matching BÀI MẪU.docx
    toc_items = [
        ("LỜI CẢM ƠN", "i"),
        ("LỜI CAM ĐOAN", "ii"),
        ("DANH MỤC CÁC BẢNG", "iii"),
        ("DANH MỤC CÁC HÌNH", "iv"),
        ("DANH MỤC CHỮ VIẾT TẮT", "v"),
        ("DANH MỤC PHỤ LỤC", "vi"),
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
        ("TÀI LIỆU THAM KHẢO", "37"),
        ("PHỤ LỤC A: Sơ đồ mặt bằng và Luồng luân chuyển hàng hóa Kho số 6", "39"),
        ("PHỤ LỤC B: Quy trình thao tác chuẩn (SOP) nhập kho ngoại quan U&I Logistics", "40"),
        ("PHỤ LỤC C: Phiếu khảo sát và Thống kê tần suất lỗi thao tác thực tế", "41"),
        ("PHỤ LỤC D: Biểu mẫu tem nhãn Barcode/QR Code đề xuất cải tiến", "42")
    ]

    for title, page_str in toc_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.line_spacing = 1.2
        p_item.paragraph_format.space_after = Pt(3)
        r_item = p_item.add_run(title)
        if title.startswith("CHƯƠNG") or title.startswith("PHỤ LỤC") or title in ["LỜI CẢM ƠN", "LỜI CAM ĐOAN", "LỜI MỞ ĐẦU", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO"]:
            r_item.bold = True
        
        dots_count = max(5, 80 - len(title))
        r_dots = p_item.add_run(" " + "." * dots_count + " " + page_str)
        r_dots.font.size = Pt(11)
        r_dots.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_page_break()

    # THÂN BÀI SỬ DỤNG HEADING STYLES CHUẨN WORD
    doc.add_heading("CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN VỀ CÔNG TY CỔ PHẦN LOGISTICS U&I", level=1)
    doc.add_heading("1.1 Lịch sử hình thành và phát triển", level=2)
    doc.add_heading("1.1.1 Tổng quan về Công ty Cổ phần Logistics U&I", level=3)
    add_p("Nội dung chi tiết giới thiệu về Công ty Cổ phần Logistics U&I...")

    doc.add_heading("CHƯƠNG 2: PHÂN TÍCH THỰC TRẠNG VÀ CÔNG VIỆC THỰC TẬP AT DOANH NGHIỆP", level=1)
    doc.add_heading("2.1 Cơ sở lý luận về quản trị kho vận và mô hình Lean Warehouse", level=2)
    add_p("Nội dung chi tiết cơ sở lý luận...")

    doc.save(output_filename)
    print(f"Native Word Automatic TOC Report saved into '{output_filename}' successfully!")

if __name__ == "__main__":
    create_native_toc_report()
