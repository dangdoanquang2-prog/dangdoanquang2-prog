import os, re, sys, json, openpyxl, urllib.request

sys.stdout.reconfigure(encoding='utf-8')

out_dir = os.path.join(os.getcwd(), 's23')
os.makedirs(out_dir, exist_ok=True)

excel_path = 'Ga 23.xlsx'
wb = openpyxl.load_workbook(excel_path, data_only=True)

downloaded_images = []
seen_ids = set()

def extract_drive_ids(text):
    if not text:
        return []
    # match patterns like id=1uBoxOI6Y6j1b7UfVK97lon7wVQ93csP4 or /d/1uBoxOI6Y6j1b7UfVK97lon7wVQ93csP4
    matches = re.findall(r'id=([a-zA-Z0-9_-]{20,})', str(text))
    matches += re.findall(r'/d/([a-zA-Z0-9_-]{20,})', str(text))
    return list(dict.fromkeys(matches))

def download_file(file_id, save_name):
    save_path = os.path.join(out_dir, save_name)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        return save_path
    
    urls = [
        f'https://lh3.googleusercontent.com/d/{file_id}',
        f'https://drive.google.com/uc?export=download&id={file_id}'
    ]
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    data = resp.read()
                    if len(data) > 1000:
                        with open(save_path, 'wb') as f:
                            f.write(data)
                        return save_path
        except Exception as e:
            continue
    return None

print("[*] Quét toàn bộ link ảnh trong các sheets của Ga 23.xlsx...")

# Sheet: CÁC TUYẾN ĐƯỜNG TIẾP CẬN (Respo
ws_road = wb['CÁC TUYẾN ĐƯỜNG TIẾP CẬN (Respo']
r_headers = [str(ws_road.cell(1, c).value or '').strip() for c in range(1, ws_road.max_column + 1)]
for r in range(2, ws_road.max_row + 1):
    row_d = {r_headers[c-1]: ws_road.cell(r, c).value for c in range(1, ws_road.max_column + 1) if ws_road.cell(r, c).value}
    road_name = row_d.get('Tên đường', f'Tuyến_{r}')
    coord = row_d.get('Toạ độ', '')
    for k, v in row_d.items():
        if 'ảnh' in k.lower() or 'photo' in k.lower() or 'drive.google' in str(v):
            for fid in extract_drive_ids(v):
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    fname = f"road_{r-1}_{fid[:8]}.jpg"
                    print(f"  [-] Đang tải ảnh tuyến đường: {road_name} -> {fname}")
                    p = download_file(fid, fname)
                    if p:
                        downloaded_images.append({
                            'category': 'road',
                            'file': fname,
                            'path': p,
                            'name': road_name,
                            'coord': coord,
                            'desc': f"Hiện trạng mặt đường và vỉa hè: {road_name}"
                        })

# Sheet: ĐIỀU KIỆN KẾT NỐI XE BUÝT (Resp
ws_bus = wb['ĐIỀU KIỆN KẾT NỐI XE BUÝT (Resp']
b_headers = [str(ws_bus.cell(1, c).value or '').strip() for c in range(1, ws_bus.max_column + 1)]
for r in range(2, ws_bus.max_row + 1):
    row_d = {b_headers[c-1]: ws_bus.cell(r, c).value for c in range(1, ws_bus.max_column + 1) if ws_bus.cell(r, c).value}
    b_name = row_d.get('Tên đường', f'Trạm_Buýt_{r}')
    b_lines = row_d.get('Số hiệu tuyến', '')
    b_dist = row_d.get('Khoảng cách đi bộ đến cửa ga gần nhất', '')
    coord = row_d.get('Toạ độ', '')
    for k, v in row_d.items():
        if 'ảnh' in k.lower() or 'photo' in k.lower() or 'drive.google' in str(v):
            for fid in extract_drive_ids(v):
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    fname = f"bus_{r-1}_{fid[:8]}.jpg"
                    print(f"  [-] Đang tải ảnh trạm buýt: {b_name} (Tuyến {b_lines}) -> {fname}")
                    p = download_file(fid, fname)
                    if p:
                        downloaded_images.append({
                            'category': 'bus',
                            'file': fname,
                            'path': p,
                            'name': b_name,
                            'coord': coord,
                            'desc': f"Trạm xe buýt {b_lines} trên đường {b_name} (cách ga {b_dist}m)"
                        })

