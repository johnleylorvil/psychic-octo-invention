# 🧪 Guide de Test Avancé - Afèpanou API

## 🎯 Scénarios de Test Complets

### 📋 **Scénario 1 : Utilisateur Client Complet**
```bash
1. Inscription nouveau client
2. Connexion avec JWT
3. Navigation landing page (banners, produits vedettes)
4. Recherche produits "ceramique"
5. Consultation détail produit
6. Vérification stock disponible
7. Ajout au panier (2 articles)
8. Modification quantité panier
9. Validation stock avant checkout
10. Création commande avec adresse livraison
11. Consultation détail commande
12. Test annulation commande
```

### 🏪 **Scénario 2 : Parcours Vendeur**
```bash
1. Inscription compte vendeur (is_seller=True)
2. Connexion et vérification profil vendeur
3. Consultation API produits (ses produits si implémenté)
4. Test fonctionnalités avancées vendeur
```

### 🛒 **Scénario 3 : Gestion Panier Avancée**
```bash
1. Connexion utilisateur existant
2. Ajout multiples produits différentes catégories
3. Modification quantités diverses
4. Test limite stock (quantité > stock)
5. Test expiration panier (30 minutes)
6. Validation stock avec erreurs simulées
7. Suppression articles individuels
8. Vidage complet panier
```

### 📦 **Scénario 4 : Workflow Commandes**
```bash
1. Création commande normale
2. Consultation timeline statuts
3. Test annulation (différentes raisons)
4. Création nouvelle commande
5. Test mise à jour statut (admin)
6. Historique complet commandes
7. Résumé statistiques commandes
```

## 🔧 Tests Spécifiques par Endpoint

### **🔐 Auth Endpoints (6)**
- `POST /auth/register/` 
  - ✅ Données valides
  - ❌ Email déjà utilisé
  - ❌ Mots de passe différents
  - ❌ Données manquantes

- `POST /auth/login/`
  - ✅ Username/password correct
  - ✅ Email/password correct
  - ❌ Credentials invalides
  - ❌ Compte désactivé

- `POST /auth/logout/`
  - ✅ Token valide
  - ❌ Token invalide/expiré

- `GET /auth/profile/`
  - ✅ Token valide
  - ❌ Non authentifié

- `PUT /auth/update_profile/`
  - ✅ Mise à jour partielle
  - ✅ Mise à jour complète
  - ❌ Données invalides

- `POST /auth/change_password/`
  - ✅ Ancien mot de passe correct
  - ❌ Ancien mot de passe incorrect

### **🏠 Landing Page Endpoints (8)**
- Tests de performance cache
- Validation structure données
- Test carrousels et bannières
- Vérification produits vedettes

### **🛍️ Products Endpoints (9)**
- Tests pagination
- Filtres avancés (prix, catégorie, stock)
- Recherche full-text avec scores
- Gestion stock temps réel

### **🛒 Cart Endpoints (7)**
- Race conditions sur stock
- Expiration automatique
- Validation continue stock
- Opérations en lot

### **📦 Orders Endpoints (6)**
- Workflow statuts complet
- Calculs totaux précis
- Gestion annulations
- Historique détaillé

## 📊 Métriques de Test

### **🎯 KPIs à Surveiller**
```python
Performance:
├── Temps réponse moyen < 500ms
├── Taux erreur < 5%
├── Cache hit ratio > 80%
└── Concurrent users support

Business Logic:
├── Stock consistency 100%
├── Calculs prix exacts
├── Workflow statuts respectés
└── Race conditions gérées

Security:
├── JWT tokens sécurisés
├── Permissions respectées  
├── Validation données stricte
└── Protection CSRF active
```

### **🔍 Points de Contrôle Critiques**

#### **Stock Management**
```bash
# Test concurrent cart additions
1. User A ajoute dernier stock item
2. User B essaie simultanément
3. Vérifier qu'un seul succède
4. Vérifier stock final cohérent
```

#### **Payment Workflow** (à venir)
```bash
# Test MonCash integration
1. Création commande
2. Redirection gateway
3. Simulation paiement
4. Webhook handling
5. Mise à jour statuts
```

