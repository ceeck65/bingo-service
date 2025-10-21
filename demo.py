#!/usr/bin/env python3
"""
Demo del microservicio de bingo - Ejemplos de uso
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import BingoCard


def demo_90_ball_cards():
    """Demo de cartones de 90 bolas"""
    print("🎯 DEMO: Cartones de Bingo de 90 bolas (Estilo Europeo)")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n📋 Cartón {i+1}:")
        card = BingoCard.create_card(bingo_type='90', user_id=f'demo_user_{i+1}')
        
        print(f"ID: {card.id}")
        print(f"Usuario: {card.user_id}")
        print(f"Fecha: {card.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nNúmeros del cartón (3x9):")
        print("   1   2   3   4   5   6   7   8   9")
        print("   |   |   |   |   |   |   |   |")
        
        for row_idx, row in enumerate(card.numbers):
            display_row = []
            for num in row:
                if num is None:
                    display_row.append("   ")
                else:
                    display_row.append(f"{num:3d}")
            print(f"{row_idx+1}  {' '.join(display_row)}")
        
        # Validación
        validation = card.validate_card()
        status = "✅ VÁLIDO" if validation['is_valid'] else "❌ INVÁLIDO"
        print(f"\nEstado: {status}")
        
        if validation['errors']:
            print(f"Errores: {', '.join(validation['errors'])}")
        
        print("-" * 60)


def demo_85_ball_cards():
    """Demo de cartones de 85 bolas"""
    print("\n🎯 DEMO: Cartones de Bingo de 85 bolas (Estilo Americano)")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n📋 Cartón {i+1}:")
        card = BingoCard.create_card(bingo_type='85', user_id=f'demo_user_{i+1}')
        
        print(f"ID: {card.id}")
        print(f"Usuario: {card.user_id}")
        print(f"Fecha: {card.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nNúmeros del cartón (5x5):")
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
        
        print("-" * 60)


def demo_api_examples():
    """Demo de ejemplos de uso de la API"""
    print("\n🌐 DEMO: Ejemplos de uso de la API REST")
    print("=" * 60)
    
    print("\n📝 Ejemplo 1: Crear un cartón de 90 bolas")
    print("POST /api/bingo/cards/create/")
    print("Content-Type: application/json")
    print(json.dumps({
        "bingo_type": "90",
        "user_id": "usuario123"
    }, indent=2))
    
    print("\n📝 Ejemplo 2: Crear un cartón de 85 bolas")
    print("POST /api/bingo/cards/create/")
    print("Content-Type: application/json")
    print(json.dumps({
        "bingo_type": "85",
        "user_id": "usuario123"
    }, indent=2))
    
    print("\n📝 Ejemplo 3: Generar múltiples cartones")
    print("POST /api/bingo/cards/generate-multiple/")
    print("Content-Type: application/json")
    print(json.dumps({
        "bingo_type": "90",
        "count": 5,
        "user_id": "usuario123"
    }, indent=2))
    
    print("\n📝 Ejemplo 4: Obtener estadísticas")
    print("GET /api/bingo/statistics/")
    
    print("\n📝 Ejemplo 5: Listar cartones")
    print("GET /api/bingo/cards/?bingo_type=90&user_id=usuario123")


def demo_statistics():
    """Demo de estadísticas del sistema"""
    print("\n📊 DEMO: Estadísticas del Sistema")
    print("=" * 60)
    
    total_cards = BingoCard.objects.count()
    cards_85 = BingoCard.objects.filter(bingo_type='85').count()
    cards_90 = BingoCard.objects.filter(bingo_type='90').count()
    
    print(f"📈 Total de cartones generados: {total_cards}")
    print(f"🎯 Cartones de 85 bolas: {cards_85}")
    print(f"🎯 Cartones de 90 bolas: {cards_90}")
    
    if total_cards > 0:
        print(f"\n📅 Cartones generados hoy: {BingoCard.objects.filter(created_at__date=datetime.now().date()).count()}")
        
        # Mostrar algunos cartones recientes
        recent_cards = BingoCard.objects.order_by('-created_at')[:5]
        print(f"\n🕒 Últimos 5 cartones generados:")
        for card in recent_cards:
            print(f"  - {card.id} ({card.bingo_type} bolas) - {card.user_id} - {card.created_at.strftime('%H:%M:%S')}")


def main():
    print("🎲 MICROSERVICIO DE BINGO EN LÍNEA - DEMO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Limpiar cartones de demo anteriores
    BingoCard.objects.filter(user_id__startswith='demo_user_').delete()
    
    # Ejecutar demos
    demo_90_ball_cards()
    demo_85_ball_cards()
    demo_api_examples()
    demo_statistics()
    
    print("\n" + "=" * 60)
    print("✅ Demo completado exitosamente!")
    print("🚀 El microservicio está listo para usar")
    print("📚 Consulta el README.md para más información")
    print("=" * 60)


if __name__ == "__main__":
    main()
