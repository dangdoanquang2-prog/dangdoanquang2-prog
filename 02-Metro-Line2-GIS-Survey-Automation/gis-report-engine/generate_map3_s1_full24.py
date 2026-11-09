import os
import sys
import math
import warnings
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import geopandas as gpd
from shapely.geometry import Point, LineString as SLineString
import contextily as ctx
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')

BASE_DIR = r"D:\baocaotudong"
excel_path = os.path.join(BASE_DIR, "Ga của Quân", "Ga 1.xlsx")
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws_b = wb['ĐIỀU KIỆN KẾT NỐI XE BUÝT (Resp']

# Station center
st_lat, st_lon = 10.828410, 106.624380
station_gdf = gpd.GeoDataFrame({'name': ['Ga ST01 - Phan Văn Hớn']}, geometry=[Point(st_lon, st_lat)], crs="EPSG:4326")
st_3857 = station_gdf.to_crs(epsg=3857)
x_c = st_3857.geometry.iloc[0].x
y_c = st_3857.geometry.iloc[0].y

# Parse all 24 bus stops
bus_items = []
for r in range(2, ws_b.max_row + 1):
    coord_str = ws_b.cell(r, 7).value
    name = ws_b.cell(r, 9).value
    lines = ws_b.cell(r, 12).value
    dist = ws_b.cell(r, 10).value
    if coord_str:
        try:
            parts = str(coord_str).replace(';', ',').split(',')
            lat, lon = float(parts[0].strip()), float(parts[1].strip())
            pt_gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat)], crs="EPSG:4326").to_crs(epsg=3857)
            x_b = pt_gdf.geometry.iloc[0].x
            y_b = pt_gdf.geometry.iloc[0].y
            
            clean_name = str(name).split(',')[0].strip() if name else f"Trạm {r-1}"
            clean_name = clean_name.replace("Phan Hữu Ích", "Phan Huy Ích")
            
            bus_items.append({
                'idx': r - 1,
                'code': f"B{r-1}",
                'lat': lat, 'lon': lon,
                'x': x_b, 'y': y_b,
                'name': clean_name,
                'lines': str(lines).strip() if lines else "",
                'dist': dist
            })
        except Exception as e:
            pass

print(f"[*] Đã tải thành công {len(bus_items)} trạm xe buýt từ Ga 1.xlsx.")

# PUDO position
pudo_lat, pudo_lon = 10.827932, 106.624707
pudo_gdf = gpd.GeoDataFrame(geometry=[Point(pudo_lon, pudo_lat)], crs="EPSG:4326").to_crs(epsg=3857)
x_pudo = pudo_gdf.geometry.iloc[0].x
y_pudo = pudo_gdf.geometry.iloc[0].y

# Build figure
fig, ax = plt.subplots(figsize=(13, 14), dpi=220)

# Set map bounds centered on station, covering all 24 stops
# Bounds: West -1450m, East +1200m, South -1050m, North +1050m
ax.set_xlim(x_c - 1450, x_c + 1200)
ax.set_ylim(y_c - 1050, y_c + 1050)

# 1. Metro Line 2 trace along Truong Chinh (Angle ~ 45 deg)
angle_metro = math.radians(45)
dx = 2500 * math.cos(angle_metro)
dy = 2500 * math.sin(angle_metro)
line_metro = SLineString([(x_c - dx, y_c - dy), (x_c + dx, y_c + dy)])
gpd.GeoDataFrame(geometry=[line_metro], crs="EPSG:3857").plot(
    ax=ax, color='#E53935', linewidth=4.0, linestyle='-', alpha=0.85, zorder=4, label='Hướng tuyến Tuyến Metro 2'
)

# 2. Concentric circles: R = 200m, 500m, 1000m
c200 = plt.Circle((x_c, y_c), 200, color='#00E676', fill=True, alpha=0.10, zorder=2)
c500 = plt.Circle((x_c, y_c), 500, color='#00B0FF', fill=False, linestyle='--', linewidth=1.6, zorder=3)
c1000 = plt.Circle((x_c, y_c), 1000, color='#D50000', fill=False, linestyle='-', linewidth=1.8, zorder=3)
ax.add_patch(c200)
ax.add_patch(c500)
ax.add_patch(c1000)

