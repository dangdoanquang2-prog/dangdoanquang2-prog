import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
from docx import Document

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"

print("==================================================")
print("1. PHÂN TÍCH FILE KMZ: MRT2S-PS-TH.kmz")
print("==================================================")
kmz_path = os.path.join(base_dir, "MRT2S-PS-TH.kmz")
with zipfile.ZipFile(kmz_path, 'r') as z:
    kml_bytes = z.read('doc.kml')

# remove xmlns or handle with default
kml_str = kml_bytes.decode('utf-8', errors='ignore')
# Remove namespace for easy querying
import re
kml_str_clean = re.sub(r'\sxmlns="[^"]+"', '', kml_str, count=1)
root = ET.fromstring(kml_str_clean)

doc_elem = root.find('Document')
folders = doc_elem.findall('Folder') if doc_elem is not None else root.findall('.//Folder')
print(f"Tổng số Folder lớn trong KMZ: {len(folders)}")
for idx, f in enumerate(folders):
    fname = f.findtext('name', default='Unknown')
    subfolders = f.findall('Folder')
    placemarks = f.findall('.//Placemark')
    print(f"  [{idx+1}] Folder: '{fname}' | Subfolders: {len(subfolders)} | Tổng Placemark bên trong: {len(placemarks)}")
    for sf in subfolders:
        sf_name = sf.findtext('name', default='Unknown')
        sf_pms = sf.findall('.//Placemark')
        print(f"       + Subfolder: '{sf_name}' ({len(sf_pms)} placemarks)")

all_pms = root.findall('.//Placemark')
print(f"\nTổng số Placemark toàn file: {len(all_pms)}")

# Check types of geometries in placemarks
geom_counts = {}
for pm in all_pms:
    geoms = []
    if pm.find('.//Point') is not None: geoms.append('Point')
    if pm.find('.//LineString') is not None: geoms.append('LineString')
    if pm.find('.//Polygon') is not None: geoms.append('Polygon')
    g_key = '+'.join(geoms) if geoms else 'None'
    geom_counts[g_key] = geom_counts.get(g_key, 0) + 1
print("Phân bố hình học:", geom_counts)

# Sample some placemarks from each folder
for idx, f in enumerate(folders):
    fname = f.findtext('name', default='Unknown')
    pms = f.findall('.//Placemark')
    print(f"\n--- Mẫu dữ liệu trong Folder: '{fname}' (hiển thị tối đa 5) ---")
    for pm in pms[:5]:
        pname = pm.findtext('name', default='(No Name)').strip()
        desc = pm.findtext('description', default='').strip()
        pt = pm.findtext('.//Point/coordinates', default='').strip()
        ls = pm.findtext('.//LineString/coordinates', default='').strip()
        poly = pm.findtext('.//Polygon/outerBoundaryIs/LinearRing/coordinates', default='').strip()
        geo_info = ""
        if pt: geo_info = f"Point({pt})"
        elif ls: geo_info = f"LineString(pts={len(ls.split())})"
        elif poly: geo_info = f"Polygon(pts={len(poly.split())})"
        print(f"  * PM: {pname:35s} | Geo: {geo_info:25s} | Desc: {desc[:60]}")

print("\n==================================================")
print("2. PHÂN TÍCH FILE EXCEL: Phat sinh -Thu hut_MRT2S.xlsx")
print("==================================================")
excel_path = os.path.join(base_dir, "Phat sinh -Thu hut_MRT2S.xlsx")
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb['Sheet1']

print(f"Kích thước bảng: {ws.max_row} hàng x {ws.max_column} cột")
headers_col1 = [ws.cell(r, 1).value for r in range(1, 16)]
print("Các loại hàng (Cột A):")
for r, h in enumerate(headers_col1, 1):
    print(f"  Hàng {r:2d}: {h}")

stations = []
for col in range(2, ws.max_column + 1):
    stt = ws.cell(1, col).value
    code = ws.cell(2, col).value
    name = ws.cell(3, col).value
    if code or name:
        stations.append({
            'col': col,
            'stt': stt,
            'code': code,
            'name': name
        })

print(f"\nTổng số cột Ga khảo sát trong Excel: {len(stations)}")
for s in stations:
    col = s['col']
    # đếm số công trình có dữ liệu trong cột này
    poi_types = ['Shopping Mall', 'Hospital', 'Residential', 'Hotel', 'School', 'Office']
    pois = {}
    for r_poi, p_type in zip([4, 6, 8, 10, 12, 14], poi_types):
        p_name = ws.cell(r_poi, col).value
        p_addr = ws.cell(r_poi+1, col).value
        if p_name or p_addr:
            pois[p_type] = (str(p_name or '').strip(), str(p_addr or '').strip())
    s['pois'] = pois
    print(f"  Col {col:2d} | STT: {s['stt']} | Mã: {s['code']:4s} | Tên Ga: {str(s['name']):25s} | Số công trình có: {len(pois)}/6")

print("\n==================================================")
print("3. PHÂN TÍCH CÁC THƯ MỤC HÌNH ẢNH & DỮ LIỆU ĐI KÈM TRONG 08")
print("==================================================")
subdirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
print(f"Các thư mục con trong '08. Phat sinh-thu hut': {subdirs}")
for sd in subdirs:
    sd_path = os.path.join(base_dir, sd)
    files = os.listdir(sd_path)
    exts = {}
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        exts[ext] = exts.get(ext, 0) + 1
    print(f"\nThư mục: '{sd}' (Tổng {len(files)} files, định dạng: {exts})")
    print("  Một số file mẫu:")
    for f in files[:10]:
        fp = os.path.join(sd_path, f)
        print(f"    - {f} ({os.path.getsize(fp)} bytes)")
