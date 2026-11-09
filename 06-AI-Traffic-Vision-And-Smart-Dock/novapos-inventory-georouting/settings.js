document.addEventListener('DOMContentLoaded', () => {
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    
    // Nếu db cũ không có lõi Setting, tự động nhồi vào
    if (!appData.settings) {
        appData.settings = { storeName: "NovaPOS", vatEnabled: false, vatRate: 8 };
        localStorage.setItem('novaPosData', JSON.stringify(appData));
    }
    
    const settings = appData.settings;

    // Phân giải UI Elements
    const storeNameInput = document.getElementById('storeNameInput');
    const btnSaveBasic = document.getElementById('btnSaveBasic');
    const vatToggle = document.getElementById('vatToggle');
    const vatRateSelect = document.getElementById('vatRateSelect');

    // Chập dữ liệu khởi điểm
    storeNameInput.value = settings.storeName || "NovaPOS";
    vatToggle.checked = settings.vatEnabled;
    vatRateSelect.value = settings.vatRate;

    // ----- CẢM BIẾN TẢI ẢNH LOGO (CANVAS BASE64) -----
    const logoUploadInput = document.getElementById('logoUploadInput');
    const logoPreview = document.getElementById('logoPreview');
    
    // Khai báo Avatar elements
    const avatarUploadInput = document.getElementById('avatarUploadInput');
    const avatarPreview = document.getElementById('avatarPreview');
    
    if (settings.storeLogo) {
        logoPreview.innerHTML = `<img src="${settings.storeLogo}" style="width:100%; height:100%; object-fit:cover;">`;
    }
    if (settings.userAvatar) {
        avatarPreview.innerHTML = `<img src="${settings.userAvatar}" style="width:100%; height:100%; object-fit:cover;">`;
    }

    // Hàm dùng chung để Nén và Lưu Ảnh (DRY Principle)
    const handleImageUpload = (file, previewElement, settingKey, alertMsg) => {
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(event) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                const MAX_SIZE = 150; 
                let w = img.width, h = img.height;
                if (w > h) { if (w > MAX_SIZE) { h *= MAX_SIZE / w; w = MAX_SIZE; } } 
                else { if (h > MAX_SIZE) { w *= MAX_SIZE / h; h = MAX_SIZE; } }
                
                canvas.width = w; canvas.height = h;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, w, h);
                
                settings[settingKey] = canvas.toDataURL('image/jpeg', 0.8);
                previewElement.innerHTML = `<img src="${settings[settingKey]}" style="width:100%; height:100%; object-fit:cover;">`;
                alert(alertMsg);
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    };

    logoUploadInput.addEventListener('change', (e) => {
        handleImageUpload(e.target.files[0], logoPreview, 'storeLogo', "✔️ Đã tải Logo công ty. Bấm 'Xác nhận' để áp dụng!");
    });
    
    avatarUploadInput.addEventListener('change', (e) => {
        handleImageUpload(e.target.files[0], avatarPreview, 'userAvatar', "✔️ Đã tải Ảnh cá nhân. Bấm 'Xác nhận' để áp dụng!");
    });

    // ----- CẢM BIẾN LƯU TÊN CỬA HÀNG & AVATAR -----
    btnSaveBasic.addEventListener('click', () => {
        const newName = storeNameInput.value.trim() || "NovaPOS";
        settings.storeName = newName;
        appData.settings = settings;
        localStorage.setItem('novaPosData', JSON.stringify(appData));
        alert("Đã Cập nhật Dữ liệu Toàn hệ thống! Trình duyệt sẽ được tải lại.");
        location.reload();
    });

    // ----- CẢM BIẾN LƯU THUẾ -----
    const saveTax = () => {
        settings.vatEnabled = vatToggle.checked;
        settings.vatRate = parseInt(vatRateSelect.value);
        appData.settings = settings;
        localStorage.setItem('novaPosData', JSON.stringify(appData));
    };
    vatToggle.addEventListener('change', saveTax);
    vatRateSelect.addEventListener('change', saveTax);

    // ----- SAO LƯU DỰ PHÒNG CHỐNG CHÁY NỔ (DOWNLOAD BLOB) -----
    document.getElementById('btnBackup').addEventListener('click', () => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData));
        
        const dlNode = document.createElement('a');
        dlNode.setAttribute("href", dataStr);
        dlNode.setAttribute("download", `DULIEU_${settings.storeName.replace(/\s/g, "")}_${timestamp}.json`);
        document.body.appendChild(dlNode);
        
        dlNode.click();
        dlNode.remove();
        alert("Đã xuất kho lưu trữ an toàn ra máy tính!");
    });

    // ----- VŨ KHÍ NGUYÊN TỬ (XÓA SẠCH VÀ LÀM LẠI MỚI TOANH) -----
    document.getElementById('btnWipe').addEventListener('click', () => {
        const pass = prompt("CẢNH BÁO MẤT TIỀN CỦA VÀ DỮ LIỆU!\nHành động này không thể hoàn tác nếu bạn chưa ấn Backup JSON ra máy. Nếu bạn muốn xóa TẤT CẢ các Hóa đơn rác lúc test để Khai trương bán thật, hãy nhập Mật Khẩu Admin (123) để Xác nhận Lệnh Xóa Trắng:");
        
        if (pass === '123') {
            appData.products = [];
            appData.suppliers_inventory = [];
            appData.customers = [];
            appData.orders = [];
            
            localStorage.setItem('novaPosData', JSON.stringify(appData));
            alert("Lệnh phá hủy Database thành công! Đã quét sạch. Hệ thống sẽ Khởi động Lại.");
            location.reload();
        } else if (pass !== null) {
            alert("Sai Cú Pháp Phá Hủy! Kích hoạt chặn Tường Lửa bảo vệ Database ngầm định.");
        }
    });
});
