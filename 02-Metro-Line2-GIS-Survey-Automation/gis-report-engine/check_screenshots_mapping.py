import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Coordinates of the 11 facilities from KMZ or addresses:
# 1. THCS Nguyễn Ảnh Thủ: 12/8 bis TTN
# 2. THPT Phan Văn Hớn: 12/22 Tổ 57 KP4, Phan Văn Hớn
# 3. THCS Hà Huy Tập: 54 Nguyễn Văn Quá
# 4. ATY CS Q12: 1/10 Huỳnh Tấn Chùa
# 5. BV Tâm Trí: 171/3 Trường Chinh
# 6. Chung cư Phú Cường Home: 02 Song Hành
# 7. Chung cư Thái An: Nguyễn Văn Quá
# 8. Chung cư Moscow Tower: 19/1 TTN 17
# 9. Chung cư Prosper Plaza: 22/14 Phan Văn Hớn
# 10. Co.opmart Phan Văn Hớn: 102 Phan Văn Hớn
# 11. Chợ Lạc Quang: Hẻm 265 Trường Chinh

print("Rà soát các ảnh trong ST01 MÔ TẢ:")
# Let's check which screenshots map to which facility
print("mota_01 (161626): Prosper Plaza (22/14 Phan Văn Hớn - TTN 10)")
print("mota_02 (162010): Co.opmart Phan Văn Hớn (102 Phan Văn Hớn / Minh Phụng)")
print("mota_03 (162440): THCS Hà Huy Tập")
print("mota_04 (162718): Mầm non Sơn Ca 7 / Tiểu học lân cận")
print("mota_05 (162834): THCS Nguyễn Ảnh Thủ")
print("mota_06 (163024): THPT Phan Văn Hớn (Khu vực TTN14 / A1)")
print("mota_07 (163323): ATY CS Q12 (Huỳnh Tấn Chùa)")
print("mota_08 (163527): BV Tâm Trí Sài Gòn (Trường Chinh)")
print("mota_09 (163657): TH Nguyễn Thị Định / TH lân cận")
print("mota_10 (163829): Lối tiếp cận hành lang ga / Song Hành")
print("mota_11 (164027): Chung cư Phú Cường Home (Song Hành)")
print("mota_12 (164817): Chung cư Moscow Tower (TTN 17)")
print("mota_13 (165231): Chợ Lạc Quang (Trường Chinh)")
print("mota_14 (115140): Chung cư Thái An (Đông Hưng Thuận 13B / Nguyễn Văn Quá)")
print("mota_15 (122910): Bản đồ quy hoạch tổng thể Ga ST01 và bán kính 1km")
