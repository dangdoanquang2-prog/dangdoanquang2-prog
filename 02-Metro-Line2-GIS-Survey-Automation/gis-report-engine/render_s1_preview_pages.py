import os
import sys
import win32com.client
import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

docx_path = os.path.abspath(r"d:\baocaotudong\output\BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.docx")
pdf_path = os.path.abspath(r"d:\baocaotudong\output\BC_KhaoSat_HienTrang_Ga_ST01_PhanVanHon.pdf")
preview_dir = r"d:\baocaotudong\preview_s1_pages"
os.makedirs(preview_dir, exist_ok=True)

print("Converting DOCX to PDF using Word COM...")
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
try:
    doc = word.Documents.Open(docx_path)
    # wdFormatPDF = 17
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close()
    print("Exported PDF successfully:", pdf_path)
finally:
    word.Quit()

print("Rendering PDF pages to PNG using PyMuPDF...")
pdf_doc = fitz.open(pdf_path)
print(f"Total pages in PDF: {len(pdf_doc)}")

page_files = []
for page_num in range(len(pdf_doc)):
    page = pdf_doc[page_num]
    pix = page.get_pixmap(dpi=150)
    out_img = os.path.join(preview_dir, f"page_{page_num+1:02d}.png")
    pix.save(out_img)
    page_files.append(out_img)
    print(f"Page {page_num+1:02d} rendered -> {out_img}")

pdf_doc.close()
print("All pages rendered successfully!")
