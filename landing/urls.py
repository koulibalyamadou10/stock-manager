from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('fonctionnalites/', views.features, name='features'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('demo/', views.demo, name='demo'),
]