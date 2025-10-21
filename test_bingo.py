#!/usr/bin/env python3
"""
Script de prueba para el microservicio de bingo
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import BingoCard


def test_90_ball_card():
    """Prueba la generación de cartones de 90 bolas"""
    print("=== Probando cartones de 90 bolas ===")
    
    for i in range(3):
        card = BingoCard.create_card(bingo_type='90', user_id=f'test_user_{i}')
        print(f"\nCartón {i+1} (ID: {card.id}):")
        print("Números:")
        for row_idx, row in enumerate(card.numbers):
            print(f"Fila {row_idx + 1}: {row}")
        
        # Validar el cartón
        validation = card.validate_card()
        print(f"Válido: {validation['is_valid']}")
        if validation['errors']:
            print(f"Errores: {validation['errors']}")
        if validation['warnings']:
            print(f"Advertencias: {validation['warnings']}")


def test_85_ball_card():
    """Prueba la generación de cartones de 85 bolas"""
    print("\n=== Probando cartones de 85 bolas ===")
    
    for i in range(3):
        card = BingoCard.create_card(bingo_type='85', user_id=f'test_user_{i}')
        print(f"\nCartón {i+1} (ID: {card.id}):")
        print("Números:")
        for row_idx, row in enumerate(card.numbers):
            print(f"Fila {row_idx + 1}: {row}")
        
        # Validar el cartón
        validation = card.validate_card()
        print(f"Válido: {validation['is_valid']}")
        if validation['errors']:
            print(f"Errores: {validation['errors']}")
        if validation['warnings']:
            print(f"Advertencias: {validation['warnings']}")


def test_statistics():
    """Muestra estadísticas de los cartones generados"""
    print("\n=== Estadísticas ===")
    total = BingoCard.objects.count()
    cards_85 = BingoCard.objects.filter(bingo_type='85').count()
    cards_90 = BingoCard.objects.filter(bingo_type='90').count()
    
    print(f"Total de cartones: {total}")
    print(f"Cartones de 85 bolas: {cards_85}")
    print(f"Cartones de 90 bolas: {cards_90}")


if __name__ == "__main__":
    print("Iniciando pruebas del microservicio de bingo...")
    
    # Limpiar cartones anteriores de prueba
    BingoCard.objects.filter(user_id__startswith='test_user_').delete()
    
    # Ejecutar pruebas
    test_90_ball_card()
    test_85_ball_card()
    test_statistics()
    
    print("\nPruebas completadas!")
