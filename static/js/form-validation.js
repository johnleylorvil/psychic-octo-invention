// Attend que le contenu de la page soit entièrement chargé avant d'exécuter le script
document.addEventListener('DOMContentLoaded', () => {

  // Ciblez tous les formulaires qui nécessitent une validation.
  // Vous pouvez leur ajouter une classe, par exemple : class="validated-form"
  const formsToValidate = document.querySelectorAll('.validated-form');

  // Fonction pour afficher un message d'erreur
  const showError = (inputElement, message) => {
    const formField = inputElement.parentElement; // On suppose que l'input est dans un div ou autre
    formField.classList.add('error');
    formField.classList.remove('success');

    // Cherche un élément d'erreur existant, sinon en crée un
    let errorElement = formField.querySelector('.error-message');
    if (!errorElement) {
      errorElement = document.createElement('small');
      errorElement.className = 'error-message';
      formField.appendChild(errorElement);
    }
    errorElement.textContent = message;
  };

  // Fonction pour effacer le message d'erreur et marquer comme succès
  const showSuccess = (inputElement) => {
    const formField = inputElement.parentElement;
    formField.classList.remove('error');
    formField.classList.add('success');

    const errorElement = formField.querySelector('.error-message');
    if (errorElement) {
      errorElement.textContent = ''; // Efface le message
    }
  };

  // Fonction de validation principale
  const validateField = (inputElement) => {
    let isValid = false;
    const value = inputElement.value.trim();
    
    // 1. Vérification des champs requis
    if (inputElement.hasAttribute('required') && value === '') {
      showError(inputElement, 'Ce champ est obligatoire.');
      return false;
    }

    // 2. Vérification du format de l'email
    if (inputElement.type === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        showError(inputElement, 'Veuillez entrer une adresse email valide.');
        return false;
      }
    }
    
    // 3. Vérification de la confirmation du mot de passe
    if (inputElement.id === 'password_confirm') {
      const passwordInput = document.querySelector('#password');
      if (passwordInput.value !== value) {
        showError(inputElement, 'Les mots de passe ne correspondent pas.');
        return false;
      }
    }

    showSuccess(inputElement);
    return true;
  };


  // Attache les écouteurs d'événements à chaque formulaire
  formsToValidate.forEach(form => {
    
    // Validation en temps réel quand l'utilisateur quitte un champ
    form.querySelectorAll('input[required], input[type="email"]').forEach(input => {
        input.addEventListener('blur', () => {
            validateField(input);
        });
    });

    // Validation finale lors de la soumission du formulaire
    form.addEventListener('submit', (event) => {
      let isFormValid = true;
      const fieldsToValidate = form.querySelectorAll('input[required], input[type="email"], #password_confirm');

      fieldsToValidate.forEach(input => {
        if (!validateField(input)) {
          isFormValid = false;
        }
      });

      // Si le formulaire n'est pas valide, on empêche son envoi
      if (!isFormValid) {
        event.preventDefault();
        console.log("Le formulaire contient des erreurs et ne sera pas soumis.");
      }
    });
  });

});