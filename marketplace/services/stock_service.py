# marketplace/services/stock_service.py

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
from django.db import transaction, IntegrityError
from django.core.mail import mail_admins
from django.conf import settings
from django.utils import timezone
from ..models import Product

logger = logging.getLogger(__name__)


class StockError(Exception):
    """Exception de base pour les erreurs de stock"""
    pass


class InsufficientStockError(StockError):
    """Exception pour stock insuffisant"""
    def __init__(self, product, requested_quantity, available_quantity):
        self.product = product
        self.requested_quantity = requested_quantity
        self.available_quantity = available_quantity
        super().__init__(
            f"Stock insuffisant pour {product.name}. "
            f"Demandé: {requested_quantity}, Disponible: {available_quantity}"
        )


class StockService:
    """
    Service pour la gestion thread-safe du stock des produits
    
    Fonctionnalités :
    - Réservation temporaire de stock (pour création commande)
    - Libération de stock (si échec paiement)
    - Confirmation d'achat (stock définitivement vendu)
    - Vérification disponibilité
    - Alertes stock bas automatiques
    """
    
    @staticmethod
    def check_availability(product: Product, quantity: int) -> Dict[str, Any]:
        """
        Vérifier la disponibilité d'un produit sans réserver
        
        Args:
            product: Instance du produit
            quantity: Quantité demandée
            
        Returns:
            Dict avec available (bool), available_quantity (int), is_digital (bool)
        """
        try:
            # Produits numériques = stock illimité
            if product.is_digital:
                return {
                    'available': True,
                    'available_quantity': 999999,  # "Illimité"
                    'is_digital': True,
                    'message': 'Produit numérique - stock illimité'
                }
            
            # Vérification stock physique
            current_stock = product.stock_quantity or 0
            is_available = current_stock >= quantity
            
            return {
                'available': is_available,
                'available_quantity': current_stock,
                'is_digital': False,
                'message': f'Stock disponible: {current_stock}' if is_available 
                          else f'Stock insuffisant. Disponible: {current_stock}, Demandé: {quantity}'
            }
            
        except Exception as exc:
            logger.error(f"Erreur vérification stock pour {product.slug}: {exc}")
            return {
                'available': False,
                'available_quantity': 0,
                'is_digital': False,
                'message': 'Erreur lors de la vérification du stock'
            }
    
    @staticmethod
    @transaction.atomic
    def reserve_stock(product_slug: str, quantity: int, reserved_for: str = "order") -> Dict[str, Any]:
        """
        Réserver du stock de manière atomique pour une commande
        
        Args:
            product_slug: Slug du produit
            quantity: Quantité à réserver
            reserved_for: Contexte de réservation (order, cart, etc.)
            
        Returns:
            Dict avec success (bool), message (str), reserved_quantity (int)
            
        Raises:
            InsufficientStockError: Si stock insuffisant
            StockError: Pour autres erreurs de stock
        """
        try:
            # 🚨 SELECT FOR UPDATE pour éviter race conditions
            product = Product.objects.select_for_update().get(
                slug=product_slug, 
                is_active=True
            )
            
            # Validation quantité
            if quantity <= 0:
                raise StockError(f"Quantité invalide: {quantity}")
            
            # Produits numériques = pas de réservation nécessaire
            if product.is_digital:
                logger.info(f"Produit numérique {product.slug} - pas de réservation stock nécessaire")
                return {
                    'success': True,
                    'message': 'Produit numérique - réservation non nécessaire',
                    'reserved_quantity': quantity,
                    'remaining_stock': 999999
                }
            
            # Vérification stock disponible
            current_stock = product.stock_quantity or 0
            if current_stock < quantity:
                raise InsufficientStockError(product, quantity, current_stock)
            
            # 🎯 RÉSERVATION ATOMIQUE
            new_stock = current_stock - quantity
            Product.objects.filter(id=product.id).update(
                stock_quantity=new_stock,
                updated_at=timezone.now()
            )
            
            # Logging pour audit
            logger.info(
                f"Stock réservé - Produit: {product.slug}, "
                f"Quantité: {quantity}, Stock restant: {new_stock}, "
                f"Contexte: {reserved_for}"
            )
            
            # 🚨 ALERTE STOCK BAS
            if new_stock <= product.min_stock_alert:
                StockService._send_low_stock_alert(product, new_stock)
            
            return {
                'success': True,
                'message': f'Stock réservé avec succès: {quantity} unités',
                'reserved_quantity': quantity,
                'remaining_stock': new_stock
            }
            
        except Product.DoesNotExist:
            error_msg = f"Produit non trouvé: {product_slug}"
            logger.error(error_msg)
            raise StockError(error_msg)
            
        except InsufficientStockError:
            # Re-raise l'exception avec les détails
            raise
            
        except Exception as exc:
            error_msg = f"Erreur réservation stock pour {product_slug}: {exc}"
            logger.error(error_msg)
            raise StockError(error_msg)
    
    @staticmethod
    @transaction.atomic  
    def release_stock(product_slug: str, quantity: int, reason: str = "cancelled") -> Dict[str, Any]:
        """
        Libérer du stock précédemment réservé (ex: commande annulée)
        
        Args:
            product_slug: Slug du produit
            quantity: Quantité à libérer
            reason: Raison de la libération
            
        Returns:
            Dict avec success (bool), message (str), released_quantity (int)
        """
        try:
            # 🚨 SELECT FOR UPDATE pour éviter race conditions
            product = Product.objects.select_for_update().get(
                slug=product_slug,
                is_active=True
            )
            
            # Validation quantité
            if quantity <= 0:
                raise StockError(f"Quantité invalide pour libération: {quantity}")
            
            # Produits numériques = pas de libération nécessaire
            if product.is_digital:
                logger.info(f"Produit numérique {product.slug} - pas de libération stock nécessaire")
                return {
                    'success': True,
                    'message': 'Produit numérique - libération non nécessaire',
                    'released_quantity': quantity,
                    'current_stock': 999999
                }
            
            # 🎯 LIBÉRATION ATOMIQUE
            current_stock = product.stock_quantity or 0
            new_stock = current_stock + quantity
            
            Product.objects.filter(id=product.id).update(
                stock_quantity=new_stock,
                updated_at=timezone.now()
            )
            
            # Logging pour audit
            logger.info(
                f"Stock libéré - Produit: {product.slug}, "
                f"Quantité: {quantity}, Nouveau stock: {new_stock}, "
                f"Raison: {reason}"
            )
            
            return {
                'success': True,
                'message': f'Stock libéré avec succès: {quantity} unités',
                'released_quantity': quantity,
                'current_stock': new_stock
            }
            
        except Product.DoesNotExist:
            error_msg = f"Produit non trouvé pour libération: {product_slug}"
            logger.error(error_msg)
            raise StockError(error_msg)
            
        except Exception as exc:
            error_msg = f"Erreur libération stock pour {product_slug}: {exc}"
            logger.error(error_msg)
            raise StockError(error_msg)
    
    @staticmethod
    @transaction.atomic
    def confirm_purchase(product_slug: str, quantity: int, order_number: str = None) -> Dict[str, Any]:
        """
        Confirmer un achat - le stock est définitivement vendu
        
        Note: Pour les commandes, le stock est déjà réservé par reserve_stock()
        Cette méthode sert principalement à l'audit et aux cas spéciaux
        
        Args:
            product_slug: Slug du produit
            quantity: Quantité achetée
            order_number: Numéro de commande pour audit
            
        Returns:
            Dict avec success (bool), message (str), confirmed_quantity (int)
        """
        try:
            product = Product.objects.select_for_update().get(
                slug=product_slug,
                is_active=True
            )
            
            # Validation quantité
            if quantity <= 0:
                raise StockError(f"Quantité invalide pour confirmation: {quantity}")
            
            # Logging pour audit (critique pour traçabilité)
            logger.info(
                f"Achat confirmé - Produit: {product.slug}, "
                f"Quantité: {quantity}, Commande: {order_number or 'N/A'}, "
                f"Stock actuel: {product.stock_quantity}"
            )
            
            return {
                'success': True,
                'message': f'Achat confirmé: {quantity} unités',
                'confirmed_quantity': quantity,
                'current_stock': product.stock_quantity,
                'order_number': order_number
            }
            
        except Product.DoesNotExist:
            error_msg = f"Produit non trouvé pour confirmation: {product_slug}"
            logger.error(error_msg)
            raise StockError(error_msg)
            
        except Exception as exc:
            error_msg = f"Erreur confirmation achat pour {product_slug}: {exc}"
            logger.error(error_msg)
            raise StockError(error_msg)
    
    @staticmethod
    def bulk_check_availability(items: list) -> Dict[str, Any]:
        """
        Vérifier la disponibilité de plusieurs produits en lot
        
        Args:
            items: Liste de dict avec 'product_slug' et 'quantity'
            
        Returns:
            Dict avec available (bool), items_status (list), unavailable_items (list)
        """
        items_status = []
        unavailable_items = []
        all_available = True
        
        for item in items:
            product_slug = item.get('product_slug')
            quantity = item.get('quantity', 1)
            
            try:
                product = Product.objects.get(slug=product_slug, is_active=True)
                availability = StockService.check_availability(product, quantity)
                
                item_status = {
                    'product_slug': product_slug,
                    'product_name': product.name,
                    'requested_quantity': quantity,
                    'available': availability['available'],
                    'available_quantity': availability['available_quantity'],
                    'is_digital': availability['is_digital']
                }
                
                items_status.append(item_status)
                
                if not availability['available']:
                    all_available = False
                    unavailable_items.append(item_status)
                    
            except Product.DoesNotExist:
                all_available = False
                unavailable_item = {
                    'product_slug': product_slug,
                    'product_name': 'Produit non trouvé',
                    'requested_quantity': quantity,
                    'available': False,
                    'error': 'Produit non trouvé'
                }
                items_status.append(unavailable_item)
                unavailable_items.append(unavailable_item)
        
        return {
            'available': all_available,
            'items_status': items_status,
            'unavailable_items': unavailable_items,
            'total_items': len(items),
            'unavailable_count': len(unavailable_items)
        }
    
    @staticmethod
    def _send_low_stock_alert(product: Product, current_stock: int):
        """
        Envoyer une alerte email pour stock bas
        
        Args:
            product: Instance du produit
            current_stock: Stock actuel
        """
        try:
            subject = f"🚨 ALERTE STOCK BAS - {product.name}"
            message = f"""
            Alerte stock bas pour le produit :
            
            Produit: {product.name} ({product.slug})
            Stock actuel: {current_stock}
            Seuil d'alerte: {product.min_stock_alert}
            Catégorie: {product.category.name}
            Vendeur: {product.seller.get_full_name() or product.seller.username}
            
            Action recommandée: Réapprovisionner le stock
            
            Lien admin: {settings.SITE_URL}/admin/marketplace/product/{product.id}/change/
            """
            
            # Envoyer aux superadmins Django
            mail_admins(
                subject=subject,
                message=message,
                fail_silently=False
            )
            
            logger.warning(f"Alerte stock bas envoyée pour {product.slug} - Stock: {current_stock}")
            
        except Exception as exc:
            logger.error(f"Erreur envoi alerte stock bas pour {product.slug}: {exc}")
    
    @staticmethod
    def get_stock_summary(product_slug: str) -> Dict[str, Any]:
        """
        Obtenir un résumé complet du stock d'un produit
        
        Args:
            product_slug: Slug du produit
            
        Returns:
            Dict avec toutes les infos de stock
        """
        try:
            product = Product.objects.get(slug=product_slug, is_active=True)
            
            return {
                'product_slug': product.slug,
                'product_name': product.name,
                'current_stock': product.stock_quantity,
                'min_stock_alert': product.min_stock_alert,
                'is_digital': product.is_digital,
                'is_low_stock': (product.stock_quantity or 0) <= product.min_stock_alert,
                'is_out_of_stock': (product.stock_quantity or 0) == 0 and not product.is_digital,
                'stock_status': StockService._get_stock_status(product),
                'last_updated': product.updated_at
            }
            
        except Product.DoesNotExist:
            return {
                'error': f'Produit non trouvé: {product_slug}',
                'stock_status': 'not_found'
            }
    
    @staticmethod
    def _get_stock_status(product: Product) -> str:
        """
        Déterminer le statut du stock d'un produit
        
        Args:
            product: Instance du produit
            
        Returns:
            str: 'digital', 'in_stock', 'low_stock', 'out_of_stock'
        """
        if product.is_digital:
            return 'digital'
        
        current_stock = product.stock_quantity or 0
        
        if current_stock == 0:
            return 'out_of_stock'
        elif current_stock <= product.min_stock_alert:
            return 'low_stock'
        else:
            return 'in_stock'