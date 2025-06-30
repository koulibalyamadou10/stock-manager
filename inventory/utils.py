import barcode
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import os
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
import csv
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import logging

logger = logging.getLogger(__name__)

def generate_barcode(code, product_name=""):
    """
    Generate barcode image for a product
    """
    try:
        # Use Code128 format
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(code, writer=ImageWriter())
        
        # Generate barcode image
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        # Create filename
        filename = f"barcode_{code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        return ContentFile(buffer.getvalue(), name=filename)
    
    except Exception as e:
        logger.error(f"Error generating barcode for {code}: {str(e)}")
        return None

def generate_qr_code(data, size=10, border=4):
    """
    Generate QR code for product information
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create filename
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        return ContentFile(buffer.getvalue(), name=filename)
    
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return None

def calculate_reorder_point(product):
    """
    Calculate optimal reorder point for a product based on consumption history
    """
    try:
        from .models import StockMovement
        
        # Get consumption data for last 90 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)
        
        consumption = StockMovement.objects.filter(
            product=product,
            movement_type='OUT',
            date__range=[start_date, end_date]
        ).aggregate(
            total_quantity=Sum('quantity'),
            movement_count=Count('id')
        )
        
        total_consumed = consumption['total_quantity'] or 0
        movement_count = consumption['movement_count'] or 0
        
        if total_consumed > 0:
            # Calculate average daily consumption
            days = (end_date - start_date).days
            daily_consumption = total_consumed / days if days > 0 else 0
            
            # Calculate lead time (assume 7 days default)
            lead_time = 7
            
            # Safety stock (25% of lead time demand)
            safety_stock = (daily_consumption * lead_time) * 0.25
            
            # Reorder point = (Daily consumption × Lead time) + Safety stock
            reorder_point = (daily_consumption * lead_time) + safety_stock
            
            return max(int(reorder_point), product.minimum_stock)
        
        return product.minimum_stock
    
    except Exception as e:
        logger.error(f"Error calculating reorder point for {product.name}: {str(e)}")
        return product.minimum_stock

def generate_stock_report(start_date, end_date, report_type='detailed'):
    """
    Generate comprehensive stock report
    """
    try:
        from .models import Product, StockMovement, Category
        
        report_data = {
            'generated_at': timezone.now(),
            'period': {
                'start': start_date,
                'end': end_date
            },
            'summary': {},
            'products': [],
            'categories': [],
            'movements': []
        }
        
        # Summary statistics
        total_products = Product.objects.filter(is_active=True).count()
        total_value = Product.objects.filter(is_active=True).aggregate(
            value=Sum(F('quantity') * F('price'))
        )['value'] or 0
        
        low_stock_count = Product.objects.filter(
            quantity__lte=F('minimum_stock'),
            is_active=True
        ).count()
        
        # Movements in period
        movements = StockMovement.objects.filter(
            date__range=[start_date, end_date]
        )
        
        total_entries = movements.filter(movement_type='IN').aggregate(
            quantity=Sum('quantity'),
            value=Sum('total_value')
        )
        
        total_exits = movements.filter(movement_type='OUT').aggregate(
            quantity=Sum('quantity'),
            value=Sum('total_value')
        )
        
        report_data['summary'] = {
            'total_products': total_products,
            'total_stock_value': total_value,
            'low_stock_products': low_stock_count,
            'entries': {
                'quantity': total_entries['quantity'] or 0,
                'value': total_entries['value'] or 0
            },
            'exits': {
                'quantity': total_exits['quantity'] or 0,
                'value': total_exits['value'] or 0
            }
        }
        
        if report_type == 'detailed':
            # Product details
            products = Product.objects.filter(is_active=True).select_related('category', 'supplier')
            for product in products:
                product_movements = movements.filter(product=product)
                
                report_data['products'].append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'category': product.category.name,
                    'current_stock': product.quantity,
                    'minimum_stock': product.minimum_stock,
                    'stock_value': product.quantity * product.price,
                    'movements_count': product_movements.count(),
                    'total_entries': product_movements.filter(movement_type='IN').aggregate(
                        Sum('quantity'))['quantity__sum'] or 0,
                    'total_exits': product_movements.filter(movement_type='OUT').aggregate(
                        Sum('quantity'))['quantity__sum'] or 0,
                    'reorder_point': calculate_reorder_point(product)
                })
            
            # Category analysis
            categories = Category.objects.filter(is_active=True).annotate(
                product_count=Count('products', filter=Q(products__is_active=True))
            )
            
            for category in categories:
                category_value = Product.objects.filter(
                    category=category,
                    is_active=True
                ).aggregate(
                    value=Sum(F('quantity') * F('price'))
                )['value'] or 0
                
                report_data['categories'].append({
                    'name': category.name,
                    'product_count': category.product_count,
                    'total_value': category_value
                })
        
        return report_data
    
    except Exception as e:
        logger.error(f"Error generating stock report: {str(e)}")
        return None

def export_to_csv(data, filename):
    """
    Export data to CSV format
    """
    try:
        output = BytesIO()
        writer = csv.writer(output)
        
        if isinstance(data, list) and len(data) > 0:
            # Write headers
            if isinstance(data[0], dict):
                headers = data[0].keys()
                writer.writerow(headers)
                
                # Write data
                for row in data:
                    writer.writerow(row.values())
        
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return None

def backup_database():
    """
    Create database backup
    """
    try:
        from django.core.management import call_command
        from django.conf import settings
        
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'stockmanager_backup_{timestamp}.json'
        
        with open(backup_file, 'w') as f:
            call_command('dumpdata', stdout=f, indent=2)
        
        logger.info(f"Database backup created: {backup_file}")
        return backup_file
    
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        return None

def analyze_sales_trends(days=90):
    """
    Analyze sales trends for predictive analytics
    """
    try:
        from billing.models import InvoiceItem
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Daily sales data
        daily_sales = []
        current_date = start_date
        
        while current_date <= end_date:
            sales = InvoiceItem.objects.filter(
                invoice__issue_date=current_date,
                invoice__status='paid'
            ).aggregate(
                total_quantity=Sum('quantity'),
                total_value=Sum(F('quantity') * F('unit_price'))
            )
            
            daily_sales.append({
                'date': current_date,
                'quantity': sales['total_quantity'] or 0,
                'value': float(sales['total_value'] or 0)
            })
            
            current_date += timedelta(days=1)
        
        # Calculate trends
        values = [day['value'] for day in daily_sales]
        if len(values) > 1:
            # Simple trend calculation
            first_half = sum(values[:len(values)//2])
            second_half = sum(values[len(values)//2:])
            
            if first_half > 0:
                trend_percentage = ((second_half - first_half) / first_half) * 100
            else:
                trend_percentage = 0
            
            return {
                'daily_sales': daily_sales,
                'trend_percentage': trend_percentage,
                'average_daily_sales': sum(values) / len(values),
                'total_sales': sum(values),
                'best_day': max(daily_sales, key=lambda x: x['value']),
                'worst_day': min(daily_sales, key=lambda x: x['value'])
            }
        
        return None
    
    except Exception as e:
        logger.error(f"Error analyzing sales trends: {str(e)}")
        return None

def generate_product_performance_report():
    """
    Generate product performance analysis
    """
    try:
        from .models import Product
        from billing.models import InvoiceItem
        
        # Get products with sales data
        products = Product.objects.filter(is_active=True)
        performance_data = []
        
        for product in products:
            # Sales data for last 90 days
            last_90_days = timezone.now() - timedelta(days=90)
            
            sales_data = InvoiceItem.objects.filter(
                product=product,
                invoice__issue_date__gte=last_90_days,
                invoice__status='paid'
            ).aggregate(
                total_quantity=Sum('quantity'),
                total_revenue=Sum(F('quantity') * F('unit_price')),
                order_count=Count('invoice', distinct=True)
            )
            
            # Calculate metrics
            total_quantity = sales_data['total_quantity'] or 0
            total_revenue = float(sales_data['total_revenue'] or 0)
            order_count = sales_data['order_count'] or 0
            
            # Profit calculation
            cost = product.cost_price * total_quantity
            profit = total_revenue - cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Stock turnover
            avg_stock = (product.quantity + product.minimum_stock) / 2
            turnover_rate = total_quantity / avg_stock if avg_stock > 0 else 0
            
            performance_data.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name,
                'current_stock': product.quantity,
                'sales_quantity': total_quantity,
                'sales_revenue': total_revenue,
                'order_count': order_count,
                'profit': profit,
                'profit_margin': profit_margin,
                'turnover_rate': turnover_rate,
                'stock_status': product.stock_status,
                'reorder_point': calculate_reorder_point(product)
            })
        
        # Sort by revenue
        performance_data.sort(key=lambda x: x['sales_revenue'], reverse=True)
        
        return performance_data
    
    except Exception as e:
        logger.error(f"Error generating product performance report: {str(e)}")
        return []

def optimize_stock_levels():
    """
    Provide stock optimization recommendations
    """
    try:
        from .models import Product
        
        recommendations = []
        products = Product.objects.filter(is_active=True)
        
        for product in products:
            current_stock = product.quantity
            minimum_stock = product.minimum_stock
            reorder_point = calculate_reorder_point(product)
            
            # Analyze stock situation
            if current_stock == 0:
                urgency = 'critical'
                action = 'Réapprovisionnement immédiat requis'
                recommended_quantity = reorder_point * 2
            elif current_stock <= minimum_stock:
                urgency = 'high'
                action = 'Réapprovisionnement urgent'
                recommended_quantity = reorder_point
            elif current_stock <= reorder_point:
                urgency = 'medium'
                action = 'Planifier réapprovisionnement'
                recommended_quantity = reorder_point - current_stock
            elif current_stock > product.maximum_stock:
                urgency = 'low'
                action = 'Surstock - Promouvoir les ventes'
                recommended_quantity = 0
            else:
                continue  # Stock OK
            
            recommendations.append({
                'product_id': product.id,
                'product_name': product.name,
                'current_stock': current_stock,
                'minimum_stock': minimum_stock,
                'reorder_point': reorder_point,
                'recommended_quantity': recommended_quantity,
                'urgency': urgency,
                'action': action,
                'estimated_cost': recommended_quantity * product.cost_price
            })
        
        # Sort by urgency
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: urgency_order.get(x['urgency'], 4))
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error optimizing stock levels: {str(e)}")
        return []

def send_stock_alerts():
    """
    Send stock alert notifications
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from .models import Product, StockAlert
        
        if not settings.ENABLE_STOCK_NOTIFICATIONS:
            return
        
        # Find products with low stock
        low_stock_products = Product.objects.filter(
            quantity__lte=F('minimum_stock'),
            is_active=True
        )
        
        if not low_stock_products.exists():
            return
        
        # Create or update alerts
        for product in low_stock_products:
            alert_type = 'OUT_OF_STOCK' if product.quantity == 0 else 'LOW_STOCK'
            message = f"Stock {'épuisé' if product.quantity == 0 else 'faible'} pour {product.name}: {product.quantity}/{product.minimum_stock}"
            
            alert, created = StockAlert.objects.get_or_create(
                product=product,
                alert_type=alert_type,
                status='ACTIVE',
                defaults={'message': message}
            )
            
            if not created:
                alert.message = message
                alert.save()
        
        # Send email notification
        if hasattr(settings, 'ADMINS') and settings.ADMINS:
            subject = f"Alerte Stock - {low_stock_products.count()} produits nécessitent attention"
            message = f"""
            Bonjour,
            
            {low_stock_products.count()} produits nécessitent votre attention:
            
            """
            
            for product in low_stock_products[:10]:  # Limit to 10 products in email
                message += f"- {product.name}: {product.quantity}/{product.minimum_stock}\n"
            
            if low_stock_products.count() > 10:
                message += f"\n... et {low_stock_products.count() - 10} autres produits.\n"
            
            message += "\nConnectez-vous au système pour plus de détails."
            
            admin_emails = [admin[1] for admin in settings.ADMINS]
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True
            )
        
        logger.info(f"Stock alerts sent for {low_stock_products.count()} products")
        
    except Exception as e:
        logger.error(f"Error sending stock alerts: {str(e)}")