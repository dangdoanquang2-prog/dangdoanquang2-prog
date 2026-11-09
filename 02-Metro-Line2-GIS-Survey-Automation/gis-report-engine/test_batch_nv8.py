import sys
import os
import io
import re
import datetime
from PIL import Image
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"
sl_base = os.path.join(base_dir, "Số liệu")
ct_base = os.path.join(base_dir, "Hình ảnh công trình")
tc_base = os.path.join(base_dir, "Hình ảnh tiếp cận mặt bằng")

STATION_NAMES = {
    "ST01": "Phan Văn Hớn",
    "ST02": "Đông Hưng Thuận",
    "ST03": "An Sương",
    "ST04": "Nguyễn Ảnh Thủ",
    "ST05": "Nguyễn Thị Sóc",
    "ST06": "Bà Triệu",
    "ST07": "Lý Thường Kiệt",
    "ST08": "Nguyễn Thị Nuôi",
    "ST09": "Vòng cung Tây Bắc 2",
    "ST10": "Vành Đai 3",
    "ST11": "An Hạ",
    "ST12": "Tân Phú Trung",
    "ST13": "Hương Lộ 2",
    "ST14": "Đào Thị Kiểm",
    "ST15": "Lê Minh Nhựt",
    "ST16": "Tân Thông Hội",
    "ST17": "Trần Tử Bình",
    "ST18": "Huỳnh Văn Cọ",
    "ST19": "Củ Chi",
    "ST20": "BV Củ Chi",
    "ST21": "Nguyễn Thị Rành",
    "ST22": "Tân An Hội",
    "ST23": "Ba Sa",
    "ST24": "Phước Hiệp",
    "ST25": "Tỉnh Lộ 7",
    "ST26": "Thái Mỹ"
}

def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=35, bottom=35, left=50, right=50):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), val)
            border.set(qn('w:sz'), sz)
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), color)
            borders.append(border)
        tblPr[0].append(borders)

def add_scaled_picture(p, img_source, max_w_in=3.35, max_h_in=2.45):
    try:
        if isinstance(img_source, (bytes, bytearray)):
            im = Image.open(io.BytesIO(img_source))
            stream = io.BytesIO(img_source)
        else:
            im = Image.open(img_source)
            stream = img_source
            
        w_px, h_px = im.size
        aspect = w_px / h_px
        
        calc_w = max_w_in
        calc_h = calc_w / aspect
        if calc_h > max_h_in:
            calc_h = max_h_in
            calc_w = calc_h * aspect
            
        run = p.add_run()
        run.add_picture(stream, width=Inches(calc_w), height=Inches(calc_h))
        return True
    except Exception as e:
        return False

print("Helper functions defined successfully.")
