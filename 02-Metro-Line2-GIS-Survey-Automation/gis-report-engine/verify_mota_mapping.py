import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# The 15 screenshots in ST01 MÔ TẢ:
# We know:
# mota_01: Screenshot 2026-09-16 161626.png -> Topaz Home / TTN 10 / Minh Phụng
# mota_02: Screenshot 2026-09-16 162010.png -> Minh Phụng & Phan Văn Hớn
# mota_03: Screenshot 2026-09-16 162440.png -> Trường THCS Hà Huy Tập (Facility 3)
# mota_04: Screenshot 2026-09-16 162718.png -> Mầm non Sơn Ca 7
# mota_05: Screenshot 2026-09-16 162834.png -> Trường THCS Nguyễn Ảnh Thủ (Facility 1)
# mota_06: Screenshot 2026-09-16 163024.png -> Khu vực công trình gần TTN 14 / Đường A1
# mota_07: Screenshot 2026-09-16 163323.png -> Hệ thống giáo dục ATY (Facility 4)
# mota_08: Screenshot 2026-09-16 163527.png -> BV Đa khoa Tâm Trí Sài Gòn (Facility 5)
# mota_09: Screenshot 2026-09-16 163657.png -> Trường Tiểu học Nguyễn Thị Định
# mota_10: Screenshot 2026-09-16 163829.png -> Trường Chinh & Song Hành
# mota_11: Screenshot 2026-09-16 164027.png -> Chung cư Phú Cường Home (Facility 6)
# mota_12: Screenshot 2026-09-16 164817.png -> Tân Thới Nhất 17 & Dương Thị Giang (Moscow Tower / Siêu thị)
# mota_13: Screenshot 2026-09-16 165231.png -> Chợ Lạc Quang (Facility 11)
# mota_14: Screenshot 2026-09-18 115140.png -> Đông Hưng Thuận 13B
# mota_15: Screenshot 2026-09-18 122910.png -> BẢN ĐỒ TỔNG THỂ 11 POI QUANH GA ST01 (Vòng tròn R=1000m)

print("=== TỔNG HỢP ÁNH XẠ 15 ẢNH SƠ ĐỒ MÔ TẢ ===")
mapping = [
    ("mota_01", "Topaz Home / TTN10", "Chung cư lân cận ga"),
    ("mota_02", "Minh Phụng & Phan Văn Hớn", "Giao lộ lối vào chung cư/siêu thị"),
    ("mota_03", "Trường THCS Hà Huy Tập", "Công trình #3 trong docx"),
    ("mota_04", "Trường Mầm non Sơn Ca 7", "Trường học lân cận ga"),
    ("mota_05", "Trường THCS Nguyễn Ảnh Thủ", "Công trình #1 trong docx"),
    ("mota_06", "Khu phức hợp TTN 14 / Đ. A1", "Khu dân cư / trường học"),
    ("mota_07", "Hệ thống giáo dục ATY CS Q.12", "Công trình #4 trong docx"),
    ("mota_08", "BV Đa khoa Tâm Trí Sài Gòn", "Công trình #5 trong docx"),
    ("mota_09", "Trường Tiểu học Nguyễn Thị Định", "Trường học lân cận"),
    ("mota_10", "Trường Chinh & Song Hành", "Lối vào tiếp cận hành lang ga"),
    ("mota_11", "Chung cư Phú Cường Home", "Công trình #6 trong docx"),
    ("mota_12", "Chung cư Moscow Tower / TTN17", "Công trình #8 trong docx"),
    ("mota_13", "Chợ Lạc Quang", "Công trình #11 trong docx"),
    ("mota_14", "Đông Hưng Thuận 13B", "Khu dân cư Thái An / Prosper"),
    ("mota_15", "BẢN ĐỒ QUY HOẠCH TỔNG THỂ GA S1", "Bản đồ lớn R=1000m bao gồm tất cả 11 POI")
]

for m, name, role in mapping:
    print(f"  {m:8s} -> {name:32s} | {role}")
