document.addEventListener('DOMContentLoaded', () => {

  // --- 1. Initialisation du Carrousel (Bannière) ---
  // NOTE: Nécessite l'ajout de la bibliothèque Swiper.js à votre projet.
  const heroCarousel = document.querySelector('.hero-carousel');
  if (heroCarousel) {
    const swiper = new Swiper('.hero-carousel', {
      // Options
      loop: true,
      effect: 'fade', // Effet de transition fondu
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },

      // Pagination (les points)
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },

      // Flèches de navigation
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
    });
  }


  // --- 2. Mobile Navigation (Burger Menu) ---
  const burgerMenu = document.querySelector('.burger-menu');
  const mainNav = document.querySelector('.main-nav');

  if (burgerMenu && mainNav) {
    burgerMenu.addEventListener('click', () => {
      burgerMenu.classList.toggle('is-active');
      mainNav.classList.toggle('is-active');
    });
  }


  // --- 3. User Account Dropdown ---
  const accountBtn = document.querySelector('.account-btn');
  const accountDropdown = document.querySelector('.account-dropdown');

  if (accountBtn && accountDropdown) {
    accountBtn.addEventListener('click', (event) => {
      event.stopPropagation();
      accountDropdown.classList.toggle('is-active');
    });

    window.addEventListener('click', () => {
      if (accountDropdown.classList.contains('is-active')) {
        accountDropdown.classList.remove('is-active');
      }
    });
  }


  // --- 4. Sticky Header on Scroll ---
  const header = document.querySelector('.main-header');
  if (header) {
    const stickyThreshold = 50;

    window.addEventListener('scroll', () => {
      if (window.scrollY > stickyThreshold) {
        header.classList.add('is-sticky');
      } else {
        header.classList.remove('is-sticky');
      }
    });
  }


  // --- 5. "Growth Motion" Animations on Scroll ---
  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });

    animatedElements.forEach(el => {
      observer.observe(el);
    });
  }

});