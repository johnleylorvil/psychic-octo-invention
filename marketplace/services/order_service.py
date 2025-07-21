# marketplace/services/order_service.py

import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from ..models import Order, OrderItem, Cart, CartItem, User, Product
from .stock_service import StockService, InsufficientStockError, StockError

logger = logging.getLogger(__name__)


class OrderError(Exception):
    """Exception de base pour les erreurs de commande"""
    pass


class CartEmptyError(OrderError):
    """Exception pour panier vide"""
    pass


class OrderService:
    """
    Service pour la gestion complète des commandes
    
    Fonctionnalités :
    - Création commande depuis panier avec validation stock
    - Calculs automatiques (totaux, taxes, livraison)
    - Annulation commande avec libération stock
    - Validation business rules
    - Audit complet des opérations
    """
    
    # Configuration par défaut (peut être overridée par settings)
    DEFAULT_SHIPPING_COST = Decimal('50.00')  # 50 HTG livraison standard
    DEFAULT_TAX_RATE = Decimal('0.00')        # Pas de taxes pour MVP
    DEFAULT_CURRENCY = 'HTG'
    
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(
        cart: Cart, 
        shipping_data: Dict[str, Any], 
        user: User = None
    ) -> Dict[str, Any]:
        """
        Créer une commande à partir d'un panier avec validation stock complète
        
        Args:
            cart: Instance du panier
            shipping_data: Dict avec adresse de livraison
            user: Utilisateur (optionnel si déjà dans cart.user)
            
        Returns:
            Dict avec order (Order), success (bool), message (str)
            
        Raises:
            CartEmptyError: Si panier vide
            InsufficientStockError: Si stock insuffisant
            OrderError: Pour autres erreurs de validation
        """
        try:
            # Validation panier
            if not cart.items.exists():
                raise CartEmptyError("Le panier est vide")
            
            # Utiliser l'utilisateur du panier ou celui passé en paramètre
            order_user = user or cart.user
            if not order_user:
                raise OrderError("Utilisateur requis pour créer une commande")
            
            # 🚨 VALIDATION STOCK EN LOT (avant réservation)
            items_for_validation = [
                {
                    'product_slug': item.product.slug,
                    'quantity': item.quantity
                }
                for item in cart.items.select_related('product').all()
            ]
            
            stock_check = StockService.bulk_check_availability(items_for_validation)
            if not stock_check['available']:
                # Construire message d'erreur détaillé
                unavailable_details = []
                for item in stock_check['unavailable_items']:
                    unavailable_details.append(
                        f"- {item['product_name']}: demandé {item['requested_quantity']}, "
                        f"disponible {item.get('available_quantity', 0)}"
                    )
                
                error_message = "Stock insuffisant pour :\n" + "\n".join(unavailable_details)
                raise InsufficientStockError(None, 0, 0)  # Sera catchée avec message custom
            
            # 🎯 CRÉATION COMMANDE ATOMIQUE
            order_data = OrderService._prepare_order_data(cart, shipping_data, order_user)
            order = Order.objects.create(**order_data)
            
            # 🎯 CRÉATION ORDER ITEMS + RÉSERVATION STOCK
            order_items_created = []
            total_reserved = 0
            
            for cart_item in cart.items.select_related('product').all():
                # Réserver stock pour chaque produit
                try:
                    stock_result = StockService.reserve_stock(
                        cart_item.product.slug,
                        cart_item.quantity,
                        f"order_{order.order_number}"
                    )
                    
                    # Créer OrderItem
                    order_item = OrderService._create_order_item(order, cart_item)
                    order_items_created.append(order_item)
                    total_reserved += cart_item.quantity
                    
                except (InsufficientStockError, StockError) as stock_exc:
                    # Rollback des réservations déjà faites
                    OrderService._rollback_stock_reservations(order_items_created)
                    raise OrderError(f"Erreur réservation stock pour {cart_item.product.name}: {stock_exc}")
            
            # 🎯 RECALCULER TOTAUX FINAUX
            OrderService._update_order_totals(order)
            
            # 🎯 NETTOYAGE PANIER
            cart.is_active = False
            cart.save()
            
            # Logging pour audit
            logger.info(
                f"Commande créée - Numéro: {order.order_number}, "
                f"Utilisateur: {order_user.username}, "
                f"Montant: {order.total_amount} {order.currency}, "
                f"Items: {len(order_items_created)}, "
                f"Stock réservé: {total_reserved} unités"
            )
            
            return {
                'success': True,
                'order': order,
                'message': f'Commande {order.order_number} créée avec succès',
                'order_number': order.order_number,
                'total_amount': order.total_amount,
                'items_count': len(order_items_created)
            }
            
        except CartEmptyError:
            raise
            
        except InsufficientStockError:
            # Message custom pour stock insuffisant en lot
            raise OrderError(error_message if 'error_message' in locals() else "Stock insuffisant")
            
        except Exception as exc:
            error_msg = f"Erreur création commande depuis panier {cart.id}: {exc}"
            logger.error(error_msg)
            raise OrderError(error_msg)
    
    @staticmethod
    def _prepare_order_data(cart: Cart, shipping_data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Préparer les données de base pour créer une commande
        
        Args:
            cart: Instance du panier
            shipping_data: Données d'adresse de livraison
            user: Utilisateur
            
        Returns:
            Dict avec toutes les données pour créer Order
        """
        # Calculs préliminaires
        subtotal = sum(item.total_price for item in cart.items.all())
        shipping_cost = OrderService._calculate_shipping_cost(cart, shipping_data)
        tax_amount = OrderService._calculate_tax_amount(subtotal, shipping_data)
        total_amount = subtotal + shipping_cost + tax_amount
        
        # Génération numéro de commande unique
        order_number = OrderService._generate_order_number()
        
        return {
            'order_number': order_number,
            'user': user,
            'customer_name': user.get_full_name() or f"{user.first_name} {user.last_name}".strip(),
            'customer_email': user.email,
            'customer_phone': shipping_data.get('customer_phone') or user.phone or '',
            
            # Adresse de livraison
            'shipping_address': shipping_data['shipping_address'],
            'shipping_city': shipping_data.get('shipping_city', 'Port-au-Prince'),
            'shipping_country': shipping_data.get('shipping_country', 'Haïti'),
            
            # Adresse de facturation (même que livraison par défaut)
            'billing_address': shipping_data.get('billing_address', shipping_data['shipping_address']),
            'billing_city': shipping_data.get('billing_city', shipping_data.get('shipping_city', 'Port-au-Prince')),
            'billing_country': shipping_data.get('billing_country', 'Haïti'),
            
            # Montants
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'discount_amount': Decimal('0.00'),  # Pour futures promos
            'total_amount': total_amount,
            'currency': OrderService.DEFAULT_CURRENCY,
            
            # Statuts
            'status': 'pending',
            'payment_status': 'pending',
            'payment_method': 'moncash',  # Par défaut
            'shipping_method': 'standard',
            
            # Métadonnées
            'notes': shipping_data.get('notes', ''),
            'source': 'web',
        }
    
    @staticmethod
    def _create_order_item(order: Order, cart_item: CartItem) -> OrderItem:
        """
        Créer un OrderItem à partir d'un CartItem
        
        Args:
            order: Instance de la commande
            cart_item: Item du panier
            
        Returns:
            OrderItem créé
        """
        # Snapshot des données produit au moment de l'achat
        primary_image = cart_item.product.images.filter(is_primary=True).first()
        product_image = primary_image.image_url if primary_image else None
        
        return OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            unit_price=cart_item.price,  # Prix fixé au moment ajout panier
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            product_image=product_image,
            product_options=cart_item.options or {}
            # total_price sera calculé automatiquement par le model
        )
    
    @staticmethod
    def _calculate_shipping_cost(cart: Cart, shipping_data: Dict[str, Any]) -> Decimal:
        """
        Calculer les frais de livraison
        
        Args:
            cart: Instance du panier
            shipping_data: Données d'adresse
            
        Returns:
            Decimal: Montant frais de livraison
        """
        # Logique simple pour MVP - peut être étendue
        shipping_city = shipping_data.get('shipping_city', '').lower()
        
        # Produits numériques = pas de frais de livraison
        has_digital_only = all(item.product.is_digital for item in cart.items.all())
        if has_digital_only:
            return Decimal('0.00')
        
        # Frais selon ville (peut être configuré en DB plus tard)
        if shipping_city in ['port-au-prince', 'petion-ville', 'delmas']:
            return Decimal('50.00')  # Zone métropolitaine
        elif shipping_city in ['cap-haitien', 'gonaives', 'les-cayes']:
            return Decimal('100.00')  # Grandes villes
        else:
            return Decimal('150.00')  # Autres zones
    
    @staticmethod
    def _calculate_tax_amount(subtotal: Decimal, shipping_data: Dict[str, Any]) -> Decimal:
        """
        Calculer les taxes (pour future extension)
        
        Args:
            subtotal: Sous-total de la commande
            shipping_data: Données d'adresse
            
        Returns:
            Decimal: Montant des taxes
        """
        # Pas de taxes pour MVP Haïti
        return Decimal('0.00')
    
    @staticmethod
    def _update_order_totals(order: Order):
        """
        Recalculer et mettre à jour les totaux de la commande
        
        Args:
            order: Instance de la commande
        """
        # Recalculer depuis les OrderItems
        items_total = sum(item.total_price for item in order.items.all())
        
        # Mise à jour atomique
        Order.objects.filter(id=order.id).update(
            subtotal=items_total,
            total_amount=items_total + order.shipping_cost + order.tax_amount - order.discount_amount,
            updated_at=timezone.now()
        )
        
        # Refresh l'instance
        order.refresh_from_db()
    
    @staticmethod
    def _generate_order_number() -> str:
        """
        Générer un numéro de commande unique
        
        Returns:
            str: Numéro de commande format AF12345678
        """
        # Format: AF + 8 caractères hexadécimaux majuscules
        unique_part = uuid.uuid4().hex[:8].upper()
        order_number = f"AF{unique_part}"
        
        # Vérifier unicité (très improbable mais sécurité)
        while Order.objects.filter(order_number=order_number).exists():
            unique_part = uuid.uuid4().hex[:8].upper()
            order_number = f"AF{unique_part}"
        
        return order_number
    
    @staticmethod
    def _rollback_stock_reservations(order_items: List[OrderItem]):
        """
        Rollback des réservations de stock en cas d'erreur
        
        Args:
            order_items: Liste des OrderItems créés
        """
        for order_item in order_items:
            try:
                StockService.release_stock(
                    order_item.product.slug,
                    order_item.quantity,
                    "order_creation_rollback"
                )
            except Exception as exc:
                logger.error(f"Erreur rollback stock pour {order_item.product.slug}: {exc}")
    
    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order, reason: str = "customer_request") -> Dict[str, Any]:
        """
        Annuler une commande et libérer le stock
        
        Args:
            order: Instance de la commande
            reason: Raison de l'annulation
            
        Returns:
            Dict avec success (bool), message (str)
            
        Raises:
            OrderError: Si commande ne peut pas être annulée
        """
        try:
            # Validation: seules les commandes pending peuvent être annulées
            if order.status not in ['pending', 'confirmed']:
                raise OrderError(
                    f"Commande {order.order_number} ne peut pas être annulée. "
                    f"Statut actuel: {order.status}"
                )
            
            if order.payment_status == 'paid':
                raise OrderError(
                    f"Commande {order.order_number} déjà payée. "
                    "Contactez le support pour remboursement."
                )
            
            # 🎯 LIBÉRATION STOCK
            stock_released = 0
            for order_item in order.items.all():
                try:
                    result = StockService.release_stock(
                        order_item.product.slug,
                        order_item.quantity,
                        f"order_cancelled_{reason}"
                    )
                    stock_released += order_item.quantity
                    
                except StockError as exc:
                    logger.warning(f"Erreur libération stock pour {order_item.product.slug}: {exc}")
                    # Continue avec les autres items
            
            # 🎯 MISE À JOUR STATUT COMMANDE
            old_status = order.status
            order.status = 'cancelled'
            order.payment_status = 'cancelled'
            order.admin_notes = f"Annulée le {timezone.now()}: {reason}"
            order.save()
            
            # Logging pour audit
            logger.info(
                f"Commande annulée - Numéro: {order.order_number}, "
                f"Ancien statut: {old_status}, "
                f"Raison: {reason}, "
                f"Stock libéré: {stock_released} unités"
            )
            
            return {
                'success': True,
                'message': f'Commande {order.order_number} annulée avec succès',
                'order_number': order.order_number,
                'stock_released': stock_released,
                'reason': reason
            }
            
        except OrderError:
            raise
            
        except Exception as exc:
            error_msg = f"Erreur annulation commande {order.order_number}: {exc}"
            logger.error(error_msg)
            raise OrderError(error_msg)
    
    @staticmethod
    def validate_shipping_data(shipping_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valider les données d'adresse de livraison
        
        Args:
            shipping_data: Données à valider
            
        Returns:
            Dict avec valid (bool), errors (list), cleaned_data (dict)
        """
        errors = []
        cleaned_data = {}
        
        # Champs requis
        required_fields = ['shipping_address']
        for field in required_fields:
            value = shipping_data.get(field, '').strip()
            if not value:
                errors.append(f"{field} est requis")
            else:
                cleaned_data[field] = value
        
        # Validation téléphone si fourni
        phone = shipping_data.get('customer_phone', '').strip()
        if phone:
            # Format Haïti: +509 XXXX-XXXX ou variations
            if not any(char.isdigit() for char in phone):
                errors.append("Numéro de téléphone invalide")
            else:
                cleaned_data['customer_phone'] = phone
        
        # Validation ville (optionnel mais normalisé)
        city = shipping_data.get('shipping_city', 'Port-au-Prince').strip()
        cleaned_data['shipping_city'] = city
        
        # Autres champs optionnels
        optional_fields = ['shipping_country', 'billing_address', 'notes']
        for field in optional_fields:
            value = shipping_data.get(field, '').strip()
            if value:
                cleaned_data[field] = value
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'cleaned_data': cleaned_data
        }
    
    @staticmethod
    def get_order_summary(order: Order) -> Dict[str, Any]:
        """
        Obtenir un résumé complet d'une commande
        
        Args:
            order: Instance de la commande
            
        Returns:
            Dict avec toutes les infos de la commande
        """
        return {
            'order_number': order.order_number,
            'status': order.status,
            'payment_status': order.payment_status,
            'customer_info': {
                'name': order.customer_name,
                'email': order.customer_email,
                'phone': order.customer_phone,
            },
            'shipping_info': {
                'address': order.shipping_address,
                'city': order.shipping_city,
                'country': order.shipping_country,
            },
            'amounts': {
                'subtotal': order.subtotal,
                'shipping_cost': order.shipping_cost,
                'tax_amount': order.tax_amount,
                'discount_amount': order.discount_amount,
                'total_amount': order.total_amount,
                'currency': order.currency,
            },
            'items': [
                {
                    'product_name': item.product_name,
                    'product_sku': item.product_sku,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                }
                for item in order.items.all()
            ],
            'dates': {
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'estimated_delivery': order.estimated_delivery,
            },
            'notes': order.notes,
        }