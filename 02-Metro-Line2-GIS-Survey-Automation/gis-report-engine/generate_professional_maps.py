import os
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import geopandas as gpd
from shapely.geometry import Point, LineString
import contextily as ctx
import warnings

# Suppress warnings for clean output
warnings.filterwarnings('ignore')

def create_station_maps(station_id="S1", station_name="Phan Văn Hớn", lat=10.836068, lon=106.618255):
    out_dir = "maps"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"[*] Generating ultra-clean maps for station {station_id} ({lat}, {lon})...")
    point = (lat, lon)
    
    # Station coordinates
    station_gdf = gpd.GeoDataFrame(
        {'name': [station_name]},
        geometry=[Point(lon, lat)],
        crs="EPSG:4326"
    )
    station_3857 = station_gdf.to_crs(epsg=3857)
    x_c = station_3857.geometry.iloc[0].x
    y_c = station_3857.geometry.iloc[0].y

    # Metro Line 2 alignment line along QL22 (Angle ~ 40 deg)
    angle_ql22 = math.radians(40)
    dx = 1800 * math.cos(angle_ql22)
    dy = 1800 * math.sin(angle_ql22)
    line_ql22 = LineString([(x_c - dx, y_c - dy), (x_c + dx, y_c + dy)])

    # Helper for Top Metro Bar
    def add_top_metro_bar(fig):
        ax_bar = fig.add_axes([0.05, 0.92, 0.90, 0.06])
        ax_bar.axis('off')
        ax_bar.set_facecolor('#F0F4F8')
        ax_bar.plot([0.05, 0.95], [0.5, 0.5], color='#003366', linewidth=4, zorder=1)
        
        stations_bar = [
            (0.10, "Tham Lương"),
            (0.30, "S1 - Phan Văn Hớn"),
            (0.50, "S2 - Đông Hưng Thuận"),
            (0.70, "S3 - An Sương"),
            (0.90, "Bến Thành")
        ]
        
        for pos, name in stations_bar:
            if "S1" in name:
                ax_bar.scatter([pos], [0.5], color='#D9381E', s=220, zorder=3, edgecolor='white', linewidth=2)
                ax_bar.text(pos, 0.85, name, fontsize=9.5, fontweight='bold', color='#D9381E', ha='center', va='bottom')
            else:
                ax_bar.scatter([pos], [0.5], color='white', s=100, zorder=2, edgecolor='#003366', linewidth=2)
                ax_bar.text(pos, 0.85, name, fontsize=8, color='#333333', ha='center', va='bottom')

    # Base Map Generator
    def build_base_figure(title_text, subtitle_text, radius_buffer=1400):
        fig = plt.figure(figsize=(10, 11), dpi=200)
        add_top_metro_bar(fig)
        
        ax = fig.add_axes([0.05, 0.08, 0.90, 0.82])
        ax.set_xlim(x_c - radius_buffer, x_c + radius_buffer)
        ax.set_ylim(y_c - radius_buffer, y_c + radius_buffer)

        # 1. METRO LINE 2 ALIGNMENT (Clean red line)
        gpd.GeoDataFrame(geometry=[line_ql22], crs="EPSG:3857").plot(
            ax=ax, color='#D9381E', linewidth=3.5, linestyle='-', alpha=0.85, label='Hành lang Tuyến Metro 2', zorder=4
        )

        # 2. ROAD NAME LABELS PUSHED TO MAP EDGES (Zero overlap with station area)
        # Using pointer arrows pointing to the basemap's actual roads
        ax.annotate("Quốc lộ 22 (Trường Chinh)", xy=(x_c - 300, y_c - 300), xytext=(x_c - 900, y_c + 700),
                    fontsize=8.5, fontweight='bold', color='#004D40',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E0F7FA", ec="#00838F", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#00838F", lw=1.2), zorder=9)
        
        ax.annotate("Đường Phan Văn Hớn", xy=(x_c + 300, y_c - 300), xytext=(x_c + 800, y_c - 800),
                    fontsize=8.5, fontweight='bold', color='#004D40',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E0F7FA", ec="#0288D1", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#0288D1", lw=1.2), zorder=9)

        ax.annotate("Đường Song Hành QL22", xy=(x_c - 200, y_c - 100), xytext=(x_c - 1000, y_c - 400),
                    fontsize=8.5, fontweight='bold', color='#E65100',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF3E0", ec="#FF9800", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#FF9800", lw=1.2), zorder=9)

        ax.annotate("Đường Tân Thới Nhất 17", xy=(x_c + 200, y_c - 150), xytext=(x_c + 800, y_c + 300),
                    fontsize=8.5, fontweight='bold', color='#1B5E20',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#4CAF50", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#4CAF50", lw=1.2), zorder=9)

        # 3. CONCENTRIC CIRCLES: 200m, 500m, 1000m
        circle_200 = plt.Circle((x_c, y_c), 200, color='#FF5722', fill=True, alpha=0.10, zorder=2)
        circle_500 = plt.Circle((x_c, y_c), 500, color='#E91E63', fill=False, linestyle='--', linewidth=1.8, zorder=3)
        circle_1000 = plt.Circle((x_c, y_c), 1000, color='#D9381E', fill=False, linestyle='-', linewidth=2.0, zorder=3)
        
        ax.add_patch(circle_200)
        ax.add_patch(circle_500)
        ax.add_patch(circle_1000)
        
        # 4. RADIUS ANNOTATIONS
        ax.text(x_c + 150, y_c + 150, "R = 200m", fontsize=8.5, fontweight='bold', color='#FF5722', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#FF5722", lw=1), zorder=7)
        ax.text(x_c + 370, y_c + 370, "R = 500m", fontsize=9.0, fontweight='bold', color='#E91E63', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#E91E63", lw=1), zorder=7)
        ax.text(x_c + 720, y_c + 720, "R = 1km", fontsize=9.5, fontweight='bold', color='#D9381E', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#D9381E", lw=1.5), zorder=7)
        
        # 5. STATION MARKER (Clean center star & badge)
        station_3857.plot(ax=ax, color='#D9381E', marker='*', markersize=650, edgecolor='white', linewidth=1.5, zorder=10, label=f'Ga {station_id} - {station_name}')
        ax.text(x_c, y_c - 80, f"GA {station_id} - {station_name.upper()}", fontsize=10, fontweight='bold', color='white', ha='center', 
                bbox=dict(boxstyle="round,pad=0.35", fc="#003366", ec="white", lw=1.5), zorder=11)
        
        # 6. BASEMAP (Esri WorldStreetMap)
        try:
            ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, zoom=15)
        except Exception as e:
            print(f"Basemap load warning: {e}")
            try:
                ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=15)
            except:
                ax.set_facecolor('#EFEFEF')
        
        ax.set_title(title_text, fontsize=12.5, fontweight='bold', color='#003366', pad=10)
        ax.set_axis_off()
        
        fig.text(0.5, 0.03, subtitle_text, fontsize=10, fontweight='bold', color='#333333', ha='center')
        
        return fig, ax

    # ---------------------------------------------------------
    # MAP 1: CHƯƠNG 1 - TỔNG QUAN MẠNG LƯỚI GIAO THÔNG (200m & 1000m)
    # ---------------------------------------------------------
    fig1, ax1 = build_base_figure(
        f"CHƯƠNG 1: BẢN ĐỒ TỔNG QUAN MẠNG LƯỚI GIAO THÔNG GA {station_id}",
        f"Hình 1.1: Sơ đồ mạng lưới giao thông bán kính 200m & 1000m - Ga {station_id} Phan Văn Hớn",
        radius_buffer=1400
    )
    ax1.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.92, fontsize=8.5)
    fig1.savefig(os.path.join(out_dir, f"{station_id}_Map1_TongQuan_1000m.png"), bbox_inches='tight')
    plt.close(fig1)

    # ---------------------------------------------------------
    # MAP 2: CHƯƠNG 2 - ĐIỀU KIỆN ĐI BỘ & VỈA HÈ (200m & 500m)
    # ---------------------------------------------------------
    fig2, ax2 = build_base_figure(
        f"CHƯƠNG 2: BẢN ĐỒ PHÂN VÙNG TIẾP CẬN ĐI BỘ GA {station_id}",
        f"Hình 2.1: Sơ đồ phân vùng hành lang đi bộ 200m & 500m quanh cửa ga S1",
        radius_buffer=1400
    )
    ax2.scatter([x_c + 80], [y_c + 60], color='#00E676', s=180, marker='D', edgecolor='black', zorder=8, label='Cửa lên xuống Exit A')
    ax2.scatter([x_c - 80], [y_c - 60], color='#00E676', s=180, marker='D', edgecolor='black', zorder=8, label='Cửa lên xuống Exit B')
    
    # Callout Annotations for Exits (Spreading outward)
    ax2.annotate("Exit A (QL22 phía Bắc)", xy=(x_c + 80, y_c + 60), xytext=(x_c + 450, y_c + 350),
                 fontsize=8.5, fontweight='bold', color='#00796B',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#E0F2F1", ec="#00796B", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#00796B", lw=1.3), zorder=9)

    ax2.annotate("Exit B (QL22 phía Nam)", xy=(x_c - 80, y_c - 60), xytext=(x_c - 600, y_c - 350),
                 fontsize=8.5, fontweight='bold', color='#00796B',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#E0F2F1", ec="#00796B", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#00796B", lw=1.3), zorder=9)

    ax2.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig2.savefig(os.path.join(out_dir, f"{station_id}_Map2_DiBo_200m_500m.png"), bbox_inches='tight')
    plt.close(fig2)

    # ---------------------------------------------------------
    # MAP 3: CHƯƠNG 3 - XE BUÝT & LÀN PUDO (CALLOUT BOXES PUSHED FAR OUTSIDE!)
    # ---------------------------------------------------------
    fig3, ax3 = build_base_figure(
        f"CHƯƠNG 3: BẢN ĐỒ MẠNG LƯỚI XE BUÝT & ĐÓ N TRẢ KHÁCH PUDO GA {station_id}",
        f"Hình 3.1: Sơ đồ trạm dừng xe buýt & vị trí làn PUDO / Kiss & Ride quanh Ga S1",
        radius_buffer=1400
    )
    # Bus stop & PUDO Icons
    ax3.scatter([x_c + 60], [y_c + 120], color='#0288D1', s=240, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-01 (QL22 - Cách ga 60m)')
    ax3.scatter([x_c - 90], [y_c - 110], color='#0288D1', s=240, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-02 (QL22 - Cách ga 85m)')
    ax3.scatter([x_c + 200], [y_c - 250], color='#0097A7', s=240, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-03 (Phan Văn Hớn - Cách ga 180m)')
    ax3.scatter([x_c - 180], [y_c + 200], color='#FF9800', s=260, marker='P', edgecolor='black', linewidth=1.5, zorder=8, label='Đề xuất Làn PUDO (Đường Song Hành QL22)')

    # ANNOTATIONS PUSHED FAR OUTSIDE TO OPEN MARGINS
    ax3.annotate("TRẠM BS-01 (QL22 - Chiều An Sương)\n► Tuyến đi qua: 04, 13, 27, 65, 94", 
                 xy=(x_c + 60, y_c + 120), xytext=(x_c + 500, y_c + 500),
                 fontsize=8, fontweight='bold', color='#0288D1',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#E1F5FE", ec="#0288D1", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#0288D1", lw=1.3), zorder=9)

    ax3.annotate("TRẠM BS-02 (QL22 - Chiều Bến Thành)\n► Tuyến đi qua: 04, 13, 27, 65, 94", 
                 xy=(x_c - 90, y_c - 110), xytext=(x_c - 850, y_c - 500),
                 fontsize=8, fontweight='bold', color='#0288D1',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#E1F5FE", ec="#0288D1", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#0288D1", lw=1.3), zorder=9)

    ax3.annotate("TRẠM BS-03 (Đường Phan Văn Hớn)\n► Tuyến buýt gom: 23 (Chợ Lớn - Hóc Môn)", 
                 xy=(x_c + 200, y_c - 250), xytext=(x_c + 450, y_c - 600),
                 fontsize=7.5, fontweight='bold', color='#00838F',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#E0F7FA", ec="#00838F", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#00838F", lw=1.3), zorder=9)

    ax3.annotate("LÀN PUDO TAXI/GRAB (Dài 45m)\n► Vị trí: Đường Song Hành QL22", 
                 xy=(x_c - 180, y_c + 200), xytext=(x_c - 850, y_c + 450),
                 fontsize=8, fontweight='bold', color='#E65100',
                 bbox=dict(boxstyle="round,pad=0.35", fc="#FFF3E0", ec="#E65100", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#E65100", lw=1.3), zorder=9)

    ax3.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8)
    fig3.savefig(os.path.join(out_dir, f"{station_id}_Map3_Bus_PUDO.png"), bbox_inches='tight')
    plt.close(fig3)

    # ---------------------------------------------------------
    # MAP 4: CHƯƠNG 4 - BÃI XE PARK & RIDE & ĐIỂM XUNG ĐỘT (200m & 1000m)
    # ---------------------------------------------------------
    fig4, ax4 = build_base_figure(
        f"CHƯƠNG 4: BẢN ĐỒ BÃI XE PARK & RIDE & ĐIỂM XUNG ĐỘT GIAO THÔNG GA {station_id}",
        f"Hình 4.1: Sơ đồ vị trí quy hoạch Bãi xe Park & Ride & Điểm nóng ùn tắc CP-01, CP-02",
        radius_buffer=1400
    )
    ax4.scatter([x_c + 220], [y_c - 180], color='#4CAF50', s=300, marker='H', edgecolor='black', linewidth=1.5, zorder=8, label='Quy hoạch Bãi xe Park & Ride (1,200 m²)')
    ax4.scatter([x_c + 150], [y_c + 100], color='#D50000', s=220, marker='X', edgecolor='white', linewidth=1.5, zorder=9, label='Điểm xung đột CP-01 (Nút QL22 - Phan Văn Hớn)')
    ax4.scatter([x_c - 250], [y_c - 200], color='#FF6D00', s=220, marker='X', edgecolor='white', linewidth=1.5, zorder=9, label='Điểm xung đột CP-02 (Mũi tàu Song Hành)')
    
    ax4.annotate("PARK & RIDE (1,200m²)\nĐường Tân Thới Nhất 17", xy=(x_c + 220, y_c - 180), xytext=(x_c + 500, y_c - 400),
                 fontsize=8, fontweight='bold', color='#2E7D32', bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#2E7D32", lw=1.2), zorder=9)

    ax4.annotate("CP-01 (Nút QL22 - Phan Văn Hớn)\nKẹt xe & Xung đột rẽ trái", xy=(x_c + 150, y_c + 100), xytext=(x_c + 450, y_c + 300),
                 fontsize=8, fontweight='bold', color='#D50000', bbox=dict(boxstyle="round,pad=0.3", fc="#FFEBEE", ec="#D50000", lw=1.2),
                 arrowprops=dict(arrowstyle="->", color="#D50000", lw=1.2), zorder=9)

    ax4.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig4.savefig(os.path.join(out_dir, f"{station_id}_Map4_ParkRide_XungDot.png"), bbox_inches='tight')
    plt.close(fig4)

    # ---------------------------------------------------------
    # MAP 5: CHƯƠNG 5 - RÀO CẢN TIẾP CẬN TRỌNG YẾU (200m & 1000m)
    # ---------------------------------------------------------
    fig5, ax5 = build_base_figure(
        f"CHƯƠNG 5: BẢN ĐỒ TỔNG HỢP MA TRẬN RÀO CẢN TIẾP CẬN GA {station_id}",
        f"Hình 5.1: Sơ đồ ma trận 16 rào cản tiếp cận & vị trí Top 3 rào cản nghiêm trọng quanh Ga S1",
        radius_buffer=1400
    )
    ax5.scatter([x_c + 120], [y_c - 150], color='#AA00FF', s=220, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 1: Hàng rong lấn chiếm vỉa hè')
    ax5.scatter([x_c - 140], [y_c + 150], color='#FFAB00', s=220, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 2: Dây điện/cáp treo thấp')
    ax5.scatter([x_c + 280], [y_c + 50], color='#00B8D4', s=220, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 3: Vỉa hè chênh cao, thiếu ram dốc NKT')
    
    ax5.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig5.savefig(os.path.join(out_dir, f"{station_id}_Map5_RaoCan_TongHop.png"), bbox_inches='tight')
    plt.close(fig5)

    print(f"[+] Done! Generated ultra-clean maps without blue vector lines.")

if __name__ == '__main__':
    create_station_maps()
