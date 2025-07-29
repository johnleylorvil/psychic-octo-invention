import os

# Définir la structure du filesystem
filesystem = {
    "marketplace": {
        "templates": {
            "base.html": None,
            "landing": {
                "home.html": None,
                "components": {
                    "header.html": None,
                    "banner-carousel.html": None,
                    "featured-products.html": None,
                    "content-sections.html": None,
                    "footer.html": None,
                },
            },
            "products": {
                "product_list.html": None,
                "product_detail.html": None,
                "category_products.html": None,
            },
            "cart": {
                "cart.html": None,
                "cart_sidebar.html": None,
            },
            "orders": {
                "order_list.html": None,
                "order_detail.html": None,
                "order_summary.html": None,
            },
            "payment": {
                "payment_init.html": None,
            },
            "auth": {
                "login.html": None,
                "register.html": None,
                "profile.html": None,
                "change_password.html": None,
            },
            "partials": {
                "messages.html": None,
                "navbar.html": None,
            },
        },
        "static": {
            "css": {
                "main.css": None,
                "landing.css": None,
                "products.css": None,
                "cart.css": None,
                "orders.css": None,
                "auth.css": None,
            },
            "js": {
                "cart.js": None,
                "payment.js": None,
                "search.js": None,
                "utils.js": None,
            },
            "images": {
                "logo.png": None,
                "placeholders": {
                    "product-placeholder.jpg": None,
                    "banner-default.jpg": None,
                },
            },
        },
    }
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if content is None:
            # Créer un fichier vide
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
        else:
            # Créer un dossier
            os.makedirs(path, exist_ok=True)
            # Appel récursif pour son contenu
            create_structure(path, content)


# Lancer la création du système de fichiers
create_structure(".", filesystem)

print("Structure de fichiers créée avec succès.")
