# -*- coding: utf-8 -*-
"""
Script xây dựng toàn diện file Báo cáo Master HKDN:
HOÀN THIỆN QUY TRÌNH GIẢI QUYẾT KHIẾU NẠI CỦA KHÁCH HÀNG TẠI CÔNG TY CỔ PHẦN LOGISTICS U&I

Bao gồm đầy đủ 100% các phần:
1. Bìa chính & Bìa phụ
2. Lời cảm ơn (chuẩn Ths. Phạm Thị Huyền Trân, Cô Đoàn Thị Mộng Dung)
3. Lời cam đoan (chuẩn ảnh mẫu người dùng cung cấp)
4. Mục lục tự động, Danh mục hình, Danh mục bảng, Danh mục từ viết tắt
5. Lời mở đầu (chuẩn 5 phần)
6. Chương 1: Giới thiệu tổng quan về U&I Logistics (1.1 - 1.7)
7. Chương 2: Phân tích thực trạng quy trình giải quyết khiếu nại (2.1 - 2.4)
8. Chương 3: Đề xuất giải pháp hoàn thiện quy trình (3.1 - 3.6):
   - 3.1.1 được bổ sung đầy đủ, học thuật, gãy gọn
   - 3.1.2 - 3.5 chuẩn xác từ file HKDN.docx
   - 3.6 Áp dụng thực nghiệm & phân tích đối chiếu Case Khách hàng Cheong Ming chuyên sâu
9. KẾT LUẬN VÀ KIẾN NGHỊ (Kết luận tổng kết, Kiến nghị cho U&I, Kiến nghị cho UTH)
10. TÀI LIỆU THAM KHẢO
11. PHỤ LỤC (Phụ lục A: Phiếu BM03; Phụ lục B: Hồ sơ Case Cheong Ming)
"""

import os
import re
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

BLACK_COLOR = RGBColor(0, 0, 0)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>\n'
                      f'  <w:top w:w="{top}" w:type="dxa"/>\n'
                      f'  <w:bottom w:w="{bottom}" w:type="dxa"/>\n'
                      f'  <w:left w:w="{left}" w:type="dxa"/>\n'
                      f'  <w:right w:w="{right}" w:type="dxa"/>\n'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F2F2"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def format_table_academic(table, col_widths=None):
    try:
        table.style = 'Table Grid'
    except Exception:
        pass
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    tblPr = table._tbl.tblPr
    existing_borders = tblPr.find(qn('w:tblBorders'))
    if existing_borders is not None:
        tblPr.remove(existing_borders)
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="1B365D"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1B365D"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)

    num_rows = len(table.rows)
    if num_rows > 0:
        trPr0 = table.rows[0]._tr.get_or_add_trPr()
        trPr0.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        is_header = (r_idx == 0)

        for c_idx, cell in enumerate(row.cells):
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            if col_widths and c_idx < len(col_widths):
                cell.width = col_widths[c_idx]
            
            if is_header:
                set_cell_shading(cell, "1B365D")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.15
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(11)
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if r_idx % 2 == 0:
                    set_cell_shading(cell, "F8F9FA")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.2
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        r.font.size = Pt(11)
                        r.font.color.rgb = BLACK_COLOR

def add_footer_page_number(sec):
    footer = sec.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(0)
    p.text = ""
    r = p.add_run()
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    p._p.append(fldSimple)

def setup_styles(doc):
    styles_elem = doc.styles.element
    for child in list(styles_elem):
        sid = child.get(qn('w:styleId'))
        if sid in ['TOC1', 'TOC2', 'TOC3', 'TOC4']:
            styles_elem.remove(child)

    # TOC 1
    toc1_xml = parse_xml(f'''
    <w:style {nsdecls("w")} w:type="paragraph" w:styleId="TOC1">
        <w:name w:val="toc 1"/>
        <w:basedOn w:val="Normal"/>
        <w:pPr>
            <w:spacing w:before="120" w:after="40"/>
            <w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9355"/></w:tabs>
        </w:pPr>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:b/>
            <w:bCs/>
            <w:color w:val="000000"/>
            <w:sz w:val="26"/>
            <w:szCs w:val="26"/>
        </w:rPr>
    </w:style>
    ''')

    # TOC 2
    toc2_xml = parse_xml(f'''
    <w:style {nsdecls("w")} w:type="paragraph" w:styleId="TOC2">
        <w:name w:val="toc 2"/>
        <w:basedOn w:val="Normal"/>
        <w:pPr>
            <w:ind w:left="340"/>
            <w:spacing w:before="60" w:after="20"/>
            <w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9355"/></w:tabs>
        </w:pPr>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:b/>
            <w:bCs/>
            <w:color w:val="000000"/>
            <w:sz w:val="25"/>
            <w:szCs w:val="25"/>
        </w:rPr>
    </w:style>
    ''')

    # TOC 3
    toc3_xml = parse_xml(f'''
    <w:style {nsdecls("w")} w:type="paragraph" w:styleId="TOC3">
        <w:name w:val="toc 3"/>
        <w:basedOn w:val="Normal"/>
        <w:pPr>
            <w:ind w:left="680"/>
            <w:spacing w:before="40" w:after="20"/>
            <w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9355"/></w:tabs>
        </w:pPr>
        <w:rPr>
            <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
            <w:i/>
            <w:iCs/>
            <w:color w:val="000000"/>
            <w:sz w:val="24"/>
            <w:szCs w:val="24"/>
        </w:rPr>
    </w:style>
    ''')

    styles_elem.append(toc1_xml)
    styles_elem.append(toc2_xml)
    styles_elem.append(toc3_xml)

print("Setup helper functions ready.")
