from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import RegisterForm
from subscriptions.models import Plan, Subscription
from django.utils import timezone
from datetime import timedelta

def register(request):
    """Vue d'inscription utilisateur"""
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Créer un abonnement gratuit par défaut
            try:
                free_plan = Plan.objects.get(plan_type='free')
                subscription = Subscription.objects.create(
                    user=user,
                    plan=free_plan,
                    status='active',
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=365*10)  # 10 ans pour le plan gratuit
                )
                
                # Créer les limites d'utilisation
                from subscriptions.models import UsageLimit
                UsageLimit.objects.create(subscription=subscription)
                
            except Plan.DoesNotExist:
                # Si le plan gratuit n'existe pas, on continue sans créer d'abonnement
                pass
            
            login(request, user)
            messages.success(request, 'Votre compte a été créé avec succès!')
            return redirect('subscriptions:pricing')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    """Vue du profil utilisateur"""
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    """Vue de modification du profil"""
    if request.method == 'POST':
        # Mettre à jour les informations du profil
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Votre profil a été mis à jour avec succès!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/edit_profile.html')

@login_required
def change_password(request):
    """Vue de changement de mot de passe"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mettre à jour la session pour éviter la déconnexion
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})