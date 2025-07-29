// AFEPANOU MARKETPLACE - MAIN.JS
// Utils, Animations, Cart, Search

class AfepanouApp {
  constructor() {
    this.cart = { items: [], count: 0 };
    this.searchTimeout = null;
    this.init();
  }

  init() {
    this.initHeader();
    this.initSearch();
    this.initCart();
    this.initAnimations();
    this.initScrollEffects();
    this.initRippleEffects();
  }

  // HEADER FUNCTIONALITY
  initHeader() {
    const header = document.getElementById('header');
    if (!header) return;

    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });

    // Mobile menu toggle
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const navCategories = document.querySelector('.nav-categories');
    
    if (mobileBtn && navCategories) {
      mobileBtn.addEventListener('click', () => {
        navCategories.classList.toggle('mobile-active');
      });
    }
  }

  // SEARCH FUNCTIONALITY
  initSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
      clearTimeout(this.searchTimeout);
      const query = e.target.value.trim();
      
      if (query.length > 2) {
        this.searchTimeout = setTimeout(() => {
          this.performSearch(query);
        }, 300);
        
        // Visual feedback
        searchInput.style.borderColor = 'var(--forest-green)';
        setTimeout(() => {
          searchInput.style.borderColor = 'var(--primary-orange)';
        }, 500);
      }
    });

    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.performSearch(searchInput.value.trim());
      }
    });
  }

  performSearch(query) {
    console.log(`Searching for: ${query}`);
    // TODO: Implement actual search API call
  }

  // CART FUNCTIONALITY
  initCart() {
    this.loadCart();
    this.updateCartBadge();

    // Add to cart buttons
    document.addEventListener('click', (e) => {
      if (e.target.matches('.product-btn, .btn-add-cart')) {
        e.preventDefault();
        this.addToCart(e.target);
      }
    });
  }

  addToCart(button) {
    const productCard = button.closest('.product-card, .content-card');
    if (!productCard) return;

    const product = {
      id: Date.now(),
      title: productCard.querySelector('.product-title, .content-title')?.textContent || 'Product',
      price: 0,
      quantity: 1
    };

    this.cart.items.push(product);
    this.cart.count++;
    this.saveCart();
    this.updateCartBadge();
    this.showCartNotification();
  }

  updateCartBadge() {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
      badge.textContent = this.cart.count;
      badge.style.transform = 'scale(1.2)';
      setTimeout(() => {
        badge.style.transform = 'scale(1)';
      }, 200);
    }
  }

  showCartNotification() {
    const notification = document.createElement('div');
    notification.className = 'cart-notification';
    notification.innerHTML = `
      <i class="fas fa-check-circle"></i>
      <span>Produit ajouté au panier</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 2000);
  }

  saveCart() {
    try {
      localStorage.setItem('afepanou_cart', JSON.stringify(this.cart));
    } catch (e) {
      console.warn('Could not save cart to localStorage');
    }
  }

  loadCart() {
    try {
      const saved = localStorage.getItem('afepanou_cart');
      if (saved) {
        this.cart = JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Could not load cart from localStorage');
    }
  }

  // ANIMATIONS
  initAnimations() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });

    // Logo glow animation
    const logo = document.querySelector('.logo');
    if (logo) {
      logo.addEventListener('mouseenter', () => {
        logo.style.animation = 'logoGlow 0.5s ease-in-out';
      });
      
      logo.addEventListener('mouseleave', () => {
        logo.style.animation = 'logoGlow 3s ease-in-out infinite alternate';
      });
    }
  }

  // SCROLL EFFECTS
  initScrollEffects() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
        }
      });
    }, observerOptions);

    // Observe scroll reveal elements
    document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right').forEach(el => {
      observer.observe(el);
    });

    // Staggered card animations
    document.querySelectorAll('.product-card, .content-card').forEach((card, index) => {
      card.style.animationDelay = `${index * 0.1}s`;
      observer.observe(card);
    });
  }

  // RIPPLE EFFECTS
  initRippleEffects() {
    document.addEventListener('click', (e) => {
      if (e.target.matches('.btn, .product-btn, .nav-btn, .action-btn')) {
        this.createRipple(e);
      }
    });
  }

  createRipple(e) {
    const button = e.target;
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  }

  // UTILITY FUNCTIONS
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  throttle(func, limit) {
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
  }

  // PERFORMANCE OPTIMIZATION
  lazyLoadImages() {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.classList.remove('lazy');
              imageObserver.unobserve(img);
            }
          }
        });
      });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }

  // ACCESSIBILITY
  initAccessibility() {
    // Skip to main content
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link';
    skipLink.textContent = 'Aller au contenu principal';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Focus management
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        document.body.classList.add('using-keyboard');
      }
    });

    document.addEventListener('mousedown', () => {
      document.body.classList.remove('using-keyboard');
    });
  }
}

// CSS for notifications and accessibility
const styles = `
.cart-notification {
  position: fixed;
  top: 100px;
  right: 20px;
  background: var(--gradient-primary);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-medium);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transform: translateX(100%);
  transition: transform 0.3s ease;
  z-index: 1000;
}

.cart-notification.show {
  transform: translateX(0);
}

.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-orange);
  color: white;
  padding: 8px;
  border-radius: 4px;
  text-decoration: none;
  z-index: 100;
  transition: top 0.3s;
}

.skip-link:focus {
  top: 6px;
}

.using-keyboard *:focus {
  outline: 2px solid var(--primary-orange);
  outline-offset: 2px;
}

.mobile-active {
  display: flex !important;
  flex-direction: column;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  box-shadow: var(--shadow-medium);
  padding: 1rem;
  border-radius: 0 0 15px 15px;
  z-index: 1000;
}

@media (max-width: 768px) {
  .nav-categories {
    display: none;
  }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.afepanouApp = new AfepanouApp();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AfepanouApp;
}