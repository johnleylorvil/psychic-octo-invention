// static/js/main.js
// Module principal de l'application Afèpanou

// S'assurer que l'objet global existe
window.afepanouStore = window.afepanouStore || {};

(function() {
    'use strict';

    // --- Initialisation au chargement de la page ---
    document.addEventListener('DOMContentLoaded', function() {
        console.log("Afèpanou Main JS chargé et DOM prêt.");

        // Initialiser les modules
        initMobileMenu();
        initSearchBar(); // Si nécessaire
        initCartIntegration();
        // initSlideshow(); // Si le slideshow a besoin de JS personnalisé, sinon il est géré par home.js

        // Gestion du cookie consent (exemple basique)
        initCookieNotice();
    });

    // --- Gestion du Menu Mobile ---
    function initMobileMenu() {
        const menuBtn = document.querySelector('.mobile-menu-btn');
        const headerContent = document.querySelector('.header-content'); // Ou un autre conteneur spécifique

        if (menuBtn && headerContent) {
            menuBtn.addEventListener('click', function() {
                headerContent.classList.toggle('mobile-open'); // Ajouter cette classe dans votre CSS
                const icon = this.querySelector('i');
                if (icon) {
                    if (headerContent.classList.contains('mobile-open')) {
                        icon.classList.remove('fa-bars');
                        icon.classList.add('fa-times');
                    } else {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
            });
        }
    }

    // --- Gestion de la Barre de Recherche (placeholder) ---
    function initSearchBar() {
        // Ajouter ici la logique pour la recherche si nécessaire (auto-complétion, soumission, etc.)
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            // Exemple: Soumission sur Entrée
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const query = this.value.trim();
                    if (query) {
                        // Rediriger vers une page de résultats ou déclencher une recherche
                        // Exemple: window.location.href = `/search?q=${encodeURIComponent(query)}`;
                        console.log("Recherche pour:", query);
                        alert(`La recherche pour "${query}" sera implémentée prochainement.`);
                    }
                }
            });
        }
    }

    // --- Intégration avec le Panier ---
    function initCartIntegration() {
        // 1. Initialiser le module du panier s'il existe
        if (typeof afepanouCart !== 'undefined' && afepanouCart.init) {
            // afepanouCart.init() est déjà appelé dans cart.js, mais on peut faire un refresh ici si besoin
            console.log("Module afepanouCart trouvé, initialisation supplémentaire si nécessaire.");
            // afepanouCart.loadCart(); // Déjà fait dans son init
        }

        // 2. Lier le bouton du panier dans le header à l'affichage du panier
        const showCartBtn = document.querySelector('.action-btn[aria-label="Panier d\'achat"]'); // Plus spécifique
        if (showCartBtn && typeof afepanouCart !== 'undefined' && afepanouCart.show) {
            // Retirer l'onclick inline du HTML si présent et gérer ici
            showCartBtn.removeAttribute('onclick'); // Supprime l'attribut onclick
            showCartBtn.addEventListener('click', function(e) {
                e.preventDefault(); // Empêcher tout comportement par défaut
                console.log("Bouton panier du header cliqué.");
                afepanouCart.show(); // Appelle la méthode show du module afepanouCart
            });
        } else if(showCartBtn) {
             // Fallback si le module n'est pas chargé
             console.warn("Module afepanouCart non trouvé, fallback sur onclick inline ou alerte.");
             // Si onclick inline est toujours là, il fonctionnera. Sinon, on peut ajouter un fallback.
             // showCartBtn.addEventListener('click', () => alert("Panier (à implémenter)"));
        }

        // 3. Charger l'état initial du panier (nombre d'articles) au chargement de la page
        loadInitialCartState();
    }

    // Charger l'état initial du panier (badge)
    function loadInitialCartState() {
        console.log("Chargement de l'état initial du panier...");
        // Utiliser la même logique que dans afepanouCart.loadCart
         fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                 'X-CSRFToken': getCsrfToken() // Utiliser la fonction utilitaire
            },
            body: new URLSearchParams({
                'action': 'cart'
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("État initial du panier chargé:", data);
            // Mettre à jour le badge
            const cartBadge = document.getElementById('cart-badge');
            if (cartBadge) {
                cartBadge.textContent = data.total_items || 0;
                if (data.total_items > 0) {
                    cartBadge.classList.remove('hidden');
                } else {
                    cartBadge.classList.add('hidden');
                }
            }
            // Si afepanouCart existe, on peut aussi l'initialiser avec ces données
            // pour éviter un deuxième appel AJAX immédiat
            // if (typeof afepanouCart !== 'undefined') {
            //     afepanouCart.updateCartDisplay(data); // Nécessite adaptation de afepanouCart
            // }
        })
        .catch(error => {
            console.error('Erreur lors du chargement de l\'état initial du panier:', error);
            // En cas d'erreur, on peut masquer le badge ou le laisser à 0
        });
    }


    // --- Gestion de la Notification de Cookies ---
    function initCookieNotice() {
        const cookieNotice = document.getElementById('cookie-notice');
        const acceptBtn = document.getElementById('accept-cookies');
        const declineBtn = document.getElementById('decline-cookies');

        if (cookieNotice) {
            // Vérifier si l'utilisateur a déjà accepté/refusé
            if (!localStorage.getItem('cookiesAccepted')) {
                // Afficher la notice après un court délai
                setTimeout(() => {
                    cookieNotice.classList.add('show');
                }, 1000);
            }

            if (acceptBtn) {
                acceptBtn.addEventListener('click', function() {
                    localStorage.setItem('cookiesAccepted', 'true');
                    cookieNotice.classList.remove('show');
                    console.log("Cookies acceptés par l'utilisateur.");
                    // Ici, vous pouvez initialiser les services qui nécessitent des cookies
                });
            }

            if (declineBtn) {
                declineBtn.addEventListener('click', function() {
                    localStorage.setItem('cookiesAccepted', 'false');
                    cookieNotice.classList.remove('show');
                    console.log("Cookies refusés par l'utilisateur.");
                    // Ici, vous pouvez désactiver les services non essentiels
                });
            }
        }
    }

    // --- Fonction utilitaire pour obtenir le token CSRF ---
    function getCsrfToken() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfTokenElement ? csrfTokenElement.value : '';
    }

    // --- Fonction pour afficher les modales (comme le panier) ---
    // Cette fonction peut servir de pont si d'autres parties du site veulent ouvrir le panier
    window.afepanouStore.showModal = function(modalId) {
        console.log(`Tentative d'ouverture de la modale: ${modalId}`);
        if (modalId === 'cart-sidebar' && typeof afepanouCart !== 'undefined' && afepanouCart.show) {
            afepanouCart.show();
        } else {
            // Gérer d'autres modales si nécessaire
            const modal = document.getElementById(modalId);
            if (modal) {
                // Logique générique pour ouvrir d'autres modales
                // Exemple: modal.classList.add('show');
                 console.warn(`Logique d'ouverture pour la modale '${modalId}' non implémentée ou module non trouvé.`);
            } else {
                 console.error(`Modale avec l'ID '${modalId}' non trouvée.`);
            }
        }
    };

    // --- Autres initialisations globales peuvent aller ici ---

})();