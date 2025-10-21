#!/usr/bin/env python3
"""
Demo del sistema de validación de ganadores y partidas de bingo
"""

import os
import sys
import django
import random
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import BingoCard, BingoGame, DrawnBall


def demo_winner_validation():
    """Demo de validación de ganadores"""
    print("🏆 DEMO: Validación de Ganadores")
    print("=" * 60)
    
    # Crear cartones de prueba
    print("\n📋 Creando cartones de prueba...")
    
    # Cartón de 90 bolas
    card_90 = BingoCard.create_card(bingo_type='90', user_id='demo_winner_90')
    print(f"✅ Cartón de 90 bolas creado: {card_90.id}")
    
    # Cartón de 85 bolas
    card_85 = BingoCard.create_card(bingo_type='85', user_id='demo_winner_85')
    print(f"✅ Cartón de 85 bolas creado: {card_85.id}")
    
    # Simular números extraídos
    print("\n🎲 Simulando números extraídos...")
    
    # Para cartón de 90 bolas - simular una línea horizontal
    drawn_90 = set()
    for num in card_90.numbers[0]:  # Primera fila
        if num is not None:
            drawn_90.add(num)
    
    # Agregar algunos números más para hacer más realista
    for _ in range(10):
        drawn_90.add(random.randint(1, 90))
    
    # Para cartón de 85 bolas - simular una línea horizontal
    drawn_85 = set()
    for num in card_85.numbers[0]:  # Primera fila
        if num is not None and num != "FREE":
            drawn_85.add(num)
    
    # Agregar algunos números más
    for _ in range(15):
        drawn_85.add(random.randint(1, 85))
    
    # Verificar ganadores
    print("\n🔍 Verificando ganadores...")
    
    # Cartón de 90 bolas
    winner_90 = card_90.check_winner(drawn_90)
    print(f"\n📊 Cartón de 90 bolas:")
    print(f"   Es ganador: {'✅ SÍ' if winner_90['is_winner'] else '❌ NO'}")
    if winner_90['is_winner']:
        print(f"   Patrones ganadores: {', '.join(winner_90['winning_patterns'])}")
    print(f"   Números marcados: {len(winner_90['marked_numbers'])}")
    print(f"   Números no marcados: {len(winner_90['unmarked_numbers'])}")
    
    # Cartón de 85 bolas
    winner_85 = card_85.check_winner(drawn_85)
    print(f"\n📊 Cartón de 85 bolas:")
    print(f"   Es ganador: {'✅ SÍ' if winner_85['is_winner'] else '❌ NO'}")
    if winner_85['is_winner']:
        print(f"   Patrones ganadores: {', '.join(winner_85['winning_patterns'])}")
    print(f"   Números marcados: {len(winner_85['marked_numbers'])}")
    print(f"   Números no marcados: {len(winner_85['unmarked_numbers'])}")


