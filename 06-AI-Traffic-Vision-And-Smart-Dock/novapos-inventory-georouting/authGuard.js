(function() {
    // 1. Chạy trước khi DOM Render
    const userStr = sessionStorage.getItem('novaPosUser');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Chưa đăng nhập thì bắt buộc bay về cổng vào
    if (!userStr && currentPage !== 'login.html') {
        window.location.href = 'login.html';
        return;
    }
    
    // 2. Chặn quyền phân cấp
    if (userStr && currentPage !== 'login.html') {
        const user = JSON.parse(userStr);
        
        // Cấp nhân viên (Thu ngân) bị cấm tiệt vào tổng quan và xuất nhập kho
        const cashierAllowed = ['pos.html'];
        if (user.role === 'cashier' && !cashierAllowed.includes(currentPage)) {
            alert("Tường lửa kích hoạt: Quyền của nhân viên không được truy cập Tình hình tài chính/Kho. Màn hình tự động khóa về Quầy Bán!");
            window.location.href = 'pos.html';
            return;
        }

        // 3. Thay đổi tên hiển thị (Đoàn Quang Đăng) sau khi DOM tải xong
        document.addEventListener('DOMContentLoaded', () => {
            
            // Apply Tên Thương Hiệu (Branding override) trên toàn bộ mọi file html
            let localData = JSON.parse(localStorage.getItem('novaPosData'));
            if (localData && localData.settings) {
                if(localData.settings.storeName) {
                    const logs = document.querySelectorAll('.logo-text');
                    logs.forEach(l => {
                        const parts = localData.settings.storeName.trim().split(' ');
                        const lastWord = parts.pop() || '';
                        l.innerHTML = `${parts.join(' ')} <span>${lastWord}</span>`;
                    });
                }
                
                if(localData.settings.storeLogo) {
                    const icons = document.querySelectorAll('.logo-icon');
                    icons.forEach(i => {
                        i.innerHTML = `<img src="${localData.settings.storeLogo}" style="width:100%; height:100%; border-radius: 8px; object-fit: cover;">`;
                        i.style.background = 'transparent'; 
                        i.style.padding = '0'; // Xóa viền khung xanh cũ đi để nhường chỗ hoàn toàn cho ảnh
                    });
                }
                
                // Mới: Gán đè ảnh đại diện chân dung nếu có
                if(localData.settings.userAvatar) {
                    const avatars = document.querySelectorAll('.avatar');
                    avatars.forEach(a => {
                        a.src = localData.settings.userAvatar;
                    });
                }
            }

            // Thay đổi chữ xin chào ở bảng Index dựa vào tên
            const welcomeText = document.querySelector('.page-title');
            if (welcomeText && welcomeText.innerText.includes('Xin chào')) {
                welcomeText.innerText = `Xin chào, sếp ${user.name} 👋`;
            }

            // Gắn event đăng xuất vô tất cả các nút .logout nếu có
            const logoutBtns = document.querySelectorAll('.logout');
            logoutBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if(confirm("Xác nhận rời khỏi hệ thống?")) {
                        sessionStorage.removeItem('novaPosUser');
                        window.location.href = 'login.html';
                    }
                });
            });
        });
    }
})();
