import os
import sys
import fitz

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"d:\baocaotudong\output\BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.pdf"
doc = fitz.open(pdf_path)

for i, page in enumerate(doc):
    text = page.get_text()
    first_few_lines = [l.strip() for l in text.split("\n") if l.strip()][:3]
    last_few_lines = [l.strip() for l in text.split("\n") if l.strip()][-2:]
    images = page.get_images()
    print(f"--- PAGE {i+1} --- (Images: {len(images)})")
    print(f"  Start: {' | '.join(first_few_lines)}")
    print(f"  End:   {' | '.join(last_few_lines)}")
