import os
import sys

sys.path.insert(0, r"D:\baocaotudong")
from export_enhanced_station_report import extract_station_data_v2

stations = [
    {'num': 1,  'code': 'ST01', 'old_id': 'S1',  'group': 'quan', 'file': 'Ga 1.xlsx',   'name': 'Phan Văn Hớn'},
    {'num': 2,  'code': 'ST02', 'old_id': 'S2',  'group': 'quan', 'file': 'Ga 2.xlsx',   'name': 'Đông Hưng Thuận'},
    {'num': 3,  'code': 'ST03', 'old_id': 'S3',  'group': 'vinh', 'file': 'Ga 3.xlsx',   'name': 'An Sương'},
    {'num': 4,  'code': 'ST04', 'old_id': 'S4',  'group': 'vinh', 'file': 'Ga 4.xlsx',   'name': 'Nguyễn Ảnh Thủ'},
    {'num': 5,  'code': 'ST05', 'old_id': 'S5',  'group': 'vinh', 'file': 'Ga 5.xlsx',   'name': 'Nguyễn Thị Sóc'},
    {'num': 6,  'code': 'ST06', 'old_id': 'S6',  'group': 'vinh', 'file': 'Ga 6.xlsx',   'name': 'Bà Triệu'},
    {'num': 7,  'code': 'ST07', 'old_id': 'S7',  'group': 'quan', 'file': 'Ga 7.xlsx',   'name': 'Lý Thường Kiệt'},
    {'num': 8,  'code': 'ST08', 'old_id': 'S8',  'group': 'quan', 'file': 'Ga 8.xlsx',   'name': 'Nguyễn Thị Nuôi'},
    {'num': 9,  'code': 'ST09', 'old_id': 'S9',  'group': 'vinh', 'file': 'Ga 9.xlsx',   'name': 'Vòng cung Tây Bắc 2'},
    {'num': 10, 'code': 'ST10', 'old_id': 'S10', 'group': 'vinh', 'file': 'Ga 10.xlsx',  'name': 'Vành Đai 3'},
    {'num': 11, 'code': 'ST11', 'old_id': 'S11', 'group': 'quan', 'file': 'Ga 11.xlsx',  'name': 'An Hạ'},
    {'num': 12, 'code': 'ST12', 'old_id': 'S12', 'group': 'quan', 'file': 'Ga 12.xlsx',  'name': 'Tân Phú Trung'},
    {'num': 13, 'code': 'ST13', 'old_id': 'S13', 'group': 'vinh', 'file': 'Ga 13.xlsx',  'name': 'Hương Lộ 2'},
    {'num': 14, 'code': 'ST14', 'old_id': 'S14', 'group': 'quan', 'file': 'Ga 14.xlsx',  'name': 'Đào Thị Kiểm'},
    {'num': 15, 'code': 'ST15', 'old_id': 'S15', 'group': 'vinh', 'file': 'Ga 15.xlsx',  'name': 'Lê Minh Nhựt'},
    {'num': 16, 'code': 'ST16', 'old_id': 'S16', 'group': 'vinh', 'file': 'Ga 16.xlsx',  'name': 'Tân Thông Hội'},
    {'num': 17, 'code': 'ST17', 'old_id': 'S17', 'group': 'vinh', 'file': 'Ga 17.xlsx',  'name': 'Trần Tử Bình'},
    {'num': 18, 'code': 'ST18', 'old_id': 'S18', 'group': 'quan', 'file': 'Ga 18.xlsx',  'name': 'Huỳnh Văn Cọ'},
    {'num': 19, 'code': 'ST19', 'old_id': 'S19', 'group': 'quan', 'file': 'Ga 19_.xlsx', 'name': 'Củ Chi'},
    {'num': 20, 'code': 'ST20', 'old_id': 'S20', 'group': 'quan', 'file': 'Ga 20.xlsx',  'name': 'BV Củ Chi'},
    {'num': 21, 'code': 'ST21', 'old_id': 'S21', 'group': 'quan', 'file': 'Ga 21.xlsx',  'name': 'Nguyễn Thị Rành'},
    {'num': 22, 'code': 'ST22', 'old_id': 'S22', 'group': 'vinh', 'file': 'Ga 22.xlsx',  'name': 'Tân An Hội'},
    {'num': 23, 'code': 'ST23', 'old_id': 'S23', 'group': 'vinh', 'file': 'Ga 23.xlsx',  'name': 'Ba Sa'},
    {'num': 24, 'code': 'ST24', 'old_id': 'S24', 'group': 'vinh', 'file': 'Ga 24.xlsx',  'name': 'Phước Hiệp'},
    {'num': 25, 'code': 'ST25', 'old_id': 'S25', 'group': 'quan', 'file': 'Ga 25.xlsx',  'name': 'Tỉnh Lộ 7'},
    {'num': 26, 'code': 'ST26', 'old_id': 'S26', 'group': 'quan', 'file': 'Ga 26.xlsx',  'name': 'Thái Mỹ'}
]

for s in stations:
    d = extract_station_data_v2(s['group'], s['file'], s['old_id'], s['name'])
    print(f"{s['code']}: roads={len(d['roads'])}, buses={len(d['buses'])}, pudo={len(d['pudo'])}, conflicts={len(d['conflicts'])}, parkride={len(d['parkride'])}")
