import os
import sys
from PIL import Image
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
from export_enhanced_station_report import ALL_26_STATIONS, BASE_DIR

oversized_maps = []
all_maps = []

for s in ALL_26_STATIONS:
    grp = s['group']
    sid = s['old_id']
    folder = os.path.join(BASE_DIR, f"maps_{grp}", sid)
    if not os.path.exists(folder):
        print(f"{s['code']} ({sid}): Folder not found!")
        continue
    for f in os.listdir(folder):
        if f.endswith(('.png', '.jpg')) and ('Map' in f):
            p = os.path.join(folder, f)
            try:
                with Image.open(p) as img:
                    w, h = img.size
                    all_maps.append((s['code'], sid, f, w, h))
                    if w > 2500 or h > 2600:
                        arr = np.array(img)
                        if arr.shape[2] == 4:
                            alpha = arr[:,:,3]
                            rgb = arr[:,:,:3]
                            content_mask = (alpha > 10) & ((rgb[:,:,0] < 250) | (rgb[:,:,1] < 250) | (rgb[:,:,2] < 250))
                        else:
                            rgb = arr[:,:,:3]
                            content_mask = (rgb[:,:,0] < 250) | (rgb[:,:,1] < 250) | (rgb[:,:,2] < 250)
                        rows = np.where(content_mask.any(axis=1))[0]
                        cols = np.where(content_mask.any(axis=0))[0]
                        cw = (cols[-1] - cols[0]) if len(cols) else 0
                        ch = (rows[-1] - rows[0]) if len(rows) else 0
                        ymin = rows[0] if len(rows) else 0
                        ymax = rows[-1] if len(rows) else 0
                        xmin = cols[0] if len(cols) else 0
                        xmax = cols[-1] if len(cols) else 0
                        oversized_maps.append((s['code'], sid, f, p, (w, h), (cw, ch), (ymin, ymax, xmin, xmax)))
            except Exception as e:
                print(f"Error reading {p}: {e}")

print(f"\nTotal maps checked: {len(all_maps)}")
print(f"Total oversized maps found: {len(oversized_maps)}")
for code, sid, f, p, (w, h), (cw, ch), bbox in oversized_maps:
    print(f"  {code} ({sid}) - {f}: image=({w}, {h}) -> content=({cw}, {ch}), bbox={bbox}")
