from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
import json
from .models import Product, Category, Supplier, StockMovement, StockAlert
from .serializers import (
    ProductSerializer, CategorySerializer, SupplierSerializer,
    StockMovementSerializer, StockAlertSerializer
)
from .utils import (
    generate_stock_report, analyze_sales_trends,
    generate_product_performance_report, optimize_stock_levels
)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status', None)
        if stock_status == 'low':
            queryset = queryset.filter(quantity__lte=F('minimum_stock'))
        elif stock_status == 'out':
            queryset = queryset.filter(quantity=0)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search)
            )
        
        return queryset.select_related('category', 'supplier')
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = self.get_queryset().filter(quantity__lte=F('minimum_stock'))
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get product performance report"""
        performance_data = generate_product_performance_report()
        return Response(performance_data)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust product stock"""
        product = self.get_object()
        quantity = request.data.get('quantity', 0)
        reason = request.data.get('reason', 'Manual adjustment')
        
        try:
            # Create stock movement
            movement = StockMovement.objects.create(
                product=product,
                movement_type='ADJUSTMENT',
                quantity=abs(quantity),
                quantity_before=product.quantity,
                quantity_after=product.quantity + quantity,
                unit_price=product.price,
                total_value=abs(quantity) * product.price,
                notes=reason,
                user=request.user
            )
            
            # Update product quantity
            product.quantity += quantity
            product.save()
            
            return Response({
                'message': 'Stock adjusted successfully',
                'new_quantity': product.quantity
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def with_stats(self, request):
        """Get categories with product statistics"""
        categories = self.get_queryset().annotate(
            product_count=Count('products', filter=Q(products__is_active=True)),
            total_value=Sum(
                F('products__quantity') * F('products__price'),
                filter=Q(products__is_active=True)
            )
        )
        
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'product_count': category.product_count or 0,
                'total_value': float(category.total_value or 0)
            })
        
        return Response(data)

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products from this supplier"""
        supplier = self.get_object()
        products = Product.objects.filter(supplier=supplier, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockMovement.objects.select_related('product', 'user')
        
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by movement type
        movement_type = self.request.query_params.get('movement_type', None)
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get movement summary statistics"""
        queryset = self.get_queryset()
        
        summary = {
            'total_movements': queryset.count(),
            'total_entries': queryset.filter(movement_type='IN').count(),
            'total_exits': queryset.filter(movement_type='OUT').count(),
            'total_value': queryset.aggregate(
                total=Sum('total_value')
            )['total'] or 0
        }
        
        return Response(summary)

class StockAlertViewSet(viewsets.ModelViewSet):
    queryset = StockAlert.objects.all()
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockAlert.objects.select_related('product')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', 'ACTIVE')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        alert.status = 'RESOLVED'
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        
        return Response({'message': 'Alert resolved successfully'})
    
    @action(detail=False, methods=['post'])
    def resolve_all(self, request):
        """Resolve all active alerts"""
        alerts = self.get_queryset().filter(status='ACTIVE')
        count = alerts.update(
            status='RESOLVED',
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        
        return Response({
            'message': f'{count} alerts resolved successfully',
            'count': count
        })

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_categories': Category.objects.filter(is_active=True).count(),
            'total_suppliers': Supplier.objects.filter(is_active=True).count(),
            'low_stock_count': Product.objects.filter(
                quantity__lte=F('minimum_stock'),
                is_active=True
            ).count(),
            'total_stock_value': Product.objects.filter(is_active=True).aggregate(
                value=Sum(F('quantity') * F('price'))
            )['value'] or 0,
            'recent_movements': StockMovement.objects.filter(
                date__gte=timezone.now() - timedelta(days=1)
            ).count()
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def sales_trends(self, request):
        """Get sales trends analysis"""
        days = int(request.query_params.get('days', 90))
        trends = analyze_sales_trends(days)
        return Response(trends or {})
    
    @action(detail=False, methods=['get'])
    def stock_optimization(self, request):
        """Get stock optimization recommendations"""
        recommendations = optimize_stock_levels()
        return Response(recommendations)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate comprehensive stock report"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        report_type = request.data.get('report_type', 'detailed')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            report = generate_stock_report(start_date, end_date, report_type)
            
            if report:
                return Response(report)
            else:
                return Response(
                    {'error': 'Failed to generate report'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )