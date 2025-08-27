/**
 * Product Image Gallery Component for Afèpanou
 * Handles product image display, zoom, and navigation
 */

class ProductGallery {
    constructor(containerSelector, options = {}) {
        this.container = document.querySelector(containerSelector);
        if (!this.container) return;
        
        this.options = {
            autoPlay: false,
            loop: true,
            navigation: true,
            thumbnails: true,
            zoom: true,
            swipeEnabled: true,
            ...options
        };
        
        this.currentIndex = 0;
        this.images = [];
        this.isZoomed = false;
        this.touchStartX = 0;
        this.touchEndX = 0;
        
        this.init();
    }
    
    init() {
        this.setupStructure();
        this.bindEvents();
        this.setupSwiper();
        
        if (this.options.zoom) {
            this.initZoom();
        }
    }
    
    setupStructure() {
        // Get all images
        this.images = Array.from(this.container.querySelectorAll('.gallery-image'));
        
        if (this.images.length === 0) return;
        
        // Create gallery structure if it doesn't exist
        if (!this.container.querySelector('.gallery-main')) {
            this.createGalleryStructure();
        }
        
        this.mainImage = this.container.querySelector('.gallery-main-image');
        this.thumbnails = Array.from(this.container.querySelectorAll('.gallery-thumbnail'));
        this.prevBtn = this.container.querySelector('.gallery-prev');
        this.nextBtn = this.container.querySelector('.gallery-next');
    }
    
    createGalleryStructure() {
        const firstImage = this.images[0];
        
        const galleryHTML = `
            <div class="gallery-main">
                <div class="gallery-main-container">
                    <img src="${firstImage.src}" alt="${firstImage.alt}" 
                         class="gallery-main-image" id="main-gallery-image">
                    
                    ${this.options.zoom ? `
                        <button class="gallery-zoom-btn" aria-label="Zoom image" title="Klike pou zoom">
                            <i class="fas fa-search-plus"></i>
                        </button>
                    ` : ''}
                    
                    ${this.images.length > 1 && this.options.navigation ? `
                        <button class="gallery-prev" aria-label="Previous image" title="Imaj anvan an">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <button class="gallery-next" aria-label="Next image" title="Pwochen imaj la">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    ` : ''}
                </div>
                
                <div class="gallery-counter">
                    <span class="gallery-current">1</span> / <span class="gallery-total">${this.images.length}</span>
                </div>
            </div>
            
            ${this.images.length > 1 && this.options.thumbnails ? `
                <div class="gallery-thumbnails">
                    <div class="gallery-thumbnails-container">
                        ${this.images.map((img, index) => `
                            <button class="gallery-thumbnail ${index === 0 ? 'gallery-thumbnail--active' : ''}" 
                                    data-index="${index}"
                                    aria-label="Montre imaj ${index + 1}">
                                <img src="${img.src}" alt="${img.alt}" loading="lazy">
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        this.container.innerHTML = galleryHTML;
    }
    
    bindEvents() {
        // Thumbnail clicks
        this.thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('click', () => {
                this.goToImage(index);
            });
            
            // Keyboard support
            thumb.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.goToImage(index);
                }
            });
        });
        
        // Navigation buttons
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.previousImage());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextImage());
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!this.isInViewport()) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousImage();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextImage();
                    break;
                case 'Escape':
                    if (this.isZoomed) {
                        this.toggleZoom();
                    }
                    break;
            }
        });
        
        // Touch/swipe support
        if (this.options.swipeEnabled && this.mainImage) {
            this.setupTouchEvents();
        }
        
        // Zoom button
        const zoomBtn = this.container.querySelector('.gallery-zoom-btn');
        if (zoomBtn) {
            zoomBtn.addEventListener('click', () => this.toggleZoom());
        }
    }
    
    setupTouchEvents() {
        this.mainImage.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        this.mainImage.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    }
    
    handleSwipe() {
        const swipeThreshold = 50;
        const swipeDistance = this.touchEndX - this.touchStartX;
        
        if (Math.abs(swipeDistance) < swipeThreshold) return;
        
        if (swipeDistance > 0) {
            this.previousImage();
        } else {
            this.nextImage();
        }
    }
    
    setupSwiper() {
        // Initialize Swiper if available
        if (typeof Swiper !== 'undefined' && this.container.querySelector('.swiper')) {
            this.swiper = new Swiper(this.container.querySelector('.swiper'), {
                loop: this.options.loop,
                navigation: {
                    nextEl: '.gallery-next',
                    prevEl: '.gallery-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                autoplay: this.options.autoPlay ? {
                    delay: 5000,
                    disableOnInteraction: true,
                } : false,
            });
        }
    }
    
    initZoom() {
        if (!this.mainImage) return;
        
        // Double-click to zoom
        this.mainImage.addEventListener('dblclick', () => {
            this.toggleZoom();
        });
        
        // Create zoom overlay
        this.createZoomOverlay();
    }
    
    createZoomOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'gallery-zoom-overlay';
        overlay.style.display = 'none';
        
        overlay.innerHTML = `
            <div class="gallery-zoom-container">
                <button class="gallery-zoom-close" aria-label="Ferme zoom">
                    <i class="fas fa-times"></i>
                </button>
                <img class="gallery-zoom-image" alt="">
                <div class="gallery-zoom-controls">
                    <button class="gallery-zoom-prev" aria-label="Imaj anvan an">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <button class="gallery-zoom-next" aria-label="Pwochen imaj la">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.zoomOverlay = overlay;
        
        // Bind zoom overlay events
        overlay.querySelector('.gallery-zoom-close').addEventListener('click', () => {
            this.closeZoom();
        });
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.closeZoom();
            }
        });
        
