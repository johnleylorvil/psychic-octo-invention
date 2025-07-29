// store.js - Afèpanou Marketplace Store Logic
// Compatible avec Django + MonCash

class AfepanouStore {
    constructor() {
        this.cart = {
            items: [],
            total: 0,
            totalItems: 0
        };
        this.currentStore = null;
        this.csrfToken = this.getCookie('csrftoken');

        this.init();
    }

    init() {
        this.detectStore();
        this.bindEvents();
        this.loadCart();
        this.initHeroSlideshow();
        this.setupScrollReveal();
    }

    // ===== UTILS =====
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async fetchJSON(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            }
        });
        return await response.json();
    }

    // ===== STORE NAVIGATION =====
    detectStore() {
        const path = window.location.pathname;
        const match = path.match(/\/store\/([^\/]+)\//);
        if (match) {
            this.currentStore = match[1];
            this.updateHeroBackground(this.currentStore);
        }
    }

    updateHeroBackground(store) {
        const hero = document.querySelector('.hero');
        const backgrounds = {
            artisanats: '/static/images/hero-artisanat.jpg',
            agriculture: '/static/images/hero-agriculture.jpg',
            services: '/static/images/hero-services.jpg'
        };
        const bg = backgrounds[store] || '/static/images/hero-default.jpg';
        hero.style.backgroundImage = `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url(${bg})`;
    }

    // ===== SLIDESHOW HERO =====
    initHeroSlideshow() {
        const slides = document.querySelectorAll('.slide');
        if (slides.length === 0) return;

        let current = 0;
        const showSlide = (index) => {
            slides.forEach(s => s.classList.remove('active'));
            slides[index].classList.add('active');
        };

        setInterval(() => {
            current = (current + 1) % slides.length;
            showSlide(current);
        }, 5000);
    }

    // ===== SCROLL REVEAL ANIMATIONS =====
    setupScrollReveal() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right').forEach(el => {
            observer.observe(el);
        });
    }

    // ===== MODALES (Produit, Checkout) =====
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    // ===== PANIER =====
    async loadCart() {
        try {
            const data = await this.fetchJSON('/store/' + this.currentStore + '/', { method: 'GET' });
            this.updateCartUI(data);
        } catch (err) {
            console.error('Erreur chargement panier', err);
        }
    }

    async addToCart(productId, quantity = 1) {
        const response = await this.fetchJSON('/store/' + this.currentStore + '/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'add_to_cart',
                product_id: productId,
                quantity: quantity
            })
        });

        if (response.error) {
            this.showError(response.error);
        } else {
            this.cart = response;
            this.updateCartUI();
            this.showSuccess('Produit ajouté au panier !');
        }
    }

    async updateCartItem(itemId, quantity) {
        if (quantity < 1) return this.removeFromCart(itemId);

        const response = await this.fetchJSON('/store/' + this.currentStore + '/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'update_cart',
                item_id: itemId,
                quantity: quantity
            })
        });

        if (!response.error) {
            this.cart = response;
            this.updateCartUI();
        }
    }

    async removeFromCart(itemId) {
        const response = await this.fetchJSON('/store/' + this.currentStore + '/', {
            method: 'POST',
            body: JSON.stringify({
                action: 'remove_from_cart',
                item_id: itemId
            })
        });

        if (!response.error) {
            this.cart = response;
            this.updateCartUI();
        }
    }

    updateCartUI(data = null) {
        const cartBadge = document.querySelector('.cart-badge');
        const cartItemsList = document.getElementById('cart-items-list');
        const cartTotal = document.getElementById('cart-total-amount');

        if (data) {
            this.cart = data;
        }

        // Mise à jour badge
        if (cartBadge) {
            cartBadge.textContent = this.cart.total_items || 0;
        }

        // Mise à jour liste
        if (cartItemsList) {
            cartItemsList.innerHTML = this.cart.items.length === 0
                ? '<p>Votre panier est vide.</p>'
                : this.cart.items.map(item => this.renderCartItem(item)).join('');
        }

        // Mise à jour total
        if (cartTotal) {
            cartTotal.textContent = `${this.cart.total_amount || 0} HTG`;
        }
    }

    renderCartItem(item) {
        return `
            <div class="cart-item" data-item-id="${item.id}">
                <img src="${item.image_url}" alt="${item.name}" width="60">
                <div class="cart-item-info">
                    <strong>${item.name}</strong>
                    <div class="quantity-control">
                        <button class="qty-btn" onclick="afepanouStore.updateCartItem(${item.id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn" onclick="afepanouStore.updateCartItem(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <div class="cart-item-price">${item.total_price} HTG</div>
                <button class="remove-btn" onclick="afepanouStore.removeFromCart(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
    }

    // ===== PRODUIT DÉTAILLÉ =====
    async showProduct(productId) {
        try {
            const response = await this.fetchJSON(`/store/${this.currentStore}/?product_id=${productId}`);
            const product = response.product;

            document.getElementById('product-name').textContent = product.name;
            document.getElementById('product-description').textContent = product.description;
            document.getElementById('product-price').textContent = `${product.current_price} HTG`;

            const mainImage = document.getElementById('main-image');
            mainImage.src = product.image_url;
            mainImage.alt = product.name;

            const thumbnails = document.getElementById('thumbnails');
            thumbnails.innerHTML = product.images.map(img => `
                <img src="${img.image_url}" alt="Variante" onclick="this.parentNode.parentNode.querySelector('#main-image').src = '${img.image_url}'" />
            `).join('');

            document.getElementById('quantity').value = 1;
            document.querySelector('.add-to-cart-modal').onclick = () => {
                const qty = parseInt(document.getElementById('quantity').value);
                this.addToCart(productId, qty);
                this.closeModal('product-modal');
            };

            this.showModal('product-modal');
        } catch (err) {
            this.showError('Produit introuvable.');
        }
    }

    changeQuantity(delta) {
        const input = document.getElementById('quantity');
        let value = parseInt(input.value) + delta;
        input.value = Math.max(1, value);
    }

    // ===== CHECKOUT =====
    async processCheckout() {
        const form = document.getElementById('checkout-form');
        const data = new FormData(form);

        const payload = {
            action: 'checkout',
            email: data.get('email'),
            phone: data.get('phone'),
            address: data.get('address'),
            city: data.get('city'),
            country: data.get('country'),
            subtotal: this.cart.total_amount,
            total_amount: this.cart.total_amount,
            shipping_cost: 0,
            tax_amount: 0
        };

        try {
            const response = await this.fetchJSON(`/store/${this.currentStore}/`, {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (response.error) {
                this.showError(response.error);
            } else {
                // Lancer le paiement MonCash
                this.processMonCashPayment(response.order_number);
            }
        } catch (err) {
            this.showError('Erreur lors du checkout.');
        }
    }

    async processMonCashPayment(orderNumber) {
        try {
            const response = await this.fetchJSON(`/store/${this.currentStore}/`, {
                method: 'POST',
                body: JSON.stringify({
                    action: 'moncash_payment',
                    order_number: orderNumber
                })
            });

            if (response.payment_url) {
                window.location.href = response.payment_url;
            } else {
                this.showError('Échec de la création du paiement.');
            }
        } catch (err) {
            this.showError('Impossible de se connecter à MonCash.');
        }
    }

    // ===== UI HELPERS =====
    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        let toast = document.getElementById('afepanou-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'afepanou-toast';
            toast.style.cssText = `
                position: fixed; top: 20px; right: 20px; padding: 12px 20px;
                border-radius: var(--radius-lg); color: white; z-index: 9999;
                font-size: var(--text-base); max-width: 300px; text-align: center;
                box-shadow: var(--shadow-strong);
            `;
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.style.background = type === 'success' ? 'var(--forest-green)' : 'var(--primary-orange)';
        toast.style.display = 'block';

        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }

    // ===== ÉVÉNEMENTS =====
    bindEvents() {
        // Navigation stores
        document.querySelectorAll('[data-category]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                window.location.href = `/store/${category}/`;
            });
        });

        // Panier
        document.querySelector('.action-btn .fa-shopping-cart')?.parentElement.addEventListener('click', () => {
            this.showModal('cart-sidebar');
        });

        // Fermeture modales
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const modal = e.target.closest('.modal, .cart-sidebar');
                if (modal) this.closeModal(modal.id);
            });
        });

        // Checkout
        const checkoutForm = document.getElementById('checkout-form');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.processCheckout();
            });
        }

        // Esc pour fermer les modales
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal('product-modal');
                this.closeModal('checkout-modal');
                this.closeModal('cart-sidebar');
            }
        });
    }
}

// Initialisation globale
document.addEventListener('DOMContentLoaded', () => {
    window.afepanouStore = new AfepanouStore();
});

// Fonctions globales accessibles depuis HTML
function showProduct(id) {
    window.afepanouStore.showProduct(id);
}

function changeQuantity(delta) {
    window.afepanouStore.changeQuantity(delta);
}

function closeModal(id) {
    window.afepanouStore.closeModal(id);
}