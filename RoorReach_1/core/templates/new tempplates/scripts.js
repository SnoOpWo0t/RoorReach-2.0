// scripts.js
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Toggle
    const mobileMenu = document.getElementById('mobile-menu');
    const navLinks = document.getElementById('nav-links');

    if (mobileMenu && navLinks) {
        mobileMenu.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Toast Notification Function
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Cart Management (Placeholder)
    function updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('rootreachCart')) || [];
        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
            cartCount.textContent = cart.length;
            cartCount.style.display = cart.length > 0 ? 'inline' : 'none';
        }
    }

    function addToCart(productId) {
        let cart = JSON.parse(localStorage.getItem('rootreachCart')) || [];
        const existingItem = cart.find(item => item.id === productId);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ id: productId, quantity: 1 });
        }
        localStorage.setItem('rootreachCart', JSON.stringify(cart));
        updateCartCount();
        showToast('Added to cart!');
    }

    // Expose functions to global scope if needed
    window.showToast = showToast;
    window.addToCart = addToCart;
    window.updateCartCount = updateCartCount;

    // Initial cart update
    updateCartCount();
});

// Toast CSS (to be added to styles.css if not present)
const toastStyles = `
    .toast {
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 1000;
    }

    .toast-success {
        background-color: var(--primary);
    }

    .toast-error {
        background-color: #f44336;
    }

    .toast.show {
        opacity: 1;
    }
`;

// Note: Add this to styles.css manually if not already included
console.log("Add the following toast styles to styles.css if not present:\n", toastStyles);