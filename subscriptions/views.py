from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
from django.utils import timezone
import json
import requests
import base64
from datetime import timedelta
from .models import Plan, Subscription, Payment, UsageLimit, BusinessType
from .services import LengoPayService

def pricing_page(request):
    """Page de tarification avec les plans d'abonnement"""
    plans = Plan.objects.filter(is_active=True).order_by('price')
    
    # Ajouter les fonctionnalités détaillées pour chaque plan
    plan_features = {
        'free': [
            'Gestion simple du stock (ajout, sortie, alerte)',
            'Enregistrement des ventes quotidiennes',
            'Historique des opérations',
            'Alertes de stock minimum',
            'Interface mobile responsive',
            'Support communautaire par WhatsApp',
            '1 seul utilisateur',
            '1 seule boutique'
        ],
        'complete': [
            'Toutes les fonctionnalités Start +',
            'Multi-utilisateur (jusqu\'à 3)',
            'Statistiques simplifiées (ventes, produits, charges)',
            'Gestion des flux financiers (entrées/sorties, bénéfices)',
            'Génération de factures PDF',
            'Envoi d\'email automatique au client',
            'Sauvegarde cloud et sécurité renforcée',
            'Support standard'
        ],
        'premium': [
            'Toutes les fonctionnalités Business +',
            'Nombre illimité de boutiques',
            'Gestion multi-utilisateurs illimitée',
            'Gestion avancée du stock (FIFO, historiques)',
            'Comptabilité simplifiée (charges, rentabilité)',
            'Modules personnalisés selon activité',
            'Exports CSV, sauvegarde automatique',
            'Accès à l\'IA (assistant + prévision ventes)',
            'Support prioritaire 24h/24'
        ]
    }
    
    context = {
        'plans': plans,
        'plan_features': plan_features,
    }
    return render(request, 'subscriptions/pricing.html', context)

@login_required
def subscribe(request, plan_id):
    """Souscrire à un plan"""
    plan = get_object_or_404(Plan, id=plan_id, is_active=True)
    business_types = BusinessType.objects.filter(is_active=True).order_by('name')
    
    # Vérifier si l'utilisateur a déjà un abonnement
    try:
        subscription = request.user.subscription
        if subscription.is_active and subscription.plan == plan:
            messages.info(request, 'Vous êtes déjà abonné à ce plan.')
            return redirect('subscriptions:my_subscription')
    except Subscription.DoesNotExist:
        subscription = None
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'lengo_pay')
        business_type_id = request.POST.get('business_type')
        
        # Vérifier si un type d'entreprise a été sélectionné
        business_type = None
        if business_type_id:
            try:
                business_type = BusinessType.objects.get(id=business_type_id)
            except BusinessType.DoesNotExist:
                pass
        
        # Créer ou mettre à jour l'abonnement
        if subscription:
            subscription.plan = plan
            subscription.status = 'pending'
            if business_type:
                subscription.business_type = business_type
            subscription.save()
        else:
            subscription = Subscription.objects.create(
                user=request.user,
                plan=plan,
                business_type=business_type,
                status='pending',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30)
            )
            
            # Créer les limites d'utilisation
            UsageLimit.objects.create(subscription=subscription)
        
        # Plan gratuit - activation immédiate
        if plan.plan_type == 'free':
            subscription.status = 'active'
            subscription.save()
            messages.success(request, 'Votre abonnement gratuit a été activé!')
            return redirect('inventory:dashboard')
        
        # Plans payants - créer un paiement
        payment = Payment.objects.create(
            subscription=subscription,
            amount=plan.price,
            payment_method=payment_method
        )
        
        if payment_method == 'lengo_pay':
            # Intégrer avec Lengo Pay
            lengo_service = LengoPayService()
            payment_url = lengo_service.create_payment(payment)
            
            if payment_url:
                return redirect(payment_url)
            else:
                messages.error(request, 'Erreur lors de la création du paiement. Veuillez réessayer.')
        
        return redirect('subscriptions:payment_pending', payment_id=payment.id)
    
    context = {
        'plan': plan,
        'subscription': subscription,
        'business_types': business_types,
    }
    return render(request, 'subscriptions/subscribe.html', context)

