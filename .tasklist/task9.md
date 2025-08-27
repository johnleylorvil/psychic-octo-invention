
## Phase 9: Frontend Enhancement & Finalization

### Task 9: Complete Frontend Implementation
**Priority**: High | **Estimated Time**: 20 hours

#### Objective
Implement a modern, responsive, and interactive frontend that provides an excellent user experience while maintaining the Haitian cultural identity and supporting the marketplace's business objectives.

#### Deliverables
- [ ] Complete CSS framework implementation
- [ ] Interactive JavaScript components
- [ ] Mobile-optimized responsive design
- [ ] Accessibility compliance
- [ ] Performance optimization

#### Implementation Steps

1. **Advanced CSS Architecture**
   ```scss
   // static/scss/main.scss
   @import 'abstracts/variables';
   @import 'abstracts/functions';
   @import 'abstracts/mixins';
   
   @import 'base/reset';
   @import 'base/typography';
   @import 'base/utilities';
   
   @import 'layout/header';
   @import 'layout/footer';
   @import 'layout/grid';
   
   @import 'components/buttons';
   @import 'components/cards';
   @import 'components/forms';
   @import 'components/modals';
   @import 'components/carousel';
   @import 'components/product-gallery';
   
   @import 'pages/home';
   @import 'pages/product-detail';
   @import 'pages/category';
   @import 'pages/checkout';
   
   // static/scss/abstracts/_variables.scss
   :root {
     // Brand Colors
     --primary-orange: #E67E22;
     --primary-orange-dark: #D35400;
     --primary-orange-light: #F39C12;
     --primary-orange-pale: #FDF2E9;
     
     // Semantic Colors
     --success: #27AE60;
     --warning: #F39C12;
     --danger: #E74C3C;
     --info: #3498DB;
     
     // Neutral Colors
     --white: #FFFFFF;
     --gray-50: #F8F9FA;
     --gray-100: #E9ECEF;
     --gray-200: #DEE2E6;
     --gray-300: #CED4DA;
     --gray-400: #ADB5BD;
     --gray-500: #6C757D;
     --gray-600: #495057;
     --gray-700: #343A40;
     --gray-800: #212529;
     --black: #000000;
     
     // Typography
     --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     --font-family-heading: 'Inter', serif;
     
     // Font Sizes (fluid typography)
     --font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
     --font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
     --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
     --font-size-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
     --font-size-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
     --font-size-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
     --font-size-3xl: clamp(1.875rem, 1.6rem + 1.375vw, 2.5rem);
     --font-size-4xl: clamp(2.25rem, 1.9rem + 1.75vw, 3rem);
     
     // Spacing Scale
     --space-xs: 0.25rem;   // 4px
     --space-sm: 0.5rem;    // 8px
     --space-md: 1rem;      // 16px
     --space-lg: 1.5rem;    // 24px
     --space-xl: 2rem;      // 32px
     --space-2xl: 3rem;     // 48px
     --space-3xl: 4rem;     // 64px
     --space-4xl: 6rem;     // 96px
     
     // Border Radius
     --radius-sm: 0.375rem;  // 6px
     --radius-md: 0.5rem;    // 8px
     --radius-lg: 0.75rem;   // 12px
     --radius-xl: 1rem;      // 16px
     --radius-full: 9999px;
     
     // Shadows
     --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
     --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
     --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
     --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
     --shadow-orange: 0 4px 20px rgba(230, 126, 34, 0.15);
     
     // Transitions
     --transition-fast: 150ms ease-in-out;
     --transition-base: 200ms ease-in-out;
     --transition-slow: 300ms ease-in-out;
     
     // Z-Index Scale
     --z-dropdown: 1000;
     --z-sticky: 1020;
     --z-fixed: 1030;
     --z-modal-backdrop: 1040;
     --z-modal: 1050;
     --z-popover: 1060;
     --z-tooltip: 1070;
   }
   ```

