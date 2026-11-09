import sys
import os
import fitz # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"D:\baocaotudong\08. Phat sinh-thu hut\BC_KhaoSat_PhatSinhThuHut_Ga_ST01_Chuan.pdf"
art_dir = r"C:\Users\Dell\.gemini\antigravity-ide\brain\b20a09a9-197b-42a1-8148-51c14105555b"

doc = fitz.open(pdf_path)
print(f"Tổng số trang PDF: {len(doc)}")

# Render each page to PNG preview
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    out_png = os.path.join(art_dir, f"st01_page_{i+1:02d}.png")
    pix.save(out_png)
    print(f"  Trang {i+1:02d}: {pix.width}x{pix.height} -> st01_page_{i+1:02d}.png")

doc.close()
print("Đã xuất xong toàn bộ ảnh preview các trang!")
