# -*- coding: utf-8 -*-
"""
Script to build the FULL, SEAMLESS MASTER REPORT for the HKDN group at UTH.
Integrates:
- Lời cảm ơn, Lời cam đoan, Lời mở đầu
- Chương 1 (Nội dung gốc của nhóm)
- Chương 2 (Nội dung gốc của nhóm với 5 case KN01-KN05 và Bảng 2.1 - 2.4)
- Chương 3 (Nội dung gốc của nhóm + Hoàn thiện 3.1.1, 3.4, 3.5, 3.6 Case study thực nghiệm & Đánh giá hiệu quả)
- KẾT LUẬN VÀ KIẾN NGHỊ
- PHỤ LỤC A (Phiếu BM03-QT06/KD hoàn chỉnh)
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

print("Helper functions defined successfully")
