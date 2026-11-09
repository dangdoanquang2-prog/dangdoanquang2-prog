import sys
import os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

# Check sample photo watermark
img_path = r"D:\baocaotudong\08. Phat sinh-thu hut\ST01\1789292862065_122107919570885670_g3851386737715031013_d25361a1772f90112e31b99a9ed82646.jpg"
im = Image.open(img_path)
w, h = im.size

# Watermark is in the bottom-left corner
# e.g., x from 0 to w*0.6, y from h*0.65 to h
crop_box = (0, int(h * 0.65), int(w * 0.6), h)
cropped = im.crop(crop_box)
crop_path = r"C:\Users\Dell\.gemini\antigravity-ide\brain\b20a09a9-197b-42a1-8148-51c14105555b\watermark_sample.jpg"
cropped.save(crop_path)
print(f"Cropped watermark area saved: {cropped.size}")

import easyocr
reader = easyocr.Reader(['vi', 'en'], gpu=False)
results = reader.readtext(crop_path, detail=0)
print("OCR Results:")
for line in results:
    print("  ", line)
