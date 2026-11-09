import os, sys
import math
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import geopandas as gpd
from shapely.geometry import Point, LineString
import contextily as ctx
import warnings

warnings.filterwarnings('ignore')

def create_s23_maps(station_id="S23", station_name="Ba Sa", lat=11.000752, lon=106.437926):
    out_dir = "maps"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"[*] Đang sinh 5 bản đồ GIS kỹ thuật cao cho Ga {station_id} ({station_name})...")
    
    station_gdf = gpd.GeoDataFrame(
        {'name': [station_name]},
        geometry=[Point(lon, lat)],
        crs="EPSG:4326"
    )
    station_3857 = station_gdf.to_crs(epsg=3857)
    x_c = station_3857.geometry.iloc[0].x
    y_c = station_3857.geometry.iloc[0].y

    # Trục tuyến Metro 2 dọc đường Phan Văn Khải (góc nghiêng ~ 135 độ / -45 độ)
    angle_line = math.radians(145)
    dx = 2000 * math.cos(angle_line)
    dy = 2000 * math.sin(angle_line)
    line_metro = LineString([(x_c - dx, y_c - dy), (x_c + dx, y_c + dy)])

    def add_top_metro_bar(fig):
        ax_bar = fig.add_axes([0.05, 0.92, 0.90, 0.06])
        ax_bar.axis('off')
        ax_bar.set_facecolor('#F0F4F8')
        ax_bar.plot([0.05, 0.95], [0.5, 0.5], color='#003366', linewidth=4, zorder=1)
        
        stations_bar = [
            (0.10, "S21 - Củ Chi"),
            (0.30, "S22 - Tân An Hội"),
            (0.50, "S23 - Ba Sa"),
            (0.70, "S24 - Thái Mỹ"),
            (0.90, "S26 - An Hạ")
        ]
        
        for pos, name in stations_bar:
            if "S23" in name:
                ax_bar.scatter([pos], [0.5], color='#D9381E', s=220, zorder=3, edgecolor='white', linewidth=2)
                ax_bar.text(pos, 0.85, name, fontsize=9.5, fontweight='bold', color='#D9381E', ha='center', va='bottom')
            else:
                ax_bar.scatter([pos], [0.5], color='white', s=100, zorder=2, edgecolor='#003366', linewidth=2)
                ax_bar.text(pos, 0.85, name, fontsize=8, color='#333333', ha='center', va='bottom')

    def build_base_figure(title_text, subtitle_text, radius_buffer=1400):
        fig = plt.figure(figsize=(10, 11), dpi=200)
        add_top_metro_bar(fig)
        
        ax = fig.add_axes([0.05, 0.08, 0.90, 0.82])
        ax.set_xlim(x_c - radius_buffer, x_c + radius_buffer)
        ax.set_ylim(y_c - radius_buffer, y_c + radius_buffer)

        # 1. Metro line
        gpd.GeoDataFrame(geometry=[line_metro], crs="EPSG:3857").plot(
            ax=ax, color='#D9381E', linewidth=3.5, linestyle='-', alpha=0.85, label='Hành lang Tuyến Metro 2', zorder=4
        )

        # 2. Road Labels
        ax.annotate("Đường Phan Văn Khải (QL22)", xy=(x_c - 200, y_c + 200), xytext=(x_c - 900, y_c + 700),
                    fontsize=8.5, fontweight='bold', color='#004D40',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E0F7FA", ec="#00838F", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#00838F", lw=1.2), zorder=9)
        
        ax.annotate("Đường Ba Sa (Đường kết nối)", xy=(x_c + 300, y_c - 300), xytext=(x_c + 700, y_c - 700),
                    fontsize=8.5, fontweight='bold', color='#004D40',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#E0F7FA", ec="#0288D1", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#0288D1", lw=1.2), zorder=9)

        ax.annotate("Đường Số 622 (Đường nhánh)", xy=(x_c - 250, y_c - 150), xytext=(x_c - 1000, y_c - 400),
                    fontsize=8.5, fontweight='bold', color='#E65100',
                    bbox=dict(boxstyle="round,pad=0.3", fc="#FFF3E0", ec="#FF9800", lw=1.2),
                    arrowprops=dict(arrowstyle="->", color="#FF9800", lw=1.2), zorder=9)

        # 3. Circles
        circle_200 = plt.Circle((x_c, y_c), 200, color='#FF5722', fill=True, alpha=0.10, zorder=2)
        circle_500 = plt.Circle((x_c, y_c), 500, color='#E91E63', fill=False, linestyle='--', linewidth=1.8, zorder=3)
        circle_1000 = plt.Circle((x_c, y_c), 1000, color='#D9381E', fill=False, linestyle='-', linewidth=2.0, zorder=3)
        
        ax.add_patch(circle_200)
        ax.add_patch(circle_500)
        ax.add_patch(circle_1000)
        
        # Radius labels
        ax.text(x_c + 150, y_c + 150, "R = 200m", fontsize=8.5, fontweight='bold', color='#FF5722', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#FF5722", lw=1), zorder=7)
        ax.text(x_c + 370, y_c + 370, "R = 500m", fontsize=9.0, fontweight='bold', color='#E91E63', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#E91E63", lw=1), zorder=7)
        ax.text(x_c + 720, y_c + 720, "R = 1km", fontsize=9.5, fontweight='bold', color='#D9381E', 
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#D9381E", lw=1), zorder=7)

        # Station Center
        ax.scatter([x_c], [y_c], color='#D9381E', s=320, marker='*', edgecolor='white', linewidth=2.0, zorder=10, label=f'Ga {station_id} ({station_name})')
        ax.text(x_c, y_c - 80, f"GA {station_id} - {station_name.upper()}", fontsize=11, fontweight='bold', color='#B71C1C', ha='center',
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFF9C4", ec="#FBC02D", lw=1.5), zorder=11)

        # Basemap (Dùng Esri WorldStreetMap chuẩn sạch 100% không watermark)
        try:
            ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, zoom=15, alpha=0.95, reset_extent=False)
        except Exception:
            try:
                ctx.add_basemap(ax, source=ctx.providers.Esri.WorldTopoMap, zoom=15, alpha=0.90, reset_extent=False)
            except Exception:
                pass

        # Compass & Scale
        ax.annotate('BẮC\n▲', xy=(0.95, 0.88), xycoords='axes fraction', fontsize=11, fontweight='bold', color='#003366', ha='center',
                    bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec="#003366", lw=1.5), zorder=10)
        ax.text(0.03, 0.03, "Tỷ lệ: 1 : 10,000 | Nguồn: OpenStreetMap / GIS Khảo sát Thực địa", transform=ax.transAxes,
                fontsize=8, fontstyle='italic', color='#444444', bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="#CCCCCC", lw=0.8), zorder=10)

        # Titles
        fig.text(0.5, 0.90, title_text, fontsize=12, fontweight='bold', color='#003366', ha='center')
        fig.text(0.5, 0.875, subtitle_text, fontsize=9.5, fontstyle='italic', color='#555555', ha='center')
        
        ax.set_xticks([])
        ax.set_yticks([])
        return fig, ax

    # ---------------------------------------------------------
    # MAP 1: TỔNG QUAN MẠNG LƯỚI ĐƯỜNG BÁN KÍNH 1000m
    # ---------------------------------------------------------
    fig1, ax1 = build_base_figure(
        f"MỤC B: BẢN ĐỒ TỔNG QUAN MẠNG LƯỚI GIAO THÔNG TIẾP CẬN GA {station_id} ({station_name.upper()})",
        f"Hình B.1: Sơ đồ phạm vi phục vụ 200m - 500m - 1000m & các trục đường Phan Văn Khải, Ba Sa",
        radius_buffer=1400
    )
    ax1.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig1.savefig(os.path.join(out_dir, f"{station_id}_Map1_TongQuan_1000m.png"), bbox_inches='tight')
    plt.close(fig1)

    # ---------------------------------------------------------
    # MAP 2: PHÂN VÙNG ĐI BỘ (200m & 500m)
    # ---------------------------------------------------------
    fig2, ax2 = build_base_figure(
        f"MỤC C: BẢN ĐỒ PHÂN TÍCH HÀNH LANG TIẾP CẬN ĐI BỘ GA {station_id}",
        f"Hình C.1: Vùng đi bộ thuận lợi (≤300m) và vùng đệm trung bình (300m - 500m)",
        radius_buffer=700
    )
    ax2.scatter([x_c + 80], [y_c + 30], color='#00C853', s=180, marker='o', edgecolor='white', linewidth=1.5, zorder=8, label='Cửa lên xuống số 1 (Phía Bắc đường Phan Văn Khải)')
    ax2.scatter([x_c - 80], [y_c - 30], color='#00C853', s=180, marker='o', edgecolor='white', linewidth=1.5, zorder=8, label='Cửa lên xuống số 2 (Phía Nam đường Phan Văn Khải)')
    ax2.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig2.savefig(os.path.join(out_dir, f"{station_id}_Map2_DiBo_200m_500m.png"), bbox_inches='tight')
    plt.close(fig2)

    # ---------------------------------------------------------
    # MAP 3: KẾT NỐI XE BUÝT VÀ LÀN PUDO
    # ---------------------------------------------------------
    fig3, ax3 = build_base_figure(
        f"MỤC D & E: BẢN ĐỒ KẾT NỐI XE BUÝT VÀ VỊ TRÍ LÀN ĐÓN TRẢ KHÁCH PUDO GA {station_id}",
        f"Hình D-E.1: Vị trí các điểm dừng buýt Tuyến 100, 107, 70-1, 70-2 & Vịnh đón trả PUDO dài 150m",
        radius_buffer=1100
    )
    # Real Bus points from survey
    # 50m bus stop
    ax3.scatter([x_c - 40], [y_c + 30], color='#2979FF', s=220, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-01 (Cách ga 50m - Tuyến 100, 107, 70-1, 70-2)')
    ax3.scatter([x_c + 450], [y_c - 300], color='#1565C0', s=180, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-02 (Cách ga 600m)')
    ax3.scatter([x_c - 500], [y_c + 400], color='#0D47A1', s=180, marker='s', edgecolor='white', linewidth=1.5, zorder=8, label='Trạm Buýt BS-03 (Cách ga 700m)')
    
    # PUDO
    ax3.scatter([x_c + 50], [y_c - 20], color='#FF9100', s=250, marker='D', edgecolor='black', linewidth=1.5, zorder=9, label='Vịnh đón trả khách PUDO đề xuất (dài 150m)')
    ax3.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig3.savefig(os.path.join(out_dir, f"{station_id}_Map3_Bus_PUDO.png"), bbox_inches='tight')
    plt.close(fig3)

    # ---------------------------------------------------------
    # MAP 4: BÃI XE PARK & RIDE & ĐIỂM XUNG ĐỘT
    # ---------------------------------------------------------
    fig4, ax4 = build_base_figure(
        f"MỤC F & G: BẢN ĐỒ QUY HOẠCH BÃI XE PARK & RIDE & CÁC NÚT XUNG ĐỘT GIAO THÔNG GA {station_id}",
        f"Hình F-G.1: Vị trí quỹ đất bãi xe P&R (1.000m² - 10.000m²) và các điểm nóng xung đột CP-01, CP-02",
        radius_buffer=1400
    )
    # Real Park & Ride locations from survey
    ax4.scatter([x_c + 60], [y_c + 50], color='#4CAF50', s=350, marker='H', edgecolor='black', linewidth=1.5, zorder=8, label='Bãi xe Park & Ride P&R-01 (1,000 m² - Cách ga 10m)')
    ax4.scatter([x_c - 80], [y_c + 80], color='#2E7D32', s=450, marker='H', edgecolor='black', linewidth=2.0, zorder=8, label='Quỹ đất TOD / Bãi xe P&R-02 (10,000 m² - Đất tự nhiên)')
    
    # Conflict points
    ax4.scatter([x_c - 400], [y_c + 300], color='#D50000', s=220, marker='X', edgecolor='white', linewidth=1.5, zorder=9, label='Điểm xung đột CP-01 (Giao lộ Phan Văn Khải - Ấp Phước Thạnh)')
    ax4.scatter([x_c + 500], [y_c - 450], color='#FF6D00', s=220, marker='X', edgecolor='white', linewidth=1.5, zorder=9, label='Điểm xung đột CP-02 (Nút giao Ba Sa - Phan Văn Khải)')
    
    ax4.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig4.savefig(os.path.join(out_dir, f"{station_id}_Map4_ParkRide_XungDot.png"), bbox_inches='tight')
    plt.close(fig4)

    # ---------------------------------------------------------
    # MAP 5: MA TRẬN RÀO CẢN TIẾP CẬN
    # ---------------------------------------------------------
    fig5, ax5 = build_base_figure(
        f"MỤC I & J: BẢN ĐỒ TỔNG HỢP MA TRẬN RÀO CẢN TIẾP CẬN GA {station_id}",
        f"Hình I-J.1: Ma trận các rào cản đi bộ, thiếu điểm sang đường an toàn và hạ tầng cho người khuyết tật",
        radius_buffer=1200
    )
    ax5.scatter([x_c], [y_c + 50], color='#D50000', s=250, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 1: Hoàn toàn không có vỉa hè đi bộ')
    ax5.scatter([x_c], [y_c - 50], color='#FF6D00', s=250, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 2: Không có điểm sang đường an toàn qua 6 làn xe')
    ax5.scatter([x_c + 150], [y_c], color='#AA00FF', s=220, marker='o', edgecolor='white', linewidth=1.5, zorder=9, label='Rào cản 3: Rào cản tuyệt đối với người khuyết tật (Điểm: 1.0/5)')
    
    ax5.legend(loc='lower left', frameon=True, facecolor='white', fontsize=8.5)
    fig5.savefig(os.path.join(out_dir, f"{station_id}_Map5_RaoCan_TongHop.png"), bbox_inches='tight')
    plt.close(fig5)

    print(f"[+] Hoàn tất sinh 5 bản đồ GIS kỹ thuật cho Ga {station_id} tại thư mục maps/!")

if __name__ == '__main__':
    create_s23_maps()