2. **Interactive JavaScript Components**
   ```javascript
   // static/js/components/carousel.js
   class HeroCarousel {
     constructor(element) {
       this.carousel = element;
       this.slides = element.querySelectorAll('.carousel-slide');
       this.dots = element.querySelectorAll('.dot');
       this.prevBtn = element.querySelector('.carousel-nav.prev');
       this.nextBtn = element.querySelector('.carousel-nav.next');
       this.currentSlide = 0;
       this.autoplayInterval = null;
       
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.startAutoplay();
       this.updateDots();
     }
     
     bindEvents() {
       this.prevBtn?.addEventListener('click', () => this.prevSlide());
       this.nextBtn?.addEventListener('click', () => this.nextSlide());
       
       this.dots.forEach((dot, index) => {
         dot.addEventListener('click', () => this.goToSlide(index));
       });
       
       // Pause autoplay on hover
       this.carousel.addEventListener('mouseenter', () => this.stopAutoplay());
       this.carousel.addEventListener('mouseleave', () => this.startAutoplay());
       
       // Handle swipe gestures on mobile
       this.bindSwipeEvents();
     }
     
     bindSwipeEvents() {
       let startX = 0;
       let endX = 0;
       
       this.carousel.addEventListener('touchstart', (e) => {
         startX = e.touches[0].clientX;
       });
       
       this.carousel.addEventListener('touchend', (e) => {
         endX = e.changedTouches[0].clientX;
         const diffX = startX - endX;
         
         if (Math.abs(diffX) > 50) { // Minimum swipe distance
           if (diffX > 0) {
             this.nextSlide();
           } else {
             this.prevSlide();
           }
         }
       });
     }
     
     goToSlide(index) {
       this.slides[this.currentSlide].classList.remove('active');
       this.dots[this.currentSlide].classList.remove('active');
       
       this.currentSlide = index;
       
       this.slides[this.currentSlide].classList.add('active');
       this.dots[this.currentSlide].classList.add('active');
     }
     
     nextSlide() {
       const nextIndex = (this.currentSlide + 1) % this.slides.length;
       this.goToSlide(nextIndex);
     }
     
     prevSlide() {
       const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
       this.goToSlide(prevIndex);
     }
     
     startAutoplay() {
       this.stopAutoplay();
       this.autoplayInterval = setInterval(() => {
         this.nextSlide();
       }, 5000); // 5 seconds
     }
     
     stopAutoplay() {
       if (this.autoplayInterval) {
         clearInterval(this.autoplayInterval);
         this.autoplayInterval = null;
       }
     }
     
     updateDots() {
       this.dots.forEach((dot, index) => {
         dot.classList.toggle('active', index === this.currentSlide);
       });
     }
   }
   
   // static/js/components/product-gallery.js
   class ProductGallery {
     constructor(element) {
       this.gallery = element;
       this.mainImage = element.querySelector('#main-product-image');
       this.thumbnails = element.querySelectorAll('.thumbnail');
       this.zoomContainer = element.querySelector('#image-zoom');
       
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.initZoom();
     }
     
     bindEvents() {
       this.thumbnails.forEach(thumbnail => {
         thumbnail.addEventListener('click', (e) => {
           e.preventDefault();
           const newImage = thumbnail.dataset.image;
           this.changeMainImage(newImage);
           this.setActiveThumbnail(thumbnail);
         });
       });
     }
     
     changeMainImage(imageSrc) {
       // Smooth transition
       this.mainImage.style.opacity = '0';
       
       setTimeout(() => {
         this.mainImage.src = imageSrc;
         this.mainImage.style.opacity = '1';
       }, 150);
     }
     
     setActiveThumbnail(activeThumbnail) {
       this.thumbnails.forEach(thumb => thumb.classList.remove('active'));
       activeThumbnail.classList.add('active');
     }
     
     initZoom() {
       this.mainImage.addEventListener('mousemove', (e) => {
         const rect = this.mainImage.getBoundingClientRect();
         const x = ((e.clientX - rect.left) / rect.width) * 100;
         const y = ((e.clientY - rect.top) / rect.height) * 100;
         
         this.zoomContainer.style.backgroundImage = `url(${this.mainImage.src})`;
         this.zoomContainer.style.backgroundPosition = `${x}% ${y}%`;
         this.zoomContainer.style.opacity = '1';
       });
       
       this.mainImage.addEventListener('mouseleave', () => {
         this.zoomContainer.style.opacity = '0';
       });
     }
   }
   
   // static/js/components/cart.js
   class ShoppingCart {
     constructor() {
       this.cartCount = 0;
       this.cartTotal = 0;
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.updateCartUI();
     }
     
     bindEvents() {
       // Add to cart buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('btn-add-cart')) {
           e.preventDefault();
           const productId = e.target.dataset.product;
           const quantity = this.getQuantity(e.target);
           this.addToCart(productId, quantity);
         }
       });
       
       // Quantity update buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('qty-btn')) {
           e.preventDefault();
           const action = e.target.dataset.action;
           const input = e.target.closest('.quantity-input').querySelector('input');
           this.updateQuantity(input, action);
         }
       });
       
       // Remove from cart buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('btn-remove-cart')) {
           e.preventDefault();
           const itemId = e.target.dataset.item;
           this.removeFromCart(itemId);
         }
       });
     }
     
     async addToCart(productId, quantity = 1) {
       try {
         const response = await fetch('/panier/ajouter/', {
           method: 'POST',
           headers: {
             'Content-Type': 'application/x-www-form-urlencoded',
             'X-CSRFToken': this.getCsrfToken(),
           },
           body: new URLSearchParams({
             product_id: productId,
             quantity: quantity
           })
         });
         
         const data = await response.json();
         
         if (data.success) {
           this.showNotification('Produit ajouté au panier', 'success');
           this.updateCartCount(data.cart_count);
           this.updateCartTotal(data.cart_total);
         } else {
           this.showNotification(data.message, 'error');
         }
       } catch (error) {
         console.error('Error adding to cart:', error);
         this.showNotification('Erreur lors de l\'ajout au panier', 'error');
       }
     }
     
     getQuantity(button) {
       const productCard = button.closest('.product-card, .product-detail');
       const quantityInput = productCard?.querySelector('input[name="quantity"]');
       return quantityInput ? parseInt(quantityInput.value) : 1;
     }
     
     updateQuantity(input, action) {
       const currentValue = parseInt(input.value) || 1;
       const maxValue = parseInt(input.max) || 999;
       
       if (action === 'increase' && currentValue < maxValue) {
         input.value = currentValue + 1;
       } else if (action === 'decrease' && currentValue > 1) {
         input.value = currentValue - 1;
       }
       
       // Trigger change event for any listeners
       input.dispatchEvent(new Event('change'));
     }
     
     showNotification(message, type = 'info') {
       const notification = document.createElement('div');
       notification.className = `notification notification-${type}`;
       notification.innerHTML = `
         <div class="notification-content">
           <span class="notification-message">${message}</span>
           <button class="notification-close">&times;</button>
         </div>
       `;
       
       document.body.appendChild(notification);
       
       // Auto-hide after 3 seconds
       setTimeout(() => {
         notification.classList.add('fade-out');
         setTimeout(() => notification.remove(), 300);
       }, 3000);
       
       // Manual close
       notification.querySelector('.notification-close').addEventListener('click', () => {
         notification.classList.add('fade-out');
         setTimeout(() => notification.remove(), 300);
       });
     }
     
     updateCartCount(count) {
       this.cartCount = count;
       const cartCountElements = document.querySelectorAll('.cart-count');
       cartCountElements.forEach(el => {
         el.textContent = count;
         el.style.display = count > 0 ? 'inline' : 'none';
       });
     }
     
     updateCartTotal(total) {
       this.cartTotal = total;
       const cartTotalElements = document.querySelectorAll('.cart-total');
       cartTotalElements.forEach(el => {
         el.textContent = `${total} HTG`;
       });
     }
     
     getCsrfToken() {
       return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
     }
   }
   ```

