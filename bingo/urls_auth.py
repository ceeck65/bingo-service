"""
URLs para el sistema de autenticación
"""

from django.urls import path
from . import views_auth

app_name = 'bingo_auth'

urlpatterns = [
    # Gestión de API Keys
    path('api-keys/', views_auth.APIKeyListView.as_view(), name='apikey-list'),
    path('api-keys/<uuid:pk>/', views_auth.APIKeyDetailView.as_view(), name='apikey-detail'),
    path('api-keys/create/', views_auth.create_api_key, name='apikey-create'),
    path('api-keys/<uuid:key_id>/revoke/', views_auth.revoke_api_key, name='apikey-revoke'),
    
    # Test de autenticación
    path('test/', views_auth.test_authentication, name='test-auth'),
]

