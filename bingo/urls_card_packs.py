"""
URLs para el sistema de reutilización de cartas
"""

from django.urls import path
from . import views_card_packs

urlpatterns = [
    # === CARD PACKS ===
    path('packs/', views_card_packs.CardPackListView.as_view(), name='cardpack-list'),
    path('packs/<uuid:pk>/', views_card_packs.CardPackDetailView.as_view(), name='cardpack-detail'),
    path('packs/<uuid:pack_id>/generate-cards/', views_card_packs.generate_cards_for_pack, name='cardpack-generate-cards'),
    path('packs/<uuid:pack_id>/cards/', views_card_packs.get_pack_cards, name='cardpack-cards'),
    
    # === PLAYER CARDS ===
    path('players/<uuid:player_id>/acquire-cards/', views_card_packs.acquire_cards, name='player-acquire-cards'),
    path('players/<uuid:player_id>/cards/', views_card_packs.get_player_cards, name='player-cards'),
    path('players/<uuid:player_id>/cards/<uuid:player_card_id>/favorite/', views_card_packs.set_card_favorite, name='player-card-favorite'),
    path('players/<uuid:player_id>/cards/<uuid:player_card_id>/nickname/', views_card_packs.set_card_nickname, name='player-card-nickname'),
    
    # === SESSION CARDS ===
    path('sessions/<uuid:session_id>/join-with-cards/', views_card_packs.join_session_with_cards, name='session-join-with-cards'),
    path('sessions/<uuid:session_id>/cards/', views_card_packs.get_session_cards, name='session-cards'),
    path('sessions/<uuid:session_id>/players/<uuid:player_id>/cards/', views_card_packs.get_player_session_cards, name='session-player-cards'),
    path('mark-number/', views_card_packs.mark_number_on_card, name='mark-number'),
]

