document.addEventListener('DOMContentLoaded', () => {

  /**
   * Retrieves the CSRF token required for Django POST requests.
   * @returns {string} The CSRF token.
   */
  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }

  /**
   * Updates the cart counter in the header.
   * @param {number} count - The new total number of items in the cart.
   */
  function updateCartCounter(count) {
    const cartCounter = document.querySelector('.cart-count');
    if (cartCounter) {
      cartCounter.textContent = count;
      cartCounter.style.display = count > 0 ? 'block' : 'none';
    }
  }

  /**
   * Handles adding a product to the cart.
   * @param {Event} e - The click event.
   */
  async function addToCart(e) {
    const button = e.target;
    const productId = button.dataset.productId;
    const url = button.dataset.url; // URL to the add-to-cart view

    if (!productId || !url) {
      console.error('Product ID or URL is missing from the button.');
      return;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          'product_id': productId,
          'quantity': 1, // Or get from a quantity input
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        updateCartCounter(data.cart_total_items);
        // Optional: Show a success message or animation
        button.textContent = 'Ajouté !';
        setTimeout(() => { button.textContent = 'Ajouter au Panier'; }, 2000);
      } else {
        console.error('Error adding to cart:', data.message);
        alert('Une erreur est survenue.');
      }
    } catch (error) {
      console.error('Fetch error:', error);
    }
  }

  /**
   * Handles updating the quantity of an item in the cart.
   * @param {Event} e - The change event.
   */
  async function updateCartItem(e) {
    const input = e.target;
    const productId = input.dataset.productId;
    const newQuantity = input.value;
    const url = input.dataset.url; // URL to the update-cart view

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          'product_id': productId,
          'quantity': newQuantity,
        }),
      });
      
      const data = await response.json();

      if (data.status === 'success') {
        // Reload the page to see all updates (subtotals, total, etc.)
        // This is the simplest approach. A more advanced version would
        // update the DOM without a reload.
        window.location.reload();
      } else {
         alert(data.message || 'Impossible de mettre à jour le panier.');
      }
    } catch (error) {
       console.error('Fetch error:', error);
    }
  }
  
  /**
   * Handles removing an item from the cart.
   * @param {Event} e - The click event.
   */
  async function removeCartItem(e) {
    const button = e.target;
    const productId = button.dataset.productId;
    const url = button.dataset.url; // URL to the remove-from-cart view

    if (!confirm('Voulez-vous vraiment retirer cet article ?')) {
      return;
    }

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ 'product_id': productId }),
      });
      
      const data = await response.json();

      if (data.status === 'success') {
        // Remove the item's row from the DOM
        button.closest('.cart-item-row').remove();
        updateCartCounter(data.cart_total_items);
        // You would also need to update the cart total on the page
      } else {
         alert(data.message || 'Impossible de retirer l\'article.');
      }
    } catch (error) {
       console.error('Fetch error:', error);
    }
  }


  // --- Event Listeners ---

  // Add to Cart buttons
  document.querySelectorAll('.add-to-cart-btn').forEach(button => {
    button.addEventListener('click', addToCart);
  });

  // Update quantity inputs
  document.querySelectorAll('.cart-quantity-input').forEach(input => {
    input.addEventListener('change', updateCartItem);
  });
  
  // Remove from cart buttons
  document.querySelectorAll('.remove-from-cart-btn').forEach(button => {
    button.addEventListener('click', removeCartItem);
  });

});