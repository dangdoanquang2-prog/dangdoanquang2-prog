// DOM Elements
const excelUpload = document.getElementById('excelUpload');
const fileNameDisplay = document.getElementById('fileName');
const runAlgorithmBtn = document.getElementById('runAlgorithmBtn');
const exportBtn = document.getElementById('exportBtn');
const mapOverlay = document.getElementById('mapOverlay');
const routeTableBody = document.querySelector('#routeTable tbody');

let excelData = null;
let globalExportSheets = {}; // To store the 3 sheets for exporting

// Mock Coordinates cho TMV và các Nhà cung cấp
const TMV_COORD = [21.2333, 105.7167]; // TMV Phúc Yên
const SUPPLIER_COORDS = {
    'S01': [21.1643, 105.7720], 'S02': [21.1680, 105.7750], 'S03': [21.0371, 105.9080],
    'S04': [21.1610, 105.7710], 'S05': [21.2858, 105.6738], 'S06': [21.1700, 105.7760],
    'S07': [21.0833, 105.8167], 'S08': [21.3000, 105.6000], 'S09': [21.1630, 105.7730],
    'S10': [21.2285, 105.8115], 'S11': [21.2300, 105.8130], 'S12': [21.0333, 105.9333],
    'S13': [20.8500, 106.6833], 'S14': [21.2250, 105.8100], 'S15': [21.1660, 105.7740]
};

// Khởi tạo bản đồ Leaflet
const map = L.map('map').setView([21.15, 105.75], 10);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO'
}).addTo(map);

const tmvIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
});
L.marker(TMV_COORD, {icon: tmvIcon}).addTo(map).bindPopup('<b>TMV Factory</b><br>Dock A & Dock W').openPopup();

let routeLayers = []; 

// Xử lý Upload File Excel
excelUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileNameDisplay.textContent = `Đã tải: ${file.name}`;
        fileNameDisplay.style.color = '#10b981';
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = new Uint8Array(event.target.result);
                excelData = XLSX.read(data, { type: 'array' });
                runAlgorithmBtn.disabled = false;
                runAlgorithmBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Chạy Thuật Toán AI (Heuristic)';
                mapOverlay.querySelector('p').textContent = "Sẵn sàng tính toán. Vui lòng bấm nút chạy!";
                mapOverlay.querySelector('.loader').style.display = 'none';
            } catch (error) {
                alert('Lỗi đọc file. Vui lòng chọn đúng file Excel (.xlsx)');
            }
        };
        reader.readAsArrayBuffer(file);
    }
});

