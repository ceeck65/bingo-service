#!/usr/bin/env python3
"""
Demo: Bolas extraídas con letras (B-I-N-G-O) para visualización
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, BingoSession, BingoGameExtended, DrawnBall
from datetime import datetime, timedelta

print("🎨 DEMO: Bolas con Letras (B-I-N-G-O)")
print("=" * 70)

# Limpiar datos
print("🧹 Limpiando datos de prueba...")
DrawnBall.objects.filter(game__name='Demo Letras').delete()
BingoGameExtended.objects.filter(name='Demo Letras').delete()
BingoSession.objects.filter(name='Demo Letras Session').delete()
Operator.objects.filter(code='demo_letras').delete()

# Crear operador, sesión y partida
operator = Operator.objects.create(
    name='Demo Letras',
    code='demo_letras',
    allowed_bingo_types=['75']
)

session = BingoSession.objects.create(
    operator=operator,
    name='Demo Letras Session',
    bingo_type='75',
    total_cards=10,
    entry_fee=5.00,
    scheduled_start=datetime.now() + timedelta(hours=1)
)

game = BingoGameExtended.objects.create(
    operator=operator,
    session=session,
    game_type='75',
    name='Demo Letras',
    is_active=True
)

print(f"✅ Partida creada: {game.name} ({game.game_type} bolas)")

# Extraer algunas bolas específicas de cada letra
print("\n🎲 Extrayendo bolas de cada letra (B-I-N-G-O)...")
print("-" * 70)

# Bolas específicas de cada categoría
sample_balls = [
    7,   # B
    26,  # I
    41,  # N
    53,  # G
    66,  # O
    12,  # B
    18,  # I
    35,  # N
    60,  # G
    75,  # O
]

for ball_num in sample_balls:
    ball = DrawnBall.objects.create(
        game=game,
        number=ball_num
    )
    
    # Obtener información de visualización
    letter = ball.get_letter()
    display = ball.get_display_name()
    color = ball.get_color()
    
    # Mostrar con color (usando códigos ANSI)
    print(f"   Bola: {display:8} | Número: {ball_num:2d} | Letra: {letter} | Color: {color}")

# Mostrar resumen por letra
print("\n📊 Resumen por letra:")
print("-" * 70)

letters = ['B', 'I', 'N', 'G', 'O']
drawn_balls = DrawnBall.objects.filter(game=game)

for letter in letters:
    balls = [b for b in drawn_balls if b.get_letter() == letter]
    numbers = [b.number for b in balls]
    
    if balls:
        color = balls[0].get_color()
        print(f"   {letter}: {numbers} | Color: {color}")

# Ejemplo de respuesta JSON
print("\n📡 Ejemplo de respuesta JSON del endpoint:")
print("-" * 70)

import json

response_example = {
    "message": "Bola I-26 extraída",
    "ball_number": 26,
    "letter": "I",
    "display_name": "I-26",
    "color": "#FF6B35",
    "total_drawn": 10,
    "remaining_balls": 65,
    "game_status": "active",
    "progress_percentage": 13.33
}

print(json.dumps(response_example, indent=2))

# Ejemplo de todas las bolas extraídas
print("\n📋 Todas las bolas extraídas con formato visual:")
print("-" * 70)

all_balls = DrawnBall.objects.filter(game=game).order_by('drawn_at')
print(f"\nTotal extraídas: {all_balls.count()}")
print("\nFormato para display:")

for ball in all_balls:
    print(f"   {ball.get_display_name()}", end="  ")

print("\n\n" + "=" * 70)
print("✅ Demo completado")
print("\n🎯 Información disponible para cada bola:")
print("   ✅ Número (ej: 26)")
print("   ✅ Letra (ej: I)")
print("   ✅ Nombre completo (ej: I-26)")
print("   ✅ Color CSS (ej: #FF6B35)")
print("\n💡 Uso en HTML/Canvas:")
print("   • Display: Mostrar 'I-26' en lugar de solo '26'")
print("   • Color: Usar el color CSS para el fondo")
print("   • Separación: Agrupar por letra en la vista")
print("=" * 70)

