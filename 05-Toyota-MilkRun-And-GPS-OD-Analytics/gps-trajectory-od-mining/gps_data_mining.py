import os
import math
import json
import pandas as pd
import numpy as np
from datetime import datetime

# --- HAVERSINE DISTANCE HELPER (Meters) ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

# --- STEP 1: STAY POINT DETECTION ALGORITHM ---
def detect_stay_points(df, dist_threshold=50.0, time_threshold_minutes=15.0):
    """
    Rule-based Stay Point Detection Algorithm:
    Group consecutive GPS logs for a device where spatial distance <= dist_threshold (meters)
    and duration >= time_threshold_minutes (minutes).
    """
    stay_points = []
    
    # Ensure sorted by device and timestamp
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by=['device_id', 'timestamp_dt']).reset_index(drop=True)
    
    for dev_id, group in df.groupby('device_id'):
        records = group.to_dict('records')
        i = 0
        n = len(records)
        
        while i < n:
            j = i + 1
            while j < n:
                dist = haversine_distance(
                    records[i]['latitude'], records[i]['longitude'],
                    records[j]['latitude'], records[j]['longitude']
                )
                if dist > dist_threshold:
                    break
                j += 1
            
            # Check duration between record i and record j-1
            t_start = records[i]['timestamp_dt']
            t_end = records[j - 1]['timestamp_dt']
            duration_minutes = (t_end - t_start).total_seconds() / 60.0
            
            if duration_minutes >= time_threshold_minutes:
                # Calculate mean location of stay point
                subset = records[i:j]
                mean_lat = sum(r['latitude'] for r in subset) / len(subset)
                mean_lon = sum(r['longitude'] for r in subset) / len(subset)
                
                stay_points.append({
                    "device_id": dev_id,
                    "start_time": t_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": t_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_minutes": round(duration_minutes, 2),
                    "latitude": round(mean_lat, 6),
                    "longitude": round(mean_lon, 6),
                    "num_points": len(subset)
                })
                i = j  # Move to next unseen point
            else:
                i += 1
                
    return pd.DataFrame(stay_points)

# --- STEP 2: TRIP EXTRACTION ALGORITHM ---
def extract_trips(df_stay_points):
    """
    Extract Trips as movements between consecutive Stay Points for each device.
    Trip Origin = Stay Point A (end_time, lat, lon)
    Trip Destination = Stay Point B (start_time, lat, lon)
    """
    trips = []
    df_stay_points['start_time_dt'] = pd.to_datetime(df_stay_points['start_time'])
    df_stay_points['end_time_dt'] = pd.to_datetime(df_stay_points['end_time'])
    
    for dev_id, group in df_stay_points.groupby('device_id'):
        group = group.sort_values(by='start_time_dt').reset_index(drop=True)
        for idx in range(len(group) - 1):
            sp_origin = group.iloc[idx]
            sp_dest = group.iloc[idx + 1]
            
            # Check time difference between trips (must be within reasonable window e.g. < 4 hours)
            departure_time = sp_origin['end_time_dt']
            arrival_time = sp_dest['start_time_dt']
            travel_time_minutes = (arrival_time - departure_time).total_seconds() / 60.0
            
            if 0 < travel_time_minutes <= 360:  # Valid trip within 6 hours
                dist_meters = haversine_distance(
                    sp_origin['latitude'], sp_origin['longitude'],
                    sp_dest['latitude'], sp_dest['longitude']
                )
                
                # Determine hour of departure for time-window aggregation
                departure_hour = departure_time.hour
                if 6 <= departure_hour < 9:
                    time_window = "06:00-09:00 (Peak Morning)"
                elif 11 <= departure_hour < 14:
                    time_window = "11:00-14:00 (Mid-day)"
                elif 16 <= departure_hour < 19:
                    time_window = "16:00-19:00 (Peak Evening)"
                else:
                    time_window = "Off-Peak"

                trips.append({
                    "device_id": dev_id,
                    "trip_index": idx + 1,
                    "origin_lat": sp_origin['latitude'],
                    "origin_lon": sp_origin['longitude'],
                    "origin_departure_time": sp_origin['end_time'],
                    "dest_lat": sp_dest['latitude'],
                    "dest_lon": sp_dest['longitude'],
                    "dest_arrival_time": sp_dest['start_time'],
                    "travel_time_minutes": round(travel_time_minutes, 2),
                    "straight_distance_km": round(dist_meters / 1000.0, 3),
                    "departure_hour": departure_hour,
                    "time_window": time_window
                })
                
    return pd.DataFrame(trips)

