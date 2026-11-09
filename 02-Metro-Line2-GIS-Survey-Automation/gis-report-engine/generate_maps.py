import json
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import osmnx as ox

def generate_map_for_station(station):
    name = station['full_name']
    lat = station['latitude']
    lon = station['longitude']
    point = (lat, lon)
    
    print(f"Đang xử lý Bản đồ cho ga: {name} (Lat: {lat}, Lon: {lon})")
    
    # 1. Bán kính quét
    dist_1000 = 1000
    out_dir = 'maps'
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Quét POIs
    tags = {'amenity': ['school', 'hospital', 'parking', 'university', 'kindergarten']}
    print("Đang quét dữ liệu OpenStreetMap (POIs)...")
    try:
        pois = ox.features_from_point(point, tags=tags, dist=dist_1000)
        pois_points = pois.copy()
        pois_points['geometry'] = pois_points['geometry'].centroid
    except Exception as e:
        print(f"Không tìm thấy POIs hoặc lỗi mạng: {e}")
        pois_points = None

    # 3. Vẽ bản đồ
    fig, ax = plt.subplots(figsize=(10, 10))
    
    station_gdf = gpd.GeoDataFrame({'name': [name]}, geometry=gpd.points_from_xy([lon], [lat]), crs="EPSG:4326")
    station_gdf_web = station_gdf.to_crs(epsg=3857)
    
    if pois_points is not None and not pois_points.empty:
        pois_points_web = pois_points.to_crs(epsg=3857)
        schools = pois_points_web[pois_points_web['amenity'].isin(['school', 'university', 'kindergarten'])]
        if not schools.empty:
            schools.plot(ax=ax, color='blue', marker='^', markersize=100, label='Trường học', alpha=0.7)
            
        hospitals = pois_points_web[pois_points_web['amenity'] == 'hospital']
        if not hospitals.empty:
            hospitals.plot(ax=ax, color='red', marker='P', markersize=100, label='Bệnh viện', alpha=0.7)
            
        parking = pois_points_web[pois_points_web['amenity'] == 'parking']
        if not parking.empty:
            parking.plot(ax=ax, color='green', marker='s', markersize=100, label='Bãi đỗ xe', alpha=0.7)

    station_gdf_web.plot(ax=ax, color='red', marker='*', markersize=500, edgecolor='black', label=f'Ga {name}')
    
    x_c, y_c = station_gdf_web.geometry.iloc[0].x, station_gdf_web.geometry.iloc[0].y
    buffer_m = 1200 
    ax.set_xlim(x_c - buffer_m, x_c + buffer_m)
    ax.set_ylim(y_c - buffer_m, y_c + buffer_m)

    print("Đang tải ảnh nền bản đồ vệ tinh...")
    try:
        # CartoDB Positron thường ổn định và dễ nhìn hơn cho bản đồ nền
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    except Exception as e:
        print(f"Lỗi tải ảnh nền, sẽ dùng nền trắng: {e}")
    
    ax.set_title(f'Bản đồ Tiện ích Đô thị Bán kính 1000m - {name}', fontsize=16, fontweight='bold')
    ax.legend(loc='lower right')
    ax.set_axis_off()

    out_file = os.path.join(out_dir, f"{station['id']}_1000m_Facilities.png")
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Thành công! Đã lưu bản đồ tại {out_file}")

if __name__ == '__main__':
    with open('stations_db.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
    s1 = next(s for s in stations if s['id'] == 'S1')
    generate_map_for_station(s1)
