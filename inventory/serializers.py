from rest_framework import serializers
from .models import Product, Category, Supplier, StockMovement, StockAlert

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'created_at', 'product_count']
        read_only_fields = ['created_at']

class SupplierSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone', 'address', 
            'contact_person', 'tax_number', 'created_at', 'product_count'
        ]
        read_only_fields = ['created_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'supplier', 'supplier_name', 'description', 'unit', 'price',
            'cost_price', 'quantity', 'minimum_stock', 'maximum_stock',
            'location', 'image', 'stock_status', 'stock_value', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sku']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['stock_value'] = instance.quantity * instance.price
        return data

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'movement_type',
            'movement_type_display', 'quantity', 'quantity_before', 'quantity_after',
            'unit_price', 'total_value', 'reference', 'notes', 'user', 'user_name',
            'date', 'created_at'
        ]
        read_only_fields = ['created_at', 'quantity_before', 'quantity_after', 'total_value']

class StockAlertSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'alert_type',
            'alert_type_display', 'message', 'status', 'status_display',
            'created_at', 'resolved_at', 'resolved_by', 'resolved_by_name'
        ]
        read_only_fields = ['created_at', 'resolved_at', 'resolved_by']