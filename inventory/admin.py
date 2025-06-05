from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, StockMovement, Supplier, StockReport

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'supplier', 'price', 'quantity', 'stock_status')
    list_filter = ('category', 'supplier', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red;">Stock bas</span>')
        return format_html('<span style="color: green;">Stock OK</span>')
    
    stock_status.short_description = "État du stock"

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity', 'date', 'unit_price')
    list_filter = ('movement_type', 'date', 'product__category')
    search_fields = ('product__name', 'notes')
    ordering = ('-date',)

@admin.register(StockReport)
class StockReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'start_date', 'end_date', 'created_at', 'download_link')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}">Télécharger</a>', obj.file.url)
        return "Pas de fichier"
    
    download_link.short_description = "Téléchargement"