3. **Mobile-First Responsive Design**
   ```scss
   // static/scss/layout/_grid.scss
   .container {
     width: 100%;
     max-width: 1200px;
     margin: 0 auto;
     padding: 0 var(--space-md);
     
     @media (min-width: 768px) {
       padding: 0 var(--space-lg);
     }
     
     @media (min-width: 1024px) {
       padding: 0 var(--space-xl);
     }
   }
   
   .grid {
     display: grid;
     gap: var(--space-md);
     
     &--2-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 768px) {
         grid-template-columns: 1fr 1fr;
       }
     }
     
     &--3-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 768px) {
         grid-template-columns: 1fr 1fr;
       }
       
       @media (min-width: 1024px) {
         grid-template-columns: repeat(3, 1fr);
       }
     }
     
     &--4-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 480px) {
         grid-template-columns: 1fr 1fr;
       }
       
       @media (min-width: 768px) {
         grid-template-columns: repeat(3, 1fr);
       }
       
       @media (min-width: 1024px) {
         grid-template-columns: repeat(4, 1fr);
       }
     }
   }
   
   // static/scss/layout/_header.scss
   .main-header {
     background: var(--white);
     border-bottom: 1px solid var(--gray-200);
     position: sticky;
     top: 0;
     z-index: var(--z-sticky);
     
     .header-container {
       display: flex;
       align-items: center;
       justify-content: space-between;
       min-height: 70px;
       gap: var(--space-md);
       
       @media (max-width: 767px) {
         flex-wrap: wrap;
         min-height: auto;
         padding: var(--space-sm) 0;
       }
     }
     
     .logo-section {
       display: flex;
       align-items: center;
       gap: var(--space-sm);
       
       img {
         height: 40px;
         width: auto;
       }
       
       .tagline {
         font-size: var(--font-size-sm);
         color: var(--gray-600);
         
         @media (max-width: 767px) {
           display: none;
         }
       }
     }
     
     .main-navigation {
       display: none;
       
       @media (min-width: 768px) {
         display: flex;
         gap: var(--space-lg);
       }
       
       .nav-item {
         display: flex;
         flex-direction: column;
         align-items: center;
         gap: var(--space-xs);
         text-decoration: none;
         color: var(--gray-700);
         font-weight: 500;
         transition: color var(--transition-fast);
         
         &:hover {
           color: var(--primary-orange);
         }
         
         icon {
           font-size: var(--font-size-lg);
         }
       }
     }
     
     .search-bar {
       flex: 1;
       max-width: 400px;
       position: relative;
       
       @media (max-width: 767px) {
         order: 3;
         flex-basis: 100%;
         max-width: none;
         margin-top: var(--space-sm);
       }
       
       input {
         width: 100%;
         padding: var(--space-sm) var(--space-lg) var(--space-sm) var(--space-md);
         border: 2px solid var(--gray-300);
         border-radius: var(--radius-lg);
         font-size: var(--font-size-base);
         transition: border-color var(--transition-fast);
         
         &:focus {
           outline: none;
           border-color: var(--primary-orange);
         }
         
         &::placeholder {
           color: var(--gray-500);
         }
       }
       
       button {
         position: absolute;
         right: var(--space-sm);
         top: 50%;
         transform: translateY(-50%);
         background: var(--primary-orange);
         color: white;
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-sm);
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: var(--primary-orange-dark);
         }
       }
     }
     
     .user-actions {
       display: flex;
       align-items: center;
       gap: var(--space-sm);
       
       .btn-icon {
         background: transparent;
         border: none;
         font-size: var(--font-size-lg);
         color: var(--gray-700);
         cursor: pointer;
         padding: var(--space-sm);
         border-radius: var(--radius-md);
         transition: color var(--transition-fast), background-color var(--transition-fast);
         position: relative;
         
         &:hover {
           background: var(--gray-100);
           color: var(--primary-orange);
         }
         
         &.cart-btn .cart-count {
           position: absolute;
           top: 0;
           right: 0;
           background: var(--primary-orange);
           color: white;
           font-size: var(--font-size-xs);
           font-weight: 600;
           padding: 2px 6px;
           border-radius: var(--radius-full);
           min-width: 18px;
           text-align: center;
         }
       }
     }
     
     // Mobile menu toggle
     .mobile-menu-toggle {
       display: block;
       background: transparent;
       border: none;
       font-size: var(--font-size-xl);
       color: var(--gray-700);
       cursor: pointer;
       
       @media (min-width: 768px) {
         display: none;
       }
     }
     
     // Mobile navigation
     .mobile-navigation {
       display: none;
       position: fixed;
       top: 100%;
       left: 0;
       right: 0;
       background: white;
       border-top: 1px solid var(--gray-200);
       padding: var(--space-lg);
       z-index: var(--z-dropdown);
       
       &.active {
         display: block;
       }
       
       @media (min-width: 768px) {
         display: none !important;
       }
       
       .mobile-nav-item {
         display: block;
         padding: var(--space-md) 0;
         text-decoration: none;
         color: var(--gray-700);
         font-weight: 500;
         border-bottom: 1px solid var(--gray-100);
         
         &:last-child {
           border-bottom: none;
         }
         
         &:hover {
           color: var(--primary-orange);
         }
       }
     }
   }
   
   // static/scss/components/_product-card.scss
   .product-card {
     background: var(--white);
     border-radius: var(--radius-lg);
     overflow: hidden;
     box-shadow: var(--shadow-sm);
     transition: transform var(--transition-base), box-shadow var(--transition-base);
     
     &:hover {
       transform: translateY(-4px);
       box-shadow: var(--shadow-lg);
     }
     
     .product-image {
       position: relative;
       aspect-ratio: 1;
       overflow: hidden;
       
       img {
         width: 100%;
         height: 100%;
         object-fit: cover;
         transition: transform var(--transition-slow);
       }
       
       &:hover img {
         transform: scale(1.05);
       }
       
       .product-actions {
         position: absolute;
         top: var(--space-sm);
         right: var(--space-sm);
         display: flex;
         flex-direction: column;
         gap: var(--space-xs);
         opacity: 0;
         transition: opacity var(--transition-base);
       }
       
       &:hover .product-actions {
         opacity: 1;
       }
       
       .btn-quick-view,
       .btn-favorite {
         background: rgba(255, 255, 255, 0.9);
         backdrop-filter: blur(4px);
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-sm);
         font-size: var(--font-size-sm);
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: white;
         }
       }
       
       .product-badge {
         position: absolute;
         top: var(--space-sm);
         left: var(--space-sm);
         background: var(--primary-orange);
         color: white;
         font-size: var(--font-size-xs);
         font-weight: 600;
         padding: var(--space-xs) var(--space-sm);
         border-radius: var(--radius-md);
         text-transform: uppercase;
         
         &.discount {
           background: var(--danger);
         }
         
         &.new {
           background: var(--success);
         }
       }
     }
     
     .product-info {
       padding: var(--space-lg);
       
       .product-category {
         font-size: var(--font-size-sm);
         color: var(--primary-orange);
         font-weight: 500;
         text-transform: uppercase;
         letter-spacing: 0.5px;
         margin-bottom: var(--space-xs);
       }
       
       h3 {
         margin: 0 0 var(--space-sm) 0;
         font-size: var(--font-size-lg);
         font-weight: 600;
         line-height: 1.3;
         
         a {
           text-decoration: none;
           color: var(--gray-800);
           transition: color var(--transition-fast);
           
           &:hover {
             color: var(--primary-orange);
           }
         }
       }
       
       .product-rating {
         display: flex;
         align-items: center;
         gap: var(--space-xs);
         margin-bottom: var(--space-sm);
         
         .star {
           color: var(--warning);
           font-size: var(--font-size-sm);
           
           &:not(.filled) {
             color: var(--gray-300);
           }
         }
         
         .rating-count {
           font-size: var(--font-size-sm);
           color: var(--gray-500);
         }
       }
       
       .product-price {
         display: flex;
         align-items: center;
         gap: var(--space-sm);
         margin-bottom: var(--space-md);
         
         .current-price {
           font-size: var(--font-size-xl);
           font-weight: 700;
           color: var(--primary-orange);
         }
         
         .original-price {
           font-size: var(--font-size-lg);
           color: var(--gray-500);
           text-decoration: line-through;
         }
         
         .discount {
           background: var(--danger);
           color: white;
           font-size: var(--font-size-xs);
           font-weight: 600;
           padding: var(--space-xs) var(--space-sm);
           border-radius: var(--radius-md);
         }
       }
       
       .product-vendor {
         font-size: var(--font-size-sm);
         color: var(--gray-600);
         margin-bottom: var(--space-md);
       }
       
       .btn-add-cart {
         width: 100%;
         background: var(--primary-orange);
         color: white;
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-md);
         font-weight: 600;
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: var(--primary-orange-dark);
         }
         
         &:disabled {
           background: var(--gray-400);
           cursor: not-allowed;
         }
       }
     }
   }
   ```

