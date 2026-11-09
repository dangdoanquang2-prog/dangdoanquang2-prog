import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
from export_enhanced_station_report import ALL_26_STATIONS, BASE_DIR

size_counts = {}
irregular = []

for s in ALL_26_STATIONS:
    grp = s['group']
    sid = s['old_id']
    folder = os.path.join(BASE_DIR, f"maps_{grp}", sid)
    if not os.path.exists(folder): continue
    for f in os.listdir(folder):
        if f.endswith(('.png', '.jpg')) and ('Map' in f):
            p = os.path.join(folder, f)
            with Image.open(p) as img:
                w, h = img.size
                size_counts[(w, h)] = size_counts.get((w, h), 0) + 1
                if (w, h) not in [(2112, 2346), (2112, 2347), (1800, 1987)]:
                    irregular.append((s['code'], sid, f, (w, h)))

print("Size distribution:")
for sz, cnt in sorted(size_counts.items(), key=lambda x: -x[1]):
    print(f"  {sz}: {cnt} images")

print(f"\nIrregular images ({len(irregular)}):")
for code, sid, f, sz in irregular:
    print(f"  {code} ({sid}) - {f}: {sz}")