@login_required
def my_subscription(request):
    """Page de gestion de l'abonnement utilisateur"""
    try:
        subscription = request.user.subscription
        usage = subscription.usage
        recent_payments = subscription.payments.order_by('-created_at')[:5]
    except Subscription.DoesNotExist:
        return redirect('subscriptions:pricing')
    
    context = {
        'subscription': subscription,
        'usage': usage,
        'recent_payments': recent_payments,
    }
    return render(request, 'subscriptions/my_subscription.html', context)

@login_required
def payment_pending(request, payment_id):
    """Page d'attente de paiement"""
    payment = get_object_or_404(Payment, id=payment_id, subscription__user=request.user)
    
    context = {
        'payment': payment,
    }
    return render(request, 'subscriptions/payment_pending.html', context)

@csrf_exempt
@require_POST
def lengo_webhook(request):
    """Webhook pour recevoir les notifications de Lengo Pay"""
    try:
        data = json.loads(request.body)
        
        # Vérifier la signature (si implémentée par Lengo Pay)
        # signature = request.headers.get('X-Lengo-Signature')
        
        payment_id = data.get('payment_id')
        status = data.get('status')
        transaction_id = data.get('transaction_id')
        
        if payment_id:
            try:
                payment = Payment.objects.get(lengo_payment_id=payment_id)
                
                if status == 'completed':
                    payment.status = 'completed'
                    payment.transaction_id = transaction_id
                    payment.payment_date = timezone.now()
                    payment.save()
                    
                    # Activer l'abonnement
                    subscription = payment.subscription
                    subscription.status = 'active'
                    subscription.save()
                    
                elif status == 'failed':
                    payment.status = 'failed'
                    payment.failure_reason = data.get('failure_reason', 'Paiement échoué')
                    payment.save()
                
                return JsonResponse({'status': 'success'})
                
            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment not found'}, status=404)
        
        return JsonResponse({'error': 'Invalid data'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_payment_status(request, payment_id):
    """API pour vérifier le statut d'un paiement"""
    try:
        payment = Payment.objects.get(id=payment_id, subscription__user=request.user)
        
        return JsonResponse({
            'status': payment.status,
            'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
            'redirect_url': '/inventory/' if payment.status == 'completed' else None
        })
        
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

@login_required
def cancel_subscription(request):
    """Annuler l'abonnement"""
    if request.method == 'POST':
        try:
            subscription = request.user.subscription
            subscription.status = 'cancelled'
            subscription.auto_renew = False
            subscription.save()
            
            messages.success(request, 'Votre abonnement a été annulé.')
            return redirect('subscriptions:my_subscription')
            
        except Subscription.DoesNotExist:
            messages.error(request, 'Aucun abonnement trouvé.')
    
    return redirect('subscriptions:my_subscription')

def check_subscription_required(user, feature_type='basic'):
    """Vérifier si l'utilisateur a accès à une fonctionnalité"""
    try:
        subscription = user.subscription
        if not subscription.is_active:
            return False, "Abonnement expiré"
        
        plan = subscription.plan
        
        if feature_type == 'ai' and not plan.has_ai_features:
            return False, "Fonctionnalité IA non disponible dans votre plan"
        
        if feature_type == 'advanced_reports' and not plan.has_advanced_reports:
            return False, "Rapports avancés non disponibles dans votre plan"
        
        if feature_type == 'api' and not plan.has_api_access:
            return False, "Accès API non disponible dans votre plan"
        
        return True, "Accès autorisé"
        
    except Subscription.DoesNotExist:
        return False, "Aucun abonnement actif"