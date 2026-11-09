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

def create_full_sample_docx(output_filename="BAO_CAO_MAU_HOAN_CHINH_FULL_v2.docx"):
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

    # 1. COVER PAGE
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH")
    r1.font.size = Pt(13)
    r1.font.name = 'Times New Roman'

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
    r4 = p4.add_run("TÊN ĐỀ TÀI")
    r4.font.size = Pt(22)
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
    r8 = p8.add_run("\nTP. Hồ Chí Minh – …/ 20..")
    r8.font.size = Pt(13)
    r8.bold = True
    r8.italic = True

    doc.add_page_break()

    # CHƯƠNG 1 & BẢNG 1.1 WITH NO-SPLIT RULES
    p_ch1 = doc.add_paragraph()
    r_ch1 = p_ch1.add_run("CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN VỀ DOANH NGHIỆP THỰC TẬP")
    r_ch1.font.size = Pt(14)
    r_ch1.bold = True

    p_11 = doc.add_paragraph()
    r_11 = p_11.add_run("1.1 Lịch sử hình thành và phát triển")
    r_11.bold = True

    p_11_t = doc.add_paragraph("Doanh nghiệp được thành lập và phát triển qua nhiều giai đoạn quan trọng, khẳng định vị thế uy tín trên thị trường.")
    p_11_t.paragraph_format.first_line_indent = Cm(1.27)

    # Caption Bảng 1.1 (với keep_with_next)
    p_t1 = doc.add_paragraph()
    r_t1 = p_t1.add_run("Bảng 1.1 Thống kê cơ cấu nhân sự theo trình độ chuyên môn")
    r_t1.bold = True
    r_t1.font.size = Pt(12)

    tbl1 = doc.add_table(rows=4, cols=4)
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
        ["1", "Sau Đại học & Đại học", "120", "60.0%"],
        ["2", "Cao đẳng & Trung cấp", "50", "25.0%"],
        ["3", "Lao động khác", "30", "15.0%"]
    ]
    for r_idx, r_data in enumerate(data1):
        for c_idx, val in enumerate(r_data):
            cell = tbl1.cell(r_idx + 1, c_idx)
            p = cell.paragraphs[0]
            p.text = val
            p.runs[0].font.size = Pt(11)
            if c_idx in [0, 2, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_s1 = doc.add_paragraph("Nguồn: Phòng Nhân sự doanh nghiệp cung cấp, 2026")
    p_s1.runs[0].font.italic = True
    p_s1.runs[0].font.size = Pt(11)

    # Apply No-Split Rule
    format_table_no_split(tbl1, caption_paragraph=p_t1, source_paragraph=p_s1)

    doc.save(output_filename)
    print(f"Full sample document with Table No-Split rule saved into '{output_filename}'!")

if __name__ == "__main__":
    create_full_sample_docx()