4. **Accessibility Implementation**
   ```javascript
   // static/js/accessibility.js
   class AccessibilityEnhancements {
     constructor() {
       this.init();
     }
     
     init() {
       this.setupKeyboardNavigation();
       this.setupFocusManagement();
       this.setupAriaLiveRegions();
       this.setupSkipLinks();
       this.addTouchTargetHelpers();
     }
     
     setupKeyboardNavigation() {
       // Keyboard navigation for custom components
       document.addEventListener('keydown', (e) => {
         // Escape key to close modals/dropdowns
         if (e.key === 'Escape') {
           this.closeModals();
           this.closeDropdowns();
         }
         
         // Arrow key navigation for product grids
         if (e.target.closest('.products-grid')) {
           this.handleArrowNavigation(e);
         }
         
         // Enter/Space for button-like elements
         if ((e.key === 'Enter' || e.key === ' ') && e.target.hasAttribute('role') && e.target.getAttribute('role') === 'button') {
           e.preventDefault();
           e.target.click();
         }
       });
     }
     
     handleArrowNavigation(e) {
       const products = Array.from(document.querySelectorAll('.product-card a'));
       const currentIndex = products.indexOf(document.activeElement);
       
       if (currentIndex === -1) return;
       
       let newIndex;
       const columns = this.getGridColumns();
       
       switch (e.key) {
         case 'ArrowRight':
           newIndex = Math.min(currentIndex + 1, products.length - 1);
           break;
         case 'ArrowLeft':
           newIndex = Math.max(currentIndex - 1, 0);
           break;
         case 'ArrowDown':
           newIndex = Math.min(currentIndex + columns, products.length - 1);
           break;
         case 'ArrowUp':
           newIndex = Math.max(currentIndex - columns, 0);
           break;
         default:
           return;
       }
       
       e.preventDefault();
       products[newIndex].focus();
     }
     
     getGridColumns() {
       const grid = document.querySelector('.products-grid');
       if (!grid) return 1;
       
       const styles = window.getComputedStyle(grid);
       const columns = styles.gridTemplateColumns.split(' ').length;
       return columns;
     }
     
     setupFocusManagement() {
       // Focus trap for modals
       document.addEventListener('focusin', (e) => {
         const modal = e.target.closest('.modal.active');
         if (modal) {
           const focusableElements = modal.querySelectorAll(
             'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
           );
           
           if (focusableElements.length === 0) return;
           
           const firstElement = focusableElements[0];
           const lastElement = focusableElements[focusableElements.length - 1];
           
           // If focus moves outside modal, bring it back
           if (!modal.contains(e.target)) {
             firstElement.focus();
           }
         }
       });
       
       // Save focus state when opening modals
       document.addEventListener('click', (e) => {
         if (e.target.hasAttribute('data-modal-trigger')) {
           e.target.dataset.returnFocus = 'true';
         }
       });
     }
     
     setupAriaLiveRegions() {
       // Create live region for cart updates
       const cartLiveRegion = document.createElement('div');
       cartLiveRegion.setAttribute('aria-live', 'polite');
       cartLiveRegion.setAttribute('aria-atomic', 'true');
       cartLiveRegion.className = 'sr-only';
       cartLiveRegion.id = 'cart-live-region';
       document.body.appendChild(cartLiveRegion);
       
       // Create live region for form errors
       const errorLiveRegion = document.createElement('div');
       errorLiveRegion.setAttribute('aria-live', 'assertive');
       errorLiveRegion.setAttribute('aria-atomic', 'true');
       errorLiveRegion.className = 'sr-only';
       errorLiveRegion.id = 'error-live-region';
       document.body.appendChild(errorLiveRegion);
     }
     
     announceCartUpdate(message) {
       const liveRegion = document.getElementById('cart-live-region');
       if (liveRegion) {
         liveRegion.textContent = message;
       }
     }
     
     announceError(message) {
       const liveRegion = document.getElementById('error-live-region');
       if (liveRegion) {
         liveRegion.textContent = message;
       }
     }
     
     setupSkipLinks() {
       // Add skip to main content link
       const skipLink = document.createElement('a');
       skipLink.href = '#main-content';
       skipLink.textContent = 'Passer au contenu principal';
       skipLink.className = 'skip-link';
       skipLink.style.cssText = `
         position: absolute;
         top: -40px;
         left: 6px;
         background: var(--primary-orange);
         color: white;
         padding: 8px;
         text-decoration: none;
         border-radius: 4px;
         z-index: 1000;
         transition: top 0.3s;
       `;
       
       skipLink.addEventListener('focus', () => {
         skipLink.style.top = '6px';
       });
       
       skipLink.addEventListener('blur', () => {
         skipLink.style.top = '-40px';
       });
       
       document.body.insertBefore(skipLink, document.body.firstChild);
     }
     
     addTouchTargetHelpers() {
       // Ensure touch targets are at least 44px for mobile
       const style = document.createElement('style');
       style.textContent = `
         @media (pointer: coarse) {
           button, 
           input[type="button"], 
           input[type="submit"], 
           .btn,
           .btn-icon {
             min-height: 44px;
             min-width: 44px;
           }
         }
       `;
       document.head.appendChild(style);
     }
     
     closeModals() {
       const activeModals = document.querySelectorAll('.modal.active');
       activeModals.forEach(modal => {
         modal.classList.remove('active');
         
         // Return focus to trigger element
         const trigger = document.querySelector('[data-return-focus="true"]');
         if (trigger) {
           trigger.focus();
           trigger.removeAttribute('data-return-focus');
         }
       });
     }
     
     closeDropdowns() {
       const activeDropdowns = document.querySelectorAll('.dropdown.active');
       activeDropdowns.forEach(dropdown => {
         dropdown.classList.remove('active');
       });
     }
   }
   
   // Screen reader only utility class
   const srOnlyCSS = `
     .sr-only {
       position: absolute;
       width: 1px;
       height: 1px;
       padding: 0;
       margin: -1px;
       overflow: hidden;
       clip: rect(0, 0, 0, 0);
       white-space: nowrap;
       border: 0;
     }
   `;
   
   const style = document.createElement('style');
   style.textContent = srOnlyCSS;
   document.head.appendChild(style);
   ```

