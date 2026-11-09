import sys
import os
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\baocaotudong\08. Phat sinh-thu hut\ST01_Số liệu.docx"
doc = Document(file_path)

print(f"=== PHÂN TÍCH TỔNG QUAN FILE: ST01_Số liệu.docx ===")
print(f"Số lượng đoạn văn (Paragraphs): {len(doc.paragraphs)}")
print(f"Số lượng bảng (Tables): {len(doc.tables)}")
print(f"Số lượng Sections: {len(doc.sections)}")

# Check inline images
img_count = 0
for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        img_count += 1
print(f"Số lượng hình ảnh nhúng trong tài liệu: {img_count}")

print("\n--- CẤU TRÚC ĐOẠN VĂN & TIÊU ĐỀ CHÍNH ---")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if txt:
        # Check if heading or bold
        is_heading = p.style.name.startswith('Heading')
        runs_bold = any(r.bold for r in p.runs)
        prefix = f"[P{i:03d}|{p.style.name}]"
        if len(txt) > 100:
            print(f"{prefix} {txt[:95]}...")
        else:
            print(f"{prefix} {txt}")

print("\n--- CHI TIẾT TỪNG BẢNG BIỂU ---")
for t_idx, tbl in enumerate(doc.tables):
    rows = len(tbl.rows)
    cols = len(tbl.columns)
    print(f"\n>>> BẢNG {t_idx+1}: {rows} hàng x {cols} cột")
    for r_idx in range(min(rows, 10)):
        cells = [tbl.rows[r_idx].cells[c].text.strip().replace('\n', ' ') for c in range(cols)]
        # eliminate duplicate text from merged cells
        unique = []
        for c in cells:
            if not unique or c != unique[-1]:
                unique.append(c)
        row_str = " | ".join(unique)
        if len(row_str) > 120:
            row_str = row_str[:115] + "..."
        print(f"   [Hàng {r_idx:2d}]: {row_str}")
    if rows > 10:
        print(f"   ... ({rows - 10} hàng tiếp theo)")
