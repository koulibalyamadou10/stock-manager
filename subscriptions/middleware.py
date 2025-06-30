from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Subscription

class SubscriptionMiddleware:
    """Middleware pour vérifier les abonnements"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs qui ne nécessitent pas d'abonnement
        self.exempt_urls = [
            '/admin/',
            '/accounts/',
            '/subscriptions/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Vérifier si l'URL est exemptée
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Vérifier si l'utilisateur est connecté
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Vérifier l'abonnement
        try:
            subscription = request.user.subscription
            
            # Rediriger vers la page de tarification si pas d'abonnement actif
            if not subscription.is_active:
                if request.path != reverse('subscriptions:pricing'):
                    messages.warning(request, 'Votre abonnement a expiré. Veuillez renouveler votre abonnement.')
                    return redirect('subscriptions:pricing')
                    
        except Subscription.DoesNotExist:
            # Rediriger vers la page de tarification si pas d'abonnement
            if request.path != reverse('subscriptions:pricing'):
                messages.info(request, 'Veuillez choisir un plan d\'abonnement pour continuer.')
                return redirect('subscriptions:pricing')
        
        return self.get_response(request)