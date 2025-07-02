from django.shortcuts import render
from django.http import JsonResponse
from subscriptions.models import Plan

def home(request):
    """Page d'accueil du site vitrine"""
    plans = Plan.objects.filter(is_active=True).order_by('price')
    
    # Statistiques fictives pour la vitrine
    stats = {
        'clients_satisfaits': 1500,
        'entreprises_actives': 850,
        'factures_generees': 45000,
        'economies_realisees': 2500000  # en GNF
    }
    
    context = {
        'plans': plans,
        'stats': stats,
    }
    return render(request, 'landing/home.html', context)

def features(request):
    """Page des fonctionnalités détaillées"""
    return render(request, 'landing/features.html')

def about(request):
    """Page à propos"""
    return render(request, 'landing/about.html')

def contact(request):
    """Page de contact"""
    if request.method == 'POST':
        # Traitement du formulaire de contact
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Ici vous pouvez ajouter la logique d'envoi d'email
        # Pour l'instant, on retourne juste un succès
        
        return JsonResponse({'success': True, 'message': 'Votre message a été envoyé avec succès!'})
    
    return render(request, 'landing/contact.html')

def demo(request):
    """Page de demande de démo"""
    return render(request, 'landing/demo.html')