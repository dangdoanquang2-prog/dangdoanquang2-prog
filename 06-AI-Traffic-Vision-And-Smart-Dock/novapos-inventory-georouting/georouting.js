document.addEventListener('DOMContentLoaded', () => {
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    if (!appData) return;

    // 1. Tải Sản phẩm vào Select
    const productSelect = document.getElementById('productSelect');
    appData.products.forEach(p => {
        let opt = document.createElement('option');
        opt.value = p.productId;
        opt.textContent = `${p.productId} - ${p.name} (Giá: ${p.price.toLocaleString()}đ)`;
        productSelect.appendChild(opt);
    });

    // 2. Tải Kho bãi vào Hệ thống Rơ-le Đa Chi Nhánh (Phase 18)
    const whContainer = document.getElementById('warehouseCheckboxes');
    let whHTML = `
        <label style="display:flex; align-items:center; gap:8px; cursor:pointer; margin-bottom:10px;">
            <input type="checkbox" id="chkAutoDistribute" checked onchange="toggleAutoDistribute()" style="width:16px; height:16px; accent-color: var(--primary-color);">
            <span style="color:var(--status-success); font-weight:bold; font-size: 14px;">🤖 Quét Toàn Quốc Khắp Bản Đồ</span>
        </label>
        <div id="whManualList" style="display:none; flex-direction:column; gap:8px; padding-left: 24px; border-left: 2px dashed rgba(255,255,255,0.1); margin-left: 6px;">
    `;
    
    appData.suppliers_inventory.forEach(wh => {
        whHTML += `
            <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                <input type="checkbox" class="wh-chk" value="${wh.supplierId}" style="width:14px; height:14px; accent-color: var(--primary-color);">
                <span style="font-size: 13px; color: var(--text-primary);">📍 ${wh.name}</span>
            </label>
        `;
    });
    whHTML += `</div>`;
    whContainer.innerHTML = whHTML;

    // Kích hoạt Switch Ngắt Mạch
    window.toggleAutoDistribute = function() {
        const isAuto = document.getElementById('chkAutoDistribute').checked;
        document.getElementById('whManualList').style.display = isAuto ? 'none' : 'flex';
    };

    // Hàm Reset Database tạo thêm kho Miền Nam và Miền Trung để demo thuật toán
    document.getElementById('btnResetDB').addEventListener('click', () => {
        if (!confirm("Hành động này sẽ khôi phục dữ liệu gốc kèm 3 kho hàng (Bắc, Trung, Nam). Bạn có chắc chắn?")) return;
        
        appData.suppliers_inventory = [
            {
                supplierId: "NCC001", name: "Kho Tổng Miền Bắc", 
                address: { city: "Hà Nội", coordinates: { lat: 21.038166, lng: 105.795493 } },
                inventory: [{ productId: "SP001", stockQuantity: 5 }, { productId: "SP002", stockQuantity: 10 }]
            },
            {
                supplierId: "NCC002", name: "Kho Tổng Miền Trung", 
                address: { city: "Đà Nẵng", coordinates: { lat: 16.054407, lng: 108.202164 } },
                inventory: [{ productId: "SP001", stockQuantity: 0 }, { productId: "SP002", stockQuantity: 5 }]
            },
            {
                supplierId: "NCC003", name: "Kho Tổng Miền Nam", 
                address: { city: "Hồ Chí Minh", coordinates: { lat: 10.823099, lng: 106.629662 } },
                inventory: [{ productId: "SP001", stockQuantity: 2 }, { productId: "SP002", stockQuantity: 20 }]
            }
        ];
        localStorage.setItem('novaPosData', JSON.stringify(appData));
        alert("Khôi phục thành công! Trang sẽ tải lại.");
        location.reload();
    });

    // --- CÔNG THỨC HAVERSINE TÍNH KHOẢNG CÁCH (KM) ---
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Bản kính trái đất (km)
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    // --- CÔNG THỨC TÍNH CƯỚC VẬN CHUYỂN AUTO (Phase 14) ---
    const calculateShippingCost = (distanceKm) => {
        if (distanceKm <= 10) return 18000;
        if (distanceKm <= 50) return 25000;
        if (distanceKm <= 300) return 35000;
        return 45000; // Xuyên việt
    };

    // --- KHỞI TẠO CHIẾN ĐỒ CHIẾN THUẬT LEAFLET (Phase 15) ---
    let tacticalMap = L.map('vietnamMap').setView([16.054407, 108.202164], 5);
    
    // Nền Dark Matter công nghệ cao
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 18
    }).addTo(tacticalMap);

    // VÙNG chứa tuyến đường và điểm khách (để dập khi bấm lệnh mới)
    let currentDrawingLayers = L.layerGroup().addTo(tacticalMap);

    // Cắm cờ các Trạm Kho (Màu xanh nước biển)
    const warehouseIcon = L.divIcon({
        className: 'custom-div-icon',
        html: "<div style='background-color:#3b82f6; width:12px; height:12px; border-radius:50%; border: 2px solid white; box-shadow: 0 0 10px #3b82f6;'></div>",
        iconAnchor: [6, 6]
    });
    
    appData.suppliers_inventory.forEach(wh => {
        if(wh.address && wh.address.coordinates) {
            L.marker([wh.address.coordinates.lat, wh.address.coordinates.lng], {icon: warehouseIcon})
             .bindPopup(`<b>${wh.name}</b><br>Kho Hàng Phân Phối`)
             .addTo(tacticalMap);
        }
    });

    const customerIcon = L.divIcon({
        className: 'custom-div-icon',
        html: "<div style='background-color:#ef4444; width:14px; height:14px; border-radius:50%; border: 2px solid white; box-shadow: 0 0 15px #ef4444;'></div>",
        iconAnchor: [7, 7]
    });

    // --- HỆ THỐNG IN LOG MÔ PHỎNG TERMINAL ---
    const consoleBody = document.getElementById('consoleBody');
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const printLog = async (message, type = 'normal') => {
        const line = document.createElement('div');
        line.className = `log-line text-${type}`;
        
        let prefix = "> ";
        if(type === 'yellow') prefix = "[ĐANG XỬ LÝ] ";
        if(type === 'red') prefix = "[THẤT BẠI] ";
        if(type === 'green') prefix = "[THÀNH CÔNG] ";

        line.innerText = prefix + message;
        consoleBody.appendChild(line);
        consoleBody.scrollTop = consoleBody.scrollHeight; // Auto scroll to bottom
        await sleep(800); // Tạo độ trễ cảm giác "Máy chủ đang chạy thuật toán"
    };

    // --- LOGIC XỬ LÝ ĐƠN HÀNG CHÍNH ---
    window.simulateOrder = async function() {
        consoleBody.innerHTML = ''; // Clear log
        currentDrawingLayers.clearLayers(); // Tẩy vết tích các đường chỉ đỏ nhện vận tải lần trước đi

        const custName = document.getElementById('customerName').value;
        const productId = document.getElementById('productSelect').value;
        const requiredQty = parseInt(document.getElementById('buyQty').value);
        const locParts = document.getElementById('locationSelect').value.split(',');
        const custLat = parseFloat(locParts[0]);
        const custLng = parseFloat(locParts[1]);

        // Thả cờ khách hàng và kéo Zoom xáp lại gần điểm đó
        let customerMarker = L.marker([custLat, custLng], {icon: customerIcon})
            .bindPopup(`<b>${custName}</b><br>Đang yêu cầu ${requiredQty} SP`)
            .addTo(currentDrawingLayers);
        customerMarker.openPopup();
        tacticalMap.setView([custLat, custLng], 5);

        await printLog(`Tiếp nhận đơn hàng mới từ Khách: ${custName} - Tọa độ [${custLat}, ${custLng}].`, 'normal');
        await printLog(`Mã Yêu Cầu: Cần ${requiredQty}x ${productId}.`, 'normal');
        
        let isAuto = document.getElementById('chkAutoDistribute').checked;
        let targetWarehouses = appData.suppliers_inventory;

        if (isAuto) {
            await printLog("Vận hành: Chế độ SMART SPLIT. Đang quét màng lưới Toàn Quốc để phân phối...", 'yellow');
        } else {
            let selectedIds = Array.from(document.querySelectorAll('.wh-chk:checked')).map(el => el.value);
            targetWarehouses = appData.suppliers_inventory.filter(wh => selectedIds.includes(wh.supplierId));
            
            if (targetWarehouses.length === 0) {
                await printLog(`🛑 LỖI PANEL: Bạn đã Ngắt Auto nhưng Không Đóng Cầu Dao Nạp Kho nào cả! Lệnh Khởi Động Bất Thành!`, 'red');
                document.getElementById('shippingFeeDisplay').innerText = `HỦY`;
                return; // Đá văng ngay lập tức
            }
            
            let whNames = targetWarehouses.map(w => w.name).join(' + ');
            await printLog(`[ RƠ-LE ĐÓNG MẠCH ] Cán bộ đã Giăng Lưới Chỉ cho phép mượn hàng từ: [${whNames}]. Cô lập và Cấm lấy Trộm từ Các Kho ngoài Tầm Ngắm!`, 'red');
        }

        // B1: Tính toán khoảng cách (Gắn Kênh Vệ Tinh OSRM Routing Thực Tế)
        await printLog("Vận hành: Đang kết nối Trạm Không Gian OSRM để vét dữ liệu Đường bộ thực tế...", 'yellow');
        
        let storesWithDistance = [];
        for (let store of targetWarehouses) {
            let dist = Infinity;
            let routeGeoJson = null;
            
            if (store.address && store.address.coordinates) {
                let whLat = store.address.coordinates.lat;
                let whLng = store.address.coordinates.lng;
                
                try {
                    let response = await fetch(`https://router.project-osrm.org/route/v1/driving/${whLng},${whLat};${custLng},${custLat}?overview=full&geometries=geojson`);
                    let data = await response.json();
                    
                    if(data.code === "Ok") {
                        dist = Math.round(data.routes[0].distance / 1000); // Km
                        routeGeoJson = data.routes[0].geometry; // Toạ độ đường gấp khúc
                        await printLog(`> [Hệ thống Đám mây Phản hồi] Quét thấy ${store.name}. Phân tích: ${dist}km đi đường Quốc Lộ.`, 'normal');
                    } else {
                        // Fallback
                        dist = Math.round(calculateDistance(custLat, custLng, whLat, whLng));
                        await printLog(`> OSRM Nghẽn sóng. Dùng cảm biến Nội bộ: ${store.name} cách ${dist}km đường chim bay.`, 'normal');
                    }
                } catch(e) {
                    dist = Math.round(calculateDistance(custLat, custLng, whLat, whLng));
                }
                
                storesWithDistance.push({
                    ...store,
                    distanceKM: dist,
                    routeGeoJson: routeGeoJson
                });
            }
        }

        // B2: Sắp xếp theo Khoảng cách tăng dần (Gần nhất đứng trước)
        storesWithDistance.sort((a, b) => a.distanceKM - b.distanceKM);
        const productInfo = appData.products.find(p => p.productId === productId);

        // B3: Vòng lặp quét ưu tiên đa kho (Split Allocation Auto Load Balancing)
        let remainingQty = requiredQty;
        let logisticsPath = [];
        let totalShippingFee = 0;
        
        document.getElementById('shippingFeeDisplay').innerText = `Đang đo xa...`;

        for (let i = 0; i < storesWithDistance.length; i++) {
            if (remainingQty <= 0) break; // Khách đã được phân bổ đủ số lượng hàng

            let currentStore = storesWithDistance[i];
            if (currentStore.distanceKM === Infinity) continue;

            await printLog(`Đã quét thấy [${currentStore.name}] cách khách hàng ${currentStore.distanceKM}km`, 'yellow');

            // Định vị Trực Tiếp Tụy Dữ Liệu
            let originalStore = appData.suppliers_inventory.find(s => s.supplierId === currentStore.supplierId);
            let invItemArray = originalStore.inventory.find(inv => inv.productId === productId);
            let currentStock = invItemArray ? invItemArray.stockQuantity : 0;

            if (currentStock > 0) {
                let toDeduct = Math.min(currentStock, remainingQty);
                invItemArray.stockQuantity -= toDeduct; // Bào dần lượng kho
                remainingQty -= toDeduct; // Bào dần nhu cầu khách
                
                let shipFee = calculateShippingCost(currentStore.distanceKM);
                totalShippingFee += shipFee;
                
                logisticsPath.push(`${toDeduct} cái từ [${currentStore.name}]`);
                await printLog(`> Nhặt hàng thành công: Cắt ${toDeduct} SP từ ${currentStore.name}. Số lượng KH vẫn đang thiếu: ${remainingQty} cái.`, 'green');
                await printLog(`💸 Cước chuyển từ Kho này: +${shipFee.toLocaleString()}đ`, 'normal');
                
                // Móc Tuyến Đường AI Nối Tới Khách (Phase 16: OSRM GeoJSON Path)
                let whLat = currentStore.address.coordinates.lat;
                let whLng = currentStore.address.coordinates.lng;
                
                let laserPath;
                if (currentStore.routeGeoJson) {
                    // Vẽ Tracking Map Uốn lượn Chuẩn Quốc Tế
                    laserPath = L.geoJSON(currentStore.routeGeoJson, {
                        style: {
                            color: '#06b6d4', // Cyan Tech
                            weight: 4,
                            opacity: 0.9,
                            dashArray: '5, 10'
                        }
                    }).addTo(currentDrawingLayers);
                } else {
                    // Đường chim bay dự phòng
                    laserPath = L.polyline([[whLat, whLng], [custLat, custLng]], {
                        color: '#f59e0b',
                        weight: 3,
                        opacity: 0.8,
                        dashArray: '10, 10',
                        lineCap: 'round'
                    }).addTo(currentDrawingLayers);
                }
                
                laserPath.bindPopup(`Tuyến xuất nạp: Thực Tế<br>Từ: ${currentStore.name} ➡️ Cửa Nhà Khách<br>Khối Lượng Vận Tải: ${toDeduct}<br>Cự Li: ${currentStore.distanceKM}km`);
            } else {
                await printLog(`Kho [${currentStore.name}] trống trơn (Chỉ có 0 cái). Lập tức bỏ qua, rà quét trạm chuyển phát xa hơn...`, 'red');
            }
        }

        // B4: Tổng kết quá trình đóng Đơn
        if (remainingQty === 0) {
            await printLog("Điều phối Chia Kho thành công! Tiến hành chốt dấu In Bill vào Trí não Hệ Thống...", 'yellow');
            
            const orderId = "GEO" + Math.floor(Math.random() * 10000).toString().padStart(4, '0');
            appData.orders.unshift({
                orderId: orderId,
                customerId: custName,
                status: "completed",
                totalAmount: (productInfo.price * requiredQty) + totalShippingFee, // Ghi nhận cả tiền cước
                orderDate: new Date().toISOString(),
                items: [{
                    productId: productId,
                    name: productInfo.name,
                    price: productInfo.price,
                    quantity: requiredQty
                }]
            });

            // Nếu mọi thứ trót lọt, đóng dấu ấn ngọc tỉ (lưu local)
            localStorage.setItem('novaPosData', JSON.stringify(appData));
            document.getElementById('shippingFeeDisplay').innerText = `${totalShippingFee.toLocaleString()} đ`;
            await printLog(`✅ TUYỆT VỜI! Mã vận đơn ${orderId} đã được ký khống Đa Điểm với Chuỗi cung ứng: [ ${logisticsPath.join(' + ')} ] !`, 'green');
            
        } else {
            await printLog(`❌ BÁO ĐỘNG ĐỎ VỀ ỨNG TRĨ: Toàn bộ hệ sinh thái kho trên cả nước đều không gom đủ, Thiếu hụt (${remainingQty} món)!`, 'red');
            await printLog("Hành động Cứu Mạng: Phủ quyết Phiếu xuất. Rollback Trả số liệu về lại ban đầu. Đẩy đơn về luồng Chờ nhập hàng.", 'red');
            
            document.getElementById('shippingFeeDisplay').innerText = `HỦY`;
            // Re-fetch appData từ CSDL cứng để đảo ngược hành vi trừ kho ảo ở RAM Array
            appData = JSON.parse(localStorage.getItem('novaPosData'));
        }
        
    };
});
