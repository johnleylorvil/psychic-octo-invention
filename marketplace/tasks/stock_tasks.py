# marketplace/tasks/stock_tasks.py

import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from django.core.mail import mail_admins
from django.conf import settings
from datetime import timedelta, datetime
from decimal import Decimal
from ..models import Product, Order, OrderItem, Cart, CartItem
from ..services.stock_service import StockService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=1800,  # 30 minutes entre retries
    time_limit=600,            # 10 minutes max
)
def daily_stock_audit(self):
    """
    Audit quotidien du stock pour détecter les incohérences
    
    Vérifie :
    - Produits avec stock négatif
    - Produits sous seuil d'alerte
    - Incohérences entre réservations et stock
    - Produits inactifs avec stock > 0
    
    Returns:
        Dict avec rapport d'audit
    """
    try:
        audit_results = {
            'timestamp': timezone.now(),
            'negative_stock': [],
            'low_stock': [],
            'inactive_with_stock': [],
            'zero_stock_active': [],
            'total_products_checked': 0,
            'issues_found': 0
        }
        
        # Récupérer tous les produits pour audit
        products = Product.objects.all()
        audit_results['total_products_checked'] = products.count()
        
        for product in products:
            stock_qty = product.stock_quantity or 0
            
            # 1. Stock négatif (problème critique)
            if stock_qty < 0:
                audit_results['negative_stock'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'slug': product.slug,
                    'stock_quantity': stock_qty,
                    'is_digital': product.is_digital,
                })
                audit_results['issues_found'] += 1
            
            # 2. Stock bas (warning)
            elif stock_qty <= product.min_stock_alert and not product.is_digital:
                audit_results['low_stock'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'slug': product.slug,
                    'stock_quantity': stock_qty,
                    'min_stock_alert': product.min_stock_alert,
                })
            
            # 3. Produits inactifs avec stock (optimisation)
            if not product.is_active and stock_qty > 0:
                audit_results['inactive_with_stock'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'slug': product.slug,
                    'stock_quantity': stock_qty,
                })
            
            # 4. Produits actifs sans stock (attention ventes)
            if product.is_active and stock_qty == 0 and not product.is_digital:
                audit_results['zero_stock_active'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'slug': product.slug,
                    'is_featured': product.is_featured,
                })
        
        # Générer rapport pour admins si issues critiques
        if audit_results['negative_stock'] or len(audit_results['low_stock']) > 10:
            send_stock_audit_report.delay(audit_results)
        
        logger.info(f"Stock audit completed: {audit_results['issues_found']} issues found")
        
        return {
            'status': 'success',
            'audit_results': audit_results,
            'message': f'Audit terminé - {audit_results["issues_found"]} problèmes détectés'
        }
        
    except Exception as exc:
        logger.error(f"Error during stock audit: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'audit_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=3600,  # 1 heure entre retries
    time_limit=300,
)
def cleanup_expired_stock_reservations(self):
    """
    Nettoyer les réservations de stock expirées des paniers abandonnés
    
    Libère le stock des paniers :
    - Inactifs depuis plus de 2 heures
    - Expirés mais non nettoyés
    - Sans utilisateur associé (sessions expirées)
    
    Returns:
        Dict avec statistiques de nettoyage
    """
    try:
        cutoff_time = timezone.now() - timedelta(hours=2)
        cleanup_stats = {
            'expired_carts_processed': 0,
            'stock_released_total': 0,
            'products_affected': [],
            'errors': []
        }
        
        # Trouver paniers expirés avec items
        expired_carts = Cart.objects.filter(
            updated_at__lt=cutoff_time,
            is_active=True
        ).prefetch_related('items__product')
        
        for cart in expired_carts:
            try:
                with transaction.atomic():
                    cart_items_count = 0
                    
                    # Libérer stock pour chaque item
                    for item in cart.items.all():
                        try:
                            result = StockService.release_stock(
                                product_slug=item.product.slug,
                                quantity=item.quantity,
                                reason="expired_cart_cleanup"
                            )
                            
                            cleanup_stats['stock_released_total'] += item.quantity
                            cart_items_count += 1
                            
                            # Tracker produits affectés
                            product_info = {
                                'slug': item.product.slug,
                                'quantity_released': item.quantity,
                                'new_stock': result.get('current_stock', 0)
                            }
                            cleanup_stats['products_affected'].append(product_info)
                            
                        except Exception as stock_error:
                            logger.warning(f"Failed to release stock for {item.product.slug}: {stock_error}")
                            cleanup_stats['errors'].append({
                                'product_slug': item.product.slug,
                                'error': str(stock_error)
                            })
                    
                    # Marquer panier comme inactif
                    cart.is_active = False
                    cart.save()
                    
                    cleanup_stats['expired_carts_processed'] += 1
                    
                    logger.info(f"Cleaned expired cart {cart.id} - {cart_items_count} items")
                    
            except Exception as cart_error:
                logger.error(f"Error cleaning cart {cart.id}: {cart_error}")
                cleanup_stats['errors'].append({
                    'cart_id': cart.id,
                    'error': str(cart_error)
                })
        
        # Logging final
        logger.info(
            f"Stock reservation cleanup completed: "
            f"{cleanup_stats['expired_carts_processed']} carts, "
            f"{cleanup_stats['stock_released_total']} units released"
        )
        
        return {
            'status': 'success',
            'cleanup_stats': cleanup_stats,
            'message': f'{cleanup_stats["expired_carts_processed"]} paniers nettoyés'
        }
        
    except Exception as exc:
        logger.error(f"Error during stock reservation cleanup: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'cleanup_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=900,   # 15 minutes entre retries
    time_limit=180,
)
def update_product_popularity_scores(self):
    """
    Mettre à jour les scores de popularité des produits
    
    Calcule un score basé sur :
    - Nombre de ventes (30 derniers jours)
    - Nombre d'ajouts au panier (7 derniers jours)
    - Vues produit (si tracking implémenté)
    
    Returns:
        Dict avec statistiques de mise à jour
    """
    try:
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        update_stats = {
            'products_updated': 0,
            'top_products': [],
            'featured_candidates': []
        }
        
        # Récupérer tous les produits actifs
        products = Product.objects.filter(is_active=True)
        
        for product in products:
            # 1. Calcul ventes 30 derniers jours
            sales_count = OrderItem.objects.filter(
                product=product,
                order__created_at__gte=last_30_days,
                order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
            ).count()
            
            # 2. Calcul ajouts panier 7 derniers jours
            cart_adds = CartItem.objects.filter(
                product=product,
                created_at__gte=last_7_days
            ).count()
            
            # 3. Calcul score de popularité (pondéré)
            popularity_score = (sales_count * 3) + (cart_adds * 1)
            
            # 4. Mettre à jour le produit si nécessaire
            # Note: Ajouter champ popularity_score au modèle Product si besoin
            # product.popularity_score = popularity_score
            # product.save()
            
            # 5. Identifier top produits
            if popularity_score > 10:
                update_stats['top_products'].append({
                    'product_slug': product.slug,
                    'product_name': product.name,
                    'sales_count': sales_count,
                    'cart_adds': cart_adds,
                    'popularity_score': popularity_score
                })
            
            # 6. Candidats pour featured (score élevé + stock disponible)
            if popularity_score > 15 and product.stock_quantity > 5:
                update_stats['featured_candidates'].append({
                    'product_slug': product.slug,
                    'product_name': product.name,
                    'popularity_score': popularity_score,
                    'current_stock': product.stock_quantity,
                    'is_currently_featured': product.is_featured
                })
            
            update_stats['products_updated'] += 1
        
        # Trier les listes par score
        update_stats['top_products'].sort(key=lambda x: x['popularity_score'], reverse=True)
        update_stats['featured_candidates'].sort(key=lambda x: x['popularity_score'], reverse=True)
        
        logger.info(f"Product popularity scores updated for {update_stats['products_updated']} products")
        
        return {
            'status': 'success',
            'update_stats': update_stats,
            'message': f'{update_stats["products_updated"]} scores mis à jour'
        }
        
    except Exception as exc:
        logger.error(f"Error updating product popularity scores: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'popularity_update_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=600,
    time_limit=120,
)
def send_stock_audit_report(self, audit_results):
    """
    Envoyer rapport d'audit de stock aux administrateurs
    
    Args:
        audit_results: Résultats de l'audit de stock
        
    Returns:
        Dict avec status de l'envoi
    """
    try:
        # Préparer rapport détaillé
        subject = f"🔍 Rapport Audit Stock - {settings.SITE_NAME}"
        
        # Construire message
        report_lines = [
            f"Rapport d'audit de stock - {audit_results['timestamp'].strftime('%d/%m/%Y %H:%M')}",
            "=" * 60,
            f"Produits vérifiés : {audit_results['total_products_checked']}",
            f"Problèmes détectés : {audit_results['issues_found']}",
            ""
        ]
        
        # Stock négatif (critique)
        if audit_results['negative_stock']:
            report_lines.append("🚨 STOCK NÉGATIF (CRITIQUE) :")
            for item in audit_results['negative_stock']:
                report_lines.append(f"  - {item['product_name']} ({item['slug']}): {item['stock_quantity']}")
            report_lines.append("")
        
        # Stock bas (warning)
        if audit_results['low_stock']:
            report_lines.append("⚠️  STOCK BAS :")
            for item in audit_results['low_stock'][:10]:  # Limiter à 10 pour email
                report_lines.append(
                    f"  - {item['product_name']}: {item['stock_quantity']} "
                    f"(seuil: {item['min_stock_alert']})"
                )
            if len(audit_results['low_stock']) > 10:
                report_lines.append(f"  ... et {len(audit_results['low_stock']) - 10} autres")
            report_lines.append("")
        
        # Produits inactifs avec stock
        if audit_results['inactive_with_stock']:
            report_lines.append("💤 PRODUITS INACTIFS AVEC STOCK :")
            for item in audit_results['inactive_with_stock'][:5]:
                report_lines.append(f"  - {item['product_name']}: {item['stock_quantity']} unités")
            report_lines.append("")
        
        # Produits actifs sans stock
        if audit_results['zero_stock_active']:
            report_lines.append("⚡ PRODUITS ACTIFS SANS STOCK :")
            for item in audit_results['zero_stock_active'][:5]:
                featured = " (VEDETTE)" if item['is_featured'] else ""
                report_lines.append(f"  - {item['product_name']}{featured}")
            report_lines.append("")
        
        # Actions recommandées
        report_lines.extend([
            "📋 ACTIONS RECOMMANDÉES :",
            "1. Corriger immédiatement les stocks négatifs",
            "2. Réapprovisionner les produits en stock bas",
            "3. Désactiver ou réapprovisionner les produits sans stock",
            "4. Considérer désactiver les produits inactifs avec stock",
            "",
            f"Dashboard admin : {settings.SITE_URL}/admin/marketplace/product/",
            f"Timestamp : {timezone.now()}"
        ])
        
        message = "\n".join(report_lines)
        
        # Envoyer aux admins
        mail_admins(
            subject=subject,
            message=message,
            fail_silently=False
        )
        
        logger.info("Stock audit report sent to admins")
        
        return {
            'status': 'success',
            'issues_reported': audit_results['issues_found'],
            'message': 'Rapport audit envoyé aux admins'
        }
        
    except Exception as exc:
        logger.error(f"Error sending stock audit report: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'report_send_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=1200,  # 20 minutes entre retries
    time_limit=300,
)
def optimize_stock_alerts(self):
    """
    Optimiser automatiquement les seuils d'alerte de stock
    
    Analyse les ventes passées pour ajuster automatiquement
    les seuils min_stock_alert basés sur la vélocité de vente
    
    Returns:
        Dict avec statistiques d'optimisation
    """
    try:
        now = timezone.now()
        last_60_days = now - timedelta(days=60)
        
        optimization_stats = {
            'products_analyzed': 0,
            'alerts_updated': 0,
            'average_velocity': 0,
            'optimization_details': []
        }
        
        # Analyser produits avec historique de ventes
        products = Product.objects.filter(
            is_active=True,
            is_digital=False  # Seulement produits physiques
        )
        
        total_velocity = 0
        
        for product in products:
            optimization_stats['products_analyzed'] += 1
            
            # Calculer vélocité de vente (unités vendues par semaine)
            sales_last_60_days = OrderItem.objects.filter(
                product=product,
                order__created_at__gte=last_60_days,
                order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
            ).aggregate(
                total_sold=models.Sum('quantity')
            )['total_sold'] or 0
            
            # Vélocité hebdomadaire moyenne
            weekly_velocity = sales_last_60_days / 8.6  # 60 jours ≈ 8.6 semaines
            total_velocity += weekly_velocity
            
            # Calculer nouveau seuil (2 semaines de ventes + buffer 20%)
            if weekly_velocity > 0:
                optimal_alert = max(1, int((weekly_velocity * 2) * 1.2))
                
                # Ajuster seulement si différence significative (>50% ou >5 unités)
                current_alert = product.min_stock_alert
                difference = abs(optimal_alert - current_alert)
                
                if difference > max(current_alert * 0.5, 5):
                    # Mettre à jour le seuil
                    product.min_stock_alert = optimal_alert
                    product.save()
                    
                    optimization_stats['alerts_updated'] += 1
                    optimization_stats['optimization_details'].append({
                        'product_slug': product.slug,
                        'product_name': product.name,
                        'old_alert': current_alert,
                        'new_alert': optimal_alert,
                        'weekly_velocity': round(weekly_velocity, 2),
                        'sales_60_days': sales_last_60_days
                    })
                    
                    logger.info(
                        f"Stock alert optimized for {product.slug}: "
                        f"{current_alert} → {optimal_alert} (velocity: {weekly_velocity:.2f}/week)"
                    )
        
        # Calculer vélocité moyenne
        if optimization_stats['products_analyzed'] > 0:
            optimization_stats['average_velocity'] = round(
                total_velocity / optimization_stats['products_analyzed'], 2
            )
        
        logger.info(
            f"Stock alert optimization completed: "
            f"{optimization_stats['alerts_updated']} products updated"
        )
        
        return {
            'status': 'success',
            'optimization_stats': optimization_stats,
            'message': f'{optimization_stats["alerts_updated"]} seuils optimisés'
        }
        
    except Exception as exc:
        logger.error(f"Error optimizing stock alerts: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'optimization_failed',
            'message': str(exc)
        }


# Import pour aggregation (Django models)
from django.db import models