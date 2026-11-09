import sys
import os
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\baocaotudong\08. Phat sinh-thu hut\ST01_Số liệu.docx"
doc = Document(file_path)

print("=== LIÊN KẾT CÔNG TRÌNH - BẢNG BIỂU - HÌNH ẢNH TRONG DOCX ===")

# Traverse the document body elements in sequence
current_facility = None
current_section = None

for elem in doc.element.body:
    tag = elem.tag.split('}')[-1]
    if tag == 'p':
        text = elem.text or ""
        # check runs text
        run_texts = [r.text for r in elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if r.text]
        full_text = "".join(run_texts).strip()
        
        # check blip (image)
        blips = elem.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
        embed_ids = [b.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') for b in blips]
        
        if full_text.startswith('A. Quy mô'):
            current_section = 'A'
        elif full_text.startswith('B. Hình ảnh'):
            current_section = 'B'
            print(f"   [Mục B - Hình ảnh] Text: {full_text}")
            
        if embed_ids:
            for eid in embed_ids:
                rel = doc.part.rels.get(eid)
                target = rel.target_ref if rel else 'unknown'
                target_part = rel.target_part if rel else None
                sz = len(target_part.blob) if target_part else 0
                print(f"      ==> EMBEDDED IMAGE: id={eid}, file={target}, size={sz:,} bytes")
                
    elif tag == 'tbl':
        # check if this is facility info
        first_cell = elem.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')
        tc_texts = [t.text for t in first_cell.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
        c_text = "".join(tc_texts).strip()
        
        # look for 'Tên công trình'
        all_cells = [t.text for t in elem.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
        row_str = " ".join(all_cells)
        if 'Tên công trình' in row_str:
            # find facility name
            for i, word in enumerate(all_cells):
                if 'Tên công trình' in word and i+1 < len(all_cells):
                    current_facility = all_cells[i+1]
                    print(f"\n>>> CÔNG TRÌNH: {current_facility}")
                    break