ax.text(x_c + 130, y_c + 140, "R = 200m", fontsize=8.5, fontweight='bold', color='#00796B', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00796B", lw=1), zorder=8)
ax.text(x_c + 360, y_c + 360, "R = 500m", fontsize=8.5, fontweight='bold', color='#0288D1', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#0288D1", lw=1), zorder=8)
ax.text(x_c + 720, y_c + 720, "R = 1000m", fontsize=9.0, fontweight='bold', color='#C62828', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#C62828", lw=1), zorder=8)

# 3. Center station marker
ax.scatter([x_c], [y_c], color='#D50000', s=300, marker='*', edgecolor='white', linewidth=1.5, zorder=15)
ax.text(x_c, y_c - 55, "TIM GA S01", fontsize=9.5, fontweight='bold', color='#B71C1C', ha='center', va='top',
        bbox=dict(boxstyle="round,pad=0.25", fc="#FFEBEE", ec="#D50000", lw=1.2), zorder=16)

# 4. PUDO marker
ax.scatter([x_pudo], [y_pudo], color='#FF6D00', s=240, marker='D', edgecolor='white', linewidth=1.5, zorder=14)
ax.text(x_pudo + 25, y_pudo - 10, "P1", fontsize=9.0, fontweight='bold', color='#BF360C',
        bbox=dict(boxstyle="circle,pad=0.2", fc="#FFE082", ec="#FF6D00", lw=1.2), zorder=15)

# 5. Plot ALL 24 Bus stops with corridor color coding
# Colors: Truong Chinh: Blue (#1976D2), Phan Van Hon: Orange (#F57C00), Nguyen Van Qua: Purple (#7B1FA2), Phan Huy Ich: Teal (#00897B)
corridor_colors = {
    'Trường Chinh': '#1565C0',
    'Phan Văn Hớn': '#E65100',
    'Nguyễn Văn Quá': '#6A1B9A',
    'Phan Huy Ích': '#00695C'
}

for b in bus_items:
    bx, by = b['x'], b['y']
    bcode = b['code']
    c_color = '#1565C0'
    for k, col in corridor_colors.items():
        if k in b['name']:
            c_color = col
            break
            
    ax.scatter([bx], [by], color=c_color, s=140, marker='s', edgecolor='white', linewidth=1.2, zorder=12)
    # Offset text slightly to prevent overlap
    offset_y = 22
    offset_x = 0
    if bcode in ['B4', 'B7']:
        offset_x = -15
    elif bcode in ['B13', 'B14']:
        offset_x = 15
        
    ax.text(bx + offset_x, by + offset_y, bcode, fontsize=7.5, fontweight='bold', color='white', ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.16", fc=c_color, ec="white", lw=0.8), zorder=13)

# 6. Add basemap (CartoDB.Voyager gives the exact clean look of the reviewer's screenshot)
try:
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Voyager, zoom=15, alpha=0.95, reset_extent=False)
except Exception as e:
    print(f"CartoDB.Voyager warning: {e}")
    try:
        ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, zoom=15, alpha=0.95, reset_extent=False)
    except Exception as e2:
        print(f"Esri warning: {e2}")

# 7. Title Block
ax.set_title(
    "BẢN ĐỒ 3: KẾT NỐI XE BUÝT VÀ VỊ TRÍ ĐÓN TRẢ PUDO\n"
    "Hiện trạng trung chuyển hành khách quanh Ga S01 (Phan Văn Hớn)",
    fontsize=13.5, fontweight='bold', color='#003366', pad=14
)
ax.set_axis_off()

# 8. North Arrow
ax.annotate('N', xy=(0.95, 0.95), xytext=(0.95, 0.89),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(facecolor='#003366', width=2.5, headwidth=9),
            ha='center', va='center', fontsize=11, fontweight='bold', color='#003366', zorder=20)

# 9. Clean Legend Table at Bottom Left (2 Columns for all 24 stops + PUDO)
leg_col1 = [
    "B1: Trường Chinh",
    "B2: Trường Chinh",
    "B3: Phan Huy Ích",
    "B4: Phan Huy Ích",
    "B5: Phan Huy Ích",
    "B6: Phan Huy Ích",
    "B7: Phan Huy Ích",
    "B8: Nguyễn Văn Quá",
    "B9: Nguyễn Văn Quá",
    "B10: Nguyễn Văn Quá",
    "B11: Nguyễn Văn Quá",
    "B12: Nguyễn Văn Quá",
]

leg_col2 = [
    "B13: Nguyễn Văn Quá",
    "B14: Nguyễn Văn Quá",
    "B15: Trường Chinh",
    "B16: Trường Chinh",
    "B17: Phan Văn Hớn",
    "B18: Phan Văn Hớn",
    "B19: Phan Văn Hớn",
    "B20: Phan Văn Hớn",
    "B21: Phan Văn Hớn",
    "B22: Phan Văn Hớn",
    "B23: Phan Văn Hớn",
    "B24: Trường Chinh",
]

col1_text = "\n".join(leg_col1)
col2_text = "\n".join(leg_col2) + "\n★ P1: Đề xuất vịnh đón trả PUDO"

# Background box for legend
leg_box = patches.FancyBboxPatch(
    (0.02, 0.02), 0.44, 0.30,
    transform=ax.transAxes,
    boxstyle="round,pad=0.01",
    facecolor='white',
    edgecolor='#003366',
    linewidth=1.2,
    alpha=0.94,
    zorder=25
)
ax.add_patch(leg_box)

ax.text(0.035, 0.295, "DANH MỤC 24 TRẠM BUÝT & ĐIỂM ĐÓN TRẢ PUDO:",
        transform=ax.transAxes, fontsize=8.5, fontweight='bold', color='#003366', va='top', zorder=26)

ax.text(0.035, 0.265, col1_text,
        transform=ax.transAxes, fontsize=7.2, color='#263238', va='top', linespacing=1.25, zorder=26)

ax.text(0.24, 0.265, col2_text,
        transform=ax.transAxes, fontsize=7.2, color='#263238', va='top', linespacing=1.25, zorder=26)

# Save to destination paths
out_paths = [
    os.path.join(BASE_DIR, "maps_quan", "S1", "S1_Map3_Buyt_PUDO.png"),
    os.path.join(BASE_DIR, "maps_quan", "S1", "S1_Map3_Bus_PUDO.png"),
    os.path.join(BASE_DIR, "maps", "S1_Map3_Bus_PUDO.png")
]

for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fig.savefig(p, bbox_inches='tight', dpi=220)
    print(f"  >>> ĐÃ LƯU BẢN ĐỒ: {p} ({os.path.getsize(p):,} bytes)")

plt.close(fig)
print("[*] THÀNH CÔNG: Đã vẽ lại Bản đồ 3 Ga S01 với ĐẦY ĐỦ 24 TRẠM XE BUÝT thực địa!")