def demo_game_simulation():
    """Demo de simulación de partida completa"""
    print("\n🎮 DEMO: Simulación de Partida Completa")
    print("=" * 60)
    
    # Crear una partida de bingo de 85 bolas
    game = BingoGame.objects.create(
        game_type='85',
        name='Demo Partida 85 Bolas'
    )
    print(f"🎯 Partida creada: {game.id}")
    print(f"   Tipo: {game.game_type} bolas")
    print(f"   Nombre: {game.name}")
    
    # Crear algunos cartones para la partida
    cards = []
    for i in range(3):
        card = BingoCard.create_card(bingo_type='85', user_id=f'jugador_{i+1}')
        cards.append(card)
        print(f"   📋 Cartón {i+1}: {card.id}")
    
    # Simular extracción de bolas
    print(f"\n🎲 Iniciando extracción de bolas...")
    
    drawn_balls = []
    for i in range(20):  # Extraer 20 bolas
        ball_number = game.draw_ball()
        
        # Verificar que no se haya extraído antes
        if not DrawnBall.objects.filter(game=game, number=ball_number).exists():
            drawn_ball = DrawnBall.objects.create(game=game, number=ball_number)
            drawn_balls.append(ball_number)
            print(f"   Bola {i+1}: {ball_number}")
        else:
            print(f"   Bola {i+1}: {ball_number} (ya extraída, saltando)")
    
    print(f"\n📊 Bolas extraídas: {len(drawn_balls)}")
    
    # Verificar ganadores
    print(f"\n🏆 Verificando ganadores...")
    drawn_numbers_set = set(drawn_balls)
    
    winners_found = False
    for i, card in enumerate(cards):
        winner_result = card.check_winner(drawn_numbers_set)
        if winner_result['is_winner']:
            winners_found = True
            print(f"   🎉 ¡GANADOR! Cartón {i+1} ({card.id})")
            print(f"      Patrones: {', '.join(winner_result['winning_patterns'])}")
            print(f"      Números marcados: {len(winner_result['marked_numbers'])}")
        else:
            print(f"   📋 Cartón {i+1}: No es ganador ({len(winner_result['marked_numbers'])} números marcados)")
    
    if not winners_found:
        print("   ⏳ No hay ganadores aún. Continuar extrayendo bolas...")
    
    # Mostrar estadísticas de la partida
    print(f"\n📈 Estadísticas de la partida:")
    print(f"   Partida ID: {game.id}")
    print(f"   Bolas extraídas: {game.drawn_balls.count()}")
    print(f"   Cartones en juego: {len(cards)}")


def demo_api_examples():
    """Demo de ejemplos de API para las nuevas funcionalidades"""
    print("\n🌐 DEMO: Ejemplos de API para Ganadores y Partidas")
    print("=" * 60)
    
    print("\n📝 Ejemplo 1: Crear una partida")
    print("POST /api/bingo/games/")
    print("Content-Type: application/json")
    print('''{
  "game_type": "85",
  "name": "Partida de Prueba"
}''')
    
    print("\n📝 Ejemplo 2: Extraer una bola")
    print("POST /api/bingo/games/draw-ball/")
    print("Content-Type: application/json")
    print('''{
  "game_id": "uuid-de-la-partida"
}''')
    
    print("\n📝 Ejemplo 3: Verificar ganador con números específicos")
    print("POST /api/bingo/cards/check-winner/")
    print("Content-Type: application/json")
    print('''{
  "card_id": "uuid-del-carton",
  "drawn_numbers": [1, 15, 22, 35, 41, 52, 67, 78]
}''')
    
    print("\n📝 Ejemplo 4: Verificar ganador usando partida")
    print("POST /api/bingo/games/check-winner/")
    print("Content-Type: application/json")
    print('''{
  "card_id": "uuid-del-carton",
  "game_id": "uuid-de-la-partida"
}''')
    
    print("\n📝 Ejemplo 5: Generar cartón para partida específica")
    print("POST /api/bingo/cards/generate-for-game/")
    print("Content-Type: application/json")
    print('''{
  "game_id": "uuid-de-la-partida",
  "user_id": "jugador123"
}''')
    
    print("\n📝 Ejemplo 6: Listar bolas extraídas de una partida")
    print("GET /api/bingo/games/{game_id}/drawn-balls/")


def main():
    print("🎲 MICROSERVICIO DE BINGO - DEMO DE GANADORES Y PARTIDAS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Limpiar datos de demo anteriores
    BingoCard.objects.filter(user_id__startswith='demo_winner_').delete()
    BingoCard.objects.filter(user_id__startswith='jugador_').delete()
    BingoGame.objects.filter(name__startswith='Demo').delete()
    
    # Ejecutar demos
    demo_winner_validation()
    demo_game_simulation()
    demo_api_examples()
    
    print("\n" + "=" * 70)
    print("✅ Demo de ganadores y partidas completado!")
    print("🚀 El sistema está listo para partidas completas de bingo")
    print("📚 Consulta el README.md para más información sobre la API")
    print("=" * 70)


if __name__ == "__main__":
    main()