5. **Performance Optimization**
   ```javascript
   // static/js/performance.js
   class PerformanceOptimizer {
     constructor() {
       this.init();
     }
     
     init() {
       this.setupLazyLoading();
       this.setupImageOptimization();
       this.setupScrollOptimization();
       this.preloadCriticalResources();
       this.initServiceWorker();
     }
     
     setupLazyLoading() {
       // Intersection Observer for lazy loading images
       if ('IntersectionObserver' in window) {
         const imageObserver = new IntersectionObserver((entries, observer) => {
           entries.forEach(entry => {
             if (entry.isIntersecting) {
               const img = entry.target;
               img.src = img.dataset.src;
               img.classList.remove('lazy');
               observer.unobserve(img);
             }
           });
         }, {
           rootMargin: '50px 0px'
         });
         
         document.querySelectorAll('img[data-src]').forEach(img => {
           imageObserver.observe(img);
         });
       } else {
         // Fallback for older browsers
         document.querySelectorAll('img[data-src]').forEach(img => {
           img.src = img.dataset.src;
         });
       }
     }
     
     setupImageOptimization() {
       // Convert images to WebP if supported
       const supportsWebP = this.checkWebPSupport();
       
       if (supportsWebP) {
         document.querySelectorAll('img[data-webp]').forEach(img => {
           img.src = img.dataset.webp;
         });
       }
       
       // Responsive images based on screen size
       this.setupResponsiveImages();
     }
     
     checkWebPSupport() {
       return new Promise(resolve => {
         const webP = new Image();
         webP.onload = webP.onerror = () => {
           resolve(webP.height === 2);
         };
         webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
       });
     }
     
     setupResponsiveImages() {
       const updateImageSources = () => {
         const screenWidth = window.innerWidth;
         
         document.querySelectorAll('img[data-sizes]').forEach(img => {
           const sizes = JSON.parse(img.dataset.sizes);
           let appropriateSize = sizes.default;
           
           Object.keys(sizes).forEach(breakpoint => {
             if (breakpoint !== 'default' && screenWidth >= parseInt(breakpoint)) {
               appropriateSize = sizes[breakpoint];
             }
           });
           
           if (img.src !== appropriateSize) {
             img.src = appropriateSize;
           }
         });
       };
       
       // Update on resize (debounced)
       let resizeTimeout;
       window.addEventListener('resize', () => {
         clearTimeout(resizeTimeout);
         resizeTimeout = setTimeout(updateImageSources, 250);
       });
       
       updateImageSources();
     }
     
     setupScrollOptimization() {
       // Throttled scroll events
       let scrollTimeout;
       let isScrolling = false;
       
       const throttledScroll = (callback) => {
         if (!isScrolling) {
           requestAnimationFrame(() => {
             callback();
             isScrolling = false;
           });
           isScrolling = true;
         }
       };
       
       window.addEventListener('scroll', () => {
         throttledScroll(() => {
           this.handleScroll();
         });
       });
     }
     
     handleScroll() {
       const scrollY = window.scrollY;
       const header = document.querySelector('.main-header');
       
       // Add/remove scrolled class for header styling
       if (scrollY > 10) {
         header.classList.add('scrolled');
       } else {
         header.classList.remove('scrolled');
       }
       
       // Show/hide back to top button
       const backToTopBtn = document.getElementById('back-to-top');
       if (backToTopBtn) {
         if (scrollY > 300) {
           backToTopBtn.style.display = 'block';
         } else {
           backToTopBtn.style.display = 'none';
         }
       }
     }
     
     preloadCriticalResources() {
       // Preload critical CSS
       const criticalCSS = document.createElement('link');
       criticalCSS.rel = 'preload';
       criticalCSS.href = '/static/css/critical.css';
       criticalCSS.as = 'style';
       document.head.appendChild(criticalCSS);
       
       // Preload important fonts
       const font = document.createElement('link');
       font.rel = 'preload';
       font.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap';
       font.as = 'style';
       document.head.appendChild(font);
       
       // DNS prefetch for external resources
       const dnsPrefetch = document.createElement('link');
       dnsPrefetch.rel = 'dns-prefetch';
       dnsPrefetch.href = '//fonts.googleapis.com';
       document.head.appendChild(dnsPrefetch);
     }
     
     initServiceWorker() {
       if ('serviceWorker' in navigator) {
         navigator.serviceWorker.register('/sw.js')
           .then(registration => {
             console.log('Service Worker registered:', registration);
           })
           .catch(error => {
             console.log('Service Worker registration failed:', error);
           });
       }
     }
     
     // Critical rendering path optimization
     optimizeCriticalPath() {
       // Move non-critical CSS to load async
       const nonCriticalCSS = document.querySelectorAll('link[rel="stylesheet"]:not([data-critical])');
       nonCriticalCSS.forEach(link => {
         const href = link.href;
         link.media = 'print';
         link.onload = () => {
           link.media = 'all';
         };
         
         // Fallback for older browsers
         setTimeout(() => {
           link.media = 'all';
         }, 100);
       });
     }
   }
   
   // Initialize performance optimizations when DOM is ready
   if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', () => {
       new PerformanceOptimizer();
     });
   } else {
     new PerformanceOptimizer();
   }
   ```

