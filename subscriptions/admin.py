from django.contrib import admin
from .models import Plan, Subscription, Payment, UsageLimit

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'max_products', 'max_users', 'is_active')
    list_filter = ('plan_type', 'is_active', 'has_ai_features', 'has_advanced_reports')
    search_fields = ('name', 'description')
    ordering = ('price',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date', 'days_remaining')
    list_filter = ('status', 'plan', 'auto_renew')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'
    
    def days_remaining(self, obj):
        return obj.days_remaining
    days_remaining.short_description = 'Jours restants'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subscription', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'currency')
    search_fields = ('subscription__user__username', 'transaction_id', 'lengo_payment_id')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(UsageLimit)
class UsageLimitAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'products_count', 'invoices_this_month', 'users_count', 'last_reset_date')
    list_filter = ('last_reset_date',)
    search_fields = ('subscription__user__username',)