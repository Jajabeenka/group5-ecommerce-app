/* JavaScript / Logic */
const socket = io();

socket.on("connect", () => {
    console.log("Connected:", socket.id);
});

socket.on("payment_success", (data) => {
    console.log("Received payment_success:", data);
    showSuccessModal();
});


const products = [
    { id: 1, name: "Espress-yo Self", image:"../static/images/espresso.jpg" ,price: 180 },
    { id: 2, name: "The Night Shift", image:"../static/images/americano.jpg" ,price: 185 },
    { id: 3, name: "Caramel Macchiato", image:"../static/images/caramel.jpg" ,price: 195 },
    { id: 4, name: "Café Diem", image:"../static/images/cafediem.jpg" ,price: 190 },
    { id: 5, name: "Out of Office Latte", image:"../static/images/outofoffice.jpg" ,price: 205 },
    { id: 6, name: "Spanish Latte", image:"../static/images/spanish.jpg",price: 200 }
];

// Cart State
const cart = {
    1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0
};

// Render products into grid
function renderProducts() {
    const grid = document.getElementById('productGrid');
    grid.innerHTML = '';

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="product-image">
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-price">₱${product.price.toFixed(2)}</div>
            </div>
            <div class="counter-container">
                <button class="btn-count" onclick="updateQty(${product.id}, -1)">−</button>
                <input type="number" class="qty-input" id="qty-${product.id}" value="${cart[product.id]}" min="0" onchange="manualInput(${product.id}, this.value)">
                <button class="btn-count" onclick="updateQty(${product.id}, 1)">+</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Update quantity via buttons
function updateQty(productId, change) {
    let newQty = cart[productId] + change;
    if (newQty < 0) newQty = 0; 
    
    cart[productId] = newQty;
    document.getElementById(`qty-${productId}`).value = newQty;
    
    updateSidebar();
}

// Update quantity via direct input
function manualInput(productId, value) {
    let newQty = parseInt(value);
    if (isNaN(newQty) || newQty < 0) newQty = 0;
    
    cart[productId] = newQty;
    document.getElementById(`qty-${productId}`).value = newQty;
    
    updateSidebar();
}

// Calculate and build the sidebar contents
function updateSidebar() {
    let totalItems = 0;
    let totalAmount = 0;
    const cartList = document.getElementById('cartItemsList');
    
    // Clear current list
    cartList.innerHTML = '';

    products.forEach(product => {
        const qty = cart[product.id];
        if (qty > 0) {
            totalItems += qty;
            const itemTotal = qty * product.price;
            totalAmount += itemTotal;

            // Build item line for sidebar
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.innerHTML = `
                <span class="cart-item-name">${product.name}</span>
                <span class="cart-item-qty">x${qty}</span>
                <span class="cart-item-price">₱${itemTotal.toFixed(2)}</span>
            `;
            cartList.appendChild(itemDiv);
        }
    });

    // Show empty message if nothing added
    if (totalItems === 0) {
        cartList.innerHTML = `<div class="empty-cart-msg">Your cart is empty</div>`;
    }

    document.getElementById('totalItems').innerText = totalItems;
    document.getElementById('totalAmount').innerText = '₱' + totalAmount.toFixed(2);
}

async function checkout() {
    const totalItems = document.getElementById('totalItems').innerText;
    const totalAmount = document.getElementById('totalAmount').innerText;

    if (totalItems === "0") {
        alert("Your cart is empty! Add some coffee first.");
        return;
    }

    const response = await fetch("/generate_qr", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            totalItems: parseInt(totalItems),
            totalAmount: totalAmount.replace("$", "")
        })
    });

    const data = await response.json();

    // Display QR image
    document.getElementById("qrImage").src =
        "data:image/png;base64," + data.qr;
    
    // Populate order totals inside modal
    document.getElementById('modalTotalItems').innerText = totalItems;
    document.getElementById('modalTotalAmount').innerText = totalAmount;

    // Display modal
    const modal = document.getElementById('checkoutModal');
    modal.classList.add('active');
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('checkoutModal');
    modal.classList.remove('active');
}

// Complete Order & Reset Cart
function finishOrder() {
    alert("Thank you for your payment! Your coffee order is being prepared.");
    
    // Reset cart state
    for (let key in cart) cart[key] = 0;
    renderProducts();
    updateSidebar();
    closeModal();
}

function showSuccessModal() {

    closeModal();
    const totalItems = document.getElementById('totalItems').innerText;
    const totalAmount = document.getElementById('totalAmount').innerText;
    document.getElementById("successModal")
        .classList.add("active");
}

function closeSuccessModal() {
    document.getElementById("successModal")
        .classList.remove("active");

     for (let key in cart) {
        cart[key] = 0;
    }

    renderProducts();
    updateSidebar();

}

// Close modal when clicking outside the content box
window.addEventListener('click', (event) => {
    const modal = document.getElementById('checkoutModal');
    if (event.target === modal) {
        closeModal();
    }
});

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    renderProducts();
    updateSidebar();
});