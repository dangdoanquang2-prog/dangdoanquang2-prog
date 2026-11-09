import os
import json
import pandas as pd

def build_interactive_html_dashboard():
    """
    Builds an interactive Leaflet HTML dashboard displaying:
    1. Stay Points (Markers with duration info)
    2. Trip Flow Lines (Arcs between Origin and Destination)
    3. Executive Summary KPI Counters
    """
    print("[3/3] Generating Interactive OD Flow Dashboard HTML...")
    data_dir = "d:\\data"
    
    trips_file = os.path.join(data_dir, "trips_extracted.csv")
    stay_file = os.path.join(data_dir, "stay_points_detected.csv")
    
    if not os.path.exists(trips_file) or not os.path.exists(stay_file):
        print("Error: Required CSV files missing. Run gps_data_mining.py first.")
        return

    df_trips = pd.read_csv(trips_file)
    df_stay = pd.read_csv(stay_file)

    # Calculate dynamic map center
    mean_lat = round(df_stay['latitude'].mean(), 4) if len(df_stay) > 0 else 39.9
    mean_lon = round(df_stay['longitude'].mean(), 4) if len(df_stay) > 0 else 116.4
    num_devices = df_stay['device_id'].nunique()

    # Convert dataframes to JSON for Leaflet rendering
    trips_json = df_trips.to_json(orient="records")
    stay_json = df_stay.to_json(orient="records")

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>PoC Đào Dữ Liệu GPS Thực Tế (GeoLife Dataset) & Ma Trận OD Giao Thông</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
        body {{ display: flex; height: 100vh; background: #0f172a; color: #f8fafc; overflow: hidden; }}
        #sidebar {{ width: 380px; background: #1e293b; border-right: 1px solid #334155; padding: 20px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }}
        #map {{ flex: 1; height: 100%; }}
        h2 {{ color: #38bdf8; font-size: 1.2rem; margin-bottom: 5px; font-weight: 700; }}
        p.subtitle {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 15px; }}
        .kpi-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .kpi-card {{ background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #334155; }}
        .kpi-value {{ font-size: 1.4rem; font-weight: 700; color: #38bdf8; }}
        .kpi-label {{ font-size: 0.75rem; color: #94a3b8; margin-top: 2px; }}
        .section-title {{ font-size: 0.9rem; font-weight: 600; color: #f1f5f9; border-left: 3px solid #38bdf8; padding-left: 8px; margin-top: 10px; }}
        .legend {{ display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; color: #cbd5e1; background: #0f172a; padding: 10px; border-radius: 6px; border: 1px solid #334155; }}
        .legend-item {{ display: flex; align-items: center; gap: 8px; }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
        .line-sample {{ width: 20px; height: 3px; display: inline-block; border-radius: 2px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; color: #cbd5e1; margin-top: 5px; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #38bdf8; font-weight: 600; }}
    </style>
</head>
<body>

<div id="sidebar">
    <div>
        <h2>PoC BÁO CÁO ĐÀO DỮ LIỆU GPS THỰC TẾ</h2>
        <p class="subtitle">Bộ dữ liệu Microsoft GeoLife Trajectory (Real Data)</p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value" id="kpi-devices">{num_devices}</div>
            <div class="kpi-label">Người dùng (Users)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" id="kpi-staypoints">{len(df_stay)}</div>
            <div class="kpi-label">Điểm dừng (Stay Points)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" id="kpi-trips">{len(df_trips)}</div>
            <div class="kpi-label">Chuyến đi (Trips)</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" id="kpi-avgtrips">REAL</div>
            <div class="kpi-label">Tọa độ thực tế</div>
        </div>
    </div>

    <div class="section-title">Chú thích Bản đồ (Legend)</div>
    <div class="legend">
        <div class="legend-item"><span class="dot" style="background:#ef4444;"></span> <span>Điểm dừng (Stay Point &gt; 15 phút)</span></div>
        <div class="legend-item"><span class="line-sample" style="background:#38bdf8;"></span> <span>Chuyến đi thực tế (Real Trip Flow)</span></div>
    </div>

    <div class="section-title">Ma trận OD Thực Tế (Zone Pairs)</div>
    <div style="overflow-x: auto;">
        <table>
            <thead>
                <tr>
                    <th>Vùng Đi (Origin)</th>
                    <th>Vùng Đến (Dest)</th>
                    <th>Khung Giờ</th>
                    <th>Lượt</th>
                </tr>
            </thead>
            <tbody id="od-table-body">
            </tbody>
        </table>
    </div>
</div>

<div id="map"></div>

<script>
    const tripsData = {trips_json};
    const stayData = {stay_json};

    // Dynamic Map center on dataset mean coordinates
    const map = L.map('map').setView([{mean_lat}, {mean_lon}], 11);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        maxZoom: 19,
        attribution: '&copy; CartoDB & OpenStreetMap'
    }}).addTo(map);

    // Render Stay Points
    stayData.forEach(sp => {{
        L.circleMarker([sp.latitude, sp.longitude], {{
            radius: 5,
            fillColor: "#ef4444",
            color: "#ffffff",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }}).addTo(map).bindPopup(`
            <b>Người dùng:</b> ${{sp.device_id}}<br>
            <b>Thời gian dừng:</b> ${{sp.duration_minutes}} phút<br>
            <b>Từ:</b> ${{sp.start_time}}<br>
            <b>Đến:</b> ${{sp.end_time}}
        `);
    }});

    // Render Trip Flow Lines
    tripsData.forEach(t => {{
        const latlngs = [
            [t.origin_lat, t.origin_lon],
            [t.dest_lat, t.dest_lon]
        ];

        L.polyline(latlngs, {{
            color: "#38bdf8",
            weight: 2,
            opacity: 0.6,
            dashArray: '4, 8'
        }}).addTo(map).bindPopup(`
            <b>Người dùng:</b> ${{t.device_id}}<br>
            <b>Khoảng cách:</b> ${{t.straight_distance_km}} km<br>
            <b>Thời gian di chuyển:</b> ${{t.travel_time_minutes}} phút<br>
            <b>Xuất phát:</b> ${{t.origin_departure_time}}
        `);
    }});

    // Populate Table Sample
    const tableBody = document.getElementById('od-table-body');
    tripsData.slice(0, 10).forEach(t => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${{t.origin_zone}}</td>
            <td>${{t.dest_zone}}</td>
            <td>${{t.time_window.split(' ')[0]}}</td>
            <td><b>1</b></td>
        `;
        tableBody.appendChild(tr);
    }});
</script>
</body>
</html>
"""
    output_html_file = os.path.join(data_dir, "od_interactive_dashboard.html")
    with open(output_html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[OK] Generated Interactive HTML Dashboard: {output_html_file}")

if __name__ == "__main__":
    build_interactive_html_dashboard()
