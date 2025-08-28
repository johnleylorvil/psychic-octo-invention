/**
 * ========================================
 * AFÈPANOU MARKETPLACE - MAIN JAVASCRIPT
 * Modern Interactive Components for Haitian E-commerce
 * ========================================
 */

(function() {
    'use strict';

    // Global configuration from Django template
    const config = window.AfepanouConfig || {};

    // Main application object
    window.Afepanou = {
        config: {
            csrfToken: config.csrfToken || '',
            baseUrl: config.baseUrl || '/',
            staticUrl: config.staticUrl || '/static/',
            mediaUrl: config.mediaUrl || '/media/',
            language: config.language || 'fr-HT',
            currency: config.currency || 'HTG',
            user: config.user || { isAuthenticated: false, isSeller: false },
            urls: config.urls || {},
            debug: config.debug || false
        },
        components: {},
        utils: {},
        state: {
            cartCount: 0,
            wishlistCount: 0,
            isOnline: navigator.onLine
        }
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
         * Make AJAX request with modern fetch API
         */
        ajax: function(options) {
            const defaults = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Afepanou.utils.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
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
                    if (Afepanou.config.debug) {
                        Afepanou.utils.showToast('Erreur de connexion', 'danger');
                    }
                    throw error;
                });
        },

        /**
         * Format currency for Haiti
         */
        formatCurrency: function(amount) {
            return new Intl.NumberFormat('fr-HT', {
                style: 'currency',
                currency: 'HTG',
                minimumFractionDigits: 2
            }).format(amount);
        },

        /**
         * Storage utilities
         */
        storage: {
            get: function(key) {
                try {
                    return JSON.parse(localStorage.getItem(`afepanou_${key}`));
                } catch (e) {
                    return null;
                }
            },
            set: function(key, value) {
                try {
                    localStorage.setItem(`afepanou_${key}`, JSON.stringify(value));
                } catch (e) {
                    console.warn('Storage not available');
                }
            },
            remove: function(key) {
                try {
                    localStorage.removeItem(`afepanou_${key}`);
                } catch (e) {
                    console.warn('Storage not available');
                }
            }
        },

        /**
         * Animate element
         */
        animate: function(element, animation, duration = 500) {
            return new Promise((resolve) => {
                element.style.animation = `${animation} ${duration}ms ease-in-out`;
                element.addEventListener('animationend', function handler() {
                    element.removeEventListener('animationend', handler);
                    element.style.animation = '';
                    resolve();
                });
            });
        },

        /**
         * Throttle function
         */
        throttle: function(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },

        /**
         * Check if user is on mobile
         */
        isMobile: function() {
            return window.innerWidth < 768;
        },

        /**
         * Generate unique ID
         */
        generateId: function() {
            return 'afepanou_' + Math.random().toString(36).substr(2, 9);
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

    // Enhanced Search component with voice recognition
    Afepanou.components.Search = {
        init: function() {
            this.bindEvents();
            this.initVoiceSearch();
            this.initQuickFilters();
            this.loadSearchHistory();
        },

        bindEvents: function() {
            const searchInputs = document.querySelectorAll('.search-input');
            searchInputs.forEach(input => {
                input.addEventListener('input', 
                    Afepanou.utils.debounce(this.handleSearchInput.bind(this), 300)
                );
                input.addEventListener('focus', this.showSuggestions.bind(this));
                input.addEventListener('blur', this.hideSuggestions.bind(this));
                input.addEventListener('keydown', this.handleKeydown.bind(this));
            });

            // Quick filter buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.quick-filter-btn')) {
                    e.preventDefault();
                    this.applyQuickFilter(e.target);
                }
            });

            // Popular search tags
            document.addEventListener('click', (e) => {
                if (e.target.matches('.popular-search-tag')) {
                    e.preventDefault();
                    const query = e.target.dataset.query;
                    this.performSearch(query);
                }
            });

            // Advanced search form
            const advancedForm = document.getElementById('advanced-search-form');
            if (advancedForm) {
                advancedForm.addEventListener('submit', this.handleAdvancedSearch.bind(this));
            }
        },

        handleSearchInput: function(event) {
            const input = event.target;
            const query = input.value.trim();
            
            if (query.length >= 2) {
                this.showLoadingState();
                this.fetchSuggestions(query, input);
            } else if (query.length === 0) {
                this.showPopularSearches();
            } else {
                this.hideSuggestions();
            }
        },

        handleKeydown: function(event) {
            const dropdown = document.getElementById('search-suggestions');
            if (!dropdown || dropdown.classList.contains('d-none')) return;

            const items = dropdown.querySelectorAll('.suggestion-item, .popular-search-tag');
            let activeIndex = Array.from(items).findIndex(item => item.classList.contains('active'));

            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    activeIndex = (activeIndex + 1) % items.length;
                    this.highlightSuggestion(items, activeIndex);
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    activeIndex = activeIndex <= 0 ? items.length - 1 : activeIndex - 1;
                    this.highlightSuggestion(items, activeIndex);
                    break;
                case 'Enter':
                    event.preventDefault();
                    if (activeIndex >= 0) {
                        const activeItem = items[activeIndex];
                        if (activeItem.dataset.query) {
                            this.performSearch(activeItem.dataset.query);
                        } else {
                            activeItem.click();
                        }
                    }
                    break;
                case 'Escape':
                    this.hideSuggestions();
                    break;
            }
        },

        highlightSuggestion: function(items, activeIndex) {
            items.forEach((item, index) => {
                item.classList.toggle('active', index === activeIndex);
            });
        },

        fetchSuggestions: function(query, input) {
            const url = Afepanou.config.urls.ajaxSearchAutocomplete || '/ajax/recherche/';
            
            fetch(`${url}?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    this.hideLoadingState();
                    if (data.success && data.suggestions && data.suggestions.length > 0) {
                        this.displaySuggestions(data.suggestions, data.products || [], input);
                    } else {
                        this.showNoResults();
                    }
                })
                .catch(error => {
                    console.error('Search suggestions error:', error);
                    this.hideLoadingState();
                    this.showNoResults();
                });
        },

        displaySuggestions: function(suggestions, products, input) {
            const dropdown = document.getElementById('search-suggestions');
            const suggestionsList = document.getElementById('suggestions-list');
            
            if (!dropdown || !suggestionsList) return;

            let html = '';

            // Product suggestions
            if (products.length > 0) {
                html += '<div class="suggestions-section">';
                html += '<h6 class="suggestion-header text-muted mb-2"><i class="fas fa-cube me-2"></i>Produits</h6>';
                products.slice(0, 5).forEach(product => {
                    html += `
                        <a href="/produit/${product.slug}/" class="suggestion-item d-flex align-items-center p-2 text-decoration-none">
                            <img src="${product.image || '/static/images/product-placeholder.jpg'}" 
                                 alt="${product.name}" class="suggestion-image me-3" width="40" height="40">
                            <div class="flex-grow-1">
                                <div class="suggestion-name">${product.name}</div>
                                <small class="text-muted">${Afepanou.utils.formatCurrency(product.price)}</small>
                            </div>
                        </a>
                    `;
                });
                html += '</div>';
            }

            // Search term suggestions
            if (suggestions.length > 0) {
                html += '<div class="suggestions-section border-top pt-2">';
                html += '<h6 class="suggestion-header text-muted mb-2"><i class="fas fa-search me-2"></i>Suggestions</h6>';
                suggestions.forEach(suggestion => {
                    html += `
                        <button type="button" class="suggestion-item w-100 text-start border-0 bg-transparent p-2" 
                                data-query="${suggestion}">
                            <i class="fas fa-search text-muted me-2"></i>
                            ${suggestion}
                        </button>
                    `;
                });
                html += '</div>';
            }

            suggestionsList.innerHTML = html;
            dropdown.classList.remove('d-none');

            // Add click handlers for dynamic elements
            suggestionsList.addEventListener('click', (e) => {
                if (e.target.dataset.query) {
                    this.performSearch(e.target.dataset.query);
                }
            });
        },

        showLoadingState: function() {
            const loading = document.getElementById('suggestions-loading');
            const list = document.getElementById('suggestions-list');
            const empty = document.getElementById('suggestions-empty');
            const popular = document.getElementById('popular-searches');
            
            if (loading) loading.classList.remove('d-none');
            if (list) list.innerHTML = '';
            if (empty) empty.classList.add('d-none');
            if (popular) popular.classList.add('d-none');
            
            document.getElementById('search-suggestions').classList.remove('d-none');
        },

        hideLoadingState: function() {
            const loading = document.getElementById('suggestions-loading');
            if (loading) loading.classList.add('d-none');
        },

        showNoResults: function() {
            const empty = document.getElementById('suggestions-empty');
            const popular = document.getElementById('popular-searches');
            
            if (empty) empty.classList.remove('d-none');
            if (popular) popular.classList.remove('d-none');
        },

        showPopularSearches: function() {
            const popular = document.getElementById('popular-searches');
            const list = document.getElementById('suggestions-list');
            
            if (popular) popular.classList.remove('d-none');
            if (list) list.innerHTML = '';
            
            document.getElementById('search-suggestions').classList.remove('d-none');
        },

        hideSuggestions: function() {
            setTimeout(() => {
                const dropdown = document.getElementById('search-suggestions');
                if (dropdown) dropdown.classList.add('d-none');
            }, 200);
        },

        performSearch: function(query) {
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.value = query;
            }
            
            // Save to search history
            this.saveSearchHistory(query);
            
            // Submit search form or navigate
            const searchForm = document.getElementById('search-form');
            if (searchForm) {
                searchForm.submit();
            } else {
                window.location.href = `${Afepanou.config.baseUrl}recherche/?query=${encodeURIComponent(query)}`;
            }
        },

        applyQuickFilter: function(button) {
            const query = button.dataset.query;
            this.performSearch(query);
        },

        saveSearchHistory: function(query) {
            let history = Afepanou.utils.storage.get('search_history') || [];
            
            // Remove existing occurrence
            history = history.filter(item => item.toLowerCase() !== query.toLowerCase());
            
            // Add to beginning
            history.unshift(query);
            
            // Keep only last 10 searches
            history = history.slice(0, 10);
            
            Afepanou.utils.storage.set('search_history', history);
        },

        loadSearchHistory: function() {
            const history = Afepanou.utils.storage.get('search_history') || [];
            // Use history to populate search suggestions when input is focused
        },

        initVoiceSearch: function() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                return; // Voice search not supported
            }

            const voiceBtn = document.getElementById('voice-search-btn');
            const voiceIcon = document.getElementById('voice-search-icon');
            const voiceContainer = document.getElementById('voice-search-container');

            if (!voiceBtn) return;

            // Show voice search button
            voiceContainer.classList.remove('d-none');

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();

            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'fr-FR'; // French for Haiti

            voiceBtn.addEventListener('click', () => {
                recognition.start();
                voiceIcon.className = 'fas fa-microphone-slash text-danger';
                voiceBtn.title = 'Arrêter l\'écoute';
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.performSearch(transcript);
            };

            recognition.onend = () => {
                voiceIcon.className = 'fas fa-microphone text-muted';
                voiceBtn.title = 'Recherche vocale';
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                Afepanou.utils.showToast('Erreur de reconnaissance vocale', 'warning');
                voiceIcon.className = 'fas fa-microphone text-muted';
            };
        },

        initQuickFilters: function() {
            // Quick filters are handled in bindEvents
        },

        handleAdvancedSearch: function(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            
            // Build query string
            const params = new URLSearchParams();
            for (let [key, value] of formData.entries()) {
                if (value.trim()) {
                    params.append(key, value);
                }
            }
            
            // Navigate to search results
            window.location.href = `${Afepanou.config.baseUrl}recherche/?${params.toString()}`;
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