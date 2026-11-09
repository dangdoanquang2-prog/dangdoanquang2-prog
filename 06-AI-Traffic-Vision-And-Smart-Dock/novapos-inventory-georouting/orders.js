document.addEventListener('DOMContentLoaded', () => {
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    if (!appData) return;

    const tbody = document.getElementById('ordersTableBody');
    const searchBox = document.getElementById('orderSearchBox');

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    };

    const renderOrdersTable = () => {
        const filterStr = searchBox.value.toLowerCase().trim();
        tbody.innerHTML = '';

        // Tách riêng danh sách order và sắp xếp mới nhất lên đầu 
        let ordersData = [...appData.orders];
        
        // Cố gắng parse Date chuẩn, nếu lỗi thì giữ nguyên. Fix lỗi chuỗi Date.
        ordersData.sort((a, b) => {
            let dateA = new Date(a.orderDate).getTime();
            let dateB = new Date(b.orderDate).getTime();
            // Nếu ngày lỗi hoặc ko xác định thì đẩy ra sau
            if(isNaN(dateA)) dateA = 0;
            if(isNaN(dateB)) dateB = 0;
            return dateB - dateA;
        });

        ordersData.forEach(order => {
            // Lọc Search theo ID đơn hoặc Tên Khách
            const orderIdStr = order.orderId ? order.orderId.toLowerCase() : "";
            const custIdStr = order.customerId ? order.customerId.toLowerCase() : "";
            
            if (filterStr && !orderIdStr.includes(filterStr) && !custIdStr.includes(filterStr)) {
                return;
            }

            // Định dạng chuỗi ngày đẹp đẽ
            let displayDate = order.orderDate;
            let pDate = new Date(order.orderDate);
            if (!isNaN(pDate.getTime())) {
                displayDate = pDate.toLocaleDateString('vi-VN', {
                    day: '2-digit', month: '2-digit', year: 'numeric',
                    hour: '2-digit', minute:'2-digit'
                });
            }

            // Badges trạng thái
            let statusBadge = `<span class="stock-status-badge warning">Đang xử lý</span>`;
            if(order.status === 'completed' || order.status === 'Hoàn thành') {
                statusBadge = `<span class="stock-status-badge success">Hoàn thành</span>`;
            } else if(order.status === 'cancelled') {
                statusBadge = `<span class="stock-status-badge danger">Đã hủy</span>`;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 600;">#${order.orderId}</td>
                <td>${order.customerId}</td>
                <td style="color: var(--text-secondary);">${displayDate}</td>
                <td style="font-weight: 600; color: var(--text-primary);">${formatCurrency(order.totalAmount)}</td>
                <td>${statusBadge}</td>
                <td style="text-align:center;">
                    <button class="btn primary-btn" style="padding: 4px 10px; font-size: 12px;" onclick="viewOrderDetails('${order.orderId}')">
                        <i class='bx bx-show'></i> Chi Tiết
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    };

    searchBox.addEventListener('input', renderOrdersTable);
    
    // Bắt sóng tín hiệu từ thanh Global Search (Trang tổng quan)
    const globalQuery = localStorage.getItem('globalSearchQuery');
    if (globalQuery) {
        searchBox.value = globalQuery;
        localStorage.removeItem('globalSearchQuery');
    }

    renderOrdersTable();

    // Hệ Thống Popup Chi Tiết Hóa Đơn (Phase 19)
    window.viewOrderDetails = (orderId) => {
        let order = appData.orders.find(o => o.orderId === orderId);
        if (!order) return;

        document.getElementById('modalOrderId').innerText = order.orderId;
        
        let pDate = new Date(order.orderDate);
        let dateStr = isNaN(pDate.getTime()) ? order.orderDate : pDate.toLocaleString('vi-VN');
        
        document.getElementById('modalOrderInfo').innerHTML = `
            <b>Tên khách hàng:</b> ${order.customerId} <br>
            <b>Ngày xác nhận:</b> ${dateStr} <br>
            <b>Trạng thái Giao dịch:</b> ${order.status === 'completed' ? 'Hoàn tất' : 'Đã hủy'}
        `;

        const tbody = document.getElementById('modalItemsBody');
        tbody.innerHTML = '';
        
        if (order.items && order.items.length > 0) {
            order.items.forEach(item => {
                let tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="padding: 8px 5px; color:var(--text-primary);">${item.name} <br> <span style="font-size:11px; color:#888;">ID: ${item.productId}</span></td>
                    <td style="padding: 8px 5px;">${formatCurrency(item.price)}</td>
                    <td style="padding: 8px 5px; font-weight:bold;">x${item.quantity}</td>
                    <td style="padding: 8px 5px; text-align: right; color:var(--text-primary); font-weight:600;">${formatCurrency(item.price * item.quantity)}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            // Lịch sử Đơn hàng phiên bản cũ chưa có Record
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 20px; color:#888;"><i>Đơn hàng phiên bản cũ (Không lưu lịch sử mặt hàng).</i></td></tr>`;
        }

        document.getElementById('modalTotalAmount').innerText = formatCurrency(order.totalAmount);
        
        // Hiện Modal
        document.getElementById('orderDetailModal').style.display = 'block';
    };

    // Đóng Modal
    document.getElementById('closeModalBtn').addEventListener('click', () => {
        document.getElementById('orderDetailModal').style.display = 'none';
    });
    
    // Bấm ra ngoài rìa để đóng modal
    window.addEventListener('click', (e) => {
        let modal = document.getElementById('orderDetailModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

});
