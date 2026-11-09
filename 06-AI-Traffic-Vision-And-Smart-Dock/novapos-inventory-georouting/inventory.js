document.addEventListener('DOMContentLoaded', () => {
    // 1. Kéo dữ liệu gốc từ Local Storage
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    if (!appData) {
        alert("Dữ liệu kho không tồn tại. Vui lòng mở lại trang Tổng quan để khởi tạo dữ liệu mẫu.");
        return;
    }

    // -- PHÂN TÍCH CẤU TRÚC LỒNG DỮ LIỆU ĐỂ GIẢI QUYẾT YÊU CẦU GEO-SCANNING TƯƠNG LAI --
    // Hiện tại appData.suppliers_inventory chứa danh sách các kho. Mỗi kho có thuộc tính `.inventory`.
    // Nếu tương lai kho nào trống hoặc không có toạ độ, chúng ta sẽ tối ưu hoá nó. 
    // Chúng ta tạo một mảng Flatten Data (Trải phẳng) ra màn hình Bảng biểu để người dùng dễ nhìn,
    // Nhưng khi thay đổi số lượng, CẬP NHẬT TRỰC TIẾP vào cấu trúc "Lồng" (nested array) gốc.

    const tbody = document.getElementById('inventoryTableBody');
    const warehouseSelect = document.getElementById('warehouseFilter');

    // 2. Tải danh sách Options cho Filter Kho
    appData.suppliers_inventory.forEach(supplier => {
        let opt = document.createElement('option');
        opt.value = supplier.supplierId;
        opt.textContent = supplier.name + (supplier.address ? ` (${supplier.address.city || 'Chưa định vị'})` : '');
        warehouseSelect.appendChild(opt);
    });

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    };

    // 3. Render Table
    const renderTable = () => {
        const filterStr = document.getElementById('invSearchBox').value.toLowerCase();
        const selectedWarehouse = warehouseSelect.value;
        
        tbody.innerHTML = '';

        // Duyệt qua từ mảng Kho (suppliers)
        appData.suppliers_inventory.forEach(supplier => {
            // Lọc kho
            if (selectedWarehouse !== "ALL" && supplier.supplierId !== selectedWarehouse) return;

            // Mỗi kho quét qua các item tồn kho của nó
            supplier.inventory.forEach(invItem => {
                const productMain = appData.products.find(p => p.productId === invItem.productId);
                if (!productMain) return; // Nếu ko tìm thấy mô tả sp

                // Bộ lọc Search text
                if (filterStr && 
                    !productMain.name.toLowerCase().includes(filterStr) && 
                    !productMain.productId.toLowerCase().includes(filterStr)) {
                    return;
                }

                // Vẽ Dòng (Row)
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${productMain.productId}</strong></td>
                    <td style="text-align: center;">
                        ${productMain.image 
                            ? `<img src="${productMain.image}" style="width:40px; height:40px; border-radius:5px; object-fit:cover; cursor:pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.3);" onclick="triggerProductUpload('${productMain.productId}')" title="Bấm để đổi ảnh">` 
                            : `<button class="btn warning-btn" style="padding: 5px 8px; font-size:16px; border-radius: 8px;" onclick="triggerProductUpload('${productMain.productId}')" title="Tải ảnh lên"><i class='bx bx-camera'></i></button>`
                        }
                    </td>
                    <td style="font-weight: 500;">${productMain.name}</td>
                    <td>${productMain.category}</td>
                    <td>${formatCurrency(productMain.price)}</td>
                    <td><span style="color: var(--brand-primary)">${supplier.name}</span></td>
                    <td>
                        <span class="stock-status-badge ${invItem.stockQuantity <= 10 ? (invItem.stockQuantity === 0 ? 'danger' : 'warning') : 'success'}">
                            ${invItem.stockQuantity}
                        </span>
                    </td>
                    <td>
                        <div class="quick-adjust-group">
                            <button class="adj-btn btn-minus" data-warehouse="${supplier.supplierId}" data-product="${productMain.productId}">-</button>
                            <button class="adj-btn btn-plus" data-warehouse="${supplier.supplierId}" data-product="${productMain.productId}">+</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });

        // Gắn lại Event Listener sau mỗi lần render
        document.querySelectorAll('.btn-minus').forEach(btn => btn.addEventListener('click', handleQuickAdjust));
        document.querySelectorAll('.btn-plus').forEach(btn => btn.addEventListener('click', handleQuickAdjust));
    };

    // 4. Logic Xử lý Nút Nhập/Xuất Nhanh (In-line Edit)
    const handleQuickAdjust = (e) => {
        const btn = e.currentTarget;
        const warehouseId = btn.getAttribute('data-warehouse');
        const productId = btn.getAttribute('data-product');
        const isPlus = btn.classList.contains('btn-plus');

        // Tìm tới đúng Object cần sửa sâu trong dữ liệu để bảo toàn tính Nested
        const warehouseObj = appData.suppliers_inventory.find(s => s.supplierId === warehouseId);
        if (warehouseObj) {
            let invObj = warehouseObj.inventory.find(i => i.productId === productId);
            if (invObj) {
                if (isPlus) {
                    invObj.stockQuantity += 1;
                } else {
                    if (invObj.stockQuantity > 0) invObj.stockQuantity -= 1;
                }
                // Đồng bộ ngược Storage
                localStorage.setItem('novaPosData', JSON.stringify(appData));
                // Vẽ lại màn hình nhanh
                renderTable();
            }
        }
    };

    // 5. Logic Xuất file CSV (Thuần JS - Không thư viện)
    const exportCSV = () => {
        // Chuẩn bị Header của CSV
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF"; // Thêm BOM (FEFF) để Excel đọc đúng font Tiếng Việt UTF-8
        csvContent += "Ma_Ban_hang,Ten_San_pham,Phan_loai,Gia_Ban,Kho_Chua,So_luong_ton\n";

        // Push Raw data tương tự lúc Render
        appData.suppliers_inventory.forEach(supplier => {
            supplier.inventory.forEach(invItem => {
                const p = appData.products.find(x => x.productId === invItem.productId);
                if (p) {
                    // Escape ký tự dấu phẩy để không bị vỡ cột trong CSV
                    let nameSafe = '"' + p.name.replace(/"/g, '""') + '"';
                    let priceSafe = p.price;
                    csvContent += `${p.productId},${nameSafe},${p.category},${priceSafe},"${supplier.name}",${invItem.stockQuantity}\n`;
                }
            });
        });

        // Kỹ thuật tải File ảo qua thẻ <a>
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `Bao_Cao_Ton_Kho_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link); // Required for FF
        
        link.click(); 
        document.body.removeChild(link);
    };

    // Events 
    document.getElementById('invSearchBox').addEventListener('input', renderTable);
    warehouseSelect.addEventListener('change', renderTable);
    document.getElementById('btnExportCSV').addEventListener('click', exportCSV);

    // 6. Logic Nhập file CSV (Import Bulk)
    const fileInput = document.getElementById('csvFileInput');
    const btnImportCSV = document.getElementById('btnImportCSV');

    btnImportCSV.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(evt) {
            const text = evt.target.result;
            // Giải phân loại cả Windows (\r\n) lẫn Unix (\n)
            const lines = text.split(/\r?\n/);
            if (lines.length < 2) return alert("File CSV trống hoặc không có thành phần dữ liệu!");

            // Thuật toán tách dòng CSV bỏ qua dấu phẩy rác trong chuỗi Text an toàn
            const parseCSVLine = (line) => {
                let ret = [], p = '', inQuote = false;
                for (let i = 0; i < line.length; i++) {
                    let c = line[i];
                    if (inQuote && c === '"' && line[i + 1] === '"') { p += '"'; i++; } // Escaped quotes
                    else if (c === '"') inQuote = !inQuote;
                    else if (c === ',' && !inQuote) { ret.push(p.trim()); p = ''; }
                    else p += c;
                }
                ret.push(p.trim());
                return ret;
            }

            let updatedCount = 0;
            // Quét từ index số 1 bỏ qua dòng Tiêu đề mẫu Header
            for (let i = 1; i < lines.length; i++) {
                if(!lines[i].trim()) continue; // Bỏ qua dòng trống trắng
                
                const cols = parseCSVLine(lines[i]);
                if (cols.length < 6) continue;

                const productId = cols[0];
                const productName = cols[1];
                const category = cols[2];
                // Lọc bỏ ký tự thừa khỏi giá tiền
                const priceVal = cols[3] ? parseInt(cols[3].replace(/[^0-9]/g, '')) : 0;
                const khoChuaName = cols[4];
                const newStock = parseInt(cols[5]);

                if(isNaN(newStock) || !productId) continue;

                // 1. (UPSERT) Quản trị Sản phẩm gốc (Master Data)
                // Nếu sản phẩm chưa có ở DB tổng, tự động tạo mới!
                let productObj = appData.products.find(p => p.productId === productId);
                if (!productObj) {
                    appData.products.push({
                        productId: productId,
                        name: productName || "Sản phẩm mới",
                        category: category || "Chưa phân loại",
                        price: priceVal || 0,
                        description: "Imported from CSV"
                    });
                } else {
                    // Update giá và tên nếu người dùng sửa ở Excel
                    if(productName) productObj.name = productName;
                    if(priceVal) productObj.price = priceVal;
                }

                // 2. Tìm hoặc Tạo Kho chứa
                // Hỗ trợ tìm kiếm xấp xỉ tên (Trong trường hợp Excel bị rút gọn)
                let khoObj = appData.suppliers_inventory.find(sup => sup.name.trim().includes(khoChuaName.trim()) || khoChuaName.trim().includes(sup.name.trim()));
                
                // NẾU tên kho HOÀN TOÀN T MỚI, Tự tạo Kho mới
                if (!khoObj && khoChuaName.trim() !== '') {
                    khoObj = {
                        supplierId: "NCC_" + Math.floor(Math.random() * 100000),
                        name: khoChuaName.trim(),
                        address: { city: "Chưa rõ", coordinates: { lat: 10.823, lng: 106.629 } }, // Gán tạm Tọa độ HCM để GeoRouting ko bị lỗi
                        inventory: []
                    };
                    appData.suppliers_inventory.push(khoObj);
                    
                    // Cập nhật Select Option ngay lập tức
                    let opt = document.createElement('option');
                    opt.value = khoObj.supplierId;
                    opt.textContent = khoObj.name;
                    document.getElementById('warehouseFilter').appendChild(opt);
                }

                // 3. (UPSERT) Cập nhật dòng Kho
                if (khoObj) {
                    let invItem = khoObj.inventory.find(inv => inv.productId === productId);
                    if (invItem) {
                        invItem.stockQuantity = newStock; // Update
                    } else {
                        khoObj.inventory.push({ productId: productId, stockQuantity: newStock }); // Create
                    }
                    updatedCount++;
                }
            }
            
            // Xong vòng lặp -> Save và Vẽ lại Lưới (Re-render)
            localStorage.setItem('novaPosData', JSON.stringify(appData));
            renderTable();
            alert(`Cập nhật hàng loạt (Bulk Import) thành công!\\nĐã áp đặt số lượng mới cho ${updatedCount} mặt hàng.`);
            fileInput.value = ''; // Giải phóng bộ nhớ input file
        };
        // Decode Tiếng Việt chuẩn
        reader.readAsText(file, 'UTF-8');
    });

    // Bắt sóng tín hiệu từ thanh Global Search (Trang tổng quan)
    const globalQuery = localStorage.getItem('globalSearchQuery');
    if (globalQuery) {
        document.getElementById('searchInput').value = globalQuery;
        localStorage.removeItem('globalSearchQuery');
        // Kích hoạt lại Event Input cho chắc ăn
        document.getElementById('searchInput').dispatchEvent(new Event('input'));
    }

    // 5. Tính năng Tải Ảnh cho riêng từng Lô Sản phẩm (HTML5 Canvas Compression)
    window.triggerProductUpload = function(productId) {
        window.currentUploadProductId = productId;
        document.getElementById('productImageUploader').click();
    };

    document.getElementById('productImageUploader').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if(!file) return;
        
        const productId = window.currentUploadProductId;
        const reader = new FileReader();
        
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                const MAX_SIZE = 200; // Giải mã độ phân giải hình ảnh icon
                let w = img.width, h = img.height;
                if (w > h) { if (w > MAX_SIZE) { h *= MAX_SIZE / w; w = MAX_SIZE; } } 
                else { if (h > MAX_SIZE) { w *= MAX_SIZE / h; h = MAX_SIZE; } }
                
                canvas.width = w; canvas.height = h;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, w, h);
                
                const base64 = canvas.toDataURL('image/jpeg', 0.82); // Mã hóa ra Chuỗi siêu nhẹ
                
                // Đẩy vào Tụy của Product Core Array
                let pObj = appData.products.find(p => p.productId === productId);
                if(pObj) {
                    pObj.image = base64;
                    localStorage.setItem('novaPosData', JSON.stringify(appData));
                    renderTable(); // Vẽ lại giao diện Khung lưới (Tránh load lại full page)
                }
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
        // Reset the value so the same file can be uploaded again if needed
        e.target.value = '';
    });

    // Initial render
    renderTable();
});
