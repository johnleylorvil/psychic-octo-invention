// static/js/cart.js
// Objet global pour gérer les fonctionnalités du panier
const afepanouCart = {
    // Éléments DOM
    cartSidebar: document.getElementById('cart-sidebar'),
    cartOverlay: document.getElementById('cart-overlay'),
    closeCartBtn: document.getElementById('close-cart-btn'),
    cartItemsContainer: document.getElementById('cart-items-container'),
    cartItemsList: document.getElementById('cart-items-list'),
    cartEmptyMessage: document.getElementById('cart-empty-message'),
    cartTotalAmount: document.getElementById('cart-total-amount'),
    cartBadge: document.getElementById('cart-badge'),
    checkoutBtn: document.getElementById('checkout-btn'),
    continueShoppingBtn: document.getElementById('continue-shopping-btn'),

    // Initialisation
    init: function() {
        console.log("Initialisation du module afepanouCart...");
        if (this.cartSidebar) {
            this.bindEvents();
            // this.loadCart(); // Déjà chargé par main.js au démarrage si nécessaire
        } else {
            console.warn("Éléments du panier non trouvés dans le DOM.");
        }
    },

    // Liaison des événements
    bindEvents: function() {
        // Fermer le panier
        if (this.closeCartBtn) {
            this.closeCartBtn.addEventListener('click', () => this.hide());
        }
        if (this.cartOverlay) {
            this.cartOverlay.addEventListener('click', () => this.hide());
        }

        // Boutons d'action dans le panier
        if (this.checkoutBtn) {
            this.checkoutBtn.addEventListener('click', () => this.proceedToCheckout());
        }
        if (this.continueShoppingBtn) {
            this.continueShoppingBtn.addEventListener('click', () => this.hide());
        }

        // Gestion des événements dynamiques pour les articles du panier
        // (Les articles sont ajoutés dynamiquement, donc on délègue l'écoute)
        if (this.cartItemsList) {
            this.cartItemsList.addEventListener('click', (e) => {
                const target = e.target;
                const cartItem = target.closest('.cart-item'); // Trouve l'article parent
                
                if (!cartItem) return; // Si pas dans un article, on sort

                const itemId = cartItem.getAttribute('data-cart-item-id');

                if (target.closest('.increase-qty')) {
                    this.updateQuantity(itemId, 1);
                } else if (target.closest('.decrease-qty')) {
                    this.updateQuantity(itemId, -1);
                } else if (target.closest('.remove-item')) {
                    this.removeItem(itemId);
                }
            });
        }
    },

    // Afficher le panier
    show: function() {
        console.log("Affichage du panier...");
        if (this.cartOverlay) this.cartOverlay.classList.add('show');
        if (this.cartSidebar) this.cartSidebar.classList.add('show');
        document.body.style.overflow = 'hidden'; // Empêcher le scroll de la page
        // S'assurer que le panier est à jour quand il s'ouvre
        this.loadCart(); 
    },

    // Cacher le panier
    hide: function() {
        console.log("Fermeture du panier...");
        if (this.cartOverlay) this.cartOverlay.classList.remove('show');
        if (this.cartSidebar) this.cartSidebar.classList.remove('show');
        document.body.style.overflow = ''; // Réactiver le scroll
    },

    // Charger le contenu du panier depuis le backend
    loadCart: function() {
        console.log("Chargement du contenu du panier...");
        // Appel à l'API StoreView avec action='cart'
        fetch(window.location.pathname, { // Ou une URL dédiée si préféré
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                if(response.status === 404) {
                     // Cas spécifique si l'URL n'est pas bonne pour GET cart
                     // On peut aussi faire un appel à une URL connue, ex: `/api/cart/`
                     // Pour cet exemple, on reste générique.
                     console.warn("GET sur l'URL actuelle pour 'cart' a échoué. Essai via POST.");
                     return this.fetchCartViaPost();
                }
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Données du panier reçues:", data);
            this.updateCartDisplay(data);
        })
        .catch(error => {
            console.error('Erreur lors du chargement du panier:', error);
            this.showErrorMessage("Impossible de charger le panier.");
        });
    },

    // Alternative: Charger le panier via POST (si GET n'est pas supporté pour 'cart')
    fetchCartViaPost: function() {
         return fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: new URLSearchParams({
                'action': 'cart'
            })
        }).then(response => response.json());
    },

    // Mettre à jour l'affichage du panier avec les données reçues
    updateCartDisplay: function(cartData) {
        if (!this.cartItemsList || !this.cartEmptyMessage || !this.cartTotalAmount) {
            console.error("Éléments DOM du panier manquants pour la mise à jour.");
            return;
        }

        // Effacer le contenu actuel
        this.cartItemsList.innerHTML = '';

        if (cartData.items && cartData.items.length > 0) {
            // Masquer le message vide, afficher la liste
            this.cartEmptyMessage.classList.add('hidden');
            this.cartItemsList.classList.remove('hidden');

            // Créer et ajouter chaque article
            cartData.items.forEach(item => {
                const itemElement = this.createCartItemElement(item);
                this.cartItemsList.appendChild(itemElement);
            });

            // Mettre à jour le total
            this.cartTotalAmount.textContent = `${parseFloat(cartData.total_amount).toFixed(2)} HTG`;

            // Activer le bouton de checkout
            if (this.checkoutBtn) {
                this.checkoutBtn.disabled = false;
                this.checkoutBtn.classList.remove('btn-ghost');
                this.checkoutBtn.classList.add('btn-primary');
                this.checkoutBtn.href = '#'; // Ou une URL de checkout si elle est connue
            }
        } else {
            // Afficher le message vide, masquer la liste
            this.cartEmptyMessage.classList.remove('hidden');
            this.cartItemsList.classList.add('hidden');
            this.cartTotalAmount.textContent = '0 HTG';

            // Désactiver le bouton de checkout
            if (this.checkoutBtn) {
                this.checkoutBtn.disabled = true;
                this.checkoutBtn.classList.remove('btn-primary');
                this.checkoutBtn.classList.add('btn-ghost');
                this.checkoutBtn.href = '#';
            }
        }

        // Mettre à jour le badge dans le header
        this.updateCartBadge(cartData.total_items);
    },

    // Créer un élément DOM pour un article du panier
    createCartItemElement: function(item) {
        // Utiliser document.createElement ou innerHTML. innerHTML est plus concis ici.
        const itemDiv = document.createElement('article');
        itemDiv.className = 'cart-item flex border border-light rounded-xl overflow-hidden animate-fade-in-up';
        itemDiv.setAttribute('data-cart-item-id', item.id);

        // Placeholder pour l'URL de l'image si elle n'existe pas
        const imageUrl = item.image_url || '/static/images/placeholder-product.jpg';

        itemDiv.innerHTML = `
            <div class="cart-item-image w-24 bg-beige flex items-center justify-center flex-shrink-0">
                <img src="${imageUrl}" alt="${item.name}" class="w-full h-full object-cover">
            </div>
            <div class="cart-item-details flex-grow p-4">
                <h3 class="cart-item-title font-medium text-dark mb-1">${item.name}</h3>
                <p class="cart-item-price text-primary font-semibold text-lg mb-3">${parseFloat(item.price).toFixed(2)} HTG</p>
                <div class="cart-item-quantity flex items-center justify-between">
                    <div class="flex items-center border border-light rounded-full overflow-hidden">
                        <button type="button" class="decrease-qty px-3 py-1 text-lg hover:bg-beige transition">-</button>
                        <span class="quantity-display px-3 py-1 text-center w-12">${item.quantity}</span>
                        <button type="button" class="increase-qty px-3 py-1 text-lg hover:bg-beige transition">+</button>
                    </div>
                    <button type="button" class="remove-item text-muted hover:text-red-500 transition" aria-label="Supprimer l'article">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                 <p class="cart-item-total text-dark font-semibold mt-2">Total: ${(item.quantity * item.price).toFixed(2)} HTG</p>
            </div>
        `;
        return itemDiv;
    },

    // Mettre à jour la quantité d'un article
    updateQuantity: function(itemId, change) {
        console.log(`Mise à jour de la quantité pour l'item ${itemId} de ${change}`);
        const itemElement = document.querySelector(`.cart-item[data-cart-item-id="${itemId}"]`);
        if (!itemElement) {
            console.error("Élément d'article non trouvé pour la mise à jour.");
            return;
        }

        const quantityDisplay = itemElement.querySelector('.quantity-display');
        let currentQuantity = parseInt(quantityDisplay.textContent);

        if (isNaN(currentQuantity)) {
            console.error("Quantité actuelle invalide.");
            return;
        }

        const newQuantity = currentQuantity + change;

        // Empêcher une quantité négative ou nulle via décrémentation
        if (newQuantity < 1) {
            this.removeItem(itemId); // Supprimer si quantité <= 0
            return;
        }

        // Animation ou feedback visuel (optionnel)
        quantityDisplay.textContent = newQuantity;
        quantityDisplay.classList.add('animate-pulse');
        setTimeout(() => quantityDisplay.classList.remove('animate-pulse'), 300);

        // Appel AJAX pour mettre à jour le backend
        this.sendCartAction('update_cart', { item_id: itemId, quantity: newQuantity })
            .then(data => {
                console.log("Quantité mise à jour avec succès:", data);
                // Mettre à jour l'affichage complet du panier avec les données du serveur
                // (Cela garantit que les totaux sont recalculés correctement côté serveur)
                this.updateCartDisplay(data);
                 // Mettre à jour le total de l'article spécifique
                 const itemTotalElement = itemElement.querySelector('.cart-item-total');
                 if (itemTotalElement && data.items) {
                      const updatedItem = data.items.find(i => i.id == itemId);
                      if (updatedItem) {
                          itemTotalElement.textContent = `Total: ${(updatedItem.quantity * updatedItem.price).toFixed(2)} HTG`;
                      }
                 }
            })
            .catch(error => {
                console.error("Erreur lors de la mise à jour de la quantité:", error);
                // Rétablir l'ancienne quantité en cas d'erreur
                quantityDisplay.textContent = currentQuantity;
                this.showErrorMessage("Impossible de mettre à jour la quantité.");
            });
    },

    // Supprimer un article du panier
    removeItem: function(itemId) {
        console.log(`Suppression de l'item ${itemId}`);
        if (!confirm("Êtes-vous sûr de vouloir supprimer cet article ?")) {
            return; // Annuler si l'utilisateur clique sur "Annuler"
        }

        const itemElement = document.querySelector(`.cart-item[data-cart-item-id="${itemId}"]`);
        if (!itemElement) {
            console.error("Élément d'article non trouvé pour la suppression.");
            return;
        }

        // Animation de suppression (optionnelle)
        itemElement.style.transition = 'opacity 0.3s, transform 0.3s';
        itemElement.style.opacity = '0';
        itemElement.style.transform = 'translateX(100px)';

        // Appel AJAX pour supprimer côté backend
        this.sendCartAction('remove_from_cart', { item_id: itemId })
            .then(data => {
                console.log("Article supprimé avec succès:", data);
                // Attendre la fin de l'animation avant de retirer du DOM
                setTimeout(() => {
                    itemElement.remove();
                    // Mettre à jour l'affichage complet du panier
                    this.updateCartDisplay(data);
                }, 300);
            })
            .catch(error => {
                console.error("Erreur lors de la suppression de l'article:", error);
                // Annuler l'animation en cas d'erreur
                itemElement.style.opacity = '';
                itemElement.style.transform = '';
                this.showErrorMessage("Impossible de supprimer l'article.");
            });
    },

    // Procéder au paiement
    proceedToCheckout: function() {
        console.log("Procéder au checkout...");
        if (!this.checkoutBtn || this.checkoutBtn.disabled) {
            console.warn("Bouton de checkout désactivé ou non trouvé.");
            return;
        }

        // Indicateur de chargement
        const originalHtml = this.checkoutBtn.innerHTML;
        this.checkoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Préparation...';
        this.checkoutBtn.disabled = true;

        // 1. Appeler l'action 'checkout' pour créer la commande
        this.sendCartAction('checkout')
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                console.log("Commande créée:", data);
                // 2. Appeler l'action 'moncash_payment' pour obtenir l'URL de paiement
                return this.sendCartAction('moncash_payment', { order_number: data.order_number });
            })
            .then(paymentData => {
                if (paymentData.error) {
                    throw new Error(paymentData.error);
                }
                console.log("URL de paiement obtenue:", paymentData.payment_url);
                // 3. Rediriger l'utilisateur vers l'URL MonCash
                window.location.href = paymentData.payment_url;
            })
            .catch(error => {
                console.error("Erreur lors du checkout:", error);
                this.showErrorMessage("Échec de la préparation du paiement. Veuillez réessayer.");
                // Rétablir le bouton
                if (this.checkoutBtn) {
                    this.checkoutBtn.innerHTML = originalHtml;
                    this.checkoutBtn.disabled = false;
                }
            });
    },

    // Fonction utilitaire pour envoyer les actions du panier
    sendCartAction: function(action, additionalData = {}) {
        const url = window.location.pathname; // URL du store actuel
        const data = new URLSearchParams();
        data.append('action', action);
        for (const key in additionalData) {
            data.append(key, additionalData[key]);
        }
        data.append('csrfmiddlewaretoken', this.getCsrfToken());

        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                // X-CSRFToken est inclus dans les données POST ici
            },
            body: data
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || `Erreur ${response.status}`);
                });
            }
            return response.json();
        });
    },

    // Mettre à jour le badge du panier dans le header
    updateCartBadge: function(totalItems) {
        if (this.cartBadge) {
            this.cartBadge.textContent = totalItems;
            if (totalItems > 0) {
                this.cartBadge.classList.remove('hidden');
                // Ajouter une animation si souhaité (nécessite un keyframe CSS)
                this.cartBadge.classList.add('animate-pulse');
                setTimeout(() => this.cartBadge.classList.remove('animate-pulse'), 1000);
            } else {
                this.cartBadge.classList.add('hidden');
            }
        }
    },

    // Afficher un message d'erreur à l'utilisateur (à améliorer)
    showErrorMessage: function(message) {
        alert(message); // Placeholder basique
        // TODO: Utiliser un système de notification plus élaboré
    },

    // Récupérer le token CSRF (nécessaire pour les requêtes POST Django)
    getCsrfToken: function() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfTokenElement ? csrfTokenElement.value : '';
    }
};

// Initialiser le module une fois le DOM chargé
document.addEventListener('DOMContentLoaded', function() {
    afepanouCart.init();
});

// Exporter pour un usage global si nécessaire (optionnel, selon le module bundler)
// window.afepanouCart = afepanouCart;