from django.urls import path
from . import views

urlpatterns = [
    # === CARTONES ===
    # Listar cartones
    path('cards/', views.BingoCardListView.as_view(), name='bingo-card-list'),
    
    # Obtener cartón específico
    path('cards/<uuid:id>/', views.BingoCardDetailView.as_view(), name='bingo-card-detail'),
    
    # Crear nuevo cartón
    path('cards/create/', views.BingoCardCreateView.as_view(), name='bingo-card-create'),
    
    # Validar cartón
    path('cards/validate/', views.BingoCardValidationView.as_view(), name='bingo-card-validate'),
    
    # Verificar si cartón es ganador
    path('cards/check-winner/', views.BingoCardWinnerView.as_view(), name='bingo-card-winner'),
    
    # Generar múltiples cartones
    path('cards/generate-multiple/', views.generate_multiple_cards, name='bingo-card-generate-multiple'),
    
    # Generar cartón para partida específica
    path('cards/generate-for-game/', views.generate_card_with_game, name='bingo-card-generate-for-game'),
    
    # === PARTIDAS ===
    # Listar y crear partidas
    path('games/', views.BingoGameListView.as_view(), name='bingo-game-list'),
    
    # Obtener, actualizar o eliminar partida específica
    path('games/<uuid:id>/', views.BingoGameDetailView.as_view(), name='bingo-game-detail'),
    
    # Extraer bola en partida
    path('games/draw-ball/', views.DrawBallView.as_view(), name='bingo-draw-ball'),
    
    # Listar bolas extraídas de una partida
    path('games/<uuid:game_id>/drawn-balls/', views.DrawnBallsListView.as_view(), name='bingo-drawn-balls'),
    
    # Verificar ganador usando partida
    path('games/check-winner/', views.check_winner_with_game, name='bingo-check-winner-with-game'),
    
    # === ESTADÍSTICAS ===
    path('statistics/', views.card_statistics, name='bingo-statistics'),
]
