import json
import zipfile
import xml.etree.ElementTree as ET
import openpyxl

def main():
    print("Bắt đầu trích xuất dữ liệu...")
    
    # 1. Đọc danh sách tên ga từ Excel
    excel_path = 'Danh sach ten nha ga TL-AH-CC (du kien).xlsx'
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active
    
    stations_info = {}
    for row in ws.iter_rows(values_only=True):
        if row[0] is not None and isinstance(row[0], (int, float)):
            # row format: TT, Nhà ga (Mã + Tên), Số, Chữ (Tên)
            code = f"S{int(row[2])}"
            name = str(row[3]).strip()
            stations_info[code] = {
                "id": code,
                "name": name,
                "full_name": f"{code} - {name}"
            }
            
    print(f"Đã đọc {len(stations_info)} nhà ga từ Excel.")

    # 2. Đọc tọa độ từ KMZ
    kmz_path = 'MRT TL-AH-CC (26 Station)-20260814.kmz'
    kmz = zipfile.ZipFile(kmz_path, 'r')
    kml_data = kmz.read('doc.kml')
    root = ET.fromstring(kml_data)
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    placemarks = root.findall('.//kml:Placemark', ns)
    
    # KML thường có nhiều điểm trùng tên (do lưu nhiều version/lớp). Ta ưu tiên lấy điểm dạng Point.
    coords_dict = {}
    for p in placemarks:
        name_node = p.find('kml:name', ns)
        if name_node is None or not name_node.text:
            continue
        
        name = name_node.text.strip()
        if name in stations_info:
            pt = p.find('.//kml:Point/kml:coordinates', ns)
            if pt is not None and pt.text:
                coords = pt.text.strip().split(',')
                # Lưu (lon, lat)
                coords_dict[name] = {
                    "longitude": float(coords[0]),
                    "latitude": float(coords[1])
                }
                
    # Gộp dữ liệu
    final_db = []
    for i in range(1, 27):
        code = f"S{i}"
        if code in stations_info and code in coords_dict:
            station_data = stations_info[code]
            station_data.update(coords_dict[code])
            final_db.append(station_data)
        else:
            print(f"CẢNH BÁO: Không tìm thấy tọa độ cho ga {code}")

    # 3. Lưu thành JSON
    output_path = 'stations_db.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_db, f, ensure_ascii=False, indent=4)
        
    print(f"Thành công! Đã lưu {len(final_db)} nhà ga vào {output_path}")

if __name__ == '__main__':
    main()
