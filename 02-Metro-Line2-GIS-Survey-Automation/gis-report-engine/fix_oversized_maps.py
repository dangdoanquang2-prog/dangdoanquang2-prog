import os
import sys
import shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
Image.MAX_IMAGE_PIXELS = None

BACKUP_DIR = r"D:\baocaotudong\maps_backup_raw"
os.makedirs(BACKUP_DIR, exist_ok=True)

targets = [
    r"D:\baocaotudong\maps_vinh\S4\S4_Map1_TongQuan_1000m.png",
    r"D:\baocaotudong\maps_vinh\S10\S10_Map3_Buyt_PUDO.png",
    r"D:\baocaotudong\maps_quan\S18\S18_Map1_TongQuan_1000m.png",
    r"D:\baocaotudong\maps_quan\S19\S19_Map1_TongQuan_1000m.png",
    r"D:\baocaotudong\maps_quan\S20\S20_Map1_TongQuan_1000m.png",
]

crop_box = (0, 0, 2112, 2346)

for p in targets:
    if not os.path.exists(p):
        print(f"File not found: {p}")
        continue
    
    fname = os.path.basename(p)
    parent_name = os.path.basename(os.path.dirname(p))
    backup_file = os.path.join(BACKUP_DIR, f"{parent_name}_{fname}")
    
    if not os.path.exists(backup_file):
        shutil.copy2(p, backup_file)
        print(f"Backed up: {fname} -> {backup_file}")
    
    with Image.open(p) as img:
        orig_size = img.size
        cropped = img.crop(crop_box)
        # Save cropped over original
        cropped.save(p, "PNG", optimize=True)
        print(f"Cropped {parent_name}/{fname}: {orig_size} -> {cropped.size} (Saved: {os.path.getsize(p):,} bytes)")

print("\nAll 5 target maps cropped and verified successfully!")
