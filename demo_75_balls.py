#!/usr/bin/env python3
"""
Demo específico para el bingo de 75 bolas (formato americano clásico)
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


def demo_75_ball_cards():
    """Demo de cartones de 75 bolas"""
    print("🎯 DEMO: Cartones de Bingo de 75 bolas (Estilo Americano Clásico)")
    print("=" * 70)
    
    for i in range(3):
        print(f"\n📋 Cartón {i+1}:")
        card = BingoCard.create_card(bingo_type='75', user_id=f'demo_75_user_{i+1}')
        
        print(f"ID: {card.id}")
        print(f"Usuario: {card.user_id}")
        print(f"Fecha: {card.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nNúmeros del cartón (5x5 - BINGO):")
        print("   B    I    N    G    O")
        print("   |    |    |    |    |")
        
        for row_idx, row in enumerate(card.numbers):
            display_row = []
            for num in row:
                if num == "FREE":
                    display_row.append("FREE")
                else:
                    display_row.append(f"{num:4d}")
            print(f"{row_idx+1}  {' '.join(display_row)}")
        
        # Validación
        validation = card.validate_card()
        status = "✅ VÁLIDO" if validation['is_valid'] else "❌ INVÁLIDO"
        print(f"\nEstado: {status}")
        
        if validation['errors']:
            print(f"Errores: {', '.join(validation['errors'])}")
        if validation['warnings']:
            print(f"Advertencias: {', '.join(validation['warnings'])}")
        
        print("-" * 70)


def demo_75_ball_winner_validation():
    """Demo de validación de ganadores para 75 bolas"""
    print("\n🏆 DEMO: Validación de Ganadores - Bingo de 75 Bolas")
    print("=" * 70)
    
    # Crear cartón de prueba
    card = BingoCard.create_card(bingo_type='75', user_id='demo_winner_75')
    print(f"📋 Cartón creado: {card.id}")
    
    # Mostrar el cartón
    print("\nNúmeros del cartón:")
    print("   B    I    N    G    O")
    print("   |    |    |    |    |")
    
    for row_idx, row in enumerate(card.numbers):
        display_row = []
        for num in row:
            if num == "FREE":
                display_row.append("FREE")
            else:
                display_row.append(f"{num:4d}")
        print(f"{row_idx+1}  {' '.join(display_row)}")
    
    # Simular diferentes patrones ganadores
    print("\n🎲 Simulando patrones ganadores...")
    
    # 1. Línea horizontal (primera fila)
    drawn_numbers_horizontal = set()
    for num in card.numbers[0]:
        if num != "FREE" and num is not None:
            drawn_numbers_horizontal.add(num)
    
    # Agregar algunos números más para hacer más realista
    for _ in range(10):
        drawn_numbers_horizontal.add(random.randint(1, 75))
    
    winner_horizontal = card.check_winner(drawn_numbers_horizontal)
    print(f"\n📊 Prueba 1 - Línea horizontal:")
    print(f"   Es ganador: {'✅ SÍ' if winner_horizontal['is_winner'] else '❌ NO'}")
    if winner_horizontal['is_winner']:
        print(f"   Patrones: {', '.join(winner_horizontal['winning_patterns'])}")
    print(f"   Números marcados: {len(winner_horizontal['marked_numbers'])}")
    
    # 2. Columna vertical (B)
    drawn_numbers_vertical = set()
    for row in card.numbers:
        if row[0] != "FREE" and row[0] is not None:
            drawn_numbers_vertical.add(row[0])
    
    # Agregar algunos números más
    for _ in range(15):
        drawn_numbers_vertical.add(random.randint(1, 75))
    
    winner_vertical = card.check_winner(drawn_numbers_vertical)
    print(f"\n📊 Prueba 2 - Columna vertical (B):")
    print(f"   Es ganador: {'✅ SÍ' if winner_vertical['is_winner'] else '❌ NO'}")
    if winner_vertical['is_winner']:
        print(f"   Patrones: {', '.join(winner_vertical['winning_patterns'])}")
    print(f"   Números marcados: {len(winner_vertical['marked_numbers'])}")
    
    # 3. Diagonal principal
    drawn_numbers_diagonal = set()
    for i in range(5):
        if card.numbers[i][i] != "FREE" and card.numbers[i][i] is not None:
            drawn_numbers_diagonal.add(card.numbers[i][i])
    
    # Agregar algunos números más
    for _ in range(20):
        drawn_numbers_diagonal.add(random.randint(1, 75))
    
    winner_diagonal = card.check_winner(drawn_numbers_diagonal)
    print(f"\n📊 Prueba 3 - Diagonal principal:")
    print(f"   Es ganador: {'✅ SÍ' if winner_diagonal['is_winner'] else '❌ NO'}")
    if winner_diagonal['is_winner']:
        print(f"   Patrones: {', '.join(winner_diagonal['winning_patterns'])}")
    print(f"   Números marcados: {len(winner_diagonal['marked_numbers'])}")


def demo_75_ball_game_simulation():
    """Demo de simulación de partida de 75 bolas"""
    print("\n🎮 DEMO: Simulación de Partida de 75 Bolas")
    print("=" * 70)
    
    # Crear una partida de bingo de 75 bolas
    game = BingoGame.objects.create(
        game_type='75',
        name='Demo Partida 75 Bolas'
    )
    print(f"🎯 Partida creada: {game.id}")
    print(f"   Tipo: {game.game_type} bolas")
    print(f"   Nombre: {game.name}")
    
    # Crear algunos cartones para la partida
    cards = []
    for i in range(3):
        card = BingoCard.create_card(bingo_type='75', user_id=f'jugador_75_{i+1}')
        cards.append(card)
        print(f"   📋 Cartón {i+1}: {card.id}")
    
    # Simular extracción de bolas
    print(f"\n🎲 Iniciando extracción de bolas...")
    
    drawn_balls = []
    for i in range(30):  # Extraer 30 bolas
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


def demo_api_examples_75():
    """Demo de ejemplos de API para bingo de 75 bolas"""
    print("\n🌐 DEMO: Ejemplos de API para Bingo de 75 Bolas")
    print("=" * 70)
    
    print("\n📝 Ejemplo 1: Crear un cartón de 75 bolas")
    print("POST /api/bingo/cards/create/")
    print("Content-Type: application/json")
    print('''{
  "bingo_type": "75",
  "user_id": "usuario123"
}''')
    
    print("\n📝 Ejemplo 2: Crear una partida de 75 bolas")
    print("POST /api/bingo/games/")
    print("Content-Type: application/json")
    print('''{
  "game_type": "75",
  "name": "Partida de 75 Bolas"
}''')
    
    print("\n📝 Ejemplo 3: Generar múltiples cartones de 75 bolas")
    print("POST /api/bingo/cards/generate-multiple/")
    print("Content-Type: application/json")
    print('''{
  "bingo_type": "75",
  "count": 5,
  "user_id": "usuario123"
}''')
    
    print("\n📝 Ejemplo 4: Verificar ganador con números específicos")
    print("POST /api/bingo/cards/check-winner/")
    print("Content-Type: application/json")
    print('''{
  "card_id": "uuid-del-carton",
  "drawn_numbers": [1, 15, 22, 35, 41, 52, 67, 75]
}''')


def main():
    print("🎲 MICROSERVICIO DE BINGO - DEMO DE 75 BOLAS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Limpiar datos de demo anteriores
    BingoCard.objects.filter(user_id__startswith='demo_75_user_').delete()
    BingoCard.objects.filter(user_id__startswith='demo_winner_75').delete()
    BingoCard.objects.filter(user_id__startswith='jugador_75_').delete()
    BingoGame.objects.filter(name__startswith='Demo Partida 75').delete()
    
    # Ejecutar demos
    demo_75_ball_cards()
    demo_75_ball_winner_validation()
    demo_75_ball_game_simulation()
    demo_api_examples_75()
    
    print("\n" + "=" * 70)
    print("✅ Demo de bingo de 75 bolas completado!")
    print("🎯 El sistema ahora soporta 3 tipos de bingo:")
    print("   - 75 bolas (Americano clásico)")
    print("   - 85 bolas (Americano extendido)")
    print("   - 90 bolas (Europeo)")
    print("🚀 ¡El microservicio está completo!")
    print("=" * 70)


if __name__ == "__main__":
    main()
