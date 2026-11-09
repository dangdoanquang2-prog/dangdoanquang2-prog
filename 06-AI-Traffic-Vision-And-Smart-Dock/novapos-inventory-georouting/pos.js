document.addEventListener('DOMContentLoaded', () => {
    // 1. Lấy dữ liệu sản phẩm từ LocalStorage
    let appData = JSON.parse(localStorage.getItem('novaPosData'));
    
    // Khởi tạo giỏ hàng rỗng
    let cart = [];

    // Mảng ảnh placeholder đẹp từ Unsplash để minh hoạ
    const demoImages = {
        "SP001": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&q=80", // Điện thoại
        "SP002": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=300&q=80", // Tai nghe
        "SP003": "https://images.unsplash.com/photo-1605342410884-6338fbccbbc4?w=300&q=80", // Ốp lưng
        "SP004": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=300&q=80"  // Sạc dự phòng
    };

    // 2. Render lưới sản phẩm
    const renderProducts = (products) => {
        const productGrid = document.getElementById('posProductList');
        productGrid.innerHTML = '';

        products.forEach(product => {
            const imgUrl = demoImages[product.productId] || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&q=80"; // fallback
            
            const card = document.createElement('div');
            card.className = 'pos-product-card';
            card.innerHTML = `
                <div class="product-img-wrapper">
                    <img src="${imgUrl}" alt="${product.name}">
                </div>
                <div class="product-info">
                    <h4>${product.name}</h4>
                    <p class="price">${formatCurrency(product.price)}</p>
                </div>
                <button class="add-to-cart-btn"><i class='bx bx-plus'></i></button>
            `;
            
            // Xử lý click thêm vào giỏ hàng
            card.addEventListener('click', () => addToCart(product));
            productGrid.appendChild(card);
        });
    };

    // Hàm định dạng tiền tệ
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
    };

    // 3. Logic: Thêm vào giỏ
    const addToCart = (product) => {
        const existingItem = cart.find(item => item.productId === product.productId);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ ...product, quantity: 1 });
        }
        renderCart();
    };

    // Logic: Giảm số lượng hoặc xóa
    const decreaseQuantity = (productId) => {
        const itemIndex = cart.findIndex(item => item.productId === productId);
        if (itemIndex > -1) {
            if (cart[itemIndex].quantity > 1) {
                cart[itemIndex].quantity -= 1;
            } else {
                cart.splice(itemIndex, 1);
            }
        }
        renderCart();
    };

    const clearCart = () => {
        cart = [];
        renderCart();
    }

    // 2.5 Lấy danh sách Kho vào Dropdown Điều phối Xuất Kho
    const initWarehouseDropdown = () => {
        const select = document.getElementById('checkoutSourceWarehouse');
        if(!select) return;
        
        select.innerHTML = '<option value="AUTO">🌟 Tự động Vét Hết Mọi Chi nhánh (Ưu tiên đủ Đơn)</option>';
        appData.suppliers_inventory.forEach(sup => {
            let opt = document.createElement('option');
            opt.value = sup.supplierId;
            opt.textContent = `🔒 Ép trừ cứng: ${sup.name}`;
            select.appendChild(opt);
        });
    };

    // 2.6 Khôi phục Hình ảnh Thumbnail trong khung giỏ hàng (Móc rễ tính năng Phase 11)
    const renderCart = () => {
        const cartContainer = document.getElementById('cartItemList');
        const cartSubtotalEl = document.getElementById('cartSubtotal');
        const cartTotalEl = document.getElementById('cartTotal');
        
        let total = 0;
        cartContainer.innerHTML = '';

        if (cart.length === 0) {
            cartContainer.innerHTML = '<div class="empty-cart-msg">Chưa có sản phẩm nào trong giỏ.</div>';
            cartSubtotalEl.innerText = '0 đ';
            cartTotalEl.innerText = '0 đ';
            return;
        }

        cart.forEach(item => {
            total += item.price * item.quantity;
            const imgSrc = item.image ? item.image : "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=100&q=80";
            
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            // Cải tiến Thumnail mini cho bill
            cartItem.innerHTML = `
                <div class="cart-item-info" style="display:flex; align-items:center; gap: 8px;">
                    <img src="${imgSrc}" style="width:30px; height:30px; object-fit:cover; border-radius: 4px;">
                    <div>
                        <p class="cart-item-name" style="font-size: 13px;">${item.name}</p>
                        <p class="cart-item-price" style="font-size: 11px;">${formatCurrency(item.price)}</p>
                    </div>
                </div>
                <div class="cart-item-actions">
                    <button class="qty-btn minus" data-id="${item.productId}">-</button>
                    <span class="qty-number">${item.quantity}</span>
                    <button class="qty-btn plus" data-id="${item.productId}">+</button>
                </div>
            `;
            cartContainer.appendChild(cartItem);
        });

        // Add Event Listeners for + and - buttons
        document.querySelectorAll('.qty-btn.plus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                const product = appData.products.find(p => p.productId === id);
                addToCart(product);
            });
        });

        document.querySelectorAll('.qty-btn.minus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                decreaseQuantity(id);
            });
        });

        cartSubtotalEl.innerText = formatCurrency(total);
        cartTotalEl.innerText = formatCurrency(total);
    };

    // 5. Thanh toán và lưu vào Kho / LocalStorage
    const checkout = () => {
        if (cart.length === 0) {
            alert('Giỏ hàng trống! Vui lòng chọn sản phẩm.');
            return;
        }

        const totalAmount = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        // Tạo mã đơn hàng mới giả lập
        const orderId = "DH" + Math.floor(Math.random() * 10000).toString().padStart(4, '0');
        
        const newOrder = {
            orderId: orderId,
            customerId: "Khách lẻ",
            status: "completed",
            totalAmount: totalAmount,
            orderDate: new Date().toISOString(),
            items: cart.map(item => ({
                productId: item.productId,
                name: item.name,
                price: item.price,
                quantity: item.quantity
            }))
        };

        // Lưu đơn hàng
        appData.orders.unshift(newOrder);

        // ĐIỀU PHỐI TỒN KHO THÔNG MINH (Phase 12)
        const selectNode = document.getElementById('checkoutSourceWarehouse');
        const sourceWhId = selectNode ? selectNode.value : "AUTO";
        
        let warningMsg = "";

        if (sourceWhId !== "AUTO") {
            // Chế độ 1: Bào Kho Cứng (Manual Allocation) - Chỉ định trừ thẳng tay một kho nhất định
            let targetWh = appData.suppliers_inventory.find(sup => sup.supplierId === sourceWhId);
            if (targetWh) {
                cart.forEach(cartItem => {
                    let inventoryItem = targetWh.inventory.find(inv => inv.productId === cartItem.productId);
                    if (inventoryItem) {
                        inventoryItem.stockQuantity -= cartItem.quantity;
                        if (inventoryItem.stockQuantity < 0) {
                            warningMsg += `⚠️ Kho [${targetWh.name}] bị ÂM ${Math.abs(inventoryItem.stockQuantity)} của SP ${cartItem.name}! Mời thủ kho nhập bù kịp thời.\n`;
                        }
                    } else {
                         targetWh.inventory.push({ productId: cartItem.productId, stockQuantity: -cartItem.quantity });
                         warningMsg += `⚠️ Kho [${targetWh.name}] chưa từng nhập SP này, bị ÂM ${cartItem.quantity} của ${cartItem.name}!\n`;
                    }
                });
            }
        } else {
            // Chế độ 2: Tự Động Rút Lõi Đa Kho (Auto Split Allocation)
            // Lặp từng món hàng của Khách mua. Trừ tới khi nào cạn nhu cầu. Nếu Kho 1 hết, mò sang Kho 2.
            cart.forEach(cartItem => {
                let qtyNeeded = cartItem.quantity;
                
                for(let i=0; i < appData.suppliers_inventory.length; i++) {
                    if (qtyNeeded <= 0) break; // Khách đã được mua thỏa mãn số lượng
                    
                    let wh = appData.suppliers_inventory[i];
                    let inventoryItem = wh.inventory.find(inv => inv.productId === cartItem.productId);
                    
                    if (inventoryItem && inventoryItem.stockQuantity > 0) {
                        let available = inventoryItem.stockQuantity;
                        let deducted = Math.min(available, qtyNeeded); // Lấy số CẦN HOẶC số CÓ SẴN (Cái nào nhỏ hơn).
                        inventoryItem.stockQuantity -= deducted;
                        qtyNeeded -= deducted;
                    }
                }
                
                // Thuật toán: Nếu đi thu lượm tất cả các kho mà hàng thực vẫn thiếu (Hết hoàn toàn, qtyNeeded > 0)
                // Ép Hệ thống ghi lại sổ nợ (Stock Nhập Âm) vào Kho đầu tiên của Chủ Doanh Nghiệp (Ví dụ Kho Tổng Miền Bắc)
                if (qtyNeeded > 0) {
                     let rootWh = appData.suppliers_inventory[0];
                     if(rootWh) {
                         let invObj = rootWh.inventory.find(inv => inv.productId === cartItem.productId);
                         if(invObj) invObj.stockQuantity -= qtyNeeded;
                         else rootWh.inventory.push({ productId: cartItem.productId, stockQuantity: -qtyNeeded });
                     }
                     warningMsg += `🔥 Toàn hệ thống đang cháy hàng món [${cartItem.name}]. Trừ cưỡng ép ${qtyNeeded} SP vào Quỹ nợ của Kho Cổng Chính!\n`;
                }
            });
        }

        // Cập nhật lại vào LocalStorage
        localStorage.setItem('novaPosData', JSON.stringify(appData));
        
        // Đẩy thông tin ra giao diện In Bill (printBillDiv)
        const printContainer = document.getElementById('printBillDiv');
        let billItemsHTML = '';
        cart.forEach(item => {
            billItemsHTML += `
                <div class="bill-item">
                    <span>${item.name} x${item.quantity}</span>
                    <span>${formatCurrency(item.price * item.quantity)}</span>
                </div>
            `;
        });

        printContainer.innerHTML = `
            <div class="bill-header">
                <h2>NOVAPOS</h2>
                <p>Khách hàng: Khách lẻ</p>
                <p>Ngày: ${new Date().toLocaleString()}</p>
                <p>Mã đơn: ${orderId}</p>
            </div>
            <div class="bill-divider"></div>
            <div class="bill-items">
                ${billItemsHTML}
            </div>
            <div class="bill-divider"></div>
            <div class="bill-total">
                <strong>TỔNG TIỀN:</strong>
                <strong>${formatCurrency(totalAmount)}</strong>
            </div>
            <div class="bill-footer">
                <p>Cảm ơn quý khách!</p>
            </div>
        `;

        // Kích hoạt cửa sổ thiết bị máy in (Lệnh Native của Trình duyệt)
        window.print();
        
        // Cảnh báo cháy hàng vào mặt Thu ngân nếu có phát sinh:
        if (warningMsg !== "") {
            alert('⚠️ BÁO CÁO CẢNH BÁO TỒN KHO ⚠️\n\n' + warningMsg);
        } else {
           alert('✅ Tạo hóa đơn thành công! Mã đơn: ' + orderId);
        }
        
        clearCart();
    };

    // Event listeners gốc
    document.getElementById('btnXoaGio').addEventListener('click', clearCart);
    document.getElementById('btnThanhToan').addEventListener('click', checkout);

    // Chạy render ban đầu
    initWarehouseDropdown(); // Load trật tự kho
    renderProducts(appData.products);
});