# Sheet: NHU CẦU ĐIỂM ĐÓN - TRẢ KHÁCH (P
ws_pudo = wb['NHU CẦU ĐIỂM ĐÓN - TRẢ KHÁCH (P']
p_headers = [str(ws_pudo.cell(1, c).value or '').strip() for c in range(1, ws_pudo.max_column + 1)]
for r in range(2, ws_pudo.max_row + 1):
    row_d = {p_headers[c-1]: ws_pudo.cell(r, c).value for c in range(1, ws_pudo.max_column + 1) if ws_pudo.cell(r, c).value}
    coord = row_d.get('Toạ độ', '')
    dist = row_d.get('Khoảng cách đến cửa ga (m)', '10')
    length = row_d.get('Chiều dài lề đường có thể sử dụng (m)', '100')
    for k, v in row_d.items():
        if 'vị trí' in k.lower() or 'ảnh' in k.lower() or 'drive.google' in str(v):
            for fid in extract_drive_ids(v):
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    fname = f"pudo_{r-1}_{fid[:8]}.jpg"
                    print(f"  [-] Đang tải ảnh vị trí PUDO -> {fname}")
                    p = download_file(fid, fname)
                    if p:
                        downloaded_images.append({
                            'category': 'pudo',
                            'file': fname,
                            'path': p,
                            'name': 'Làn PUDO đón trả khách',
                            'coord': coord,
                            'desc': f"Lề đường dự kiến bố trí làn PUDO dài {length}m (cách cửa ga {dist}m)"
                        })

# Sheet: ĐÁNH GIÁ NHU CẦU PARK & RIDE (R
ws_pr = wb['ĐÁNH GIÁ NHU CẦU PARK & RIDE (R']
pr_headers = [str(ws_pr.cell(1, c).value or '').strip() for c in range(1, ws_pr.max_column + 1)]
for r in range(2, ws_pr.max_row + 1):
    row_d = {pr_headers[c-1]: ws_pr.cell(r, c).value for c in range(1, ws_pr.max_column + 1) if ws_pr.cell(r, c).value}
    coord = row_d.get('Toạ độ', '')
    area = row_d.get('Diện tích ước tính (m2)', '1000')
    dist = row_d.get('Khoảng cách đi bộ đến ga', '10')
    for k, v in row_d.items():
        if 'vị trí' in k.lower() or 'ảnh' in k.lower() or 'drive.google' in str(v):
            for fid in extract_drive_ids(v):
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    fname = f"parkride_{r-1}_{fid[:8]}.jpg"
                    print(f"  [-] Đang tải ảnh quỹ đất Park & Ride ({area}m2) -> {fname}")
                    p = download_file(fid, fname)
                    if p:
                        downloaded_images.append({
                            'category': 'parkride',
                            'file': fname,
                            'path': p,
                            'name': 'Quỹ đất Park & Ride',
                            'coord': coord,
                            'desc': f"Khu đất trống {area}m² cách ga {dist}m đề xuất làm bãi xe Park & Ride"
                        })

# Sheet: CÁC ĐIỂM XUNG ĐỘT GIAO THÔNG QU
ws_cf = wb['CÁC ĐIỂM XUNG ĐỘT GIAO THÔNG QU']
cf_headers = [str(ws_cf.cell(1, c).value or '').strip() for c in range(1, ws_cf.max_column + 1)]
for r in range(2, ws_cf.max_row + 1):
    row_d = {cf_headers[c-1]: ws_cf.cell(r, c).value for c in range(1, ws_cf.max_column + 1) if ws_cf.cell(r, c).value}
    c_name = row_d.get('Tên đường/nút', f'Nút_Xung_Đột_{r}')
    c_type = row_d.get('Loại xung đột', '')
    coord = row_d.get('Toạ độ', '')
    for k, v in row_d.items():
        if 'ảnh' in k.lower() or 'drive.google' in str(v):
            for fid in extract_drive_ids(v):
                if fid not in seen_ids:
                    seen_ids.add(fid)
                    fname = f"conflict_{r-1}_{fid[:8]}.jpg"
                    print(f"  [-] Đang tải ảnh điểm xung đột: {c_name} -> {fname}")
                    p = download_file(fid, fname)
                    if p:
                        downloaded_images.append({
                            'category': 'conflict',
                            'file': fname,
                            'path': p,
                            'name': c_name,
                            'coord': coord,
                            'desc': f"Điểm nóng xung đột: {c_name} ({c_type})"
                        })

# Save manifest
manifest_path = os.path.join(out_dir, 'images_manifest.json')
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(downloaded_images, f, ensure_ascii=False, indent=2)

print(f"\n[+] HOÀN TẤT! Đã tải thành công {len(downloaded_images)} hình ảnh vào thư mục 's23/'!")
