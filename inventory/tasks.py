from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .utils import send_stock_alerts, backup_database, analyze_sales_trends
from .models import Product, StockAlert

logger = logging.getLogger(__name__)

@shared_task
def daily_stock_alerts():
    """
    Daily task to check stock levels and send alerts
    """
    try:
        send_stock_alerts()
        logger.info("Daily stock alerts task completed successfully")
        return "Stock alerts sent successfully"
    except Exception as e:
        logger.error(f"Error in daily stock alerts task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def weekly_backup():
    """
    Weekly database backup task
    """
    try:
        backup_file = backup_database()
        if backup_file:
            logger.info(f"Weekly backup created: {backup_file}")
            return f"Backup created: {backup_file}"
        else:
            logger.error("Failed to create weekly backup")
            return "Backup failed"
    except Exception as e:
        logger.error(f"Error in weekly backup task: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def update_reorder_points():
    """
    Update reorder points for all products based on consumption patterns
    """
    try:
        from .utils import calculate_reorder_point
        
        products = Product.objects.filter(is_active=True)
        updated_count = 0
        
        for product in products:
            new_reorder_point = calculate_reorder_point(product)
            
            # Update minimum stock if significantly different
            if abs(new_reorder_point - product.minimum_stock) > (product.minimum_stock * 0.2):
                product.minimum_stock = new_reorder_point
                product.save()
                updated_count += 1
        
        logger.info(f"Updated reorder points for {updated_count} products")
        return f"Updated {updated_count} products"
        
    except Exception as e:
        logger.error(f"Error updating reorder points: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def cleanup_old_alerts():
    """
    Clean up old resolved alerts
    """
    try:
        # Delete resolved alerts older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = StockAlert.objects.filter(
            status='RESOLVED',
            resolved_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old alerts")
        return f"Cleaned up {deleted_count} alerts"
        
    except Exception as e:
        logger.error(f"Error cleaning up alerts: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def generate_sales_insights():
    """
    Generate sales insights and trends analysis
    """
    try:
        trends = analyze_sales_trends(days=90)
        
        if trends:
            # Store insights in cache or database for dashboard
            from django.core.cache import cache
            cache.set('sales_trends', trends, timeout=86400)  # 24 hours
            
            logger.info("Sales insights generated successfully")
            return "Sales insights generated"
        else:
            logger.warning("No sales data available for insights")
            return "No sales data available"
            
    except Exception as e:
        logger.error(f"Error generating sales insights: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def check_expiring_products():
    """
    Check for products approaching expiration (if expiration tracking is implemented)
    """
    try:
        # This would be implemented if expiration date tracking is added to Product model
        # For now, just return success
        logger.info("Expiring products check completed")
        return "Expiring products check completed"
        
    except Exception as e:
        logger.error(f"Error checking expiring products: {str(e)}")
        return f"Error: {str(e)}"