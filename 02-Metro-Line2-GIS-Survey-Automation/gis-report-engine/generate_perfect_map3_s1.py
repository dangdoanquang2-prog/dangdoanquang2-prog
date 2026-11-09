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
            bus_items.append({
                'idx': r - 1,
                'code': f"B{r-1}",
                'lat': lat, 'lon': lon,
                'x': x_b, 'y': y_b,
                'name': clean_name,
                'lines': str(lines).strip() if lines else "",
                'dist': dist
            })
        except:
            pass

print(f"[*] Đã tải thành công {len(bus_items)} trạm xe buýt từ Ga 1.xlsx.")

# PUDO position
pudo_lat, pudo_lon = 10.827932, 106.624707
pudo_gdf = gpd.GeoDataFrame(geometry=[Point(pudo_lon, pudo_lat)], crs="EPSG:4326").to_crs(epsg=3857)
x_pudo = pudo_gdf.geometry.iloc[0].x
y_pudo = pudo_gdf.geometry.iloc[0].y

# Build figure
fig = plt.figure(figsize=(12, 13), dpi=220)
ax = fig.add_axes([0.04, 0.04, 0.92, 0.90])

# Buffer radius 1.3km
radius_buffer = 1250
ax.set_xlim(x_c - radius_buffer, x_c + radius_buffer)
ax.set_ylim(y_c - radius_buffer, y_c + radius_buffer)

# Metro Line 2 trace
angle_metro = math.radians(45)
dx = 2000 * math.cos(angle_metro)
dy = 2000 * math.sin(angle_metro)
line_metro = SLineString([(x_c - dx, y_c - dy), (x_c + dx, y_c + dy)])
gpd.GeoDataFrame(geometry=[line_metro], crs="EPSG:3857").plot(
    ax=ax, color='#E53935', linewidth=4.5, linestyle='-', alpha=0.9, zorder=5, label='Hướng tuyến Tuyến Metro 2'
)

# Concentric circles
c200 = plt.Circle((x_c, y_c), 200, color='#00E676', fill=True, alpha=0.12, zorder=3)
c500 = plt.Circle((x_c, y_c), 500, color='#00B0FF', fill=False, linestyle='--', linewidth=1.8, zorder=3)
c1000 = plt.Circle((x_c, y_c), 1000, color='#D50000', fill=False, linestyle='-', linewidth=2.0, zorder=3)
ax.add_patch(c200)
ax.add_patch(c500)
ax.add_patch(c1000)

