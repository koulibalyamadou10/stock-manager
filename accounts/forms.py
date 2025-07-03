from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text='Requis. Entrez une adresse email valide.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des messages d'aide
        self.fields['username'].help_text = 'Lettres, chiffres et @/./+/-/_ uniquement.'
        self.fields['password1'].help_text = 'Votre mot de passe doit contenir au moins 8 caractères et ne peut pas être entièrement numérique.'
        self.fields['password2'].help_text = 'Entrez le même mot de passe que précédemment, pour vérification.'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email