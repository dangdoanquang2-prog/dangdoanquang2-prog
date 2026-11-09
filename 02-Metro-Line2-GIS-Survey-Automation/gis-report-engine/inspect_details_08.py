import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"D:\baocaotudong\08. Phat sinh-thu hut"

print("==================================================")
print("CHI TIẾT 6 PLACEMARK TRONG TỪNG GA Ở FILE KMZ")
print("==================================================")
kmz_path = os.path.join(base_dir, "MRT2S-PS-TH.kmz")
with zipfile.ZipFile(kmz_path, 'r') as z:
    kml_str = z.read('doc.kml').decode('utf-8', errors='ignore')

import re
kml_clean = re.sub(r'\sxmlns="[^"]+"', '', kml_str, count=1)
root = ET.fromstring(kml_clean)

folders = root.findall('.//Folder/Folder')
print(f"Số folder con tương ứng các Ga: {len(folders)}")

kmz_data = {}
for f in folders:
    g_name = f.findtext('name', default='').strip()
    pms = f.findall('.//Placemark')
    pm_list = []
    for pm in pms:
        name = pm.findtext('name', default='').strip()
        desc = pm.findtext('description', default='').strip()
        coords = pm.findtext('.//Point/coordinates', default='').strip()
        pm_list.append({'name': name, 'coords': coords, 'desc': desc})
    kmz_data[g_name] = pm_list

for g_name, pms in list(kmz_data.items())[:5]:
    print(f"\nGa: {g_name} ({len(pms)} POIs):")
    for p in pms:
        print(f"   - {p['name']:25s} | Coords: {p['coords']}")

print("\n... và tương tự cho tất cả 27 Ga.")

print("\n==================================================")
print("KIỂM TRA EXIF TỌA ĐỘ VÀ NỘI DUNG ẢNH TRONG THƯ MỤC ST01")
print("==================================================")
st01_dir = os.path.join(base_dir, "ST01")
sample_files = [os.path.join(st01_dir, f) for f in os.listdir(st01_dir) if f.lower().endswith('.jpg')][:10]

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif = image._getexif()
        if not exif:
            return None, None
        exif_data = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value
        
        gps_info = {}
        if 'GPSInfo' in exif_data:
            for key in exif_data['GPSInfo'].keys():
                sub_tag = GPSTAGS.get(key, key)
                gps_info[sub_tag] = exif_data['GPSInfo'][key]
        return exif_data.get('DateTimeOriginal') or exif_data.get('DateTime'), gps_info
    except Exception as e:
        return None, None

gps_count = 0
for f in os.listdir(st01_dir):
    if f.lower().endswith('.jpg'):
        fp = os.path.join(st01_dir, f)
        dt, gps = get_exif_data(fp)
        if gps:
            gps_count += 1

print(f"Tổng số ảnh trong ST01: {len(os.listdir(st01_dir))}")
print(f"Số lượng ảnh có gắn tọa độ GPS EXIF: {gps_count}/{len(os.listdir(st01_dir))}")

# Check 3 sample images
for fp in sample_files[:3]:
    dt, gps = get_exif_data(fp)
    fname = os.path.basename(fp)
    print(f"  File: {fname[:35]}... | Time: {dt} | GPS keys: {list(gps.keys()) if gps else 'No GPS'}")

print("\n==================================================")
print("KIỂM TRA CÁC ẢNH SCREENSHOT TRONG 'ST01 MÔ TẢ'")
print("==================================================")
mota_dir = os.path.join(base_dir, "ST01 MÔ TẢ")
mota_files = os.listdir(mota_dir)
print(f"Danh sách các ảnh mô tả ({len(mota_files)} ảnh):")
for f in mota_files:
    fp = os.path.join(mota_dir, f)
    im = Image.open(fp)
    print(f"  - {f:35s} | Size: {im.size} | Mode: {im.mode}")