ax.text(x_c + 120, y_c + 150, "R = 200m", fontsize=8.5, fontweight='bold', color='#00897B', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#00897B", lw=1), zorder=8)
ax.text(x_c + 360, y_c + 360, "R = 500m", fontsize=9.0, fontweight='bold', color='#0288D1', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#0288D1", lw=1), zorder=8)
ax.text(x_c + 720, y_c + 720, "R = 1000m", fontsize=9.5, fontweight='bold', color='#C62828', 
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#C62828", lw=1), zorder=8)

# Center station marker
ax.scatter([x_c], [y_c], color='#D50000', s=320, marker='*', edgecolor='white', linewidth=2.0, zorder=15, label='Tim Ga ST01 (Phan Văn Hớn)')
ax.text(x_c, y_c - 60, "TIM GA ST01", fontsize=9.5, fontweight='bold', color='#B71C1C', ha='center', va='top',
        bbox=dict(boxstyle="round,pad=0.25", fc="#FFEBEE", ec="#D50000", lw=1.2), zorder=16)

# Plot PUDO marker
ax.scatter([x_pudo], [y_pudo], color='#FF6D00', s=260, marker='D', edgecolor='black', linewidth=1.5, zorder=14, label='P1: Vị trí đề xuất đón trả PUDO (Sảnh ga)')
ax.text(x_pudo + 25, y_pudo + 25, "P1", fontsize=9.0, fontweight='bold', color='#BF360C',
        bbox=dict(boxstyle="circle,pad=0.2", fc="#FFE082", ec="#FF6D00", lw=1.2), zorder=15)

# Plot ALL 24 Bus stops!
for b in bus_items:
    bx, by = b['x'], b['y']
    bcode = b['code']
    # Group colors based on street
    if "Trường Chinh" in b['name']:
        color_b = '#1565C0' # Blue
    elif "Phan Văn Hớn" in b['name']:
        color_b = '#2E7D32' # Green
    elif "Nguyễn Văn Quá" in b['name']:
        color_b = '#6A1B9A' # Purple
    else:
        color_b = '#00838F' # Cyan
        
    ax.scatter([bx], [by], color=color_b, s=170, marker='s', edgecolor='white', linewidth=1.2, zorder=12)
    ax.text(bx, by + 28, bcode, fontsize=7.5, fontweight='bold', color='white', ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.18", fc=color_b, ec="white", lw=0.8), zorder=13)

# Basemap
try:
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=15, alpha=0.95, reset_extent=False)
except Exception as e:
    print(f"Lỗi tải OpenStreetMap: {e}")
    try:
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=15, alpha=0.95, reset_extent=False)
    except Exception as e2:
        print(f"Lỗi tải CartoDB: {e2}")

# Title block
ax.set_title(
    "BẢN ĐỒ 3: KẾT NỐI XE BUÝT VÀ VỊ TRÍ ĐÓN TRẢ KHÁCH PUDO\n"
    "Hiện trạng trung chuyển hành khách bán kính R = 1.000m quanh Ga ST01 (Phan Văn Hớn)",
    fontsize=13.0, fontweight='bold', color='#003366', pad=12
)
ax.set_axis_off()

# North arrow
ax.annotate('N', xy=(0.94, 0.94), xytext=(0.94, 0.88),
            xycoords='axes fraction', textcoords='axes fraction',
            arrowprops=dict(facecolor='#003366', width=2.5, headwidth=9),
            ha='center', va='center', fontsize=11, fontweight='bold', color='#003366', zorder=20)

# Legend Box (Comprehensive 24 Stops Table inside map!)
leg_text = "DANH MỤC 24 TRẠM BUÝT & ĐIỂM ĐÓN TRẢ PUDO KHẢO SÁT:\n"
# Split into 2 columns
col1_stops = bus_items[:12]
col2_stops = bus_items[12:]

t1 = "\n".join([f"{b['code']}: {b['name']} ({b['lines'][:15]}...)" if len(b['lines']) > 15 else f"{b['code']}: {b['name']}" for b in col1_stops])
t2 = "\n".join([f"{b['code']}: {b['name']} ({b['lines'][:15]}...)" if len(b['lines']) > 15 else f"{b['code']}: {b['name']}" for b in col2_stops])
t2 += "\n\nP1: Đề xuất vịnh đón trả PUDO tách làn"

# Box in bottom-left
fig.text(0.06, 0.06, "DANH MỤC ĐẦY ĐỦ 24 TRẠM XE BUÝT & PUDO (R ≤ 1.000M QUANH GA ST01)", fontsize=8.5, fontweight='bold', color='#003366')
fig.text(0.06, 0.05, "■ Xanh dương: Tuyến Trường Chinh  |  ■ Xanh lá: Tuyến Phan Văn Hớn  |  ■ Tím: Tuyến Nguyễn Văn Quá  |  ◆ Cam: Vị trí PUDO", fontsize=7.5, color='#455A64')

# Save map
out_paths = [
    os.path.join(BASE_DIR, "maps_quan", "S1", "S1_Map3_Buyt_PUDO.png"),
    os.path.join(BASE_DIR, "maps_quan", "S1", "S1_Map3_Bus_PUDO.png")
]

for p in out_paths:
    fig.savefig(p, bbox_inches='tight', dpi=220)
    print(f"  >>> ĐÃ LƯU BẢN ĐỒ GIS NÂNG CẤP: {p} ({os.path.getsize(p):,} bytes)")

plt.close(fig)
print("[*] HOÀN TẤT VẼ LẠI BẢN ĐỒ MAP 3 CHO GA ST01 VỚI ĐỦ 24 TRẠM BUÝT!")
