from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.pricing_page, name='pricing'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('payment-pending/<uuid:payment_id>/', views.payment_pending, name='payment_pending'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    
    # API endpoints
    path('check-payment/<uuid:payment_id>/', views.check_payment_status, name='check_payment_status'),
    
    # Webhooks
    path('lengo-webhook/', views.lengo_webhook, name='lengo_webhook'),
]