import sys
import os
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"D:\baocaotudong\08. Phat sinh-thu hut\ST01_Số liệu.docx"
doc = Document(file_path)

print(f"=== CHI TIẾT TẤT CẢ CÁC CÔNG TRÌNH TRONG: ST01_Số liệu.docx ===")

# Check doc structure in flow
print("\n--- DUYỆT THEO THỨ TỰ NỘI DUNG (PARAGRAPHS VÀ TABLES) ---")

body_elements = []
for child in doc.element.body:
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        # find corresponding paragraph
        txt = child.text or ""
        # or find from doc.paragraphs
        body_elements.append(('p', child))
    elif tag == 'tbl':
        body_elements.append(('tbl', child))

print(f"Tổng số phần tử body: {len(body_elements)}")

# Let's inspect each table safely
facility_count = 0
for t_idx, tbl in enumerate(doc.tables):
    rows = tbl.rows
    num_rows = len(rows)
    print(f"\n=======================================================")
    print(f"BẢNG #{t_idx+1} ({num_rows} hàng)")
    print(f"=======================================================")
    for r_idx, row in enumerate(rows):
        cells_text = [c.text.strip().replace('\n', ' ') for c in row.cells]
        # deduplicate adjacent
        dedup = []
        for ct in cells_text:
            if not dedup or ct != dedup[-1]:
                dedup.append(ct)
        line = " | ".join(dedup)
        if len(line) > 130:
            line = line[:125] + "..."
        print(f"  R{r_idx:02d}: {line}")

print("\n--- KIỂM TRA HÌNH ẢNH TRONG FILE ---")
# Extract info about embedded images
image_parts = []
for rel in doc.part.rels.values():
    if "image" in rel.target_ref:
        img_part = rel.target_part
        image_parts.append((rel.target_ref, len(img_part.blob), img_part.content_type))

print(f"Tổng số ảnh nhúng: {len(image_parts)}")
for idx, (ref, size, ctype) in enumerate(image_parts):
    print(f"  Ảnh {idx+1}: ref={ref} | size={size:,} bytes | type={ctype}")
