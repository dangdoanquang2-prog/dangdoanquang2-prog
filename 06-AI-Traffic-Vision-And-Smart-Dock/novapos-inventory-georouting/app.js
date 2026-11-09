document.addEventListener('DOMContentLoaded', () => {
    // 1. Dữ liệu mẫu ban đầu (Mock Data)
    const initialData = {
        products: [
            { productId: "SP001", name: "Điện thoại H-Phone 15", category: "Điện tử", price: 25000000 },
            { productId: "SP002", name: "Tai nghe Bluetooth Pro", category: "Phụ kiện", price: 3500000 },
            { productId: "SP003", name: "Ốp lưng siêu mỏng", category: "Phụ kiện", price: 250000 },
            { productId: "SP004", name: "Sạc dự phòng 10000mAh", category: "Phụ kiện", price: 800000 }
        ],
        suppliers_inventory: [
            {
                supplierId: "NCC001", name: "Kho Tổng miền Bắc", 
                inventory: [
                    { productId: "SP001", stockQuantity: 15 },
                    { productId: "SP002", stockQuantity: 42 },
                    { productId: "SP003", stockQuantity: 120 }
                ]
            }
        ],
        customers: [
            { customerId: "KH001", name: "Nguyễn Văn A" },
            { customerId: "KH002", name: "Trần Thị B" },
            { customerId: "KH003", name: "Lê Hoàng C" }
        ],
        orders: [
            { orderId: "DH001", customerId: "KH001", status: "completed", totalAmount: 25000000, orderDate: new Date().toISOString() },
            { orderId: "DH002", customerId: "KH002", status: "pending", totalAmount: 3500000, orderDate: new Date(Date.now() - 86400000).toISOString() },
            { orderId: "DH003", customerId: "KH003", status: "completed", totalAmount: 25800000, orderDate: new Date(Date.now() - 172800000).toISOString() }
        ]
    };

    // 2. Khởi tạo LocalStorage nếu chưa có
    if (!localStorage.getItem('novaPosData')) {
        localStorage.setItem('novaPosData', JSON.stringify(initialData));
    }

    // 3. Lấy dữ liệu từ LocalStorage
    const appData = JSON.parse(localStorage.getItem('novaPosData'));

    // 4. Hàm định dạng tiền tệ VD: 25.000.000 đ
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    };

    // 5. Cập nhật ngày tháng trên Header
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').innerText = new Date().toLocaleDateString('vi-VN', dateOptions);

    // 6. Tính toán và cập nhật Widgets
    const totalRevenue = appData.orders
        .filter(o => o.status === 'completed')
        .reduce((sum, order) => sum + order.totalAmount, 0);
    
    document.getElementById('totalRevenue').innerText = formatCurrency(totalRevenue);
    document.getElementById('totalOrders').innerText = appData.orders.length;
    document.getElementById('totalCustomers').innerText = appData.customers.length;
    document.getElementById('totalProducts').innerText = appData.products.length;

    // 7. Render danh sách Đơn hàng gần đây
    const tbody = document.getElementById('recentOrdersBody');
    appData.orders.slice(0, 5).forEach(order => {
        const customer = appData.customers.find(c => c.customerId === order.customerId);
        const orderDate = new Date(order.orderDate).toLocaleDateString('vi-VN');
        const statusClass = order.status === 'completed' ? 'completed' : 'pending';
        const statusText = order.status === 'completed' ? 'Hoàn thành' : 'Đang xử lý';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>#${order.orderId}</strong></td>
            <td>${customer ? customer.name : 'Khách vãng lai'}</td>
            <td>${orderDate}</td>
            <td><strong>${formatCurrency(order.totalAmount)}</strong></td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
        `;
        tbody.appendChild(tr);
    });

    // 8. Render Tình trạng kho (Miền Bắc)
    const inventoryList = document.getElementById('inventoryList');
    const mienBacInventory = appData.suppliers_inventory.find(inv => inv.supplierId === "NCC001")?.inventory || [];
    
    mienBacInventory.forEach(item => {
        const product = appData.products.find(p => p.productId === item.productId);
        if (product) {
            const li = document.createElement('li');
            li.className = 'product-item';
            li.innerHTML = `
                <div class="product-info">
                    <span class="product-name">${product.name}</span>
                    <span class="product-stock">Mã SP: ${product.productId}</span>
                </div>
                <div class="stock-count">${item.stockQuantity} sẵn có</div>
            `;
            inventoryList.appendChild(li);
        }
    });

    // Hệ thống Thanh tìm kiếm Tổng quát (Global Search & Auto-Suggest Phase 21)
    const globalSearchBox = document.getElementById('globalSearchBox');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
    if (globalSearchBox) {
        
        globalSearchBox.addEventListener('input', (e) => {
            const query = e.target.value.trim().toLowerCase();
            if (!query) {
                if(searchSuggestions) searchSuggestions.style.display = 'none';
                return;
            }
            
            // Tìm sản phẩm khớp
            const matchedProducts = appData.products.filter(p => 
                p.productId.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
            ).slice(0, 4); // Lấy tối đa 4 món
            
            // Tìm đơn hàng khớp
            const matchedOrders = appData.orders.filter(o => 
                o.orderId.toLowerCase().includes(query) || o.customerId.toLowerCase().includes(query)
            ).slice(0, 2); // Lấy tối đa 2 đơn
            
            if (matchedProducts.length === 0 && matchedOrders.length === 0) {
                if(searchSuggestions) {
                    searchSuggestions.innerHTML = `<div style="padding: 12px; color: #888; font-size: 13px; text-align: center;">Không tìm thấy kết quả</div>`;
                    searchSuggestions.style.display = 'block';
                }
                return;
            }

            let html = '';
            
            matchedProducts.forEach(p => {
                html += `
                    <div class="suggestion-item" onclick="executeSearch('${p.name}')">
                        <i class='bx bx-package'></i>
                        <div class="suggestion-info">
                            <span class="suggestion-name">${p.name}</span>
                            <span class="suggestion-type">Sản phẩm • ID: ${p.productId}</span>
                        </div>
                    </div>
                `;
            });

            matchedOrders.forEach(o => {
                html += `
                    <div class="suggestion-item" onclick="executeSearch('${o.orderId}')">
                        <i class='bx bx-receipt' style="color: var(--status-warning);"></i>
                        <div class="suggestion-info">
                            <span class="suggestion-name">Đơn hàng #${o.orderId}</span>
                            <span class="suggestion-type">Khách: ${o.customerId}</span>
                        </div>
                    </div>
                `;
            });
            
            if(searchSuggestions) {
                searchSuggestions.innerHTML = html;
                searchSuggestions.style.display = 'block';
            }
        });

        // Đóng dropdown khi click ra ngoài
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-box') && searchSuggestions) {
                searchSuggestions.style.display = 'none';
            }
        });

        window.executeSearch = (explicitQuery) => {
            if(explicitQuery) {
                globalSearchBox.value = explicitQuery;
                if(searchSuggestions) searchSuggestions.style.display = 'none';
            }
            
            const query = globalSearchBox.value.trim();
            if (!query) return;

            localStorage.setItem('globalSearchQuery', query);
            
            const lowerQuery = query.toLowerCase();
            const isProductMatch = appData.products.some(p => 
                p.productId.toLowerCase().includes(lowerQuery) || p.name.toLowerCase().includes(lowerQuery)
            );

            if (isProductMatch) {
                window.location.href = 'inventory.html';
            } else {
                window.location.href = 'orders.html';
            }
        };

        globalSearchBox.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                executeSearch();
            }
        });
    }

    // Biểu đồ Doanh thu Chart.js (Feature: Data Analytics)
    const renderRevenueChart = () => {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        // Generator tạo trục hoành 7 ngày
        const last7Days = [];
        const revenueData = [];
        
        for (let i = 6; i >= 0; i--) {
            const d = new Date();
            d.setDate(d.getDate() - i);
            last7Days.push(d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }));
            
            const startOfDay = new Date(d.setHours(0,0,0,0)).getTime();
            const endOfDay = new Date(d.setHours(23,59,59,999)).getTime();
            
            // Loop càn quét tất cả order trong ngày
            const dailyTotal = appData.orders.reduce((sum, order) => {
                if(order.status === 'completed' || order.status === 'Hoàn thành') {
                    const oDateMs = new Date(order.orderDate).getTime();
                    // Lưu ý: data mẫu json chưa gắn ngày chuẩn nên ta lọc những date sinh ra valid
                    if(!isNaN(oDateMs) && oDateMs >= startOfDay && oDateMs <= endOfDay) {
                        return sum + order.totalAmount;
                    }
                }
                return sum;
            }, 0);
            
            revenueData.push(dailyTotal);
        }

        // Nếu máy không có dữ liệu 7 ngày qua, ta auto mock 1 chút số liệu giả để test Chart
        if (revenueData.every(val => val === 0)) {
            revenueData[4] = 45000000;
            revenueData[5] = 12500000;
            revenueData[6] = totalRevenue; // Đổi bằng số thực tế hôm nay
        }

        new Chart(ctx, {
            type: 'bar', // Có thể chuyển thành line để vẽ đường
            data: {
                labels: last7Days,
                datasets: [{
                    label: 'Doanh thu',
                    data: revenueData,
                    backgroundColor: 'rgba(59, 130, 246, 0.4)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBackgroundColor: 'rgba(59, 130, 246, 0.9)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        callbacks: {
                            label: function(context) {
                                return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(context.raw);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value >= 1000000 ? (value / 1000000) + ' Tr' : value;
                            }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    };
    
    // Khởi chạy Máy quét Vẽ đồ thị
    renderRevenueChart();

});