6. **Main Application Initialization**
   ```javascript
   // static/js/main.js
   document.addEventListener('DOMContentLoaded', function() {
     // Initialize core components
     initializeComponents();
     
     // Initialize accessibility enhancements
     new AccessibilityEnhancements();
     
     // Initialize shopping cart
     window.shoppingCart = new ShoppingCart();
     
     // Initialize search functionality
     initializeSearch();
     
     // Set up CSRF token for all AJAX requests
     setupCSRFToken();
     
     // Initialize animations
     initializeAnimations();
   });
   
   function initializeComponents() {
     // Initialize hero carousel
     const heroCarousel = document.querySelector('.hero-carousel');
     if (heroCarousel) {
       new HeroCarousel(heroCarousel);
     }
     
     // Initialize product galleries
     document.querySelectorAll('.product-gallery').forEach(gallery => {
       new ProductGallery(gallery);
     });
     
     // Initialize mobile menu
     const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
     const mobileMenu = document.querySelector('.mobile-navigation');
     
     if (mobileMenuToggle && mobileMenu) {
       mobileMenuToggle.addEventListener('click', () => {
         mobileMenu.classList.toggle('active');
         mobileMenuToggle.setAttribute('aria-expanded', 
           mobileMenu.classList.contains('active')
         );
       });
     }
     
     // Initialize modals
     document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
       trigger.addEventListener('click', (e) => {
         e.preventDefault();
         const modalId = trigger.dataset.modalTrigger;
         const modal = document.getElementById(modalId);
         if (modal) {
           openModal(modal);
         }
       });
     });
     
     // Initialize tooltips
     initializeTooltips();
   }
   
   function initializeSearch() {
     const searchForm = document.querySelector('.search-bar form');
     const searchInput = searchForm?.querySelector('input[name="query"]');
     
     if (searchInput) {
       // Search suggestions
       let searchTimeout;
       searchInput.addEventListener('input', (e) => {
         clearTimeout(searchTimeout);
         searchTimeout = setTimeout(() => {
           if (e.target.value.length >= 2) {
             fetchSearchSuggestions(e.target.value);
           }
         }, 300);
       });
       
       // Clear suggestions on focus out
       searchInput.addEventListener('blur', () => {
         setTimeout(() => {
           clearSearchSuggestions();
         }, 200);
       });
     }
   }
   
   async function fetchSearchSuggestions(query) {
     try {
       const response = await fetch(`/api/v1/autocomplete/?q=${encodeURIComponent(query)}`);
       const data = await response.json();
       displaySearchSuggestions(data.suggestions);
     } catch (error) {
       console.error('Search suggestions error:', error);
     }
   }
   
   function displaySearchSuggestions(suggestions) {
     let suggestionsContainer = document.getElementById('search-suggestions');
     
     if (!suggestionsContainer) {
       suggestionsContainer = document.createElement('div');
       suggestionsContainer.id = 'search-suggestions';
       suggestionsContainer.className = 'search-suggestions';
       document.querySelector('.search-bar').appendChild(suggestionsContainer);
     }
     
     suggestionsContainer.innerHTML = suggestions.map(suggestion => 
       `<button type="button" class="suggestion-item" data-query="${suggestion.query}">
         ${suggestion.name}
         <span class="suggestion-category">${suggestion.category}</span>
       </button>`
     ).join('');
     
     // Add click handlers
     suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
       item.addEventListener('click', () => {
         const query = item.dataset.query;
         document.querySelector('.search-bar input').value = query;
         document.querySelector('.search-bar form').submit();
       });
     });
   }
   
   function clearSearchSuggestions() {
     const container = document.getElementById('search-suggestions');
     if (container) {
       container.remove();
     }
   }
   
   function setupCSRFToken() {
     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
     
     if (csrfToken) {
       // Set default headers for fetch requests
       const originalFetch = window.fetch;
       window.fetch = function(url, options = {}) {
         if (options.method && options.method.toUpperCase() !== 'GET') {
           options.headers = options.headers || {};
           options.headers['X-CSRFToken'] = csrfToken;
         }
         return originalFetch(url, options);
       };
     }
   }
   
   function openModal(modal) {
     modal.classList.add('active');
     modal.setAttribute('aria-hidden', 'false');
     
     // Focus first focusable element
     const focusableElement = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
     if (focusableElement) {
       focusableElement.focus();
     }
     
     // Close on backdrop click
     modal.addEventListener('click', (e) => {
       if (e.target === modal) {
         closeModal(modal);
       }
     });
     
     // Close button
     const closeBtn = modal.querySelector('.modal-close');
     if (closeBtn) {
       closeBtn.addEventListener('click', () => closeModal(modal));
     }
   }
   
   function closeModal(modal) {
     modal.classList.remove('active');
     modal.setAttribute('aria-hidden', 'true');
   }
   
   function initializeTooltips() {
     document.querySelectorAll('[data-tooltip]').forEach(element => {
       element.addEventListener('mouseenter', showTooltip);
       element.addEventListener('mouseleave', hideTooltip);
       element.addEventListener('focus', showTooltip);
       element.addEventListener('blur', hideTooltip);
     });
   }
   
   function showTooltip(e) {
     const tooltip = document.createElement('div');
     tooltip.className = 'tooltip';
     tooltip.textContent = e.target.dataset.tooltip;
     tooltip.setAttribute('role', 'tooltip');
     
     document.body.appendChild(tooltip);
     
     const rect = e.target.getBoundingClientRect();
     tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
     tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
     
     e.target.tooltipElement = tooltip;
   }
   
   function hideTooltip(e) {
     if (e.target.tooltipElement) {
       e.target.tooltipElement.remove();
       delete e.target.tooltipElement;
     }
   }
   
   function initializeAnimations() {
     // Intersection Observer for scroll animations
     if ('IntersectionObserver' in window) {
       const animationObserver = new IntersectionObserver((entries) => {
         entries.forEach(entry => {
           if (entry.isIntersecting) {
             entry.target.classList.add('animate-in');
             animationObserver.unobserve(entry.target);
           }
         });
       }, {
         threshold: 0.1,
         rootMargin: '0px 0px -50px 0px'
       });
       
       document.querySelectorAll('.animate-on-scroll').forEach(element => {
         animationObserver.observe(element);
       });
     }
   }
   
   // Back to top button
   const backToTopBtn = document.createElement('button');
   backToTopBtn.id = 'back-to-top';
   backToTopBtn.innerHTML = '↑';
   backToTopBtn.setAttribute('aria-label', 'Retour en haut');
   backToTopBtn.style.cssText = `
     position: fixed;
     bottom: 20px;
     right: 20px;
     background: var(--primary-orange);
     color: white;
     border: none;
     border-radius: 50%;
     width: 50px;
     height: 50px;
     font-size: 20px;
     cursor: pointer;
     display: none;
     z-index: 1000;
     box-shadow: var(--shadow-lg);
     transition: all var(--transition-base);
   `;
   
   backToTopBtn.addEventListener('click', () => {
     window.scrollTo({ top: 0, behavior: 'smooth' });
   });
   
   document.body.appendChild(backToTopBtn);
   ```

#### Acceptance Criteria
- [ ] Complete CSS framework with design system variables implemented
- [ ] All interactive components work smoothly across devices
- [ ] Mobile-first responsive design implemented and tested
- [ ] WCAG 2.1 AA accessibility compliance achieved
- [ ] Performance metrics: LCP < 2.5s, FID < 100ms, CLS < 0.1
- [ ] Cross-browser compatibility verified (Chrome, Firefox, Safari, Edge)
- [ ] Search functionality with autocomplete working
- [ ] Shopping cart updates without page refresh
- [ ] Image lazy loading and optimization implemented
- [ ] Keyboard navigation fully functional
- [ ] Screen reader compatibility verified

---