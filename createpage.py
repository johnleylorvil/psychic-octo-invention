#!/usr/bin/env python
"""
Script d'insertion des pages statiques pour le site e-commerce
Ce script ajoute les pages essentielles : À Propos, CGU, Politique de Confidentialité, etc.
"""

import os
import sys
import django
from datetime import datetime
import pytz

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from marketplace.models import Page, Category

def create_static_pages():
    """Crée les pages statiques essentielles dans la base de données"""
    print("Création des pages statiques...")
    
    # Vérifier si les catégories principales existent
    main_categories = [
        'agricole', 'patriotiques', 'petite-industrie', 
        'services', 'store-produits-de-premiere-necessite'
    ]
    
    for slug in main_categories:
        try:
            Category.objects.get(slug=slug)
            print(f"✅ Catégorie existante trouvée: {slug}")
        except Category.DoesNotExist:
            print(f"❌ Catégorie non trouvée: {slug}. Veuillez créer les catégories principales avant d'exécuter ce script.")
    
    static_pages = [
        {
            'title': 'À Propos de Nous',
            'slug': 'a-propos',
            'content': '<h2>Notre Histoire</h2>\n<p>Nous sommes une plateforme de commerce électronique haïtienne créée en 2023 avec pour mission de promouvoir les produits locaux et de soutenir les entrepreneurs haïtiens.</p>\n\n<h2>Notre Mission</h2>\n<p>Notre mission est de connecter les producteurs haïtiens avec des consommateurs locaux et internationaux, en mettant en avant la qualité et l\'authenticité des produits haïtiens.</p>\n\n<h2>Nos Valeurs</h2>\n<ul>\n<li><strong>Patriotisme</strong> : Promouvoir les produits haïtiens avec fierté</li>\n<li><strong>Qualité</strong> : Sélectionner des produits de haute qualité</li>\n<li><strong>Service</strong> : Offrir un service client exceptionnel</li>\n<li><strong>Transparence</strong> : Être clair sur nos processus et nos produits</li>\n</ul>',
            'excerpt': 'Découvrez notre histoire et notre engagement envers les produits haïtiens.',
            'featured_image': '/media/pages/about-us.jpg',
            'template': 'default',
            'meta_title': 'À Propos de Nous - Boutique Haïtienne',
            'meta_description': 'Découvrez notre histoire et notre engagement envers les produits haïtiens.',
            'is_active': True,
            'is_featured': True,
            'sort_order': 1
        },
        {
            'title': 'Conditions Générales d\'Utilisation',
            'slug': 'cgu',
            'content': '<h2>1. Acceptation des Conditions</h2>\n<p>En utilisant ce site web, vous acceptez d\'être lié par les présentes conditions générales d\'utilisation.</p>\n\n<h2>2. Commandes et Paiements</h2>\n<p>Toutes les commandes passées sur notre site sont soumises à disponibilité des produits. Les prix sont indiqués en gourdes haïtiennes (HTG).</p>\n\n<h2>3. Livraison</h2>\n<p>Nous livrons dans toute Haïti. Les délais de livraison varient selon la région. Les produits numériques sont disponibles immédiatement après paiement.</p>\n\n<h2>4. Retours et Remboursements</h2>\n<p>Les produits physiques peuvent être retournés dans les 14 jours suivant la réception. Les produits numériques ne sont pas remboursables.</p>\n\n<h2>5. Propriété Intellectuelle</h2>\n<p>Tout le contenu de ce site est la propriété de notre entreprise et est protégé par les lois haïtiennes sur la propriété intellectuelle.</p>\n\n<h2>6. Modifications des Conditions</h2>\n<p>Nous nous réservons le droit de modifier ces conditions à tout moment. Les modifications prendront effet immédiatement après leur publication sur ce site.</p>',
            'excerpt': 'Conditions d\'utilisation de notre plateforme de commerce électronique.',
            'template': 'default',
            'meta_title': 'Conditions Générales d\'Utilisation - Boutique Haïtienne',
            'meta_description': 'Consultez nos conditions générales d\'utilisation pour commander en toute sécurité.',
            'is_active': True,
            'is_featured': False,
            'sort_order': 2
        },
        {
            'title': 'Politique de Confidentialité',
            'slug': 'confidentialite',
            'content': '<h2>1. Collecte des Informations</h2>\n<p>Nous collectons les informations personnelles nécessaires à la réalisation de vos commandes, notamment votre nom, adresse email, adresse de livraison et informations de paiement.</p>\n\n<h2>2. Utilisation des Données</h2>\n<p>Vos données sont utilisées uniquement pour traiter vos commandes, améliorer votre expérience utilisateur et vous envoyer des communications relatives à vos achats.</p>\n\n<h2>3. Sécurité des Données</h2>\n<p>Nous mettons en œuvre des mesures de sécurité appropriées pour protéger vos informations contre tout accès non autorisé.</p>\n\n<h2>4. Partage des Données</h2>\n<p>Nous ne partageons vos données qu\'avec des partenaires de confiance nécessaires au traitement de votre commande (transporteurs, processeurs de paiement).</p>\n\n<h2>5. Vos Droits</h2>\n<p>Vous avez le droit d\'accéder, de modifier ou de supprimer vos données personnelles à tout moment. Contactez-nous pour exercer ces droits.</p>\n\n<h2>6. Cookies</h2>\n<p>Nous utilisons des cookies pour améliorer votre expérience sur notre site. Vous pouvez configurer votre navigateur pour refuser les cookies.</p>',
            'excerpt': 'Comment nous protégeons vos données personnelles et votre vie privée.',
            'template': 'default',
            'meta_title': 'Politique de Confidentialité - Boutique Haïtienne',
            'meta_description': 'Découvrez comment nous protégeons vos données personnelles et votre vie privée.',
            'is_active': True,
            'is_featured': False,
            'sort_order': 3
        },
        {
            'title': 'Politique de Retour et Remboursement',
            'slug': 'retours-remboursements',
            'content': '<h2>1. Droit de Rétractation</h2>\n<p>Vous avez 14 jours à compter de la réception de votre commande pour exercer votre droit de rétractation sans avoir à justifier de motifs.</p>\n\n<h2>2. Conditions de Retour</h2>\n<p>Pour être éligible à un remboursement, l\'article doit être dans son état d\'origine, non utilisé et dans son emballage d\'origine.</p>\n\n<h2>3. Processus de Retour</h2>\n<ol>\n<li>Contactez notre service client pour initier un retour</li>\n<li>Emballer soigneusement l\'article</li>\n<li>Nous vous enverrons une étiquette d\'expédition prépayée</li>\n<li>Expédiez le colis</li>\n<li>Une fois reçu, nous traiterons votre remboursement</li>\n</ol>\n\n<h2>4. Délais de Remboursement</h2>\n<p>Les remboursements sont traités dans les 5-7 jours ouvrables suivant la réception de l\'article retourné.</p>\n\n<h2>5. Exceptions</h2>\n<p>Les produits numériques, les articles personnalisés et les produits périssables ne sont pas éligibles aux retours.</p>\n\n<h2>6. Frais de Retour</h2>\n<p>Les frais de retour sont à la charge du client, sauf en cas de défaut ou d\'erreur de notre part.</p>',
            'excerpt': 'Conditions de retour et remboursement pour vos achats sur notre plateforme.',
            'template': 'default',
            'meta_title': 'Politique de Retour et Remboursement - Boutique Haïtienne',
            'meta_description': 'Consultez nos conditions de retour et remboursement pour vos achats en ligne.',
            'is_active': True,
            'is_featured': False,
            'sort_order': 4
        },
        {
            'title': 'Foire Aux Questions',
            'slug': 'faq',
            'content': '<h2>Commandes et Paiements</h2>\n<h3>Comment passer une commande ?</h3>\n<p>Parcourez nos catégories, sélectionnez les produits qui vous intéressent, ajoutez-les à votre panier et suivez les étapes du processus de checkout.</p>\n\n<h3>Quels modes de paiement acceptez-vous ?</h3>\n<p>Nous acceptons les paiements via MonCash et d\'autres méthodes de paiement seront bientôt disponibles.</p>\n\n<h2>Livraison</h2>\n<h3>Où livrez-vous ?</h3>\n<p>Nous livrons dans toute Haïti, avec des délais variables selon la région.</p>\n\n<h3>Combien de temps prend la livraison ?</h3>\n<p>Les délais de livraison varient entre 2 et 7 jours ouvrables selon votre localisation.</p>\n\n<h2>Produits</h2>\n<h3>Les produits sont-ils authentiques ?</h3>\n<p>Oui, tous nos produits sont authentiques et proviennent directement des producteurs haïtiens.</p>\n\n<h3>Comment puis-je vérifier la disponibilité d\'un produit ?</h3>\n<p>La disponibilité est indiquée sur la page du produit. Si un produit est en rupture de stock, vous pouvez vous inscrire pour être notifié quand il sera de nouveau disponible.</p>\n\n<h2>Compte Client</h2>\n<h3>Pourquoi créer un compte ?</h3>\n<p>Un compte vous permet de suivre vos commandes, de sauvegarder vos informations de livraison et de bénéficier d\'une expérience personnalisée.</p>\n\n<h3>Comment puis-je modifier mes informations personnelles ?</h3>\n<p>Connectez-vous à votre compte et accédez à la section "Mon Profil" pour modifier vos informations.</p>',
            'excerpt': 'Réponses aux questions fréquemment posées sur notre plateforme.',
            'template': 'default',
            'meta_title': 'Foire Aux Questions - Boutique Haïtienne',
            'meta_description': 'Trouvez des réponses aux questions fréquemment posées sur notre plateforme.',
            'is_active': True,
            'is_featured': False,
            'sort_order': 5
        },
        {
            'title': 'Contact',
            'slug': 'contact',
            'content': '<h2>Nous Contacter</h2>\n<p>Nous sommes à votre écoute pour toute question, suggestion ou problème. N\'hésitez pas à nous contacter par les moyens suivants :</p>\n\n<div class="contact-info">\n<h3>Coordonnées</h3>\n<p><i class="fas fa-map-marker-alt"></i> Adresse: Centre-ville, Port-au-Prince, Haïti</p>\n<p><i class="fas fa-phone"></i> Téléphone: +509 44 11 22 33</p>\n<p><i class="fas fa-envelope"></i> Email: contact@boutiquehaitienne.ht</p>\n<p><i class="fas fa-clock"></i> Horaires: Lundi-Vendredi 8h-17h, Samedi 9h-13h</p>\n</div>\n\n<h2>Formulaire de Contact</h2>\n<p>Utilisez ce formulaire pour nous envoyer un message directement :</p>\n<!-- Le formulaire sera géré par le template -->\n\n<h2>Questions Fréquentes</h2>\n<p>Pour des questions rapides, consultez notre <a href="/?page=faq">FAQ</a>.</p>\n\n<h2>Réseaux Sociaux</h2>\n<p>Suivez-nous sur les réseaux sociaux pour rester informé des nouveautés :</p>\n<div class="social-links">\n<a href="#"><i class="fab fa-facebook"></i> Facebook</a>\n<a href="#"><i class="fab fa-instagram"></i> Instagram</a>\n<a href="#"><i class="fab fa-twitter"></i> Twitter</a>\n<a href="#"><i class="fab fa-youtube"></i> YouTube</a>\n</div>',
            'excerpt': 'Contactez notre équipe pour toute question ou assistance.',
            'template': 'contact',
            'meta_title': 'Contact - Boutique Haïtienne',
            'meta_description': 'Contactez notre équipe pour toute question ou assistance concernant vos achats.',
            'is_active': True,
            'is_featured': False,
            'sort_order': 6
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    # Obtenir le fuseau horaire par défaut de Django
    try:
        from django.utils import timezone
        now = timezone.now()
    except:
        now = datetime.now()
    
    for page_data in static_pages:
        # Vérifier si la page existe déjà
        try:
            # Utiliser get pour vérifier l'existence
            page = Page.objects.get(slug=page_data['slug'])
            # Si la page existe, on va la mettre à jour
            for field, value in page_data.items():
                setattr(page, field, value)
            page.updated_at = now
            page.save()
            print(f"🔄 Page mise à jour: {page.title}")
            updated_count += 1
        except Page.DoesNotExist:
            # Si la page n'existe pas, on la crée
            page = Page(**page_data)
            page.created_at = now
            page.updated_at = now
            page.save()
            print(f"✅ Page créée: {page.title}")
            created_count += 1
    
    print(f"\nOpération terminée: {created_count} pages créées, {updated_count} pages mises à jour")
    return created_count, updated_count

if __name__ == "__main__":
    try:
        print("Démarrage du script d'insertion des pages statiques...\n")
        create_static_pages()
        print("\nScript exécuté avec succès!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution du script: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)