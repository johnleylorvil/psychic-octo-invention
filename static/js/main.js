/**
 * Afèpanou - Main JavaScript
 * ===========================
 * Main application JavaScript with core functionality
 */

(function() {
    'use strict';

    // Global app object
    window.Afepanou = {
        config: {
            csrfToken: window.csrfToken || '',
            apiBaseUrl: '/api/v1/',
            debug: false
        },
        components: {},
        utils: {}
    };

    // Utility functions
    Afepanou.utils = {
        /**
         * Get CSRF token for AJAX requests
         */
        getCSRFToken: function() {
            return Afepanou.config.csrfToken;
        },

        /**
         * Show loading state on element
         */
        showLoading: function(element) {
            if (element) {
                element.classList.add('loading');
                element.disabled = true;
            }
        },

        /**
         * Hide loading state on element
         */
        hideLoading: function(element) {
            if (element) {
                element.classList.remove('loading');
                element.disabled = false;
            }
        },

        /**
         * Show toast notification
         */
        showToast: function(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} alert-dismissible fade show`;
            toast.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-info-circle me-2"></i>
                    <span>${message}</span>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const container = document.querySelector('.messages-container') || document.body;
            container.appendChild(toast);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 150);
                }
            }, 5000);
        },

        /**
         * Format price for display
         */
        formatPrice: function(price) {
            return parseFloat(price).toFixed(2) + ' HTG';
        },

        /**
         * Debounce function
         */
        debounce: function(func, wait, immediate) {
            let timeout;
            return function executedFunction() {
                const context = this;
                const args = arguments;
                const later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                const callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        },

        /**
         * Make AJAX request
         */
        ajax: function(options) {
            const defaults = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Afepanou.utils.getCSRFToken()
                }
            };

            const config = Object.assign(defaults, options);

            return fetch(config.url, config)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('AJAX Error:', error);
                    throw error;
                });
        }
    };

    // Cart component
    Afepanou.components.Cart = {
        init: function() {
            this.bindEvents();
            this.updateCartCount();
        },

        bindEvents: function() {
            // Add to cart buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.btn-add-to-cart') || e.target.closest('.btn-add-to-cart')) {
                    e.preventDefault();
                    const button = e.target.matches('.btn-add-to-cart') ? e.target : e.target.closest('.btn-add-to-cart');
                    this.addToCart(button);
                }
            });

            // Remove from cart buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.remove-item') || e.target.closest('.remove-item')) {
                    e.preventDefault();
                    const button = e.target.matches('.remove-item') ? e.target : e.target.closest('.remove-item');
                    this.removeFromCart(button);
                }
            });

            // Quantity controls
            document.addEventListener('click', (e) => {
                if (e.target.matches('.quantity-increase')) {
                    this.increaseQuantity(e.target);
                } else if (e.target.matches('.quantity-decrease')) {
                    this.decreaseQuantity(e.target);
                }
            });
        },

        addToCart: function(button) {
            const form = button.closest('form') || button.closest('.add-to-cart-form');
            const productId = form ? form.dataset.productId : button.dataset.productId;
            const quantityInput = form ? form.querySelector('input[name="quantity"]') : null;
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

            if (!productId) {
                Afepanou.utils.showToast('Erreur: Produit non trouvé', 'error');
                return;
            }

            Afepanou.utils.showLoading(button);

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);
            formData.append('csrfmiddlewaretoken', Afepanou.utils.getCSRFToken());

            fetch('/ajax/add-to-cart/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Afepanou.utils.showToast(data.message, 'success');
                    this.updateCartCount(data.cart_count);
                    this.updateCartTotal(data.cart_total);
                } else {
                    Afepanou.utils.showToast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Afepanou.utils.showToast('Erreur lors de l\'ajout au panier', 'error');
            })
            .finally(() => {
                Afepanou.utils.hideLoading(button);
            });
        },

        removeFromCart: function(button) {
            const itemId = button.dataset.itemId;
            
            if (!itemId) return;

            Afepanou.utils.showLoading(button);

            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('csrfmiddlewaretoken', Afepanou.utils.getCSRFToken());

            fetch('/ajax/remove-from-cart/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const cartItem = button.closest('.cart-item');
                    if (cartItem) {
                        cartItem.remove();
                    }
                    this.updateCartCount(data.cart_count);
                    this.updateCartTotal(data.cart_total);
                    Afepanou.utils.showToast('Produit retiré du panier', 'success');
                } else {
                    Afepanou.utils.showToast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Afepanou.utils.showToast('Erreur lors de la suppression', 'error');
            })
            .finally(() => {
                Afepanou.utils.hideLoading(button);
            });
        },

        increaseQuantity: function(button) {
            const input = button.parentNode.querySelector('.quantity-input');
            if (input) {
                const current = parseInt(input.value);
                const max = parseInt(input.max);
                if (current < max) {
                    input.value = current + 1;
                }
            }
        },

        decreaseQuantity: function(button) {
            const input = button.parentNode.querySelector('.quantity-input');
            if (input) {
                const current = parseInt(input.value);
                const min = parseInt(input.min) || 1;
                if (current > min) {
                    input.value = current - 1;
                }
            }
        },

        updateCartCount: function(count) {
            const cartCountElements = document.querySelectorAll('.cart-count, #cart-count');
            if (count !== undefined) {
                cartCountElements.forEach(el => el.textContent = count);
            }
        },

        updateCartTotal: function(total) {
            const cartTotalElements = document.querySelectorAll('.cart-total, .total-amount');
            if (total !== undefined) {
                cartTotalElements.forEach(el => {
                    el.textContent = Afepanou.utils.formatPrice(total);
                });
            }
        }
    };

    // Search component
    Afepanou.components.Search = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            const searchInputs = document.querySelectorAll('.search-input');
            searchInputs.forEach(input => {
                input.addEventListener('input', 
                    Afepanou.utils.debounce(this.handleSearchInput.bind(this), 300)
                );
                input.addEventListener('focus', this.showSuggestions.bind(this));
                input.addEventListener('blur', this.hideSuggestions.bind(this));
            });
        },

        handleSearchInput: function(event) {
            const input = event.target;
            const query = input.value.trim();
            
            if (query.length >= 2) {
                this.fetchSuggestions(query, input);
            } else {
                this.hideSuggestions();
            }
        },

        fetchSuggestions: function(query, input) {
            fetch(`/ajax/search-suggestions/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        this.displaySuggestions(data.suggestions, input);
                    } else {
                        this.hideSuggestions();
                    }
                })
                .catch(error => {
                    console.error('Search suggestions error:', error);
                });
        },

        displaySuggestions: function(suggestions, input) {
            const container = input.closest('.search-container');
            let suggestionsEl = container.querySelector('.search-suggestions');
            
            if (!suggestionsEl) {
                suggestionsEl = document.createElement('div');
                suggestionsEl.className = 'search-suggestions';
                container.appendChild(suggestionsEl);
            }

            let html = '<div class="suggestions-header"><h6>Suggestions</h6></div><div class="suggestions-list">';
            suggestions.forEach(suggestion => {
                html += `<a href="/search/?q=${encodeURIComponent(suggestion.name)}" class="suggestion-item d-block p-2">`;
                html += `<i class="fas fa-search me-2"></i>${suggestion.name}`;
                html += '</a>';
            });
            html += '</div>';

            suggestionsEl.innerHTML = html;
            suggestionsEl.style.display = 'block';
        },

        showSuggestions: function() {
            // Show suggestions if they exist
        },

        hideSuggestions: function() {
            setTimeout(() => {
                const suggestions = document.querySelectorAll('.search-suggestions');
                suggestions.forEach(el => el.style.display = 'none');
            }, 200);
        }
    };

    // Wishlist component
    Afepanou.components.Wishlist = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('.btn-wishlist') || e.target.closest('.btn-wishlist')) {
                    e.preventDefault();
                    const button = e.target.matches('.btn-wishlist') ? e.target : e.target.closest('.btn-wishlist');
                    this.toggleWishlist(button);
                }
            });
        },

        toggleWishlist: function(button) {
            const productId = button.dataset.productId;
            
            if (!productId) return;

            Afepanou.utils.showLoading(button);

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('csrfmiddlewaretoken', Afepanou.utils.getCSRFToken());

            fetch('/ajax/toggle-wishlist/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const icon = button.querySelector('i');
                    if (data.added) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        Afepanou.utils.showToast('Ajouté aux favoris', 'success');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        Afepanou.utils.showToast('Retiré des favoris', 'info');
                    }
                } else {
                    Afepanou.utils.showToast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Afepanou.utils.showToast('Erreur lors de la mise à jour', 'error');
            })
            .finally(() => {
                Afepanou.utils.hideLoading(button);
            });
        }
    };

    // Product Quick View component
    Afepanou.components.QuickView = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('.quick-view-btn') || e.target.closest('.quick-view-btn')) {
                    e.preventDefault();
                    const button = e.target.matches('.quick-view-btn') ? e.target : e.target.closest('.quick-view-btn');
                    this.showQuickView(button);
                }
            });
        },

        showQuickView: function(button) {
            const productId = button.dataset.productId;
            
            if (!productId) return;

            Afepanou.utils.showLoading(button);

            fetch(`/ajax/product-quick-view/${productId}/`)
                .then(response => response.text())
                .then(html => {
                    // Create or update modal
                    let modal = document.getElementById('productQuickView');
                    if (!modal) {
                        modal = document.createElement('div');
                        modal.innerHTML = html;
                        document.body.appendChild(modal.firstElementChild);
                    } else {
                        modal.innerHTML = html;
                    }

                    // Show modal
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                })
                .catch(error => {
                    console.error('Error:', error);
                    Afepanou.utils.showToast('Erreur lors du chargement', 'error');
                })
                .finally(() => {
                    Afepanou.utils.hideLoading(button);
                });
        }
    };

    // Back to top component
    Afepanou.components.BackToTop = {
        init: function() {
            this.button = document.getElementById('backToTop');
            if (this.button) {
                this.bindEvents();
            }
        },

        bindEvents: function() {
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 300) {
                    this.button.classList.add('visible');
                } else {
                    this.button.classList.remove('visible');
                }
            });

            this.button.addEventListener('click', (e) => {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    };

    // Form validation component
    Afepanou.components.FormValidation = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', this.handleFormSubmit.bind(this));
            });
        },

        handleFormSubmit: function(event) {
            const form = event.target;
            const submitButton = form.querySelector('button[type="submit"]');
            
            if (submitButton) {
                Afepanou.utils.showLoading(submitButton);
            }

            // Let the form submit naturally, loading state will be cleared on page load
        }
    };

    // Mobile menu component
    Afepanou.components.MobileMenu = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            // Submenu toggles
            document.addEventListener('click', (e) => {
                if (e.target.matches('.submenu-toggle')) {
                    e.preventDefault();
                    const submenu = e.target.nextElementSibling;
                    if (submenu) {
                        submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
                        const arrow = e.target.querySelector('.submenu-arrow');
                        if (arrow) {
                            arrow.classList.toggle('fa-chevron-down');
                            arrow.classList.toggle('fa-chevron-up');
                        }
                    }
                }
            });
        }
    };

    // Image gallery component for product detail
    Afepanou.components.ImageGallery = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            const thumbnails = document.querySelectorAll('.thumbnail-image');
            thumbnails.forEach(thumbnail => {
                thumbnail.addEventListener('click', this.handleThumbnailClick.bind(this));
            });
        },

        handleThumbnailClick: function(event) {
            const thumbnail = event.target;
            const mainImageSrc = thumbnail.dataset.mainImage;
            const mainImage = document.getElementById('mainProductImage') || 
                             document.getElementById('quickViewMainImage');
            
            if (mainImage && mainImageSrc) {
                mainImage.src = mainImageSrc;
                
                // Update active thumbnail
                document.querySelectorAll('.thumbnail-image').forEach(t => {
                    t.classList.remove('active');
                });
                thumbnail.classList.add('active');
            }
        }
    };

    // Initialize all components when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        try {
            // Initialize all components
            Object.keys(Afepanou.components).forEach(componentName => {
                const component = Afepanou.components[componentName];
                if (component && typeof component.init === 'function') {
                    component.init();
                }
            });

            console.log('Afèpanou app initialized successfully');
        } catch (error) {
            console.error('Error initializing Afèpanou app:', error);
        }
    });

    // Handle page unload
    window.addEventListener('beforeunload', function() {
        // Clean up any ongoing operations
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => {
            Afepanou.utils.hideLoading(el);
        });
    });

})();