document.addEventListener('DOMContentLoaded', () => {
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    if (!appData) return;

    const tbody = document.getElementById('crmTableBody');
    const searchBox = document.getElementById('crmSearchBox');

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    };

    const renderCRMTable = () => {
        const filterStr = searchBox.value.toLowerCase().trim();
        tbody.innerHTML = '';

        // Thuật toán: Tạo một mảng mới chứa tổng chi tiêu
        let customersData = appData.customers.map(cust => {
            // Quét qua toàn bộ đơn hàng (orders) để tìm đơn của khách này
            let custOrders = appData.orders.filter(o => o.customerId === cust.customerId || o.customerId === cust.name);
            let totalSpent = custOrders.reduce((sum, order) => sum + (order.status === 'completed' ? order.totalAmount : 0), 0);
            
            // Xếp hạng Thẻ
            let rank = 'Thành viên mới (Bronze)';
            let badgeClass = 'normal';
            if (totalSpent >= 20000000) { rank = 'KIM CƯƠNG (Diamond)'; badgeClass = 'primary'; }
            else if (totalSpent >= 10000000) { rank = 'VÀNG (Gold)'; badgeClass = 'warning'; }
            else if (totalSpent >= 5000000) { rank = 'BẠC (Silver)'; badgeClass = 'success'; }

            return {
                ...cust,
                totalOrders: custOrders.length,
                totalSpent: totalSpent,
                rank: rank,
                badgeClass: badgeClass
            };
        });

        // Sắp xếp người mua nhiều nhất lên đầu
        customersData.sort((a, b) => b.totalSpent - a.totalSpent);

        customersData.forEach(cust => {
            // Lọc Search
            if (filterStr && 
                !cust.name.toLowerCase().includes(filterStr) && 
                !(cust.phone && cust.phone.includes(filterStr))) {
                return;
            }

            const phoneStr = cust.phone ? cust.phone : "Chưa cập nhật";

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${cust.customerId}</strong></td>
                <td style="color: var(--text-primary); font-weight: 500;">
                    <div style="display:flex; align-items:center; gap: 8px;">
                        <img src="https://ui-avatars.com/api/?name=${encodeURIComponent(cust.name)}&background=random" style="width: 24px; height: 24px; border-radius: 50%;">
                        ${cust.name}
                    </div>
                </td>
                <td>${phoneStr}</td>
                <td>${cust.totalOrders} đơn</td>
                <td style="color: var(--status-success); font-weight: 600;">${formatCurrency(cust.totalSpent)}</td>
                <td><span class="stock-status-badge ${cust.badgeClass}" style="font-size: 11px;">${cust.rank}</span></td>
            `;
            tbody.appendChild(tr);
        });
    };

    searchBox.addEventListener('input', renderCRMTable);
    renderCRMTable();
});
