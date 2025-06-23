from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import InvoiceItem, Payment, Invoice
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_totals(sender, instance, **kwargs):
    """
    Update invoice totals when invoice items are modified
    """
    try:
        if instance.invoice_id:
            invoice = instance.invoice
            invoice.calculate_totals()
            invoice.save()
    except Exception as e:
        logger.error(f"Error updating invoice totals: {str(e)}")

@receiver(post_save, sender=Payment)
def check_invoice_payment_status(sender, instance, created, **kwargs):
    """
    Check if invoice is fully paid when a payment is added
    """
    if created:
        try:
            invoice = instance.invoice
            total_payments = invoice.payments.aggregate(
                total=models.Sum('amount'))['total'] or 0
            
            if total_payments >= invoice.total_amount:
                invoice.mark_as_paid()
            elif invoice.status == 'paid' and total_payments < invoice.total_amount:
                # If total payments are less than invoice amount, change status back
                invoice.status = 'sent'
                invoice.save()
                
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")

@receiver(post_save, sender=Invoice)
def check_overdue_status(sender, instance, **kwargs):
    """
    Check if invoice is overdue and update status
    """
    try:
        if instance.is_overdue and instance.status == 'sent':
            instance.status = 'overdue'
            Invoice.objects.filter(pk=instance.pk).update(status='overdue')
    except Exception as e:
        logger.error(f"Error checking overdue status: {str(e)}")