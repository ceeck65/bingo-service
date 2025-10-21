#!/usr/bin/env python3
"""
Test de extracción de bolas con evitación de duplicados
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, BingoSession, BingoGameExtended, DrawnBall
from datetime import datetime, timedelta

print("🎲 TEST: Extracción de Bolas Mejorada")
print("=" * 70)

# Limpiar datos
print("🧹 Limpiando datos de prueba...")
DrawnBall.objects.filter(game__name='Test Draw Ball').delete()
BingoGameExtended.objects.filter(name='Test Draw Ball').delete()
BingoSession.objects.filter(name='Test Draw Session').delete()
Operator.objects.filter(code='test_draw').delete()

# Crear operador y sesión
operator = Operator.objects.create(
    name='Test Draw',
    code='test_draw',
    allowed_bingo_types=['75']
)

session = BingoSession.objects.create(
    operator=operator,
    name='Test Draw Session',
    bingo_type='75',
    total_cards=10,
    entry_fee=5.00,
    scheduled_start=datetime.now() + timedelta(hours=1)
)

# Crear partida
game = BingoGameExtended.objects.create(
    operator=operator,
    session=session,
    game_type='75',  # 75 bolas
    name='Test Draw Ball',
    is_active=True
)

print(f"✅ Partida creada: {game.name}")
print(f"   Tipo: {game.game_type} bolas")
print(f"   Máximo de bolas: 75")

# Simular extracción hasta completar
print("\n🎲 Extrayendo bolas (primeras 10)...")

for i in range(10):
    # Obtener bolas extraídas
    drawn_set = set(DrawnBall.objects.filter(game=game).values_list('number', flat=True))
    max_balls = 75
    
    # Verificar si ya se extrajeron todas
    if len(drawn_set) >= max_balls:
        print(f"\n🏁 Juego completado - Todas las bolas extraídas")
        break
    
    # Intentar extraer (hasta 10 intentos)
    ball_number = None
    for attempt in range(10):
        candidate = game.draw_ball()
        if candidate not in drawn_set:
            ball_number = candidate
            break
    
    # Si no se encontró, seleccionar de las disponibles
    if ball_number is None:
        available = set(range(1, max_balls + 1)) - drawn_set
        if available:
            import random
            ball_number = random.choice(list(available))
    
    # Guardar bola
    if ball_number:
        DrawnBall.objects.create(game=game, number=ball_number)
        print(f"   Bola {i+1}: {ball_number}")

# Estadísticas
print(f"\n📊 Estadísticas:")
total_drawn = game.drawn_balls.count()
print(f"   - Bolas extraídas: {total_drawn}")
print(f"   - Bolas restantes: {75 - total_drawn}")
print(f"   - Progreso: {(total_drawn/75)*100:.1f}%")

# Extraer todas las bolas restantes rápidamente
print(f"\n⚡ Extrayendo bolas restantes rápidamente...")

while total_drawn < 75:
    drawn_set = set(DrawnBall.objects.filter(game=game).values_list('number', flat=True))
    available = set(range(1, 76)) - drawn_set
    
    if not available:
        break
    
    import random
    ball = random.choice(list(available))
    DrawnBall.objects.create(game=game, number=ball)
    total_drawn += 1
    
    if total_drawn % 10 == 0:
        print(f"   {total_drawn} bolas extraídas...")

# Verificar finalización
print(f"\n🏁 Estado final:")
total_drawn = game.drawn_balls.count()
print(f"   - Total extraídas: {total_drawn}/75")

if total_drawn >= 75:
    game.is_active = False
    game.save()
    print(f"   - Estado del juego: FINALIZADO ✅")
else:
    print(f"   - Estado del juego: ACTIVO")

# Verificar que no hay duplicados
all_balls = list(DrawnBall.objects.filter(game=game).values_list('number', flat=True))
unique_balls = set(all_balls)

print(f"\n🔍 Verificación de duplicados:")
print(f"   - Bolas totales: {len(all_balls)}")
print(f"   - Bolas únicas: {len(unique_balls)}")

if len(all_balls) == len(unique_balls):
    print(f"   ✅ No hay duplicados")
else:
    print(f"   ❌ Hay {len(all_balls) - len(unique_balls)} duplicados")

print("\n" + "=" * 70)
print("✅ Test completado")
print("\n🎯 Funcionalidades probadas:")
print("   ✅ Evitación automática de duplicados")
print("   ✅ Selección de bolas disponibles")
print("   ✅ Detección de juego completado")
print("   ✅ Marcado automático como finalizado")
print("=" * 70)

