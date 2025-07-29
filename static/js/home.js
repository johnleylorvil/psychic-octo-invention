// AFEPANOU MARKETPLACE - HOME.JS
// Slideshow + Homepage Interactions

class HomepageController {
  constructor() {
    this.slideIndex = 1;
    this.slides = [];
    this.dots = [];
    this.autoSlideInterval = null;
    this.isSliding = false;
    this.init();
  }

  init() {
    this.initSlideshow();
    this.initProductGrid();
    this.initContentCards();
    this.initScrollAnimations();
    this.initCTAButtons();
  }

  // SLIDESHOW FUNCTIONALITY
  initSlideshow() {
    this.slides = document.querySelectorAll('.slide');
    this.dots = document.querySelectorAll('.slide-dot');
    
    if (this.slides.length === 0) return;

    // Initialize first slide
    this.showSlide(1);
    
    // Dot navigation
    this.dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        this.currentSlide(index + 1);
      });
    });

    // Arrow navigation
    const prevBtn = document.querySelector('.slide-prev');
    const nextBtn = document.querySelector('.slide-next');
    
    if (prevBtn) prevBtn.addEventListener('click', () => this.previousSlide());
    if (nextBtn) nextBtn.addEventListener('click', () => this.nextSlide());

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') this.previousSlide();
      if (e.key === 'ArrowRight') this.nextSlide();
    });

    // Touch/swipe support
    this.initTouchControls();

    // Auto-advance
    this.startAutoSlide();

    // Pause on hover
    const hero = document.querySelector('.hero');
    if (hero) {
      hero.addEventListener('mouseenter', () => this.stopAutoSlide());
      hero.addEventListener('mouseleave', () => this.startAutoSlide());
    }
  }

  showSlide(n) {
    if (this.isSliding) return;
    
    if (n > this.slides.length) this.slideIndex = 1;
    if (n < 1) this.slideIndex = this.slides.length;
    
    this.isSliding = true;
    
    // Update slides
    this.slides.forEach(slide => slide.classList.remove('active'));
    this.dots.forEach(dot => dot.classList.remove('active'));
    
    if (this.slides[this.slideIndex - 1]) {
      this.slides[this.slideIndex - 1].classList.add('active');
    }
    
    if (this.dots[this.slideIndex - 1]) {
      this.dots[this.slideIndex - 1].classList.add('active');
    }

    // Reset sliding flag
    setTimeout(() => {
      this.isSliding = false;
    }, 1200);
  }

  currentSlide(n) {
    this.slideIndex = n;
    this.showSlide(this.slideIndex);
  }

  nextSlide() {
    this.slideIndex++;
    this.showSlide(this.slideIndex);
  }

  previousSlide() {
    this.slideIndex--;
    this.showSlide(this.slideIndex);
  }

  startAutoSlide() {
    this.stopAutoSlide();
    this.autoSlideInterval = setInterval(() => {
      this.nextSlide();
    }, 5000);
  }

  stopAutoSlide() {
    if (this.autoSlideInterval) {
      clearInterval(this.autoSlideInterval);
      this.autoSlideInterval = null;
    }
  }

  // TOUCH CONTROLS
  initTouchControls() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    let startX = 0;
    let startY = 0;
    let endX = 0;
    let endY = 0;

    hero.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });

    hero.addEventListener('touchmove', (e) => {
      e.preventDefault();
    });

    hero.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      endY = e.changedTouches[0].clientY;
      
      const deltaX = startX - endX;
      const deltaY = startY - endY;
      
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          this.nextSlide();
        } else {
          this.previousSlide();
        }
      }
    });
  }

  // PRODUCT GRID INTERACTIONS
  initProductGrid() {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach((card, index) => {
      // Staggered animation
      card.style.animationDelay = `${index * 0.1}s`;
      
      // Hover effects
      card.addEventListener('mouseenter', () => {
        this.animateProductIcon(card);
      });

      // Click handling
      card.addEventListener('click', (e) => {
        if (!e.target.matches('.product-btn')) {
          this.handleProductClick(card);
        }
      });
    });
  }

  animateProductIcon(card) {
    const icon = card.querySelector('.product-image i');
    if (icon) {
      icon.style.transform = 'scale(1.2) rotate(5deg)';
      setTimeout(() => {
        icon.style.transform = 'scale(1) rotate(0deg)';
      }, 300);
    }
  }

  handleProductClick(card) {
    const title = card.querySelector('.product-title')?.textContent;
    console.log(`Navigating to product: ${title}`);
    // TODO: Implement navigation to product category
  }

  // CONTENT CARDS
  initContentCards() {
    const contentCards = document.querySelectorAll('.content-card');
    
    contentCards.forEach(card => {
      // Tag interactions
      const tags = card.querySelectorAll('.tag');
      tags.forEach(tag => {
        tag.addEventListener('click', (e) => {
          e.stopPropagation();
          this.handleTagClick(tag.textContent);
        });
      });

      // Card click
      card.addEventListener('click', () => {
        this.handleContentClick(card);
      });
    });
  }

  handleTagClick(tagName) {
    console.log(`Filtering by tag: ${tagName}`);
    // TODO: Implement tag filtering
  }

  handleContentClick(card) {
    const title = card.querySelector('.content-title')?.textContent;
    console.log(`Opening content: ${title}`);
    // TODO: Implement content navigation
  }

  // SCROLL ANIMATIONS
  initScrollAnimations() {
    const sections = document.querySelectorAll('.popular-products, .media-content');
    
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.animateSection(entry.target);
        }
      });
    }, {
      threshold: 0.2,
      rootMargin: '0px 0px -100px 0px'
    });

    sections.forEach(section => {
      sectionObserver.observe(section);
    });

    // Parallax effect for background patterns
    this.initParallax();
  }

  animateSection(section) {
    const cards = section.querySelectorAll('.product-card, .content-card');
    
    cards.forEach((card, index) => {
      setTimeout(() => {
        card.classList.add('animate-fade-in-up');
      }, index * 100);
    });
  }

  initParallax() {
    const parallaxElements = document.querySelectorAll('.popular-products::before');
    
    window.addEventListener('scroll', this.throttle(() => {
      const scrolled = window.pageYOffset;
      const rate = scrolled * -0.5;
      
      parallaxElements.forEach(el => {
        el.style.transform = `translate3d(0, ${rate}px, 0)`;
      });
    }, 10));
  }

  // CTA BUTTONS
  initCTAButtons() {
    const ctaButtons = document.querySelectorAll('.cta-hero, .btn-cta-primary, .btn-cta-secondary');
    
    ctaButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        this.handleCTAClick(e, button);
      });

      // Growth arrow animation
      const arrow = button.querySelector('.growth-arrow, i');
      if (arrow) {
        button.addEventListener('mouseenter', () => {
          arrow.style.transform = 'rotate(-45deg) translate(3px, -3px)';
        });
        
        button.addEventListener('mouseleave', () => {
          arrow.style.transform = 'rotate(-45deg) translate(0, 0)';
        });
      }
    });
  }

  handleCTAClick(e, button) {
    e.preventDefault();
    
    const buttonText = button.textContent.trim();
    
    if (buttonText.includes('Explorer')) {
      this.scrollToProducts();
    } else if (buttonText.includes('Artisanats')) {
      this.navigateToCategory('artisanats');
    } else if (buttonText.includes('Agricole')) {
      this.navigateToCategory('agriculture');
    } else {
      console.log(`CTA clicked: ${buttonText}`);
    }
  }

  scrollToProducts() {
    const productsSection = document.querySelector('.popular-products');
    if (productsSection) {
      productsSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  navigateToCategory(category) {
    console.log(`Navigating to category: ${category}`);
    // TODO: Implement category navigation
  }

  // UTILITY FUNCTIONS
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

  // RESIZE HANDLING
  handleResize() {
    // Recalculate slideshow dimensions
    clearTimeout(this.resizeTimeout);
    this.resizeTimeout = setTimeout(() => {
      this.showSlide(this.slideIndex);
    }, 250);
  }

  // CLEANUP
  destroy() {
    this.stopAutoSlide();
    
    // Remove event listeners
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('keydown', this.handleKeydown);
    
    // Clear timeouts
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
  }
}

// Initialize homepage controller
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('.hero')) {
    window.homepageController = new HomepageController();
  }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
  if (window.homepageController) {
    if (document.hidden) {
      window.homepageController.stopAutoSlide();
    } else {
      window.homepageController.startAutoSlide();
    }
  }
});

// Handle resize
window.addEventListener('resize', () => {
  if (window.homepageController) {
    window.homepageController.handleResize();
  }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HomepageController;
}