# --- STEP 3: SPATIAL ZONE GRIDDING & OD MATRIX GENERATION ---
def generate_od_matrix(df_trips, grid_size_deg=0.005):
    """
    Bins coordinates into Spatial Grid Cells (~500m x 500m grid cell size)
    and constructs the Origin-Destination (OD) Matrix.
    """
    def lat_lon_to_zone(lat, lon):
        # Round coordinates to grid cells
        lat_grid = round(math.floor(lat / grid_size_deg) * grid_size_deg, 4)
        lon_grid = round(math.floor(lon / grid_size_deg) * grid_size_deg, 4)
        return f"ZONE_{lat_grid}_{lon_grid}"

    df_trips['origin_zone'] = df_trips.apply(lambda r: lat_lon_to_zone(r['origin_lat'], r['origin_lon']), axis=1)
    df_trips['dest_zone'] = df_trips.apply(lambda r: lat_lon_to_zone(r['dest_lat'], r['dest_lon']), axis=1)

    # Group by Origin Zone, Dest Zone, and Time Window
    od_grouped = df_trips.groupby(['origin_zone', 'dest_zone', 'time_window']).size().reset_index(name='trip_count')
    od_total = df_trips.groupby(['origin_zone', 'dest_zone']).size().reset_index(name='total_trips')
    
    return df_trips, od_grouped, od_total

# --- MAIN EXECUTION ---
def main():
    print("[2/3] Executing GPS Data Mining Pipeline (Stay Point & Trip Extraction)...")
    data_dir = "d:\\data"
    geolife_real_file = os.path.join(data_dir, "raw_gps_logs_geolife_real.csv")
    geolife_file = os.path.join(data_dir, "raw_gps_logs_geolife.csv")
    sample_file = os.path.join(data_dir, "raw_gps_logs_sample.csv")
    
    if os.path.exists(geolife_real_file):
        input_file = geolife_real_file
        print(f"Using REAL Microsoft GeoLife Dataset (217k records): {input_file}")
    elif os.path.exists(geolife_file):
        input_file = geolife_file
        print(f"Using Real GeoLife Dataset: {input_file}")
    elif os.path.exists(sample_file):
        input_file = sample_file
        print(f"Using Sample GPS Dataset: {input_file}")
    else:
        print("Error: No GPS dataset found.")
        return

    # Load Raw Logs
    df_raw = pd.read_csv(input_file)
    print(f"Loaded {len(df_raw)} raw GPS records.")
    
    # 1. Stay Point Detection
    df_stay = detect_stay_points(df_raw, dist_threshold=50.0, time_threshold_minutes=15.0)
    stay_out_file = os.path.join(data_dir, "stay_points_detected.csv")
    df_stay.to_csv(stay_out_file, index=False)
    print(f"[OK] Extracted {len(df_stay)} Stay Points. Saved to: {stay_out_file}")

    # 2. Trip Extraction
    df_trips = extract_trips(df_stay)
    
    # 3. OD Matrix Generation
    df_trips_with_zones, od_window, od_total = generate_od_matrix(df_trips, grid_size_deg=0.005)
    
    trips_out_file = os.path.join(data_dir, "trips_extracted.csv")
    od_out_file = os.path.join(data_dir, "od_matrix_result.csv")
    
    df_trips_with_zones.to_csv(trips_out_file, index=False)
    od_window.to_csv(od_out_file, index=False)
    print(f"[OK] Extracted {len(df_trips)} Trips. Saved to: {trips_out_file}")
    print(f"[OK] Generated OD Matrix with {len(od_window)} zone-pair records. Saved to: {od_out_file}")

    # 4. Generate Executive Summary Metrics
    avg_trips_per_device_day = round(len(df_trips) / (df_raw['device_id'].nunique() * 2.0), 2)
    summary = {
        "total_raw_gps_points": len(df_raw),
        "total_devices_analyzed": int(df_raw['device_id'].nunique()),
        "total_stay_points_detected": len(df_stay),
        "total_trips_extracted": len(df_trips),
        "avg_trips_per_device_per_day": avg_trips_per_device_day,
        "total_od_pairs_generated": len(od_window),
        "execution_status": "SUCCESS"
    }
    
    summary_file = os.path.join(data_dir, "poc_summary_metrics.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Summary Metrics saved to: {summary_file}")
    print("\n--- SUMMARY METRICS ---")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
