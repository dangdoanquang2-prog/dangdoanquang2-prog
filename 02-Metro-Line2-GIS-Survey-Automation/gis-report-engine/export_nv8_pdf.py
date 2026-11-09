import os
import sys
import win32com.client
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"
docx_path = os.path.join(base_dir, "Bao_cao_Tong_hop_Nhiem_vu_8_Ga_ST01_Chuan.docx")
pdf_path = os.path.join(base_dir, "Bao_cao_Tong_hop_Nhiem_vu_8_Ga_ST01_Chuan.pdf")

print(f"Bắt đầu chuyển đổi DOCX -> PDF:\n  DOCX: {docx_path}\n  PDF:  {pdf_path}")

pythoncom.CoInitialize()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = False

try:
    doc = word.Documents.Open(docx_path)
    # wdFormatPDF = 17
    doc.SaveAs(pdf_path, FileFormat=17)
    doc.Close(False)
    print(f">>> XUẤT THÀNH CÔNG PDF: {pdf_path}")
    print(f"    Dung lượng: {os.path.getsize(pdf_path):,} bytes")
except Exception as e:
    print(f"LỖI: {e}")
finally:
    word.Quit()
    pythoncom.CoUninitialize()
