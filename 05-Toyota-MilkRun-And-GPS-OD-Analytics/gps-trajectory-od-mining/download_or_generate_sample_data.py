import os
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_realistic_gps_data():
    """
    Generates realistic 2-day GPS trajectory dataset for 8 internal test devices 
    moving across a city (Hanoi/HCMC area coordinates).
    Simulates Home -> Morning Commute -> Work -> Lunch/Cafe -> Evening Commute -> Home.
    """
    print("[1/3] Generating realistic multi-device GPS trajectory dataset...")
    
    # 8 Test Devices
    devices = [f"DEVICE_{i:02d}" for i in range(1, 9)]
    
    # Base locations (Home and Work locations for each device)
    # Centered around HCMC / Hanoi coordinates with realistic distances
    base_coords = [
        # (Home Lat, Home Lon, Work Lat, Work Lon)
        (10.7769, 106.7009, 10.7950, 106.6880), # District 1 -> District 3
        (10.8010, 106.7110, 10.7720, 106.6980), # Binh Thanh -> District 1
        (10.7550, 106.6600, 10.7800, 106.6900), # District 5 -> District 1
        (10.8230, 106.6290, 10.7980, 106.6800), # Tan Binh -> Phu Nhuan
        (10.7300, 106.7200, 10.7750, 106.7010), # District 7 -> District 1
        (10.8500, 106.7500, 10.8000, 106.7000), # Thu Duc -> Binh Thanh
        (10.7600, 106.6800, 10.7769, 106.7009), # District 10 -> District 1
        (10.7900, 106.6500, 10.7400, 106.7100), # Tan Binh -> District 7
    ]
    
    start_date = datetime(2026, 8, 17, 6, 0, 0) # Monday morning 6 AM
    records = []
    
    for idx, dev_id in enumerate(devices):
        h_lat, h_lon, w_lat, w_lon = base_coords[idx]
        
        # Simulate 2 days (Day 1 & Day 2)
        for day in range(2):
            day_start = start_date + timedelta(days=day)
            
            # --- Event 1: Stay at Home (06:00 - 07:30) ---
            t = day_start
            t_end = day_start + timedelta(hours=1, minutes=30)
            while t < t_end:
                # Slight GPS jitter around home (within ~10m)
                records.append({
                    "device_id": dev_id,
                    "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": h_lat + random.uniform(-0.0001, 0.0001),
                    "longitude": h_lon + random.uniform(-0.0001, 0.0001),
                    "accuracy": random.uniform(5.0, 15.0)
                })
                t += timedelta(seconds=random.randint(45, 90))
                
            # --- Event 2: Morning Commute Home -> Work (07:30 - 08:15) ---
            t_end = day_start + timedelta(hours=2, minutes=15)
            steps = 40
            for s in range(steps):
                ratio = s / float(steps)
                lat = h_lat + ratio * (w_lat - h_lat) + random.uniform(-0.0003, 0.0003)
                lon = h_lon + ratio * (w_lon - h_lon) + random.uniform(-0.0003, 0.0003)
                curr_t = t + timedelta(seconds=int(45 * 60 * ratio))
                records.append({
                    "device_id": dev_id,
                    "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": random.uniform(8.0, 20.0)
                })
                
            # --- Event 3: Stay at Work (08:15 - 12:00) ---
            t = day_start + timedelta(hours=2, minutes=15)
            t_end = day_start + timedelta(hours=6)
            while t < t_end:
                records.append({
                    "device_id": dev_id,
                    "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": w_lat + random.uniform(-0.0001, 0.0001),
                    "longitude": w_lon + random.uniform(-0.0001, 0.0001),
                    "accuracy": random.uniform(5.0, 15.0)
                })
                t += timedelta(seconds=random.randint(60, 120))
                
            # --- Event 4: Lunch / Cafe Trip (12:00 - 13:00) ---
            c_lat = w_lat + random.uniform(-0.005, 0.005) # Cafe nearby
            c_lon = w_lon + random.uniform(-0.005, 0.005)
            # Trip Work -> Cafe (12:00 - 12:10)
            t = day_start + timedelta(hours=6)
            t_end = t + timedelta(minutes=10)
            steps = 10
            for s in range(steps):
                ratio = s / float(steps)
                lat = w_lat + ratio * (c_lat - w_lat)
                lon = w_lon + ratio * (c_lon - w_lon)
                curr_t = t + timedelta(seconds=int(10 * 60 * ratio))
                records.append({
                    "device_id": dev_id,
                    "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": random.uniform(5.0, 15.0)
                })
            # Stay at Cafe (12:10 - 12:50)
            t = day_start + timedelta(hours=6, minutes=10)
            t_end = day_start + timedelta(hours=6, minutes=50)
            while t < t_end:
                records.append({
                    "device_id": dev_id,
                    "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": c_lat + random.uniform(-0.0001, 0.0001),
                    "longitude": c_lon + random.uniform(-0.0001, 0.0001),
                    "accuracy": random.uniform(5.0, 15.0)
                })
                t += timedelta(seconds=random.randint(60, 120))
            # Trip Cafe -> Work (12:50 - 13:00)
            t = day_start + timedelta(hours=6, minutes=50)
            t_end = day_start + timedelta(hours=7)
            steps = 10
            for s in range(steps):
                ratio = s / float(steps)
                lat = c_lat + ratio * (w_lat - c_lat)
                lon = c_lon + ratio * (w_lon - c_lon)
                curr_t = t + timedelta(seconds=int(10 * 60 * ratio))
                records.append({
                    "device_id": dev_id,
                    "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": random.uniform(5.0, 15.0)
                })

            # --- Event 5: Afternoon Work (13:00 - 17:30) ---
            t = day_start + timedelta(hours=7)
            t_end = day_start + timedelta(hours=11, minutes=30)
            while t < t_end:
                records.append({
                    "device_id": dev_id,
                    "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": w_lat + random.uniform(-0.0001, 0.0001),
                    "longitude": w_lon + random.uniform(-0.0001, 0.0001),
                    "accuracy": random.uniform(5.0, 15.0)
                })
                t += timedelta(seconds=random.randint(60, 120))

            # --- Event 6: Evening Commute Work -> Home (17:30 - 18:30) ---
            t = day_start + timedelta(hours=11, minutes=30)
            steps = 45
            for s in range(steps):
                ratio = s / float(steps)
                lat = w_lat + ratio * (h_lat - w_lat) + random.uniform(-0.0003, 0.0003)
                lon = w_lon + ratio * (h_lon - w_lon) + random.uniform(-0.0003, 0.0003)
                curr_t = t + timedelta(seconds=int(60 * 60 * ratio))
                records.append({
                    "device_id": dev_id,
                    "timestamp": curr_t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": random.uniform(8.0, 20.0)
                })
                
            # --- Event 7: Stay at Home (18:30 - 23:59) ---
            t = day_start + timedelta(hours=12, minutes=30)
            t_end = day_start + timedelta(hours=17, minutes=59)
            while t < t_end:
                records.append({
                    "device_id": dev_id,
                    "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "latitude": h_lat + random.uniform(-0.0001, 0.0001),
                    "longitude": h_lon + random.uniform(-0.0001, 0.0001),
                    "accuracy": random.uniform(5.0, 15.0)
                })
                t += timedelta(seconds=random.randint(120, 300))

    df = pd.DataFrame(records)
    output_path = os.path.join("d:\\data", "raw_gps_logs_sample.csv")
    df.to_csv(output_path, index=False)
    print(f"[OK] Generated {len(df)} raw GPS logs for {len(devices)} devices saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_realistic_gps_data()
