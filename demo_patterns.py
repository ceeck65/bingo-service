#!/usr/bin/env python3
"""
Demo del sistema de patrones de victoria
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import WinningPattern, BingoCard

print("🎯 DEMO: Sistema de Patrones de Victoria")
print("=" * 70)

# Generar un cartón de 75 bolas para pruebas
print("\n1️⃣  Generar Cartón de Prueba (75 bolas)")
print("-" * 70)

card = BingoCard.create_card('75', 'user_test')
print(f"✅ Cartón generado")
print("\nCartón:")
for row in card.numbers:
    print("  " + " ".join(f"{num:2}" if num != 0 else "  " for num in row))

# Obtener patrones
patterns = WinningPattern.objects.filter(compatible_with__in=['all', '75'], is_active=True)

print(f"\n2️⃣  Patrones Compatibles: {patterns.count()}")
print("-" * 70)

for pattern in patterns:
    print(f"\n🎲 {pattern.name}")
    print(f"   Código: {pattern.code}")
    print(f"   Categoría: {pattern.get_category_display()}")
    print(f"   Premio: x{pattern.prize_multiplier}")
    if pattern.has_jackpot:
        print(f"   🎰 Jackpot: Máx {pattern.jackpot_max_balls} bolas")

# Probar verificación de patrones
print("\n3️⃣  Verificar Patrones")
print("-" * 70)

# Simular línea horizontal (primera fila)
first_row_numbers = [num for num in card.numbers[0] if num != 0]
print(f"\nMarcar primera fila: {first_row_numbers}")

horizontal_pattern = WinningPattern.objects.get(code='horizontal_line')
result = horizontal_pattern.check_pattern(
    marked_numbers=first_row_numbers,
    card_numbers=card.numbers,
    bingo_type='75'
)

print(f"Resultado: {'🏆 GANADOR!' if result['is_winner'] else '❌ No ganador'}")
if result['is_winner']:
    print(f"Patrón: {result['pattern_name']}")
    print(f"Multiplicador: x{result['prize_multiplier']}")

# Probar línea vertical
print(f"\nMarcar primera columna:")
first_col_numbers = [card.numbers[row][0] for row in range(5) if card.numbers[row][0] != 0]
print(f"Números: {first_col_numbers}")

vertical_pattern = WinningPattern.objects.get(code='vertical_line')
result = vertical_pattern.check_pattern(
    marked_numbers=first_col_numbers,
    card_numbers=card.numbers,
    bingo_type='75'
)

print(f"Resultado: {'🏆 GANADOR!' if result['is_winner'] else '❌ No ganador'}")

# Probar cuatro esquinas
print(f"\nMarcar cuatro esquinas:")
corners = [
    card.numbers[0][0],   # Top-left
    card.numbers[0][4],   # Top-right
    card.numbers[4][0],   # Bottom-left
    card.numbers[4][4]    # Bottom-right
]
corners = [c for c in corners if c != 0]
print(f"Números: {corners}")

corners_pattern = WinningPattern.objects.get(code='four_corners')
result = corners_pattern.check_pattern(
    marked_numbers=corners,
    card_numbers=card.numbers,
    bingo_type='75'
)

print(f"Resultado: {'🏆 GANADOR!' if result['is_winner'] else '❌ No ganador'}")

# Probar cartón lleno
print(f"\nMarcar todos los números:")
all_numbers = []
for row in card.numbers:
    all_numbers.extend([num for num in row if num != 0])
print(f"Total números: {len(all_numbers)}")

full_card_pattern = WinningPattern.objects.get(code='full_card')
result = full_card_pattern.check_pattern(
    marked_numbers=all_numbers,
    card_numbers=card.numbers,
    bingo_type='75'
)

print(f"Resultado: {'🏆 GANADOR!' if result['is_winner'] else '❌ No ganador'}")
if result['is_winner']:
    print(f"Patrón: {result['pattern_name']}")
    print(f"Multiplicador: x{result['prize_multiplier']}")

# Probar jackpot
print(f"\n4️⃣  Verificar Jackpot (cartón lleno en 40 bolas)")
print("-" * 70)

jackpot_pattern = WinningPattern.objects.get(code='blackout_jackpot')
result_40 = jackpot_pattern.check_pattern(
    marked_numbers=all_numbers,
    card_numbers=card.numbers,
    bingo_type='75',
    balls_drawn=40
)

result_60 = jackpot_pattern.check_pattern(
    marked_numbers=all_numbers,
    card_numbers=card.numbers,
    bingo_type='75',
    balls_drawn=60
)

print(f"\nCon 40 bolas extraídas:")
print(f"  Ganador: {'🏆 SÍ' if result_40['is_winner'] else '❌ No'}")
print(f"  Jackpot: {'🎰 SÍ!' if result_40.get('is_jackpot') else '❌ No'}")
print(f"  Multiplicador: x{result_40['prize_multiplier']}")

print(f"\nCon 60 bolas extraídas:")
print(f"  Ganador: {'🏆 SÍ' if result_60['is_winner'] else '❌ No'}")
print(f"  Jackpot: {'🎰 SÍ!' if result_60.get('is_jackpot') else '❌ No'}")
print(f"  Multiplicador: x{result_60['prize_multiplier']}")

# Resumen
print("\n" + "=" * 70)
print("✅ Demo completado")
print("\n🎯 Sistema de Patrones Implementado:")
print("   ✅ 9 patrones predefinidos")
print("   ✅ Patrones clásicos (líneas, diagonal, cartón lleno)")
print("   ✅ Patrones especiales (esquinas, X, letras)")
print("   ✅ Sistema de jackpot progresivo")
print("   ✅ Multiplicadores de premio")
print("   ✅ Verificación automática de patrones")
print("=" * 70)

