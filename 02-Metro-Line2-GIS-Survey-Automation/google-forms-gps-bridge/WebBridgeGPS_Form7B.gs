// ============================================================================
// GOOGLE APPS SCRIPT: ĐỊNH VỊ TỰ ĐỘNG & TỰ ĐIỀN TỌA ĐỘ + TÊN ĐƯỜNG (FORM 12)
// LINK FORM: https://docs.google.com/forms/d/e/1FAIpQLSfgsxnAWDxkO_c28y-ON66Umd7L2zNJsfud587XJqjj8WRHCg/viewform
// ENTRY TỌA ĐỘ: entry.1682751531
// ENTRY TÊN ĐƯỜNG / ĐỊA CHỈ: entry.136885345
// ============================================================================

function doGet() {
  // Đường dẫn gốc của Form
  var formBaseUrl = "https://docs.google.com/forms/d/e/1FAIpQLSfgsxnAWDxkO_c28y-ON66Umd7L2zNJsfud587XJqjj8WRHCg/viewform?usp=pp_url";
  
  // Mã Entry Tọa độ & Tên đường/Địa chỉ
  var entryGps = "entry.1682751531";
  var entryAddress = "entry.136885345";

  var htmlTemplate = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trợ Lý Định Vị Tự Động - Khảo Sát Thực Địa</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 15px; 
            margin: 0;
        }
        .card { 
            border: none; 
            border-radius: 20px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.3); 
            width: 100%; 
            max-width: 440px; 
            background: #ffffff; 
            overflow: hidden;
        }
        .card-header { 
            background: linear-gradient(135deg, #0d47a1, #1976d2); 
            color: white; 
            text-align: center; 
            padding: 25px 20px; 
        }
        .card-header h4 { margin: 0; font-weight: 700; font-size: 1.25rem; }
        .status-box { 
            background-color: #eef5fc; 
            border-left: 5px solid #1976d2; 
            padding: 16px; 
            border-radius: 12px; 
            margin-bottom: 20px; 
        }
        .field-label { 
            font-size: 0.8rem; 
            font-weight: 700; 
            color: #0d47a1; 
            text-transform: uppercase; 
            letter-spacing: 0.5px;
            margin-top: 10px;
            margin-bottom: 4px;
        }
        .field-label:first-child { margin-top: 0; }
        .field-value { 
            font-size: 1rem; 
            font-weight: 700; 
            color: #1a237e; 
            background: #ffffff; 
            padding: 10px 12px; 
            border-radius: 10px; 
            border: 1px solid #bbdefb; 
            word-break: break-word; 
        }
        .btn-custom { 
            background: linear-gradient(135deg, #1565c0, #0d47a1); 
            color: white; 
            font-weight: 700; 
            padding: 14px; 
            border-radius: 12px; 
            border: none; 
            width: 100%; 
            font-size: 1.05rem;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 12px rgba(21, 101, 192, 0.4);
        }
        .btn-custom:disabled { background: #90caf9; opacity: 0.7; box-shadow: none; }
        .btn-custom:hover:not(:disabled) { transform: translateY(-1px); color: white; }
    </style>
</head>
<body>
<div class="card">
    <div class="card-header">
        <h4><i class="fa-solid fa-location-crosshairs me-2"></i> TRỢ LÝ ĐỊNH VỊ TỰ ĐỘNG</h4>
        <small style="opacity:0.9;">Lấy Tọa độ & Tên đường điền Google Form</small>
    </div>
    <div class="card-body p-4">
        <div class="status-box">
            <div class="field-label"><i class="fa-solid fa-crosshairs me-1"></i> Tọa độ GPS</div>
            <div id="gps-coords" class="field-value">
                <i class="fa-solid fa-spinner fa-spin me-2"></i>Đang xác định vị trí...
            </div>

            <div class="field-label"><i class="fa-solid fa-map-location-dot me-1"></i> Tên đường / Địa chỉ</div>
            <div id="address-text" class="field-value">
                <i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tìm tên đường...
            </div>
        </div>

        <button class="btn btn-custom mb-2" id="btn-open" onclick="openForm()" disabled>
            <i class="fa-solid fa-spinner fa-spin me-2"></i> ĐANG ĐỊNH VỊ...
        </button>

        <button class="btn btn-outline-secondary w-100" onclick="getLocation()" style="border-radius:12px; font-weight:600;">
            <i class="fa-solid fa-rotate me-1"></i> Thử lại / Cập nhật vị trí
        </button>
    </div>
</div>

<script>
    const baseUrl = "[[FORM_BASE_URL]]";
    const entryGps = "[[ENTRY_GPS]]";
    const entryAddress = "[[ENTRY_ADDRESS]]";

    let currentLat = null;
    let currentLng = null;
    let currentAddress = "";

    function getLocation() {
        const btn = document.getElementById('btn-open');
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> ĐANG ĐỊNH VỊ...';
        document.getElementById('gps-coords').innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Đang xác định vị trí...';
        document.getElementById('address-text').innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Đang tìm tên đường...';

        let hasResponded = false;

        const timerGuard = setTimeout(() => {
            if (!hasResponded) {
                fetchIpFallback();
            }
        }, 4000);

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    if (hasResponded) return;
                    hasResponded = true;
                    clearTimeout(timerGuard);
                    onSuccess(pos.coords.latitude, pos.coords.longitude);
                },
                (err) => {
                    if (hasResponded) return;
                    navigator.geolocation.getCurrentPosition(
                        (pos2) => {
                            if (hasResponded) return;
                            hasResponded = true;
                            clearTimeout(timerGuard);
                            onSuccess(pos2.coords.latitude, pos2.coords.longitude);
                        },
                        (err2) => {
                            if (hasResponded) return;
                            hasResponded = true;
                            clearTimeout(timerGuard);
                            fetchIpFallback();
                        },
                        { enableHighAccuracy: false, timeout: 3000, maximumAge: 0 }
                    );
                },
                { enableHighAccuracy: true, timeout: 3000, maximumAge: 0 }
            );
        } else {
            hasResponded = true;
            clearTimeout(timerGuard);
            fetchIpFallback();
        }
    }

    function onSuccess(lat, lng) {
        currentLat = parseFloat(lat).toFixed(6);
        currentLng = parseFloat(lng).toFixed(6);
        const coordsStr = currentLat + ", " + currentLng;
        document.getElementById('gps-coords').innerText = coordsStr;

        // Tra cứu tên đường & địa chỉ chi tiết
        fetchAddressDetails(currentLat, currentLng);
    }

    function fetchAddressDetails(lat, lng) {
        const coordsStr = lat + ", " + lng;
        
        // Thử giải mã bằng Nominatim OpenStreetMap
        fetch('https://nominatim.openstreetmap.org/reverse?format=json&lat=' + lat + '&lon=' + lng + '&accept-language=vi')
            .then(res => res.json())
            .then(data => {
                if (data && data.address) {
                    let a = data.address;
                    let parts = [];
                    
                    // Tên đường
                    let road = a.road || a.pedestrian || a.street || "";
                    let house = a.house_number || a.building || "";
                    if (house && road) parts.push(house + " " + road);
                    else if (road) parts.push(road);

                    // Phường / Xã
                    let ward = a.quarter || a.suburb || a.village || a.neighbourhood || a.ward || "";
                    if (ward && !parts.includes(ward)) parts.push(ward);

                    // Quận / Huyện
                    let district = a.city_district || a.district || a.county || "";
                    if (district && !parts.includes(district)) parts.push(district);

                    // Tỉnh / TP
                    let city = a.city || a.state || a.province || "";
                    if (city && !parts.includes(city)) parts.push(city);

                    currentAddress = parts.length > 0 ? parts.join(", ") : (data.display_name || coordsStr);
                } else {
                    currentAddress = coordsStr;
                }
                finishGeocoding();
            })
            .catch(() => {
                // Dự phòng giải mã bằng BigDataCloud
                fetch('https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=' + lat + '&longitude=' + lng + '&localityLanguage=vi')
                    .then(r => r.json())
                    .then(bdata => {
                        if (bdata && bdata.locality) {
                            currentAddress = bdata.locality + ", " + (bdata.city || "") + ", " + (bdata.principalSubdivision || "");
                        } else {
                            currentAddress = coordsStr;
                        }
                        finishGeocoding();
                    })
                    .catch(() => {
                        currentAddress = coordsStr;
                        finishGeocoding();
                    });
            });
    }

    function finishGeocoding() {
        document.getElementById('address-text').innerText = currentAddress;
        enableButton();
        setTimeout(openForm, 1200);
    }

    function fetchIpFallback() {
        fetch('https://api.bigdatacloud.net/data/reverse-geocode-client')
            .then(r => r.json())
            .then(data => {
                if (data && data.latitude && data.longitude) {
                    onSuccess(data.latitude, data.longitude);
                } else {
                    showError();
                }
            })
            .catch(() => showError());
    }

    function enableButton() {
        const btn = document.getElementById('btn-open');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-paper-plane me-2"></i> MỞ FORM (ĐÃ ĐIỀN TỌA ĐỘ & TÊN ĐƯỜNG)';
    }

    function showError() {
        document.getElementById('gps-coords').innerText = "Không thể lấy vị trí thiết bị";
        document.getElementById('address-text').innerText = "Không có địa chỉ";
        
        const btn = document.getElementById('btn-open');
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-arrow-right-from-bracket me-2"></i> MỞ FORM KHÔNG CÓ DỮ LIỆU';
    }

    function openForm() {
        let finalUrl = baseUrl;
        if (currentLat && currentLng) {
            const gpsVal = encodeURIComponent(currentLat + ", " + currentLng);
            finalUrl += '&' + entryGps + '=' + gpsVal;
        }
        if (currentAddress) {
            const addrVal = encodeURIComponent(currentAddress);
            finalUrl += '&' + entryAddress + '=' + addrVal;
        }
        
        // Chuyển hướng cửa sổ chính thoát iframe
        const a = document.createElement('a');
        a.href = finalUrl;
        a.target = '_top';
        document.body.appendChild(a);
        a.click();
    }

    window.onload = getLocation;
</script>
</body>
</html>`;

  var finalHtml = htmlTemplate
    .replace("[[FORM_BASE_URL]]", formBaseUrl)
    .replace("[[ENTRY_GPS]]", entryGps)
    .replace("[[ENTRY_ADDRESS]]", entryAddress);

  return HtmlService.createHtmlOutput(finalHtml)
      .setTitle("Trợ Lý Định Vị Google Form")
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