        overlay.querySelector('.gallery-zoom-prev').addEventListener('click', () => {
            this.previousImage();
            this.updateZoomImage();
        });
        
        overlay.querySelector('.gallery-zoom-next').addEventListener('click', () => {
            this.nextImage();
            this.updateZoomImage();
        });
    }
    
    goToImage(index) {
        if (index < 0 || index >= this.images.length) return;
        
        this.currentIndex = index;
        this.updateMainImage();
        this.updateThumbnails();
        this.updateCounter();
        
        if (this.isZoomed) {
            this.updateZoomImage();
        }
    }
    
    nextImage() {
        let nextIndex = this.currentIndex + 1;
        if (nextIndex >= this.images.length) {
            nextIndex = this.options.loop ? 0 : this.images.length - 1;
        }
        this.goToImage(nextIndex);
    }
    
    previousImage() {
        let prevIndex = this.currentIndex - 1;
        if (prevIndex < 0) {
            prevIndex = this.options.loop ? this.images.length - 1 : 0;
        }
        this.goToImage(prevIndex);
    }
    
    updateMainImage() {
        if (!this.mainImage || !this.images[this.currentIndex]) return;
        
        const currentImg = this.images[this.currentIndex];
        
        // Smooth transition
        this.mainImage.style.opacity = '0';
        
        setTimeout(() => {
            this.mainImage.src = currentImg.src;
            this.mainImage.alt = currentImg.alt;
            this.mainImage.style.opacity = '1';
        }, 150);
    }
    
    updateThumbnails() {
        this.thumbnails.forEach((thumb, index) => {
            if (index === this.currentIndex) {
                thumb.classList.add('gallery-thumbnail--active');
                thumb.setAttribute('aria-selected', 'true');
            } else {
                thumb.classList.remove('gallery-thumbnail--active');
                thumb.setAttribute('aria-selected', 'false');
            }
        });
    }
    
    updateCounter() {
        const current = this.container.querySelector('.gallery-current');
        if (current) {
            current.textContent = this.currentIndex + 1;
        }
    }
    
    toggleZoom() {
        if (this.isZoomed) {
            this.closeZoom();
        } else {
            this.openZoom();
        }
    }
    
    openZoom() {
        if (!this.zoomOverlay) return;
        
        this.isZoomed = true;
        this.updateZoomImage();
        this.zoomOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus management
        this.zoomOverlay.querySelector('.gallery-zoom-close').focus();
    }
    
    closeZoom() {
        if (!this.zoomOverlay) return;
        
        this.isZoomed = false;
        this.zoomOverlay.style.display = 'none';
        document.body.style.overflow = '';
        
        // Return focus
        this.mainImage.focus();
    }
    
    updateZoomImage() {
        if (!this.zoomOverlay || !this.images[this.currentIndex]) return;
        
        const zoomImg = this.zoomOverlay.querySelector('.gallery-zoom-image');
        const currentImg = this.images[this.currentIndex];
        
        zoomImg.src = currentImg.src;
        zoomImg.alt = currentImg.alt;
    }
    
    isInViewport() {
        const rect = this.container.getBoundingClientRect();
        return rect.top < window.innerHeight && rect.bottom > 0;
    }
    
    // Public API methods
    destroy() {
        if (this.swiper) {
            this.swiper.destroy();
        }
        
        if (this.zoomOverlay) {
            this.zoomOverlay.remove();
        }
    }
    
    refresh() {
        this.setupStructure();
        this.updateMainImage();
        this.updateThumbnails();
        this.updateCounter();
    }
}

// Auto-initialize product galleries
document.addEventListener('DOMContentLoaded', function() {
    const galleries = document.querySelectorAll('.product-gallery');
    galleries.forEach(gallery => {
        new ProductGallery(gallery);
    });
});

// Export for manual initialization
window.ProductGallery = ProductGallery;