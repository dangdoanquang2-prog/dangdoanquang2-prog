import sys
import os
import openpyxl
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

# Facilities in ST01_Số liệu.docx
facilities = [
    {"id": 1, "name": "Trường THCS Nguyễn Ảnh Thủ", "type": "School", "addr": "12/8 bis, Đông Hưng Thuận, Hồ Chí Minh, Vietnam"},
    {"id": 2, "name": "Trường THPT Phan Văn Hớn", "type": "School", "addr": "12/22 Tổ 57 KP4, Đông Hưng Thuận, Hồ Chí Minh, Vietnam"},
    {"id": 3, "name": "Trường THCS Hà Huy Tập", "type": "School", "addr": "54 Nguyễn Văn Quá Kp5 - ĐHT, P. Phú Thuận, Đông Hưng Thuận, Hồ Chí Minh, Vietnam"},
    {"id": 4, "name": "Hệ thống giáo dục ATY – Cơ sở Quận 12", "type": "School", "addr": "1/10 Huỳnh Tấn Chùa, Đông Hưng Thuận, Hồ Chí Minh 700000, Vietnam"},
    {"id": 5, "name": "Bệnh viện Đa khoa Tâm Trí Sài Gòn", "type": "Hospital", "addr": "171/3 Trường Chinh, Vinh Phuoc Pagoda, Đông Hưng Thuận, Hồ Chí Minh 71510, Vietnam"},
    {"id": 6, "name": "Chung cư Phu Cuong Home", "type": "Residential", "addr": "02 Đ. Song Hành, Đông Hưng Thuận, Hồ Chí Minh 70000, Vietnam"},
    {"id": 7, "name": "Khu chung cư Thái An", "type": "Residential", "addr": "Đ. Nguyễn Văn Quá, Đông Hưng Thuận, Hồ Chí Minh, Vietnam"},
    {"id": 8, "name": "Chung cư Moscow Tower", "type": "Residential", "addr": "19/1 Tân Thới Nhất 17, Phường, Quận 12, Hồ Chí Minh 700000, Vietnam"},
    {"id": 9, "name": "Chung cư Prosper Plaza", "type": "Residential", "addr": "22/14 Đ. Phan Văn Hớn, Đông Hưng Thuận, Hồ Chí Minh 70000, Vietnam"},
    {"id": 10, "name": "Co.opmart Phan Văn Hớn", "type": "Mall", "addr": "102 Đ. Phan Văn Hớn, Tân Thới Nhất, Quận 12, Hồ Chí Minh 71510, Vietnam"},
    {"id": 11, "name": "Chợ Lạc Quang", "type": "Market", "addr": "Hẻm 265 Khu Phố 33, Đông Hưng Thuận, Hồ Chí Minh, Vietnam"}
]

print("=== RÀ SOÁT DANH MỤC 11 CÔNG TRÌNH VÀ TÀI NGUYÊN TƯƠNG ỨNG ===")

# Check Excel G1
excel_path = r"D:\baocaotudong\08. Phat sinh-thu hut\Phat sinh -Thu hut_MRT2S.xlsx"
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb['Sheet1']
g1_excel = {}
for r in [4, 6, 8, 10, 12, 14]:
    t = ws.cell(r, 1).value
    n = ws.cell(r, 2).value
    a = ws.cell(r+1, 2).value
    g1_excel[t] = (n, a)

print("\n--- Đối chiếu với Excel G1: ---")
for t, (n, a) in g1_excel.items():
    print(f"  {t:15s}: {n} | {a}")

print("\n--- Nhận xét đối chiếu Excel và ST01_Số liệu: ---")
print("  * Excel G1 có 6 công trình tiêu biểu: Siêu thị BHX, BV Medic Hạnh Phúc, Thiên Nam Residence, Green Riverside Hotel, TH Phan Huy Ích, Cty Alen.")
print("  * File ST01_Số liệu.docx khảo sát thực địa mở rộng lên 11 công trình trọng điểm lớn hơn trong bán kính 1km (4 trường học, 1 BV lớn, 4 đại chung cư, 1 đại siêu thị Co.opmart, 1 chợ lớn).")
print("  * Điều này rất hợp lý cho mô hình PTV VISUM vì khảo sát thực tế cần bao quát các nguồn phát sinh - thu hút lưu lượng lớn nhất!")
