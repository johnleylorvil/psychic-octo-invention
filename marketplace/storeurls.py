# urls.py (dans votre application 'store')
from django.urls import path
from .storeview import StoreView, MonCashCallbackView, MonCashReturnView

app_name = 'store'

urlpatterns = [
    # Route pour afficher un store spécifique (produits d'une catégorie)
    # Cette route gère maintenant les 5 catégories statiques définies dans la vue
    path('store/<str:store_name>/', StoreView.as_view(), name='store_view'),
    path('moncash/callback/', MonCashCallbackView.as_view(), name='moncash_callback'),
    path('moncash/return/', MonCashReturnView.as_view(), name='moncash_return'),
]