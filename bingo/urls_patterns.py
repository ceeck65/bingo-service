"""
URLs para el sistema de patrones de victoria
"""

from django.urls import path
from . import views_patterns

app_name = 'patterns'

urlpatterns = [
    # CRUD de Patrones
    path('', views_patterns.WinningPatternListView.as_view(), name='pattern-list'),
    path('<uuid:pk>/', views_patterns.WinningPatternDetailView.as_view(), name='pattern-detail'),
    path('create/', views_patterns.WinningPatternCreateView.as_view(), name='pattern-create'),
    path('<uuid:pk>/update/', views_patterns.WinningPatternUpdateView.as_view(), name='pattern-update'),
    path('<uuid:pk>/delete/', views_patterns.WinningPatternDeleteView.as_view(), name='pattern-delete'),
    
    # Patrones por tipo de bingo
    path('available/<str:bingo_type>/', views_patterns.get_available_patterns_for_bingo_type, name='patterns-by-type'),
    
    # Configuración de sesiones
    path('sessions/<uuid:session_id>/configure/', views_patterns.configure_session_patterns, name='session-configure-patterns'),
    path('sessions/<uuid:session_id>/patterns/', views_patterns.get_session_patterns, name='session-patterns'),
    
    # Verificación de ganadores
    path('check-winner/', views_patterns.check_winner_with_patterns, name='check-winner'),
    path('games/<uuid:game_id>/check-all-cards/', views_patterns.check_all_cards_in_game, name='check-all-cards'),
]

