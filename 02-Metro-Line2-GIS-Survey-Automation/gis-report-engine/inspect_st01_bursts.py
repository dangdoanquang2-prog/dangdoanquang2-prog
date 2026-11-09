import sys
import os
import datetime

sys.stdout.reconfigure(encoding='utf-8')

st01_dir = r"D:\baocaotudong\08. Phat sinh-thu hut\ST01"
files = [f for f in os.listdir(st01_dir) if f.lower().endswith('.jpg')]

# Parse epoch timestamp from prefix of filename
records = []
for f in files:
    parts = f.split('_')
    epoch_ms = int(parts[0])
    dt = datetime.datetime.fromtimestamp(epoch_ms / 1000.0)
    records.append((dt, f))

records.sort(key=lambda x: x[0])

print(f"Tổng số ảnh trong ST01: {len(records)}")
print(f"Thời gian ảnh đầu tiên: {records[0][0]}")
print(f"Thời gian ảnh cuối cùng: {records[-1][0]}")

# Group into bursts (gap > 5 minutes)
bursts = []
curr_burst = [records[0]]
for r in records[1:]:
    if (r[0] - curr_burst[-1][0]).total_seconds() > 300:
        bursts.append(curr_burst)
        curr_burst = [r]
    else:
        curr_burst.append(r)
if curr_burst:
    bursts.append(curr_burst)

print(f"\nSố đợt chụp / cụm địa điểm (bursts): {len(bursts)}")
for idx, b in enumerate(bursts):
    t_start = b[0][0].strftime('%Y-%m-%d %H:%M:%S')
    t_end = b[-1][0].strftime('%H:%M:%S')
    print(f"  Cụm {idx+1:2d}: {t_start} -> {t_end} ({len(b):2d} ảnh)")
