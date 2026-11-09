import os, sys, json

sys.stdout.reconfigure(encoding='utf-8')

def build_interactive_html():
    manifest_file = os.path.join('s23', 'images_manifest.json')
    images_by_cat = {'road': [], 'bus': [], 'pudo': [], 'parkride': [], 'conflict': []}
    if os.path.exists(manifest_file):
        with open(manifest_file, 'r', encoding='utf-8') as f:
            all_imgs = json.load(f)
            for item in all_imgs:
                cat = item.get('category', 'road')
                if cat in images_by_cat:
                    images_by_cat[cat].append(item)

    road_imgs = images_by_cat.get('road', [])
    bus_imgs = images_by_cat.get('bus', [])
    pudo_imgs = images_by_cat.get('pudo', [])
    pr_imgs = images_by_cat.get('parkride', [])
    cf_imgs = images_by_cat.get('conflict', [])

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chỉnh Sửa & Ghi Chú - Báo Cáo Ga S23 Ba Sa</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #003366;
            --primary-light: #e8f0fe;
            --accent: #d32f2f;
            --text-main: #24292f;
            --text-muted: #57606a;
            --bg-page: #f0f3f6;
            --bg-card: #ffffff;
            --border: #d0d7de;
            --note-bg: #fffbf0;
            --note-border: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-page);
            color: var(--text-main);
            line-height: 1.6;
            padding: 70px 20px 40px 20px;
        }}

        /* FLOATING ACTION BAR */
        .floating-top-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 58px;
            background: #002244;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.18);
            z-index: 9999;
        }}
        .bar-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .bar-title {{
            font-size: 14.5px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        .badge-count {{
            background: #f59e0b;
            color: #000;
            font-size: 12px;
            font-weight: 700;
            padding: 2px 9px;
            border-radius: 12px;
        }}
        .bar-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .btn {{
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        .btn-primary {{
            background: #10b981;
            color: #fff;
            box-shadow: 0 2px 6px rgba(16, 185, 129, 0.4);
        }}
        .btn-primary:hover {{
            background: #059669;
            transform: translateY(-1px);
        }}
        .btn-secondary {{
            background: rgba(255,255,255,0.15);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .btn-secondary:hover {{
            background: rgba(255,255,255,0.25);
        }}

        /* TOAST ALERT */
        #toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: #fff;
            padding: 14px 22px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            display: none;
            z-index: 10000;
            animation: slideUp 0.3s ease;
        }}
        @keyframes slideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        /* REPORT CONTAINER */
        .container {{
            max-width: 1060px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            padding: 44px;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 24px;
            margin-bottom: 30px;
        }}
        .sub-header {{
            font-size: 12.5px;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        h1 {{
            font-size: 25px;
            color: var(--primary);
            margin: 10px 0 6px;
            line-height: 1.3;
        }}
        .meta {{
            font-size: 13.5px;
            color: var(--text-muted);
            font-style: italic;
        }}

        .section-title {{
            font-size: 17.5px;
            font-weight: 700;
            color: var(--primary);
            margin: 36px 0 14px;
            padding-bottom: 6px;
            border-bottom: 1.5px solid #eaecef;
        }}
        .h2-title {{
            font-size: 14.5px;
            font-weight: 600;
            color: #333;
            margin: 18px 0 10px;
        }}
        p {{
            font-size: 14px;
            margin-bottom: 12px;
            color: #333;
        }}

        /* NOTE BOX COMPONENT */
        .note-card {{
            background: var(--note-bg);
            border: 1.5px solid var(--note-border);
            border-radius: 8px;
            padding: 14px 18px;
            margin: 16px 0 28px 0;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
        }}
        .note-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .note-title {{
            font-size: 13px;
            font-weight: 700;
            color: #b45309;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .note-quick-tags {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .quick-tag {{
            font-size: 11px;
            background: #fff;
            border: 1px solid #d97706;
            color: #b45309;
            padding: 2px 8px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .quick-tag:hover {{
            background: #f59e0b;
            color: #fff;
        }}
        .note-textarea {{
            width: 100%;
            min-height: 64px;
            padding: 10px 12px;
            font-family: inherit;
            font-size: 13px;
            border: 1px solid #fcd34d;
            border-radius: 6px;
            background: #fff;
            color: #1f2937;
            resize: vertical;
        }}
        .note-textarea:focus {{
            outline: none;
            border-color: #f59e0b;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
        }}

        /* TABLES */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0 20px;
            font-size: 13.5px;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 10px 14px;
            text-align: left;
            vertical-align: middle;
        }}
        th {{
            background-color: var(--primary);
            color: #ffffff;
            font-weight: 600;
            font-size: 13px;
        }}
        tr:nth-child(even) {{
            background-color: #fcfcfc;
        }}
        .table-light-bg td {{
            background-color: #f8fafc;
        }}

        /* MAPS */
        .map-card {{
            text-align: center;
            margin: 18px 0 24px;
            background: #fff;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
        }}
        .map-card img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        .map-caption {{
            font-size: 12.5px;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 8px;
        }}

        /* PHOTOS */
        .photo-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin: 14px 0 20px;
        }}
        .photo-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            background: #fafafa;
        }}
        .photo-card img {{
            width: 100%;
            height: 210px;
            object-fit: cover;
            display: block;
        }}
        .photo-info {{
            padding: 10px 12px;
            font-size: 12.5px;
            color: #444;
            line-height: 1.5;
        }}

        /* BADGES */
        .badge {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-warning {{ background: #fff3e0; color: #e65100; }}
        .badge-danger {{ background: #ffebee; color: #c62828; }}
        .badge-info {{ background: #e1f5fe; color: #0277bd; }}
        .oas-total {{
            background: #e3f2fd !important;
            font-weight: bold;
            color: var(--primary);
            font-size: 14px;
        }}

        /* IN-PLACE EDITABLE HIGHLIGHT */
        [contenteditable="true"] {{
            outline: 1px dashed transparent;
            border-radius: 3px;
            transition: all 0.2s;
        }}
        body.edit-mode-active [contenteditable="true"]:hover {{
            background: #fef3c7;
            outline: 1.5px dashed #f59e0b;
        }}
        body.edit-mode-active [contenteditable="true"]:focus {{
            background: #fffbeb;
            outline: 2px solid #3b82f6;
        }}

        .signature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-top: 36px;
            padding-top: 20px;
            border-top: 1px dashed var(--border);
        }}
        .sign-box {{
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .sign-title {{
            font-weight: 700;
            color: var(--primary);
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .sign-body {{
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            font-size: 13px;
            color: #555;
        }}

        @media print {{
            body {{ background: #fff; padding: 0; }}
            .floating-top-bar, .note-card {{ display: none !important; }}
            .container {{ box-shadow: none; padding: 0; max-width: 100%; }}
        }}
    </style>
</head>
<body>

<!-- TOP ACTION BAR -->
<div class="floating-top-bar">
    <div class="bar-left">
        <span class="bar-title">📝 Báo Cáo Ga S23 - Ba Sa (Chế độ Xem & Ghi Chú)</span>
        <span id="noteCounter" class="badge-count">0 ghi chú</span>
    </div>
    <div class="bar-actions">
        <label style="font-size: 12.5px; display: flex; align-items: center; gap: 6px; cursor: pointer; margin-right: 8px;">
            <input type="checkbox" id="toggleDirectEdit" onchange="toggleDirectEditing(this.checked)">
            <span>Sửa văn bản trực tiếp</span>
        </label>
        <button class="btn btn-secondary" onclick="exportJSONFile()">📥 Tải file JSON</button>
        <button class="btn btn-secondary" onclick="window.print()">🖨️ In / PDF</button>
        <button class="btn btn-primary" onclick="saveAllFeedback()">💾 LƯU & GỬI CHO AI</button>
    </div>
</div>

<div id="toast">✅ Đã lưu góp ý thành công vào Workspace!</div>

<div class="container">
    <div class="header">
        <div class="sub-header">Dự Án Đường Sắt Đô Thị Thành Phố Hồ Chí Minh (Metro Tuyến 2 - Giai Đoạn 2)</div>
        <h1>BÁO CÁO KHẢO SÁT HIỆN TRẠNG TIẾP CẬN VÀ TRUNG CHUYỂN<br>GA S23 – BA SA</h1>
        <div class="meta">Quy chuẩn kỹ thuật A đến M (Nhiệm vụ 9) | Bóc tách từ file Ga 23.xlsx | Khảo sát: 03/09/2026</div>
    </div>

    <!-- Ô GHI CHÚ CHUNG TỔNG THỂ -->
    <div class="note-card" style="background: #eef2ff; border-color: #6366f1;">
        <div class="note-header">
            <span class="note-title" style="color: #4338ca;">⭐ Ghi Chú & Yêu Cầu Tổng Thể Cho Toàn Bộ Báo Cáo:</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_general', '+ Cần chỉnh sửa bản đồ')">+ Sửa bản đồ</span>
                <span class="quick-tag" onclick="appendTag('note_general', '+ Cần thay đổi số liệu')">+ Đổi số liệu</span>
                <span class="quick-tag" onclick="appendTag('note_general', '+ Cần thêm thông tin')">+ Thêm thông tin</span>
            </div>
        </div>
        <textarea id="note_general" class="note-textarea" placeholder="Nhập yêu cầu chỉnh sửa chung cho báo cáo Ga S23 tại đây..."></textarea>
    </div>

    <!-- MỤC A -->
    <div class="section-title">MỤC A. THÔNG TIN CHUNG NHÀ GA</div>
    <table class="table-light-bg">
        <tr>
            <td style="width: 25%;"><strong>Mã nhà ga:</strong></td>
            <td style="width: 25%;" data-edit-id="a_code">S23</td>
            <td style="width: 25%;"><strong>Tên nhà ga:</strong></td>
            <td style="width: 25%;" data-edit-id="a_name"><strong>Ba Sa</strong> (S23 - Ba Sa)</td>
        </tr>
        <tr>
            <td><strong>Tuyến Metro:</strong></td>
            <td data-edit-id="a_metro">Metro Tuyến 2 (Đoạn kéo dài Củ Chi)</td>
            <td><strong>Vị trí quy hoạch:</strong></td>
            <td data-edit-id="a_pos">Trên cao / Đi bằng (Trục Phan Văn Khải)</td>
        </tr>
        <tr>
            <td><strong>Địa giới hành chính:</strong></td>
            <td data-edit-id="a_location">Xã Thái Mỹ & Tân An Hội, Củ Chi</td>
            <td><strong>Tọa độ GPS tim ga:</strong></td>
            <td data-edit-id="a_gps"><span class="badge badge-info">11.000752 N, 106.437926 E</span></td>
        </tr>
        <tr>
            <td><strong>Thời gian khảo sát:</strong></td>
            <td data-edit-id="a_time">03/09/2026 (08:20 – 11:25)</td>
            <td><strong>Thời tiết & Tầm nhìn:</strong></td>
            <td data-edit-id="a_weather">Nắng nhẹ, khô ráo, tầm nhìn tốt</td>
        </tr>
        <tr>
            <td><strong>Khảo sát viên:</strong></td>
            <td data-edit-id="a_surveyor">Nguyễn Thành Vinh</td>
            <td><strong>Email liên hệ:</strong></td>
            <td data-edit-id="a_email">antoniusnttvinh7325@gmail.com</td>
        </tr>
    </table>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục A (Thông tin chung):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_a', '+ Đổi tên ga')">+ Đổi tên ga</span>
                <span class="quick-tag" onclick="appendTag('note_sec_a', '+ Sửa tọa độ GPS')">+ Sửa GPS</span>
                <span class="quick-tag" onclick="appendTag('note_sec_a', '+ Cập nhật khảo sát viên')">+ Cập nhật người KS</span>
            </div>
        </div>
        <textarea id="note_sec_a" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục A..."></textarea>
    </div>

    <!-- MỤC B -->
    <div class="section-title">MỤC B. HIỆN TRẠNG ĐƯỜNG TIẾP CẬN GA</div>
    <div class="h2-title">1. Bản đồ GIS Mạng lưới Đường Giao thông Tiếp cận (Bán kính 1000m)</div>
    <div class="map-card">
        <img src="maps/S23_Map1_TongQuan_1000m.png" alt="Bản đồ 1: Tổng quan mạng lưới">
        <div class="map-caption">Hình B.1: Sơ đồ mạng lưới giao thông bán kính 200m - 500m - 1000m quanh Ga S23 Ba Sa (Nền Esri WorldStreetMap)</div>
    </div>

    <div class="h2-title">2. Bảng Thống kê Thông số Kỹ thuật Tuyến đường tiếp cận</div>
    <table>
        <thead>
            <tr>
                <th>Mã tuyến</th>
                <th>Tên tuyến đường</th>
                <th>Phân loại</th>
                <th>Số làn & Mặt đường</th>
                <th>Lộ giới</th>
                <th>Hiện trạng & Đánh giá tiếp cận</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>R1</strong></td>
                <td data-edit-id="b_r1_name"><strong>Phan Văn Khải (QL22)</strong></td>
                <td><span class="badge badge-success">Đường chính</span></td>
                <td data-edit-id="b_r1_width">6 làn xe (30.0 m)</td>
                <td data-edit-id="b_r1_limit">60 m</td>
                <td data-edit-id="b_r1_eval">Trục đại lộ có dải phân cách cứng, không ùn tắc. Xe buýt, ô tô, xe máy tiếp cận rất tốt.</td>
            </tr>
            <tr>
                <td><strong>R2</strong></td>
                <td data-edit-id="b_r2_name"><strong>Đường Ba Sa</strong></td>
                <td><span class="badge badge-info">Đường thứ yếu</span></td>
                <td data-edit-id="b_r2_width">2 làn xe (7.5 m)</td>
                <td data-edit-id="b_r2_limit">16 m</td>
                <td data-edit-id="b_r2_eval">Tuyến giao cắt đấu nối khu dân cư. Tiếp cận ô tô, xe máy thuận lợi; xe buýt hạn chế.</td>
            </tr>
            <tr>
                <td><strong>R3</strong></td>
                <td data-edit-id="b_r3_name"><strong>Đường Số 622</strong></td>
                <td><span class="badge badge-info">Đường thứ yếu</span></td>
                <td data-edit-id="b_r3_width">2 làn xe (7.5 m)</td>
                <td data-edit-id="b_r3_limit">16 m</td>
                <td data-edit-id="b_r3_eval">Đường dân sinh kết nối ấp Phước Thạnh. Mặt đường bê tông nhựa tốt.</td>
            </tr>
            <tr>
                <td><strong>R4</strong></td>
                <td data-edit-id="b_r4_name">Đường Nguyễn Thị Nhia</td>
                <td>Đường nhánh</td>
                <td>2 làn xe (7.5 m)</td>
                <td>16 m</td>
                <td>Tuyến đường phân khu tiếp cận phía ấp Phước Hiệp.</td>
            </tr>
            <tr>
                <td><strong>R5</strong></td>
                <td data-edit-id="b_r5_name">Đường Phạm Thị Thung</td>
                <td>Đường nhánh</td>
                <td>2 làn xe (7.5 m)</td>
                <td>16 m</td>
                <td>Đường kết nối ấp Phước Hòa, vỉa hè tự nhiên có cây xanh.</td>
            </tr>
        </tbody>
    </table>

    <div class="h2-title">3. Hình ảnh Minh họa Tuyến đường Tiếp cận</div>
    <div class="photo-grid">
        <div class="photo-card">
            <img src="{road_imgs[0]['path'] if len(road_imgs)>0 else ''}" alt="Đường Phan Văn Khải">
            <div class="photo-info">
                <strong>• Tuyến:</strong> {road_imgs[0]['name'] if len(road_imgs)>0 else 'Phan Văn Khải'}<br>
                <strong>• Tọa độ GPS:</strong> {road_imgs[0]['coord'] if len(road_imgs)>0 else ''}<br>
                <strong>• Hiện trạng:</strong> Mặt đường chính rộng 30m, 6 làn xe lưu thông 2 chiều thông thoáng.
            </div>
        </div>
        <div class="photo-card">
            <img src="{road_imgs[10]['path'] if len(road_imgs)>10 else (road_imgs[1]['path'] if len(road_imgs)>1 else '')}" alt="Đường Ba Sa">
            <div class="photo-info">
                <strong>• Tuyến:</strong> Đường Ba Sa (Giao cắt Ga S23)<br>
                <strong>• Tọa độ GPS:</strong> 10.992704, 106.448811<br>
                <strong>• Hiện trạng:</strong> Mặt đường 7.5m, lộ giới 16m kết nối trực tiếp vào ga.
            </div>
        </div>
    </div>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục B (Đường tiếp cận & Bản đồ 1):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_b', '+ Sửa bề rộng mặt đường')">+ Sửa bề rộng</span>
                <span class="quick-tag" onclick="appendTag('note_sec_b', '+ Bổ sung tuyến đường mới')">+ Thêm tuyến đường</span>
                <span class="quick-tag" onclick="appendTag('note_sec_b', '+ Yêu cầu sửa Bản đồ 1')">+ Sửa Bản đồ 1</span>
            </div>
        </div>
        <textarea id="note_sec_b" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục B..."></textarea>
    </div>

    <!-- MỤC C -->
    <div class="section-title">MỤC C. ĐIỀU KIỆN ĐI BỘ ĐẾN GA</div>
    <div class="h2-title">1. Bản đồ GIS Phân vùng Tiếp cận Đi bộ (Bán kính 200m & 500m)</div>
    <div class="map-card">
        <img src="maps/S23_Map2_DiBo_200m_500m.png" alt="Bản đồ 2: Vùng đi bộ">
        <div class="map-caption">Hình C.1: Sơ đồ vùng tiếp cận đi bộ cự ly gần (≤300m) và cự ly trung bình (300m - 500m) quanh Ga S23</div>
    </div>

    <div class="h2-title">2. Bảng Đánh giá Chất lượng Hạ tầng Đi bộ Ga S23</div>
    <table>
        <thead>
            <tr>
                <th style="width: 8%;">STT</th>
                <th style="width: 42%;">Tiêu chí đánh giá hạ tầng đi bộ</th>
                <th style="width: 50%;">Kết quả khảo sát thực tế (Thang điểm 1 - 5)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Hiện trạng vỉa hè đi bộ</td>
                <td><span class="badge badge-danger">KHÔNG CÓ VỈA HÈ</span> Đất trống tự nhiên ven đường, chưa lát gạch.</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Vị trí sang đường cho người đi bộ</td>
                <td><span class="badge badge-danger">KHÔNG CÓ ĐIỂM SANG ĐƯỜNG</span> Thiếu vạch đi bộ và đèn tín hiệu qua 6 làn.</td>
            </tr>
            <tr>
                <td>3</td>
                <td>Tính liên tục của tuyến đi bộ</td>
                <td><strong>3.0 / 5.0 (Trung bình)</strong> - Mặt bằng ven đường rộng nhưng chưa thành lối chuẩn.</td>
            </tr>
            <tr>
                <td>4</td>
                <td>An toàn giao thông khi đi bộ</td>
                <td><span class="badge badge-warning">2.7 / 5.0 (Kém)</span> - Xe tải nặng trên Phan Văn Khải lớn, nguy cơ tai nạn cao.</td>
            </tr>
            <tr>
                <td>5</td>
                <td>Tiện nghi đi bộ (Bóng mát, chiếu sáng)</td>
                <td><span class="badge badge-warning">1.7 / 5.0 (Rất kém)</span> - Thiếu mảng xanh che bóng, thiếu đèn chiếu sáng vỉa hè.</td>
            </tr>
            <tr>
                <td>6</td>
                <td>Khả năng tiếp cận người khuyết tật (NKT)</td>
                <td><span class="badge badge-danger">1.0 / 5.0 (RẤT KÉM)</span> - Tuyệt đối không thể tiếp cận xe lăn do chưa có ram dốc.</td>
            </tr>
            <tr>
                <td>7</td>
                <td>Dễ nhận biết hướng đi đến ga</td>
                <td><span class="badge badge-success">4.3 / 5.0 (Tốt)</span> - Trục đường thẳng, tầm nhìn thoáng đãng, dễ định vị.</td>
            </tr>
        </tbody>
    </table>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục C (Điều kiện đi bộ & Bản đồ 2):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_c', '+ Sửa vị trí cửa ga Exit A/B')">+ Sửa Exit A/B</span>
                <span class="quick-tag" onclick="appendTag('note_sec_c', '+ Chấm lại điểm đánh giá đi bộ')">+ Chấm lại điểm</span>
                <span class="quick-tag" onclick="appendTag('note_sec_c', '+ Yêu cầu sửa Bản đồ 2')">+ Sửa Bản đồ 2</span>
            </div>
        </div>
        <textarea id="note_sec_c" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục C..."></textarea>
    </div>

    <!-- MỤC D & E -->
    <div class="section-title">MỤC D & E. ĐIỀU KIỆN KẾT NỐI XE BUÝT VÀ ĐIỂM PUDO (PICK-UP / DROP-OFF)</div>
    <div class="h2-title">1. Bản đồ GIS Trạm Xe Buýt và Vị trí Quy hoạch Làn Đón trả khách PUDO</div>
    <div class="map-card">
        <img src="maps/S23_Map3_Bus_PUDO.png" alt="Bản đồ 3: Xe buýt và PUDO">
        <div class="map-caption">Hình D-E.1: Sơ đồ vị trí các điểm dừng buýt Tuyến 100, 107, 70-1, 70-2 và Vịnh đón trả khách PUDO 150m</div>
    </div>

    <div class="h2-title">2. Bảng Thống kê Mạng lưới Trạm Xe Buýt Lân cận Ga S23</div>
    <table>
        <thead>
            <tr>
                <th>Mã trạm</th>
                <th>Vị trí trạm buýt</th>
                <th>Cự ly ga</th>
                <th>Tuyến phục vụ</th>
                <th>Tần suất</th>
                <th>Hiện trạng tiện ích nhà chờ</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>BS-01</strong></td>
                <td>Phan Văn Khải, Ấp Phước Thạnh</td>
                <td><span class="badge badge-success">50 m</span></td>
                <td data-edit-id="bs1_routes">100, 107, 70-1, 70-2</td>
                <td>25 phút</td>
                <td>Có mái che, bảng thông tin tuyến. Đi bộ thuận tiện.</td>
            </tr>
            <tr>
                <td><strong>BS-02</strong></td>
                <td>Phan Văn Khải, Ấp Phước Thạnh</td>
                <td>600 m</td>
                <td>100, 107, 70-1, 70-2</td>
                <td>25 phút</td>
                <td>Có mái che, thông tin tuyến; chưa có vịnh dừng riêng.</td>
            </tr>
            <tr>
                <td><strong>BS-03</strong></td>
                <td>Phan Văn Khải, Ấp Phước Thạnh</td>
                <td>700 m</td>
                <td>100, 107, 70-1, 70-2</td>
                <td>25 phút</td>
                <td>Có nhà chờ, ghế ngồi, mái che, chiếu sáng. Đi bộ hạn chế.</td>
            </tr>
        </tbody>
    </table>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục D & E (Buýt, PUDO & Bản đồ 3):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_de', '+ Thêm tuyến buýt mới')">+ Thêm tuyến buýt</span>
                <span class="quick-tag" onclick="appendTag('note_sec_de', '+ Điều chỉnh chiều dài vịnh PUDO')">+ Chỉnh vịnh PUDO</span>
                <span class="quick-tag" onclick="appendTag('note_sec_de', '+ Yêu cầu sửa Bản đồ 3')">+ Sửa Bản đồ 3</span>
            </div>
        </div>
        <textarea id="note_sec_de" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục D & E..."></textarea>
    </div>

    <!-- MỤC F & G -->
    <div class="section-title">MỤC F & G. NHU CẦU BÃI ĐỖ XE VÀ ĐIỂM XUNG ĐỘT GIAO THÔNG</div>
    <div class="h2-title">1. Bản đồ GIS Quy hoạch Bãi xe Park & Ride & Điểm nóng Xung đột Giao thông</div>
    <div class="map-card">
        <img src="maps/S23_Map4_ParkRide_XungDot.png" alt="Bản đồ 4: Bãi xe và Điểm xung đột">
        <div class="map-caption">Hình F-G.1: Sơ đồ vị trí quỹ đất bãi xe P&R (1.000m² - 10.000m²) và các điểm nóng xung đột CP-01, CP-02, CP-03</div>
    </div>

    <div class="h2-title">2. Bảng Tiềm năng Bãi xe Park & Ride và Điểm Xung Đột</div>
    <table>
        <thead>
            <tr>
                <th>Mã bãi</th>
                <th>Hiện trạng</th>
                <th>Diện tích</th>
                <th>Cự ly</th>
                <th>Đề xuất phương án</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>P&R-01</strong></td>
                <td>Đất tự nhiên</td>
                <td data-edit-id="pr1_area">1,000 m²</td>
                <td>10 m</td>
                <td>Làm bãi đỗ xe máy trung chuyển giai đoạn 1 (~400-500 xe máy).</td>
            </tr>
            <tr>
                <td><strong>P&R-02</strong></td>
                <td>Đất tự nhiên</td>
                <td data-edit-id="pr2_area"><strong>10,000 m²</strong></td>
                <td>10 m</td>
                <td><strong>Quy hoạch Trung tâm TOD</strong> kết hợp Bãi đỗ xe đa tầng cho cả ô tô và xe máy.</td>
            </tr>
        </tbody>
    </table>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục F & G (Bãi xe, Xung đột & Bản đồ 4):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_fg', '+ Sửa diện tích bãi xe')">+ Sửa diện tích P&R</span>
                <span class="quick-tag" onclick="appendTag('note_sec_fg', '+ Thêm điểm xung đột giao thông')">+ Thêm điểm xung đột</span>
                <span class="quick-tag" onclick="appendTag('note_sec_fg', '+ Yêu cầu sửa Bản đồ 4')">+ Sửa Bản đồ 4</span>
            </div>
        </div>
        <textarea id="note_sec_fg" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục F & G..."></textarea>
    </div>

    <!-- MỤC H, I, J -->
    <div class="section-title">MỤC H, I & J. KHÔNG GIAN TRUNG CHUYỂN, RÀO CẢN VÀ OAS SCORECARD</div>
    <div class="h2-title">1. Bản đồ GIS Ma trận Rào cản Tiếp cận Ga S23</div>
    <div class="map-card">
        <img src="maps/S23_Map5_RaoCan_TongHop.png" alt="Bản đồ 5: Ma trận rào cản">
        <div class="map-caption">Hình H-I-J.1: Bản đồ định vị các rào cản đi bộ, điểm sang đường nguy hiểm và trở ngại đối với người khuyết tật</div>
    </div>

    <div class="h2-title">2. Bảng Thẻ điểm OAS Đánh giá Toàn diện Ga S23</div>
    <table>
        <thead>
            <tr>
                <th style="width: 8%;">STT</th>
                <th style="width: 52%;">Nhóm tiêu chí đánh giá tiếp cận & trung chuyển</th>
                <th style="width: 40%;">Điểm số khảo sát thực tế (Thang 1 - 5)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Khả năng tiếp cận bằng đường bộ (Mục B)</td>
                <td data-edit-id="oas_1"><strong>3.67 / 5.0 (Khá)</strong> - Mặt đường 30m, 6 làn thông suốt</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Điều kiện đi bộ đến ga (Mục C)</td>
                <td data-edit-id="oas_2"><strong>2.67 / 5.0 (Trung bình)</strong> - Chưa có vỉa hè kiên cố lát gạch</td>
            </tr>
            <tr>
                <td>3</td>
                <td>Kết nối mạng lưới xe buýt (Mục D)</td>
                <td data-edit-id="oas_3"><span class="badge badge-success">4.00 / 5.0 (Tốt)</span> - Có 4 tuyến buýt chạy liên tục</td>
            </tr>
            <tr>
                <td>4</td>
                <td>Khả năng tổ chức làn đón trả khách PUDO (Mục E)</td>
                <td data-edit-id="oas_4"><span class="badge badge-success">4.67 / 5.0 (Rất tốt)</span> - Lề đường rộng 150m, tách làn an toàn</td>
            </tr>
            <tr>
                <td>5</td>
                <td>Khả năng bố trí bãi xe Park & Ride (Mục F)</td>
                <td data-edit-id="oas_5"><span class="badge badge-success">4.67 / 5.0 (Rất tốt)</span> - Quỹ đất tự nhiên lên đến 10,000m²</td>
            </tr>
            <tr>
                <td>6</td>
                <td>An toàn giao thông quanh khu vực ga (Mục G)</td>
                <td data-edit-id="oas_6"><strong>3.67 / 5.0 (Khá)</strong> - Không ùn tắc, nhưng cần kiểm soát tốc độ</td>
            </tr>
            <tr>
                <td>7</td>
                <td>Khả năng tổ chức không gian trung chuyển (Mục H)</td>
                <td data-edit-id="oas_7"><span class="badge badge-success">4.00 / 5.0 (Tốt)</span> - Đủ diện tích quy hoạch hiện đại</td>
            </tr>
            <tr>
                <td>8</td>
                <td>Khả năng tiếp cận người khuyết tật (Mục I)</td>
                <td data-edit-id="oas_8"><span class="badge badge-danger">1.00 / 5.0 (RẤT KÉM)</span> - Điểm nghẽn lớn nhất, chưa có ram dốc</td>
            </tr>
            <tr class="oas-total">
                <td colspan="2" style="text-align: right; padding-right: 20px;">ĐIỂM TỔNG HỢP OAS TOÀN DIỆN KHU VỰC GA S23:</td>
                <td data-edit-id="oas_total"><strong>3.55 / 5.0 — XẾP LOẠI B (MỨC KHÁ)</strong></td>
            </tr>
        </tbody>
    </table>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục H, I & J (Rào cản, OAS & Bản đồ 5):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_hij', '+ Thêm rào cản đi bộ')">+ Thêm rào cản</span>
                <span class="quick-tag" onclick="appendTag('note_sec_hij', '+ Điều chỉnh điểm số OAS')">+ Đổi điểm OAS</span>
                <span class="quick-tag" onclick="appendTag('note_sec_hij', '+ Yêu cầu sửa Bản đồ 5')">+ Sửa Bản đồ 5</span>
            </div>
        </div>
        <textarea id="note_sec_hij" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục H, I & J..."></textarea>
    </div>

    <!-- MỤC K -->
    <div class="section-title">MỤC K. ĐỀ XUẤT CẢI THIỆN VÀ GIẢI PHÁP KỸ THUẬT</div>
    <div data-edit-id="k_content">
        <p><strong>1. Ưu tiên 1 - Xử lý cấp bách (Trước khi vận hành khai thác):</strong></p>
        <p style="padding-left: 20px;">
            • <strong>Xây dựng vỉa hè tiêu chuẩn:</strong> Đầu tư xây dựng vỉa hè rộng tối thiểu 3.0m dọc hai bên trục Phan Văn Khải trong phạm vi bán kính 500m quanh ga, hoàn thiện gạch dẫn hướng và ram dốc cho người khuyết tật.<br>
            • <strong>Tổ chức sang đường an toàn:</strong> Bắt buộc xây dựng <strong>Cầu vượt bộ hành</strong> kết nối trực tiếp vào sảnh ga S23 qua trục đại lộ 6 làn xe; hoặc bổ sung nút đèn tín hiệu đi bộ có nút bấm ưu tiên và đảo trú chân giữa dải phân cách.
        </p>

        <p><strong>2. Ưu tiên 2 - Ngắn hạn (Giai đoạn 1 - 2 năm):</strong></p>
        <p style="padding-left: 20px;">
            • <strong>Xây dựng Vịnh đón trả khách PUDO:</strong> Khoét lề đường Phan Văn Khải để tạo làn tách riêng dài 150m cho Taxi, Grab và xe ô tô/xe máy đón trả người nhà.<br>
            • <strong>Đầu tư Bãi đỗ xe Park & Ride giai đoạn 1:</strong> Khai thác khu đất 1,000 m² sát ga làm bãi đỗ xe máy có mái che, bố trí trạm sạc xe máy điện công cộng.<br>
            • <strong>Nâng cấp hạ tầng xe buýt:</strong> Bổ sung vịnh dừng xe buýt đạt chuẩn cho trạm cách ga 50m (Tuyến 100, 107, 70-1, 70-2) để tránh xung đột với làn xe cơ giới.
        </p>

        <p><strong>3. Ưu tiên 3 - Dài hạn & Định hướng Phát triển TOD:</strong></p>
        <p style="padding-left: 20px;">
            • <strong>Quy hoạch Trung tâm TOD Củ Chi:</strong> Tích hợp khu đất tự nhiên 10,000 m² đối diện ga thành Trung tâm TOD đa chức năng (Bãi đỗ xe cao tầng thông minh, trạm chuyển tiếp xe buýt liên tỉnh TP.HCM - Tây Ninh, khu thương mại dịch vụ tiện ích).<br>
            • <strong>Mở các tuyến buýt gom (Feeder Bus / Minibus):</strong> Kết nối xuyên suốt từ trung tâm Huyện Củ Chi, Xã Thái Mỹ, Tân An Hội và các khu công nghiệp lân cận dồn khách về Ga S23.
        </p>
    </div>

    <div class="note-card">
        <div class="note-header">
            <span class="note-title">📝 Ghi chú / Chỉnh sửa cho Mục K (Đề xuất giải pháp):</span>
            <div class="note-quick-tags">
                <span class="quick-tag" onclick="appendTag('note_sec_k', '+ Bổ sung giải pháp cầu vượt')">+ Giải pháp cầu vượt</span>
                <span class="quick-tag" onclick="appendTag('note_sec_k', '+ Đổi thứ tự ưu tiên')">+ Đổi thứ tự ưu tiên</span>
                <span class="quick-tag" onclick="appendTag('note_sec_k', '+ Thêm kiến nghị chính sách')">+ Kiến nghị chính sách</span>
            </div>
        </div>
        <textarea id="note_sec_k" class="note-textarea" placeholder="Nhập ghi chú chỉnh sửa cho Mục K..."></textarea>
    </div>

    <!-- MỤC L & M -->
    <div class="section-title">MỤC L & M. HỒ SƠ ẢNH VÀ BIÊN BẢN XÁC NHẬN KHẢO SÁT</div>
    <div class="signature-grid">
        <div class="sign-box">
            <div class="sign-title">ĐẠI DIỆN ĐỘI KHẢO SÁT THỰC ĐỊA (MỤC M.1)</div>
            <div class="sign-body">
                <strong>Khảo sát viên: Nguyễn Thành Vinh</strong><br>
                Email: antoniusnttvinh7325@gmail.com<br>
                Ngày khảo sát: 03/09/2026
            </div>
        </div>
        <div class="sign-box">
            <div class="sign-title">ĐẠI DIỆN ĐƠN VỊ KIỂM TRA & PHÊ DUYỆT (MỤC M.2)</div>
            <div class="sign-body">
                <strong>Người kiểm tra: ....................................................</strong><br>
                Chức vụ: Trưởng bộ phận Thẩm định Dự án<br>
                Ngày phê duyệt: ....../....../2026
            </div>
        </div>
    </div>
</div>

<script>
    const NOTE_KEYS = ['note_general', 'note_sec_a', 'note_sec_b', 'note_sec_c', 'note_sec_de', 'note_sec_fg', 'note_sec_hij', 'note_sec_k'];

    // 1. Phục hồi dữ liệu đã lưu từ LocalStorage
    window.addEventListener('DOMContentLoaded', () => {{
        loadCachedData();
        updateNoteCounter();

        // Lắng nghe sự kiện gõ phím để tự động lưu vào LocalStorage
        NOTE_KEYS.forEach(id => {{
            const el = document.getElementById(id);
            if (el) {{
                el.addEventListener('input', () => {{
                    saveToLocalStorage();
                    updateNoteCounter();
                }});
            }}
        }});
    }});

    function updateNoteCounter() {{
        let count = 0;
        NOTE_KEYS.forEach(id => {{
            const el = document.getElementById(id);
            if (el && el.value.trim().length > 0) count++;
        }});
        const badge = document.getElementById('noteCounter');
        if (badge) badge.innerText = `${{count}} mục đã ghi chú`;
    }}

    function appendTag(textareaId, tagText) {{
        const el = document.getElementById(textareaId);
        if (el) {{
            if (el.value.trim().length > 0) {{
                el.value += '\\n' + tagText + ': ';
            }} else {{
                el.value = tagText + ': ';
            }}
            el.focus();
            saveToLocalStorage();
            updateNoteCounter();
        }}
    }}

    function toggleDirectEditing(enable) {{
        document.body.classList.toggle('edit-mode-active', enable);
        const editableElements = document.querySelectorAll('[data-edit-id]');
        editableElements.forEach(el => {{
            el.contentEditable = enable ? "true" : "false";
        }});
        showToast(enable ? '✏️ Đã bật chế độ sửa văn bản trực tiếp' : '🔒 Đã tắt chế độ sửa văn bản');
    }}

    function gatherAllData() {{
        const notes = {{}};
        NOTE_KEYS.forEach(id => {{
            const el = document.getElementById(id);
            if (el && el.value.trim()) {{
                notes[id] = el.value.trim();
            }}
        }});

        const editedTexts = {{}};
        document.querySelectorAll('[data-edit-id]').forEach(el => {{
            const key = el.getAttribute('data-edit-id');
            editedTexts[key] = el.innerText.trim();
        }});

        return {{
            station: 'Ga S23 - Ba Sa',
            saved_at: new Date().toLocaleString('vi-VN'),
            notes: notes,
            edited_texts: editedTexts
        }};
    }}

    function saveToLocalStorage() {{
        const payload = gatherAllData();
        localStorage.setItem('s23_feedback_cache', JSON.stringify(payload));
    }}

    function loadCachedData() {{
        const cached = localStorage.getItem('s23_feedback_cache');
        if (!cached) return;
        try {{
            const data = JSON.parse(cached);
            if (data.notes) {{
                for (const [id, text] of Object.entries(data.notes)) {{
                    const el = document.getElementById(id);
                    if (el) el.value = text;
                }}
            }}
            if (data.edited_texts) {{
                for (const [key, text] of Object.entries(data.edited_texts)) {{
                    const el = document.querySelector(`[data-edit-id="${{key}}"]`);
                    if (el) el.innerText = text;
                }}
            }}
        }} catch(e) {{
            console.error(e);
        }}
    }}

    async function saveAllFeedback() {{
        const payload = gatherAllData();
        saveToLocalStorage();

        let savedToServer = false;
        try {{
            const res = await fetch('http://127.0.0.1:8088/api/save', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(payload)
            }});
            if (res.ok) {{
                const resJson = await res.json();
                savedToServer = true;
            }}
        }} catch(err) {{
            console.log('Local server connection note:', err);
        }}

        if (savedToServer) {{
            showToast('✅ Đã lưu trực tiếp vào workspace (s23_user_feedback.json)!');
        }} else {{
            // Tự động tải file JSON dự phòng nếu server chưa bật
            exportJSONFile();
            showToast('✅ Đã tải file s23_user_feedback.json về máy của bạn!');
        }}
    }}

    function exportJSONFile() {{
        const payload = gatherAllData();
        const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 's23_user_feedback.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }}

    function showToast(msg) {{
        const toast = document.getElementById('toast');
        toast.innerText = msg;
        toast.style.display = 'block';
        setTimeout(() => {{ toast.style.display = 'none'; }}, 4000);
    }}
</script>

</body>
</html>"""

    out_file = 'BaoCao_KhaoSat_ThucDia_Ga_S23_BaSa_XemTruoc.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[+] Đã nâng cấp giao diện tương tác ghi chú: {out_file}")

if __name__ == '__main__':
    build_interactive_html()