#### **Cache Coherence**
```bash
# Test invalidation cache
1. Modification produit admin
2. Vérifier cache invalidé
3. Nouvelles données servies
4. Performance maintenue
```

## 🐛 Debugging Avancé

### **📋 Log Analysis**
```python
# Patterns à surveiller dans logs
ERROR_PATTERNS = [
    "InsufficientStockError",
    "JWT token expired", 
    "ValidationError",
    "Race condition detected",
    "Cache miss critical path"
]

PERFORMANCE_PATTERNS = [
    "Query time > 100ms",
    "API response > 1s",
    "Memory usage spike",
    "Database connections peak"
]
```

### **🔧 Configuration Debug**
```python
# Variables environnement pour tests
TEST_CONFIG = {
    'API_BASE_URL': 'http://localhost:8000/api',
    'LOG_LEVEL': 'DEBUG',
    'ENABLE_PERFORMANCE_TRACKING': True,
    'MOCK_PAYMENT_GATEWAY': True,
    'TEST_USER_PREFIX': 'test_',
    'AUTO_CLEANUP': True
}
```

## 🚀 Automatisation Tests

### **📅 Tests Programmés**
```bash
# Cron job pour tests réguliers
# Chaque heure : Health check
0 * * * * /path/to/test_health_check.py

# Chaque jour : Full workflow test  
0 2 * * * /path/to/test_full_workflow.py

# Chaque semaine : Performance test
0 2 * * 0 /path/to/test_performance.py
```

### **🔄 CI/CD Integration**
```yaml
# .github/workflows/api_tests.yml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run API tests
        run: python -m pytest api_tests/
      - name: Run Streamlit tests
        run: streamlit run afepanou_api_tester.py --headless
```

## 📈 Optimisations Performance

### **⚡ Recommandations**
```python
# Optimisations identifiées via tests
OPTIMIZATIONS = {
    'Database': [
        'Index sur slug, is_active',
        'Select_related produits->catégorie',
        'Prefetch_related images',
        'Pagination efficace'
    ],
    'Cache': [
        'Cache landing page 5min',
        'Cache produits vedettes 30min', 
        'Cache catégories 1h',
        'Invalidation intelligente'
    ],
    'API': [
        'Compression gzip',
        'Rate limiting',
        'Response pagination',
        'Minimal field sets'
    ]
}
```

## 🎭 Mock & Test Data

### **📊 Jeux de Données Test**
```python
# Génération données cohérentes
TEST_DATA = {
    'users': 100,          # Mix clients/vendeurs
    'categories': 20,      # Hiérarchie 3 niveaux
    'products': 500,       # Stock variables
    'orders': 200,         # Différents statuts
    'reviews': 1000,       # Notes réparties
}

# Scénarios edge cases
EDGE_CASES = [
    'Stock = 0',
    'Stock = 1 (dernière unité)',
    'Produit digital (stock infini)',
    'Panier expiré',
    'Token JWT expiré',
    'Paiement échoué',
    'Commande annulée'
]
```

## 🏆 Validation Finale

### **✅ Checklist Pré-Production**
```bash
□ Tous endpoints testés
□ Authentification sécurisée
□ Stock management robuste  
□ Performance acceptable
□ Cache fonctionnel
□ Logs informatifs
□ Erreurs gérées proprement
□ Documentation complète
□ Tests automatisés
□ Monitoring activé
```

### **📋 Métriques Succès**
```python
SUCCESS_CRITERIA = {
    'API Coverage': '100%',           # Tous endpoints testés
    'Error Rate': '< 1%',            # Très stable
    'Response Time': '< 300ms',       # Performance excellente
    'Cache Hit': '> 85%',            # Cache efficace
    'Stock Accuracy': '100%',         # Cohérence parfaite
    'Security Score': 'A+',          # Sécurité maximale
}
```

---

## 🎯 Conclusion

Ce guide permet de valider complètement votre API Afèpanou avec :
- **Couverture 100%** des endpoints
- **Tests réalistes** du workflow e-commerce  
- **Debugging avancé** avec logs détaillés
- **Validation performance** et sécurité
- **Automatisation** pour CI/CD

L'outil Streamlit fournit une interface visuelle complète pour identifier rapidement les problèmes et valider les corrections. 🚀