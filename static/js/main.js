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

    // Cart Management Component
    Afepanou.components.Cart = {
        init: function() {
            this.bindEvents();
            this.updateCartUI();
        },

        bindEvents: function() {
            // Add to cart buttons
            document.addEventListener('click', (e) => {
                if (e.target.matches('.add-to-cart-btn') || e.target.closest('.add-to-cart-btn')) {
                    this.handleAddToCart(e);
                }
            });

            // Remove from cart
            document.addEventListener('click', (e) => {
                if (e.target.matches('.remove-from-cart') || e.target.closest('.remove-from-cart')) {
                    this.handleRemoveFromCart(e);
                }
            });

            // Update quantity
            document.addEventListener('change', (e) => {
                if (e.target.matches('.cart-quantity-input')) {
                    this.handleQuantityChange(e);
                }
            });

            // Cart dropdown toggle
            const cartTrigger = document.querySelector('.cart-trigger');
            if (cartTrigger) {
                cartTrigger.addEventListener('mouseenter', this.showCartDropdown.bind(this));
                cartTrigger.addEventListener('mouseleave', this.hideCartDropdownDelay.bind(this));
            }
        },

        handleAddToCart: async function(event) {
            event.preventDefault();
            const button = event.target.closest('.add-to-cart-btn');
            const productId = button.dataset.productId;
            const quantity = parseInt(button.dataset.quantity || '1');
            const variantId = button.dataset.variantId;

            if (!productId) return;

            // Show loading state
            button.classList.add('loading');
            button.disabled = true;

            try {
                const response = await fetch('/api/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': Afepanou.config.csrfToken
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: quantity,
                        variant_id: variantId
                    })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.updateCartUI(data);
                    Afepanou.components.Notifications.show('Produit ajouté au panier', 'success');
                    
                    // Update button state
                    button.textContent = 'Ajouté ✓';
                    setTimeout(() => {
                        button.textContent = 'Ajouter au panier';
                        button.classList.remove('loading');
                        button.disabled = false;
                    }, 2000);
                } else {
                    throw new Error(data.error || 'Erreur lors de l\'ajout');
                }
            } catch (error) {
                console.error('Add to cart error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
                button.classList.remove('loading');
                button.disabled = false;
            }
        },

        handleRemoveFromCart: async function(event) {
            event.preventDefault();
            const button = event.target.closest('.remove-from-cart');
            const itemId = button.dataset.itemId;

            try {
                const response = await fetch(`/api/cart/remove/${itemId}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': Afepanou.config.csrfToken
                    }
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.updateCartUI(data);
                    Afepanou.components.Notifications.show('Produit retiré du panier', 'info');
                } else {
                    throw new Error(data.error || 'Erreur lors de la suppression');
                }
            } catch (error) {
                console.error('Remove from cart error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
            }
        },

        handleQuantityChange: async function(event) {
            const input = event.target;
            const itemId = input.dataset.itemId;
            const quantity = parseInt(input.value);

            if (quantity < 1) {
                input.value = 1;
                return;
            }

            try {
                const response = await fetch(`/api/cart/update/${itemId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': Afepanou.config.csrfToken
                    },
                    body: JSON.stringify({ quantity: quantity })
                });

                const data = await response.json();
                
                if (response.ok) {
                    this.updateCartUI(data);
                } else {
                    throw new Error(data.error || 'Erreur lors de la mise à jour');
                }
            } catch (error) {
                console.error('Update quantity error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
            }
        },

        updateCartUI: function(cartData) {
            // Update cart badge
            const cartBadge = document.getElementById('cart-badge');
            if (cartBadge && cartData) {
                cartBadge.textContent = cartData.items_count || 0;
                cartBadge.style.display = (cartData.items_count > 0) ? 'inline' : 'none';
            }

            // Update cart total in various locations
            if (cartData && cartData.total) {
                const totalElements = document.querySelectorAll('.cart-total');
                totalElements.forEach(el => {
                    el.textContent = `${cartData.total} HTG`;
                });
            }

            // Update cart dropdown content
            if (cartData && cartData.html) {
                const cartDropdown = document.getElementById('cart-dropdown-content');
                if (cartDropdown) {
                    cartDropdown.innerHTML = cartData.html;
                }
            }
        },

        showCartDropdown: function() {
            const dropdown = document.getElementById('cart-dropdown');
            if (dropdown) {
                dropdown.classList.remove('d-none');
                this.loadCartContent();
            }
        },

        hideCartDropdownDelay: function() {
            setTimeout(() => {
                const dropdown = document.getElementById('cart-dropdown');
                if (dropdown && !dropdown.matches(':hover')) {
                    dropdown.classList.add('d-none');
                }
            }, 300);
        },

        loadCartContent: async function() {
            const content = document.getElementById('cart-dropdown-content');
            if (!content) return;

            try {
                const response = await fetch('/api/cart/preview/');
                const data = await response.json();
                
                if (response.ok) {
                    content.innerHTML = data.html;
                } else {
                    content.innerHTML = '<p class="text-center p-3">Erreur de chargement</p>';
                }
            } catch (error) {
                console.error('Load cart content error:', error);
                content.innerHTML = '<p class="text-center p-3">Erreur de chargement</p>';
            }
        }
    };

    // Wishlist Component
    Afepanou.components.Wishlist = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('.wishlist-btn') || e.target.closest('.wishlist-btn')) {
                    this.handleWishlistToggle(e);
                }
            });
        },

        handleWishlistToggle: async function(event) {
            event.preventDefault();
            
            if (!Afepanou.config.user.isAuthenticated) {
                Afepanou.components.Notifications.show('Veuillez vous connecter', 'warning');
                return;
            }

            const button = event.target.closest('.wishlist-btn');
            const productId = button.dataset.productId;
            const isInWishlist = button.classList.contains('in-wishlist');

            try {
                const url = isInWishlist ? `/api/wishlist/remove/${productId}/` : `/api/wishlist/add/`;
                const method = isInWishlist ? 'DELETE' : 'POST';
                const body = isInWishlist ? null : JSON.stringify({ product_id: productId });

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': Afepanou.config.csrfToken
                    },
                    body: body
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Toggle button state
                    button.classList.toggle('in-wishlist');
                    const icon = button.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fas');
                        icon.classList.toggle('far');
                    }

                    // Update wishlist count
                    const wishlistCount = document.querySelector('.wishlist-count');
                    if (wishlistCount && data.wishlist_count !== undefined) {
                        wishlistCount.textContent = data.wishlist_count;
                    }

                    const message = isInWishlist ? 'Retiré des favoris' : 'Ajouté aux favoris';
                    Afepanou.components.Notifications.show(message, 'success');
                } else {
                    throw new Error(data.error || 'Erreur');
                }
            } catch (error) {
                console.error('Wishlist toggle error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
            }
        }
    };

    // Notifications Component
    Afepanou.components.Notifications = {
        init: function() {
            this.createContainer();
        },

        createContainer: function() {
            if (document.getElementById('notifications-container')) return;

            const container = document.createElement('div');
            container.id = 'notifications-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1060';
            document.body.appendChild(container);
        },

        show: function(message, type = 'info', duration = 5000) {
            this.createContainer();
            
            const container = document.getElementById('notifications-container');
            const notification = document.createElement('div');
            
            const typeClasses = {
                'success': 'alert-success',
                'error': 'alert-danger',
                'warning': 'alert-warning',
                'info': 'alert-info'
            };

            const icons = {
                'success': 'fas fa-check-circle',
                'error': 'fas fa-exclamation-circle',
                'warning': 'fas fa-exclamation-triangle',
                'info': 'fas fa-info-circle'
            };

            notification.className = `alert ${typeClasses[type]} alert-dismissible fade show`;
            notification.innerHTML = `
                <i class="${icons[type]} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            container.appendChild(notification);

            // Auto-remove after duration
            if (duration > 0) {
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, duration);
            }
        }
    };

    // Product Quick View Component
    Afepanou.components.QuickView = {
        init: function() {
            this.bindEvents();
        },

        bindEvents: function() {
            document.addEventListener('click', (e) => {
                if (e.target.matches('.quick-view-btn') || e.target.closest('.quick-view-btn')) {
                    this.handleQuickView(e);
                }
            });
        },

        handleQuickView: async function(event) {
            event.preventDefault();
            const button = event.target.closest('.quick-view-btn');
            const productId = button.dataset.productId;

            if (!productId) return;

            try {
                const response = await fetch(`/api/products/${productId}/quick-view/`);
                const data = await response.json();
                
                if (response.ok) {
                    this.showQuickViewModal(data);
                } else {
                    throw new Error(data.error || 'Erreur de chargement');
                }
            } catch (error) {
                console.error('Quick view error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
            }
        },

        showQuickViewModal: function(productData) {
            // Create modal if it doesn't exist
            let modal = document.getElementById('quickViewModal');
            if (!modal) {
                modal = this.createQuickViewModal();
                document.body.appendChild(modal);
            }

            // Populate modal with product data
            modal.querySelector('.modal-body').innerHTML = productData.html;

            // Show modal using Bootstrap
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();

            // Initialize product gallery for quick view
            Afepanou.components.ProductGallery.init();
        },

        createQuickViewModal: function() {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'quickViewModal';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Aperçu Rapide</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Product content will be loaded here -->
                        </div>
                    </div>
                </div>
            `;
            return modal;
        }
    };

    // Lazy Loading Component
    Afepanou.components.LazyLoading = {
        init: function() {
            if ('IntersectionObserver' in window) {
                this.initIntersectionObserver();
            } else {
                this.fallbackLazyLoad();
            }
        },

        initIntersectionObserver: function() {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        observer.unobserve(img);
                    }
                });
            });

            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => imageObserver.observe(img));
        },

        fallbackLazyLoad: function() {
            const lazyImages = document.querySelectorAll('img[data-src]');
            
            const loadImagesInViewport = () => {
                lazyImages.forEach(img => {
                    if (this.isInViewport(img)) {
                        this.loadImage(img);
                    }
                });
            };

            loadImagesInViewport();
            window.addEventListener('scroll', Afepanou.utils.throttle(loadImagesInViewport, 200));
            window.addEventListener('resize', Afepanou.utils.throttle(loadImagesInViewport, 200));
        },

        loadImage: function(img) {
            const src = img.dataset.src;
            if (src) {
                img.src = src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                img.removeAttribute('data-src');
            }
        },

        isInViewport: function(element) {
            const rect = element.getBoundingClientRect();
            return (
                rect.top < window.innerHeight &&
                rect.bottom > 0 &&
                rect.left < window.innerWidth &&
                rect.right > 0
            );
        }
    };

    // Form Enhancement Component
    Afepanou.components.FormEnhancement = {
        init: function() {
            this.initFormValidation();
            this.initFormSaving();
            this.bindEvents();
        },

        bindEvents: function() {
            // Auto-save form data
            document.addEventListener('input', this.handleFormChange.bind(this));
            document.addEventListener('change', this.handleFormChange.bind(this));
            
            // Form submission enhancement
            document.addEventListener('submit', this.handleFormSubmit.bind(this));
        },

        handleFormChange: function(event) {
            const form = event.target.closest('form');
            if (form && form.dataset.autosave === 'true') {
                this.saveFormData(form);
            }
        },

        handleFormSubmit: function(event) {
            const form = event.target;
            if (form.classList.contains('ajax-form')) {
                event.preventDefault();
                this.submitFormAjax(form);
            }
        },

        saveFormData: function(form) {
            const formData = new FormData(form);
            const data = {};
            
            formData.forEach((value, key) => {
                data[key] = value;
            });

            const formId = form.id || `form_${Date.now()}`;
            Afepanou.utils.storage.set(`form_data_${formId}`, data, 86400000); // 24 hours
        },

        loadFormData: function(formId) {
            return Afepanou.utils.storage.get(`form_data_${formId}`);
        },

        submitFormAjax: async function(form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.textContent : '';

            try {
                if (submitBtn) {
                    Afepanou.utils.showLoading(submitBtn);
                    submitBtn.disabled = true;
                }

                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: form.method || 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': Afepanou.config.csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    Afepanou.components.Notifications.show(data.message || 'Formulaire soumis avec succès', 'success');
                    
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        form.reset();
                    }
                } else {
                    throw new Error(data.error || 'Erreur lors de la soumission');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                Afepanou.components.Notifications.show(error.message, 'error');
            } finally {
                if (submitBtn) {
                    Afepanou.utils.hideLoading(submitBtn);
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            }
        },

        initFormValidation: function() {
            // Add custom validation styles
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', (e) => {
                    if (!form.checkValidity()) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                    form.classList.add('was-validated');
                });
            });
        },

        initFormSaving: function() {
            // Restore saved form data on page load
            const forms = document.querySelectorAll('form[data-autosave="true"]');
            forms.forEach(form => {
                const formId = form.id;
                if (formId) {
                    const savedData = this.loadFormData(formId);
                    if (savedData) {
                        Object.keys(savedData).forEach(key => {
                            const input = form.querySelector(`[name="${key}"]`);
                            if (input) {
                                input.value = savedData[key];
                            }
                        });
                    }
                }
            });
        }
    };

    // Performance Monitor Component
    Afepanou.components.Performance = {
        init: function() {
            this.monitorPageLoad();
            this.monitorUserInteractions();
        },

        monitorPageLoad: function() {
            window.addEventListener('load', () => {
                if ('performance' in window) {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
                    
                    // Log performance metrics (could be sent to analytics)
                    console.info(`Page load time: ${loadTime}ms`);
                    
                    // Show warning for slow pages
                    if (loadTime > 3000) {
                        console.warn('Slow page load detected');
                    }
                }
            });
        },

        monitorUserInteractions: function() {
            // Track Core Web Vitals if supported
            if ('PerformanceObserver' in window) {
                try {
                    const observer = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            console.info(`${entry.entryType}:`, entry);
                        }
                    });
                    
                    observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
                } catch (e) {
                    console.warn('Performance monitoring not fully supported');
                }
            }
        }
    };

    // Service Worker Registration
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('ServiceWorker registered successfully:', registration.scope);
                })
                .catch(error => {
                    console.warn('ServiceWorker registration failed:', error);
                });
        });
    }

    // Handle page unload
    window.addEventListener('beforeunload', function() {
        // Clean up any ongoing operations
        const loadingElements = document.querySelectorAll('.loading');
        loadingElements.forEach(el => {
            Afepanou.utils.hideLoading(el);
        });

        // Clear temporary data
        if (Afepanou.utils.storage) {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('temp_')) {
                    localStorage.removeItem(key);
                }
            });
        }
    });

    // Expose Afepanou object globally
    window.Afepanou = Afepanou;

})(window, document);

})();