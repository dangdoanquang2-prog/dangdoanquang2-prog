import os
import sys
import openpyxl
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import geopandas as gpd
from shapely.geometry import Point

sys.stdout.reconfigure(encoding='utf-8')

# Affine transformation matrix from EPSG:3857 to pixel coordinates of the base image
M_x = np.array([8.31954594e-01, 5.47834905e-03, -9.88015881e+06])
M_y = np.array([3.92867113e-02, -6.00650298e-01, 2.63251612e+05])

wb = openpyxl.load_workbook(r"D:\baocaotudong\Ga của Quân\Ga 1.xlsx", data_only=True)
ws = wb['ĐIỀU KIỆN KẾT NỐI XE BUÝT (Resp']

coords = []
bus_data = []
for r in range(2, ws.max_row + 1):
    c = ws.cell(r, 7).value
    st = ws.cell(r, 9).value
    lines = ws.cell(r, 12).value
    if c:
        parts = str(c).replace(';', ',').split(',')
        lat, lon = float(parts[0].strip()), float(parts[1].strip())
        coords.append((lon, lat))
        clean_st = str(st).split(',')[0].strip().replace('Phan Hữu Ích', 'Phan Huy Ích')
        bus_data.append({
            'code': f'B{r-1}',
            'street': clean_st,
            'lines': str(lines).strip() if lines else '',
            'lat': lat, 'lon': lon
        })

gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in coords], crs='EPSG:4326').to_crs(epsg=3857)
coords_3857 = np.array([(p.x, p.y) for p in gdf.geometry])
X = np.hstack([coords_3857, np.ones((len(coords_3857), 1))])
pred_x = X @ M_x
pred_y = X @ M_y

for i in range(len(bus_data)):
    bus_data[i]['px'] = pred_x[i]
    bus_data[i]['py'] = pred_y[i]

# Load base image (original clean extract)
base_img_path = r"D:\baocaotudong\scratch\word\media\image8.png"
im = Image.open(base_img_path).convert('RGB')
draw = ImageDraw.Draw(im)

# Fonts
font_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
font_code = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
font_text = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
font_marker = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)
font_marker_sm = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)

# Offsets for opposite-direction pairs across streets
offsets = {
    'B4': (14, -14),
    'B6': (-14, 14),
    'B9': (-16, 0),
    'B14': (16, 0),
    'B10': (-16, 0),
    'B13': (16, 0),
    'B11': (15, 0),
    'B12': (-15, 0),
    'B15': (12, -12),
    'B24': (-12, 12),
    'B19': (0, -15),
    'B21': (0, 15),
}

# 1. Draw markers on map for all 24 stops
BOX_SIZE = 30
for b in bus_data:
    code = b['code']
    dx, dy = offsets.get(code, (0, 0))
    cx = b['px'] + dx
    cy = b['py'] + dy
    
    x0 = int(round(cx - BOX_SIZE / 2))
    y0 = int(round(cy - BOX_SIZE / 2))
    x1 = x0 + BOX_SIZE
    y1 = y0 + BOX_SIZE
    
    # Blue box with white border
    draw.rectangle([x0, y0, x1, y1], fill=(2, 119, 189), outline=(255, 255, 255), width=2)
    
    # Stop Code text centered
    f_use = font_marker_sm if len(code) >= 3 else font_marker
    bbox = draw.textbbox((0, 0), code, font=f_use)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x0 + (BOX_SIZE - tw) // 2
    ty = y0 + (BOX_SIZE - th) // 2 - 1
    draw.text((tx, ty), code, fill=(255, 255, 255), font=f_use)

# 2. Draw Legend Box at bottom-left
leg_x0, leg_y0 = 40, 1920
leg_x1, leg_y1 = 820, 2315

# Solid white background with blue border (matching Map 1 style)
draw.rectangle([leg_x0, leg_y0, leg_x1, leg_y1], fill=(255, 255, 255), outline=(0, 51, 102), width=2)

# Title
draw.text((leg_x0 + 16, leg_y0 + 14), "DANH MỤC TRẠM BUÝT & ĐIỂM ĐÓN TRẢ:", fill=(0, 51, 102), font=font_title)

# Draw items in 2 columns
col1 = bus_data[:12]
col2 = bus_data[12:]

y_start = leg_y0 + 48
line_h = 27

# Column 1
for idx, b in enumerate(col1):
    y_pos = y_start + idx * line_h
    code = b['code'] + '.'
    text = f"Trạm buýt: {b['street']}"
    
    # Text
    draw.text((leg_x0 + 18, y_pos), f"{code:4s}", fill=(0, 51, 102), font=font_code)
    draw.text((leg_x0 + 64, y_pos), text, fill=(0, 51, 102), font=font_text)

# Column 2
col2_x = leg_x0 + 400
for idx, b in enumerate(col2):
    y_pos = y_start + idx * line_h
    code = b['code'] + '.'
    text = f"Trạm buýt: {b['street']}"
    
    # Text
    draw.text((col2_x, y_pos), f"{code:4s}", fill=(0, 51, 102), font=font_code)
    draw.text((col2_x + 46, y_pos), text, fill=(0, 51, 102), font=font_text)

# P1 item at bottom of col 2 (idx = 12)
p1_y = y_start + 12 * line_h
draw.text((col2_x, p1_y), "P1.", fill=(0, 51, 102), font=font_code)
draw.text((col2_x + 46, p1_y), "Đề xuất vịnh đón trả khách PUDO", fill=(0, 51, 102), font=font_text)

# Save result to target map locations
out_paths = [
    r"D:\baocaotudong\maps_quan\S1\S1_Map3_Buyt_PUDO.png",
    r"D:\baocaotudong\maps_quan\S1\S1_Map3_Bus_PUDO.png",
    r"D:\baocaotudong\maps\S1_Map3_Bus_PUDO.png"
]

for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p, dpi=(300, 300))
    print(f"[*] Đã lưu bản đồ hoàn hảo Map 3: {p} ({os.path.getsize(p):,} bytes)")

print("[+] THÀNH CÔNG: Đã vẽ lại Bản đồ 3 Ga S01 với ĐỦ 24 TRẠM XE BUÝT thực địa!")
