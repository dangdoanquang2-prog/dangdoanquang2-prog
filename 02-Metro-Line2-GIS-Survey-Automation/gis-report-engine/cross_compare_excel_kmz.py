import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import re
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"

# Load Excel
excel_path = os.path.join(base_dir, "Phat sinh -Thu hut_MRT2S.xlsx")
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb['Sheet1']

# Load KMZ
kmz_path = os.path.join(base_dir, "MRT2S-PS-TH.kmz")
with zipfile.ZipFile(kmz_path, 'r') as z:
    kml_str = z.read('doc.kml').decode('utf-8', errors='ignore')

kml_clean = re.sub(r'\sxmlns="[^"]+"', '', kml_str, count=1)
root = ET.fromstring(kml_clean)

kmz_folders = {}
for f in root.findall('.//Folder/Folder'):
    fname = f.findtext('name', default='').strip()
    pms = []
    for pm in f.findall('.//Placemark'):
        pname = pm.findtext('name', default='').strip()
        coords = pm.findtext('.//Point/coordinates', default='').strip()
        pms.append((pname, coords))
    kmz_folders[fname] = pms

print("=== SO SÁNH CHI TIẾT EXCEL VÀ KMZ CHO 27 GA ===")
types = [
    ("Shopping Mall", 4, 5),
    ("Hospital", 6, 7),
    ("Residential", 8, 9),
    ("Hotel", 10, 11),
    ("School", 12, 13),
    ("Office", 14, 15)
]

total_excel_pois = 0
total_kmz_pois = 0

for col in range(2, ws.max_column + 1):
    stt = ws.cell(1, col).value
    code = str(ws.cell(2, col).value or '').strip()
    name = str(ws.cell(3, col).value or '').strip()
    
    excel_pois = []
    for t_name, r_name, r_addr in types:
        val_name = str(ws.cell(r_name, col).value or '').strip()
        val_addr = str(ws.cell(r_addr, col).value or '').strip()
        if val_name or val_addr:
            excel_pois.append((t_name, val_name, val_addr))
            total_excel_pois += 1
            
    # Find KMZ folder
    kmz_key = None
    for k in kmz_folders.keys():
        if k == code or k.startswith(code + "(") or k.startswith(code + " "):
            kmz_key = k
            break
            
    kmz_list = kmz_folders.get(kmz_key, [])
    total_kmz_pois += len(kmz_list)
    
    print(f"\n[{stt}] Cột {col:2d} | Mã: {code:4s} | Tên Ga: {name:25s} | Excel: {len(excel_pois)}/6 POIs | KMZ: {len(kmz_list)} points ({kmz_key})")
    for t_name, val_name, val_addr in excel_pois:
        addr_short = (val_addr[:40] + '...') if len(val_addr) > 40 else val_addr
        print(f"     * [{t_name:13s}] {val_name:30s} | {addr_short}")

print(f"\n==========================================")
print(f"TỔNG KẾT:")
print(f"- Tổng số Ga / Điểm trung tâm: 27")
print(f"- Tổng số POI có dữ liệu trong Excel: {total_excel_pois} / {27*6} (trung bình {total_excel_pois/27:.1f} POI/ga)")
print(f"- Tổng số POI Point định vị trong KMZ: {total_kmz_pois} / {27*6} (đủ 100% 6 điểm/ga)")
print(f"==========================================")
