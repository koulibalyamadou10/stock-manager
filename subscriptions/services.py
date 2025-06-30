import requests
import base64
import json
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class LengoPayService:
    """Service pour intégrer l'API Lengo Pay"""
    
    def __init__(self):
        self.api_url = "https://portal.lengopay.com/api/v1/payments"
        self.website_id = getattr(settings, 'LENGO_PAY_WEBSITE_ID', 'STOCKMANAGER_PRO')
        self.license_key = getattr(settings, 'LENGO_PAY_LICENSE_KEY', '')
        
    def get_headers(self):
        """Générer les headers pour l'API Lengo Pay"""
        auth_string = base64.b64encode(f"{self.license_key}:".encode()).decode()
        
        return {
            'Authorization': f'Basic {auth_string}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def create_payment(self, payment):
        """Créer un paiement via l'API Lengo Pay"""
        try:
            # Construire l'URL de retour
            return_url = f"{settings.SITE_URL}/subscriptions/payment-success/"
            callback_url = f"{settings.SITE_URL}/subscriptions/lengo-webhook/"
            
            payload = {
                'websiteid': self.website_id,
                'amount': float(payment.amount),
                'currency': payment.currency,
                'return_url': return_url,
                'callback_url': callback_url,
                'reference': str(payment.id),
                'description': f"Abonnement {payment.subscription.plan.name} - StockManager Pro"
            }
            
            response = requests.post(
                self.api_url,
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Sauvegarder les informations de paiement
                payment.lengo_payment_id = data.get('payment_id')
                payment.lengo_payment_url = data.get('payment_url')
                payment.save()
                
                logger.info(f"Paiement Lengo Pay créé: {payment.lengo_payment_id}")
                
                return data.get('payment_url')
            else:
                logger.error(f"Erreur API Lengo Pay: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion Lengo Pay: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erreur création paiement Lengo Pay: {str(e)}")
            return None
    
    def check_payment_status(self, payment_id):
        """Vérifier le statut d'un paiement"""
        try:
            url = f"{self.api_url}/{payment_id}/status"
            
            response = requests.get(
                url,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur vérification statut: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur vérification statut: {str(e)}")
            return None