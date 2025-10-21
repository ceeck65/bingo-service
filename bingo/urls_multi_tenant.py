"""
URLs para el sistema multi-tenant
"""

from django.urls import path
from . import views_multi_tenant

app_name = 'bingo_multi_tenant'

urlpatterns = [
    # === OPERADORES ===
    path('operators/', views_multi_tenant.OperatorListView.as_view(), name='operator-list'),
    path('operators/<uuid:pk>/', views_multi_tenant.OperatorDetailView.as_view(), name='operator-detail'),
    path('operators/<uuid:operator_id>/statistics/', views_multi_tenant.operator_statistics, name='operator-statistics'),
    
    # === JUGADORES ===
    path('players/', views_multi_tenant.PlayerListView.as_view(), name='player-list'),
    path('players/<uuid:pk>/', views_multi_tenant.PlayerDetailView.as_view(), name='player-detail'),
    path('players/register-by-phone/', views_multi_tenant.register_player_by_phone, name='register-player-by-phone'),
    path('players/link-social/', views_multi_tenant.link_social_account, name='link-social-account'),
    
    # === SESIONES ===
    path('sessions/', views_multi_tenant.BingoSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:pk>/', views_multi_tenant.BingoSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/statistics/', views_multi_tenant.session_statistics, name='session-statistics'),
    path('sessions/join/', views_multi_tenant.join_session, name='join-session'),
    path('sessions/leave/', views_multi_tenant.leave_session, name='leave-session'),
    
    # === PARTICIPACIÓN EN SESIONES ===
    path('player-sessions/', views_multi_tenant.PlayerSessionListView.as_view(), name='player-session-list'),
    
    # === CARTONES EXTENDIDOS ===
    path('cards/', views_multi_tenant.BingoCardExtendedListView.as_view(), name='card-list'),
    path('cards/<uuid:pk>/', views_multi_tenant.BingoCardExtendedDetailView.as_view(), name='card-detail'),
    path('cards/generate-for-session/', views_multi_tenant.generate_cards_for_session, name='generate-cards-for-session'),
    path('cards/select/', views_multi_tenant.select_card, name='select-card'),
    path('cards/select-multiple/', views_multi_tenant.select_multiple_cards, name='select-multiple-cards'),
    path('cards/confirm-purchase/', views_multi_tenant.confirm_card_purchase, name='confirm-card-purchase'),
    path('cards/confirm-multiple-purchase/', views_multi_tenant.confirm_multiple_cards_purchase, name='confirm-multiple-purchase'),
    path('cards/release/', views_multi_tenant.release_card, name='release-card'),
    path('cards/reuse/', views_multi_tenant.reuse_cards_in_session, name='reuse-cards'),
    path('sessions/<uuid:session_id>/available-cards/', views_multi_tenant.get_available_cards, name='available-cards'),
    path('sessions/<uuid:session_id>/player/<uuid:player_id>/cards/', views_multi_tenant.get_player_cards, name='player-cards'),
    
    # === PARTIDAS EXTENDIDAS ===
    path('games/', views_multi_tenant.BingoGameExtendedListView.as_view(), name='game-list'),
    path('games/<uuid:pk>/', views_multi_tenant.BingoGameExtendedDetailView.as_view(), name='game-detail'),
    path('sessions/<uuid:session_id>/game/', views_multi_tenant.get_session_game, name='session-game'),
    path('games/draw-ball/', views_multi_tenant.draw_ball, name='draw-ball'),
    path('games/<uuid:game_id>/draw-ball/', views_multi_tenant.draw_ball_by_id, name='draw-ball-by-id'),
    path('games/<uuid:game_id>/drawn-balls/', views_multi_tenant.get_drawn_balls, name='drawn-balls'),
    path('games/check-winner/', views_multi_tenant.check_winner, name='check-winner'),
]