function calcDistance(coord1, coord2) {
    const R = 6371; 
    const dLat = (coord2[0] - coord1[0]) * Math.PI / 180;
    const dLon = (coord2[1] - coord1[1]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(coord1[0] * Math.PI / 180) * Math.cos(coord2[0] * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const straightDist = R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return straightDist * 1.35; 
}

async function drawRealRoute(route, renderId) {
    const coords = route.coords;
    const color = route.truck.color;
    
    // Khởi tạo nội dung Popup
    const popupContent = `
        <div style="font-family: 'Inter', sans-serif; min-width: 200px; color: #333;">
            <h3 style="margin: 0 0 8px 0; color: ${color}; border-bottom: 1px solid #ccc; padding-bottom: 5px;">
                <i class="fa-solid fa-truck-fast"></i> ${route.id}
            </h3>
            <p style="margin: 4px 0;"><b>Loại xe:</b> ${route.truck.type}</p>
            <p style="margin: 4px 0;"><b>Hành trình:</b> ${route.nodes.join(' ➔ ')}</p>
            <p style="margin: 4px 0;"><b>Thể tích:</b> ${route.volume.toFixed(2)} / ${route.truck.capacity} m³</p>
            <p style="margin: 4px 0;"><b>Lấp đầy:</b> ${(route.volume / route.truck.capacity * 100).toFixed(1)}%</p>
            <p style="margin: 4px 0;"><b>Quãng đường:</b> ${route.distance.toFixed(1)} km</p>
            <p style="margin: 4px 0; color: #ef4444; font-weight: 600;"><b>Tổng phí:</b> ${Math.round(route.totalCost).toLocaleString()} VNĐ</p>
        </div>
    `;

    const waypoints = coords.map(c => `${c[1]},${c[0]}`).join(';');
    const url = `https://router.project-osrm.org/route/v1/driving/${waypoints}?overview=full&geometries=geojson`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // Nếu đã click sang tuyến khác trước khi API phản hồi thì hủy vẽ
        if (window.currentRenderId !== renderId) return;
        
        if (data.routes && data.routes.length > 0) {
            const routeGeoJSON = data.routes[0].geometry;
            const roadLayer = L.geoJSON(routeGeoJSON, {
                style: { color: color, weight: 5, opacity: 0.8 }
            }).bindPopup(popupContent).addTo(map);
            
            // Hiệu ứng hover cho đường thực tế
            roadLayer.on('mouseover', function(e) {
                this.setStyle({ weight: 9, opacity: 1 });
            });
            roadLayer.on('mouseout', function(e) {
                this.setStyle({ weight: 5, opacity: 0.8 });
            });
            
            routeLayers.push(roadLayer);
        } else {
            let polyline = L.polyline(coords, {color: color, weight: 5, opacity: 0.8, dashArray: '5, 5'})
                .bindPopup(popupContent).addTo(map);
            routeLayers.push(polyline);
        }
    } catch (e) {
        if (window.currentRenderId !== renderId) return;
        let polyline = L.polyline(coords, {color: color, weight: 5, opacity: 0.8, dashArray: '5, 5'})
            .bindPopup(popupContent).addTo(map);
        routeLayers.push(polyline);
    }
}

function minsToTime(totalMins) {
    const h = Math.floor(totalMins / 60) % 24;
    const m = Math.floor(totalMins % 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

runAlgorithmBtn.addEventListener('click', () => {
    if (!excelData) return;
    runAlgorithmBtn.disabled = true;
    runAlgorithmBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Xử lý Logic & Time Window...';
    exportBtn.style.display = 'none';
    
    setTimeout(() => {
        try {
            processOptimizationEngine();
            mapOverlay.classList.add('hidden');
            runAlgorithmBtn.innerHTML = '<i class="fa-solid fa-check"></i> Hoàn thành Tối ưu';
            runAlgorithmBtn.disabled = false;
            exportBtn.style.display = 'block'; 
        } catch (error) {
            console.error(error);
            alert("Lỗi khi giải bài toán! Đảm bảo cấu trúc file chuẩn SCRACE.");
            runAlgorithmBtn.innerHTML = '<i class="fa-solid fa-microchip"></i> Chạy Thuật Toán AI (Heuristic)';
            runAlgorithmBtn.disabled = false;
        }
    }, 500);
});

// CORE ENGINE
function processOptimizationEngine() {
    const sheet2 = excelData.Sheets[excelData.SheetNames[1]];
    const data2 = XLSX.utils.sheet_to_json(sheet2, {header: 1});
    
    let supplierDemands = {};
    
    for (let i = 1; i < data2.length; i++) {
        const row = data2[i];
        if (!row || row.length < 5) continue;
        
        const dateRaw = row[1];
        let dateStr = dateRaw;
        // Excel lưu trữ ngày tháng dưới dạng số serial đếm từ 01/01/1900.
        if (typeof dateRaw === 'number') {
            const jsDate = new Date(Math.round((dateRaw - 25569) * 86400 * 1000));
            const d = jsDate.getDate().toString().padStart(2, '0');
            const m = (jsDate.getMonth() + 1).toString().padStart(2, '0');
            const y = jsDate.getFullYear();
            dateStr = `${d}/${m}/${y}`;
        }
        
        const supplier = row[2];
        if (typeof supplier === 'string' && supplier.startsWith('S')) {
            const itemCode = row[3] || 'UNKNOWN';
            const qty = parseFloat(row[4]) || 1;
            const type = row[5] || 'Module';
            const d = parseFloat(row[6]) || 0;
            const r = parseFloat(row[7]) || 0;
            const c = parseFloat(row[8]) || 0;
            const destDock = row[9] || 'Dock A';
            const leadTimeStr = (row[10] || '').toString();
            const leadTime = parseFloat(leadTimeStr) || (type.toUpperCase() === 'PALLET' ? 2.68 : 2.04); 
            
            // Tính thể tích (Nếu đầu vào d, r, c > 10 tức là dùng đơn vị mm, cần đổi sang m3)
            let vol = d * r * c * qty;
            if (d > 10 || r > 10 || c > 10) {
                vol = vol / 1000000000; 
            }
            
            if (vol > 0) {
                if (!supplierDemands[supplier]) {
                    supplierDemands[supplier] = { 
                        volume: 0, items: [], coords: SUPPLIER_COORDS[supplier] || [21.1+Math.random()*0.1, 105.7+Math.random()*0.1] 
                    };
                }
                supplierDemands[supplier].volume += vol;
                supplierDemands[supplier].items.push({
                    itemCode, qty, type, vol, destDock, leadTime, dateStr, supplier
                });
            }
        }
    }

    const trucks = [
        { type: 'Xe tải 10 tấn', capacity: 49.19, costPerKm: 18000, dropFee: 10000, color: '#ef4444' },
        { type: 'Xe tải 7 tấn', capacity: 34.91, costPerKm: 16031, dropFee: 10000, color: '#3b82f6' },
        { type: 'Xe tải 5 tấn', capacity: 31.74, costPerKm: 14429, dropFee: 17500, color: '#10b981' }
    ];

    let routes = [];
    
    // Arrays representing Exact structures required
    let exportAOA4 = [
        ["Tối ưu vận tải Milk Run trong vận chuyển linh kiện nội địa"],
        ["Câu trả lời:"],
        ["Attach #4: Lịch xe hàng ngày và số tiền cần thanh toán cho đơn vị vận tải"],
        [],
        ["", "", "", "", "Lưu ý không thay đổi tên sheet, thứ tự cột, cấu trúc sheet"],
        ["No.", "Ngày làm việc", "Trip", "Cung đường", "Tải trọng xe", "Quãng đường (km)", "Số tiền", "Ảnh Google map"]
    ];

    let exportAOA2 = [
        ["Tối ưu vận tải Milk Run trong vận chuyển linh kiện nội địa"],
        ["Câu trả lời:"],
        ["Attach #5: Lịch chi tiết tuyến xe hàng ngày"],
        [],
        ["", "", "", "", "Lưu ý không thay đổi tên sheet, thứ tự cột, cấu trúc sheet"],
        ["No.", "Ngày làm việc", "Trip", "Điểm đến", "Giờ Bắt đầu", "Giờ Kết thúc", "Travel distance (km)", "Thời gian di chuyển"]
    ];

    let exportAOA3 = [
        ["Tối ưu vận tải Milk Run trong vận chuyển linh kiện nội địa"],
        ["Câu trả lời:"],
        ["Attach #6: Bảng chi tiết module/ pallet của từng trip"],
        [],
        ["", "", "", "Lưu ý không thay đổi tên sheet, thứ tự cột, cấu trúc sheet"],
        ["No.", "Ngày làm việc", "Trip", "Nhà cung cấp", "Pallet/ Dolly/Module No."]
    ];

    let unassignedDemands = JSON.parse(JSON.stringify(supplierDemands));
    routeLayers.forEach(layer => map.removeLayer(layer));
    routeLayers = [];
    
    let totalOverallCost = 0;
    let tripCounter = 1;
    
    while(Object.keys(unassignedDemands).length > 0) {
        let maxSupp = Object.keys(unassignedDemands).reduce((a, b) => unassignedDemands[a].volume > unassignedDemands[b].volume ? a : b);
        let remVol = unassignedDemands[maxSupp].volume;
        
        let chosenTruck = trucks[0]; 
        // Cải tiến: Chọn xe sao cho phù hợp với lượng hàng nhất để tránh lãng phí, nhưng nếu hàng quá nhiều thì ưu tiên xe to
        for (let t of [...trucks].reverse()) {
            if (t.capacity >= remVol * 0.9) {
                chosenTruck = t; break;
            }
        }
        // Nếu remVol nhỏ, code sẽ tự pick xe 5 tấn, nếu lớn thì lấy 10 tấn.
        
        const tripId = `TRIP-${tripCounter.toString().padStart(3, '0')}`;
        tripCounter++;
        
        let route = {
            id: tripId, truck: chosenTruck,
            nodes: ['TMV'], coords: [TMV_COORD],
            volume: 0, distance: 0, stops: 0,
            date: "", itemsLoaded: [], schedule: []
        };
        
        let currentCoord = TMV_COORD;
        let capacityLeft = chosenTruck.capacity;
        
        let currentTimeMins = 6 * 60; // 06:00
        
        route.schedule.push({
            point: 'TMV', arrival: '-', departure: minsToTime(currentTimeMins), 
            distFromPrev: 0, loadTime: 0, travelMinsFromPrev: 0
        });

        let totalLoadTimeMins = 0;
        
        while (capacityLeft > 0 && Object.keys(unassignedDemands).length > 0) {
            let nearestSupp = null;
            let bestScore = Infinity;
            for (let supp in unassignedDemands) {
                let dist = calcDistance(currentCoord, unassignedDemands[supp].coords);
                let availableVol = unassignedDemands[supp].volume;
                // Cải tiến: Heuristic xét cả khoảng cách và lượng hàng có thể lấy. 
                // Điểm nào càng gần và càng lấy được nhiều hàng lên xe thì càng được ưu tiên.
                let loadableVol = Math.min(capacityLeft, availableVol);
                let score = dist / (loadableVol + 0.1); 
                
                if (score < bestScore) { 
                    bestScore = score; 
                    nearestSupp = supp; 
                }
            }
            if (!nearestSupp) break;
            
            let suppItems = unassignedDemands[nearestSupp].items;
            let loadVol = 0;
            let loadTimeForThisStop = 0;
            
            let itemsToTake = [];
            let itemsToLeave = [];
            
            for (let item of suppItems) {
                if (capacityLeft >= item.vol) {
                    itemsToTake.push(item);
                    capacityLeft -= item.vol;
                    loadVol += item.vol;
                    loadTimeForThisStop += (item.leadTime * item.qty);
                } else {
                    itemsToLeave.push(item);
                }
            }
            
            if (itemsToTake.length === 0) break; 
            
            route.date = itemsToTake[0].dateStr;
            
            // Tính lại dist vì ra khỏi vòng lặp dist không tồn tại
            let distToNearest = calcDistance(currentCoord, unassignedDemands[nearestSupp].coords);
            let travelMins = (distToNearest / 40) * 60; 
            let arrivalTimeMins = currentTimeMins + travelMins;
            
            // --- TIME WINDOW CẢI TIẾN ---
            // S01, S03 mở lúc 6:00. S04 mở 7:00. Đa số còn lại mở 8:00 (480 mins)
            let twStartMins = 8 * 60; 
            if (['S01', 'S03'].includes(nearestSupp)) twStartMins = 6 * 60;
            else if (['S04'].includes(nearestSupp)) twStartMins = 7 * 60;
            
            let waitTimeMins = 0;
            if (arrivalTimeMins < twStartMins) {
                waitTimeMins = twStartMins - arrivalTimeMins;
                arrivalTimeMins = twStartMins; // Xe phải chờ đến giờ mở cửa
            }
            
            currentTimeMins = arrivalTimeMins;
            let arrivalTime = minsToTime(currentTimeMins);
            
            currentTimeMins += loadTimeForThisStop;
            let departureTime = minsToTime(currentTimeMins);
            totalLoadTimeMins += loadTimeForThisStop + waitTimeMins; // Tính cả thời gian chờ vào wait cost
            
            route.schedule.push({
                point: nearestSupp, arrival: arrivalTime, departure: departureTime, 
                distFromPrev: distToNearest, loadTime: loadTimeForThisStop, travelMinsFromPrev: travelMins,
                waitTime: waitTimeMins
            });
            
            itemsToTake.forEach(item => {
                route.itemsLoaded.push(item);
            });
            
            route.nodes.push(nearestSupp);
            route.coords.push(unassignedDemands[nearestSupp].coords);
            route.volume += loadVol;
            route.distance += distToNearest;
            route.stops += 1;
            
            currentCoord = unassignedDemands[nearestSupp].coords;
            unassignedDemands[nearestSupp].items = itemsToLeave;
            unassignedDemands[nearestSupp].volume = itemsToLeave.reduce((s, i) => s + i.vol, 0);
            
            if (itemsToLeave.length === 0) {
                delete unassignedDemands[nearestSupp];
            }
            
            if (capacityLeft / chosenTruck.capacity < 0.05) break;
        }
        
        let distToTMV = calcDistance(currentCoord, TMV_COORD);
        route.distance += distToTMV;
        route.nodes.push('TMV');
        route.coords.push(TMV_COORD);
        
        let travelMinsTMV = (distToTMV / 40) * 60;
        currentTimeMins += travelMinsTMV;
        
        let hasDockA = route.itemsLoaded.some(i => i.destDock.includes('A'));
        let hasDockW = route.itemsLoaded.some(i => i.destDock.includes('W'));
        let tmvUnloadTime = (route.itemsLoaded.reduce((s, i) => s + i.leadTime*i.qty, 0));
        
        if (hasDockA && hasDockW) currentTimeMins += 10;
        
        let arrivalTMV = minsToTime(currentTimeMins);
        currentTimeMins += tmvUnloadTime;
        
        route.schedule.push({
            point: 'TMV', arrival: arrivalTMV, departure: minsToTime(currentTimeMins), 
            distFromPrev: distToTMV, loadTime: tmvUnloadTime, travelMinsFromPrev: travelMinsTMV
        });
        
        let costKm = route.distance * route.truck.costPerKm;
        let costDrop = route.stops * route.truck.dropFee;
        let costWait = (totalLoadTimeMins / 60) * 60000; 
        route.totalCost = costKm + costDrop + costWait;
        
        totalOverallCost += route.totalCost;
        routes.push(route);
        
        // PUSH DATA TO EXPORT AOA ARRAYS
        
        // 4. KQ_B1
        exportAOA4.push([
            exportAOA4.length - 5, // No. starts at 1
            route.date, 
            route.id,
            route.nodes.join(' - '),
            route.truck.type,
            route.distance.toFixed(2),
            Math.round(route.totalCost),
            "" // Ảnh Google Map
        ]);
        
        // 5. KQ_B2
        route.schedule.forEach(stop => {
            exportAOA2.push([
                exportAOA2.length - 5,
                route.date,
                route.id,
                stop.point,
                stop.arrival === '-' ? stop.departure : stop.arrival, // Giờ bắt đầu
                stop.departure, // Giờ kết thúc
                stop.distFromPrev.toFixed(2),
                Math.round(stop.travelMinsFromPrev) // Thời gian di chuyển (phút)
            ]);
        });
        
        // 6. KQ_B3
        route.itemsLoaded.forEach(item => {
            exportAOA3.push([
                exportAOA3.length - 5,
                route.date,
                route.id,
                item.supplier,
                item.itemCode
            ]);
        });
    }
    
    globalExportSheets = {
        sheet4: exportAOA4,
        sheet2: exportAOA2,
        sheet3: exportAOA3
    };
    
    // UI Update
    let totalVol = routes.reduce((sum, r) => sum + r.volume, 0);
    let totalCap = routes.reduce((sum, r) => sum + r.truck.capacity, 0);
    let avgFill = (totalVol / totalCap * 100).toFixed(1);
    
    document.getElementById('totalCost').textContent = Math.round(totalOverallCost).toLocaleString() + ' VNĐ';
    document.getElementById('totalTrucks').textContent = routes.length + ' Xe';
    let fillRateEl = document.getElementById('fillRate');
    fillRateEl.textContent = avgFill + '%';
    fillRateEl.style.color = avgFill >= 90 ? '#10b981' : '#f59e0b'; 
    
    routeTableBody.innerHTML = '';
    window.currentRenderId = 0;

    const showRouteOnMap = (selectedRoute) => {
        window.currentRenderId++;
        let myRenderId = window.currentRenderId;
        
        // Xoá đường cũ trên bản đồ
        routeLayers.forEach(layer => map.removeLayer(layer));
        routeLayers = [];
        
        // Vẽ đường mới
        drawRealRoute(selectedRoute, myRenderId);
        
        // Vẽ marker
        selectedRoute.nodes.forEach((node, i) => {
            if (node !== 'TMV' && node !== 'TMV (Trả hàng)') {
                let marker = L.circleMarker(selectedRoute.coords[i], {
                    radius: 7, fillColor: '#f59e0b', color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.9
                }).addTo(map).bindPopup(`<b>${node}</b>`);
                routeLayers.push(marker);
            }
        });
        
        // Zoom khung hình
        let bounds = L.latLngBounds(selectedRoute.coords);
        map.fitBounds(bounds.pad(0.2));
    };

    routes.forEach((r, idx) => {
        let fillPct = (r.volume / r.truck.capacity * 100).toFixed(1);
        let tr = document.createElement('tr');
        tr.innerHTML = `
            <td><b>${r.id}</b></td>
            <td><span style="color:${r.truck.color}; font-weight:bold; background:rgba(255,255,255,0.1); padding:4px 8px; border-radius:4px;">${r.truck.type}</span></td>
            <td>${r.nodes.join(' ➔ ')}</td>
            <td>${r.volume.toFixed(2)}</td>
            <td>
                <div style="background:rgba(255,255,255,0.1); border-radius:4px; width:100%; height:8px; margin-top:5px; overflow:hidden;">
                    <div style="background:${fillPct >= 90 ? '#10b981' : '#f59e0b'}; width:${fillPct}%; height:100%; border-radius:4px;"></div>
                </div>
                <small>${fillPct}%</small>
            </td>
            <td style="color:#ef4444; font-weight:600;">${Math.round(r.totalCost).toLocaleString()}</td>
        `;
        
        // Click sự kiện
        tr.addEventListener('click', () => {
            document.querySelectorAll('#routeTable tbody tr').forEach(row => row.classList.remove('active-row'));
            tr.classList.add('active-row');
            showRouteOnMap(r);
        });
        
        routeTableBody.appendChild(tr);
    });
    
    // Mặc định chọn tuyến xe đầu tiên
    if (routes.length > 0) {
        document.querySelector('#routeTable tbody tr').click();
    }
}

// Hàm format Sheet với style cơ bản (nếu SheetJS hỗ trợ)
function styleSheet(ws) {
    // Để style màu đỏ chữ "Lưu ý", cần XLSX-style (phiên bản trả phí hoặc branch riêng), 
    // Tuy nhiên chúng ta có thể set độ rộng cột để file đẹp hơn:
    const colWidths = [
        { wch: 5 }, { wch: 15 }, { wch: 10 }, { wch: 30 }, { wch: 15 }, { wch: 20 }, { wch: 15 }, { wch: 20 }
    ];
    ws['!cols'] = colWidths;
    return ws;
}

// Xử lý Sự kiện Xuất Excel (File Lời Giải)
exportBtn.addEventListener('click', () => {
    if (!globalExportSheets.sheet4 || globalExportSheets.sheet4.length === 0) {
        alert("Chưa có kết quả. Vui lòng bấm 'Chạy Tối ưu hoá' trước!");
        return;
    }
    
    const wb = XLSX.utils.book_new();
    
    // Convert Array of Arrays (aoa) to sheets
    const ws4 = XLSX.utils.aoa_to_sheet(globalExportSheets.sheet4);
    const ws2 = XLSX.utils.aoa_to_sheet(globalExportSheets.sheet2);
    const ws3 = XLSX.utils.aoa_to_sheet(globalExportSheets.sheet3);
    
    // Format column width
    styleSheet(ws4);
    styleSheet(ws2);
    styleSheet(ws3);
    
    // Gắn Sheet với TÊN CHÍNH XÁC YÊU CẦU
    XLSX.utils.book_append_sheet(wb, ws4, "4. KQ_B1");
    XLSX.utils.book_append_sheet(wb, ws2, "5. KQ_B2");
    XLSX.utils.book_append_sheet(wb, ws3, "6. KQ_B3");
    
    // Tải xuống
    XLSX.writeFile(wb, "SCRACE_Case1_LoiGiai.xlsx");
});
