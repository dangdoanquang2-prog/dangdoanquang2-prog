import os
import sys
import fitz # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\baocaotudong\08. Phat sinh-thu hut\Bao_cao_Tong_hop_Nhiem_vu_8_Ga_ST01_Chuan.pdf"
preview_dir = r"D:\baocaotudong\output\preview_nv8_st01"
os.makedirs(preview_dir, exist_ok=True)

if not os.path.exists(pdf_path):
    print(f"Chưa tìm thấy file PDF: {pdf_path}")
    sys.exit(1)

doc = fitz.open(pdf_path)
print(f"Tổng số trang PDF: {len(doc)}")

for page_num in range(len(doc)):
    page = doc[page_num]
    pix = page.get_pixmap(dpi=150)
    out_img = os.path.join(preview_dir, f"page_{page_num + 1:02d}.png")
    pix.save(out_img)
    print(f"Đã render trang {page_num + 1:02d} -> {out_img}")

print("=== HOÀN TẤT RENDER PREVIEW ===")
