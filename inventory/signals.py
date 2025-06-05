from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import StockMovement, Product
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=StockMovement)
def validate_stock_movement(sender, instance, **kwargs):
    """
    Validate stock movement before saving:
    - Ensure sufficient stock for outgoing movements
    - Calculate and update product quantity
    """
    try:
        if not instance.pk:  # Only for new movements
            if instance.movement_type == 'OUT':
                # Get current stock level
                current_stock = instance.product.quantity
                
                # Check if there's enough stock
                if current_stock < instance.quantity:
                    raise ValueError(
                        f"Stock insuffisant. Quantité disponible : {current_stock}"
                    )
    except Exception as e:
        logger.error(f"Erreur lors de la validation du mouvement de stock: {str(e)}")
        raise

@receiver(post_save, sender=StockMovement)
def update_stock_quantity(sender, instance, created, **kwargs):
    """
    Update product quantity after stock movement is saved
    """
    try:
        if created:
            product = instance.product
            
            # Update quantity based on movement type
            if instance.movement_type == 'IN':
                product.quantity += instance.quantity
            else:  # OUT
                product.quantity -= instance.quantity
            
            # Save product without triggering other signals
            Product.objects.filter(pk=product.pk).update(
                quantity=product.quantity,
                updated_at=timezone.now()
            )
            
            # Check if stock is low after update
            check_low_stock(product)
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la quantité: {str(e)}")
        raise

@receiver(post_save, sender=Product)
def check_low_stock(sender, instance=None, created=False, **kwargs):
    """
    Check if product stock is below threshold and send notification if needed
    """
    try:
        if instance is None:
            return
            
        product = instance
        
        # Check if stock is below minimum threshold
        if product.quantity <= product.minimum_stock:
            # Log the low stock alert
            logger.warning(
                f"Stock bas pour {product.name}: {product.quantity}/{product.minimum_stock}"
            )
            
            # Send notification if enabled
            if getattr(settings, 'ENABLE_STOCK_NOTIFICATIONS', False):
                subject = f"Alerte Stock Bas - {product.name}"
                message = (
                    f"Le produit {product.name} est en stock bas.\n"
                    f"Quantité actuelle: {product.quantity}\n"
                    f"Stock minimum: {product.minimum_stock}\n"
                    f"Catégorie: {product.category.name}\n"
                    f"Fournisseur: {product.supplier.name if product.supplier else 'Non spécifié'}"
                )
                
                try:
                    # Send email to administrators
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[admin[1] for admin in settings.ADMINS],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de l'email d'alerte: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du stock bas: {str(e)}")

@receiver(post_save, sender=StockMovement)
def log_stock_movement(sender, instance, created, **kwargs):
    """
    Log all stock movements for audit purposes
    """
    if created:
        try:
            logger.info(
                f"Mouvement de stock: {instance.get_movement_type_display()} - "
                f"Produit: {instance.product.name} - "
                f"Quantité: {instance.quantity} - "
                f"Prix unitaire: {instance.unit_price}"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la journalisation du mouvement: {str(e)}")
