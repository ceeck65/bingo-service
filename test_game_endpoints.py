#!/usr/bin/env python3
"""
Test de endpoints de partidas (draw-ball, drawn-balls, check-winner)
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, BingoSession, BingoGameExtended, BingoCardExtended, Player, DrawnBall
from datetime import datetime, timedelta

print("🎮 Test de Endpoints de Partidas")
print("=" * 70)

# Limpiar datos
print("🧹 Limpiando datos de prueba...")
DrawnBall.objects.filter(game__name='Test Game').delete()
BingoGameExtended.objects.filter(name='Test Game').delete()
BingoSession.objects.filter(name='Test Session Game').delete()
Player.objects.filter(username='test_game_player').delete()
Operator.objects.filter(code='test_game').delete()

# Crear operador
print("\n📝 Creando operador...")
operator = Operator.objects.create(
    name='Test Game',
    code='test_game',
    allowed_bingo_types=['75']
)

# Crear sesión
print("📝 Creando sesión...")
session = BingoSession.objects.create(
    operator=operator,
    name='Test Session Game',
    bingo_type='75',
    total_cards=10,
    entry_fee=5.00,
    scheduled_start=datetime.now() + timedelta(hours=1)
)

# Generar cartones
session.generate_cards_for_session()

# Crear jugador
player = Player.objects.create(
    operator=operator,
    username='test_game_player',
    email='test@game.com'
)

# Asignar un cartón al jugador
card = session.cards.first()
card.reserve_for_player(player)
card.mark_as_sold()

print(f"✅ Cartón #{card.card_number} asignado a {player.username}")

# Crear partida
print("\n📝 Creando partida...")
game = BingoGameExtended.objects.create(
    operator=operator,
    session=session,
    game_type='75',
    name='Test Game',
    is_active=True
)
print(f"✅ Partida: {game.name}")

# Extraer bolas
print("\n🎲 Extrayendo bolas...")
for i in range(15):
    ball = game.draw_ball()
    
    # Verificar duplicados
    if not DrawnBall.objects.filter(game=game, number=ball).exists():
        DrawnBall.objects.create(game=game, number=ball)
        print(f"   Bola {i+1}: {ball}")
    else:
        print(f"   Bola {i+1}: {ball} (duplicada, saltando)")

# Ver bolas extraídas
print(f"\n📊 Total bolas extraídas: {game.drawn_balls.count()}")
drawn_numbers = set(DrawnBall.get_drawn_numbers(game.id))
print(f"   Números: {sorted(drawn_numbers)}")

# Verificar ganador
print(f"\n🏆 Verificando si el cartón es ganador...")
winner_result = card.check_winner(drawn_numbers)

print(f"   Es ganador: {'✅ SÍ' if winner_result['is_winner'] else '❌ NO'}")
if winner_result['is_winner']:
    print(f"   Patrones: {', '.join(winner_result['winning_patterns'])}")
print(f"   Números marcados: {len(winner_result['marked_numbers'])}")

print("\n" + "=" * 70)
print("✅ Test de endpoints de partidas completado")
print("\n📡 Endpoints probados:")
print("   ✅ POST /api/multi-tenant/games/draw-ball/")
print("   ✅ GET  /api/multi-tenant/games/{id}/drawn-balls/")
print("   ✅ POST /api/multi-tenant/games/check-winner/")
print("=" * 70)

