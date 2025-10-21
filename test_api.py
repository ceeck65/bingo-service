#!/usr/bin/env python3
"""
Script para probar la API REST del microservicio de bingo
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/bingo"

def test_create_90_ball_card():
    """Prueba crear un cartón de 90 bolas"""
    print("=== Creando cartón de 90 bolas ===")
    
    data = {
        "bingo_type": "90",
        "user_id": "test_user_api"
    }
    
    response = requests.post(f"{BASE_URL}/cards/create/", json=data)
    
    if response.status_code == 201:
        card_data = response.json()
        print(f"✅ Cartón creado exitosamente")
        print(f"ID: {card_data['id']}")
        print(f"Tipo: {card_data['bingo_type']}")
        print(f"Válido: {card_data['validation_result']['is_valid']}")
        return card_data['id']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_create_85_ball_card():
    """Prueba crear un cartón de 85 bolas"""
    print("\n=== Creando cartón de 85 bolas ===")
    
    data = {
        "bingo_type": "85",
        "user_id": "test_user_api"
    }
    
    response = requests.post(f"{BASE_URL}/cards/create/", json=data)
    
    if response.status_code == 201:
        card_data = response.json()
        print(f"✅ Cartón creado exitosamente")
        print(f"ID: {card_data['id']}")
        print(f"Tipo: {card_data['bingo_type']}")
        print(f"Válido: {card_data['validation_result']['is_valid']}")
        return card_data['id']
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def test_generate_multiple_cards():
    """Prueba generar múltiples cartones"""
    print("\n=== Generando 3 cartones de 90 bolas ===")
    
    data = {
        "bingo_type": "90",
        "count": 3,
        "user_id": "test_user_api"
    }
    
    response = requests.post(f"{BASE_URL}/cards/generate-multiple/", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ {result['count']} cartones generados")
        print(f"Tipo: {result['bingo_type']}")
        return [card['id'] for card in result['cards']]
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return []

def test_get_card(card_id):
    """Prueba obtener un cartón específico"""
    print(f"\n=== Obteniendo cartón {card_id} ===")
    
    response = requests.get(f"{BASE_URL}/cards/{card_id}/")
    
    if response.status_code == 200:
        card_data = response.json()
        print(f"✅ Cartón obtenido")
        print(f"ID: {card_data['id']}")
        print(f"Tipo: {card_data['bingo_type']}")
        print(f"Usuario: {card_data['user_id']}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_validate_card(card_id):
    """Prueba validar un cartón"""
    print(f"\n=== Validando cartón {card_id} ===")
    
    data = {"card_id": card_id}
    
    response = requests.post(f"{BASE_URL}/cards/validate/", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Validación completada")
        print(f"Válido: {result['validation_result']['is_valid']}")
        if result['validation_result']['errors']:
            print(f"Errores: {result['validation_result']['errors']}")
        if result['validation_result']['warnings']:
            print(f"Advertencias: {result['validation_result']['warnings']}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_list_cards():
    """Prueba listar cartones"""
    print("\n=== Listando cartones ===")
    
    response = requests.get(f"{BASE_URL}/cards/")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {len(result['results'])} cartones encontrados")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_statistics():
    """Prueba obtener estadísticas"""
    print("\n=== Obteniendo estadísticas ===")
    
    response = requests.get(f"{BASE_URL}/statistics/")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Estadísticas obtenidas")
        print(f"Total de cartones: {stats['total_cards']}")
        print(f"Cartones de 85 bolas: {stats['cards_85_balls']}")
        print(f"Cartones de 90 bolas: {stats['cards_90_balls']}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def main():
    print("Iniciando pruebas de la API REST...")
    print("Asegúrate de que el servidor Django esté ejecutándose en http://localhost:8000")
    print("-" * 60)
    
    # Crear cartones individuales
    card_90_id = test_create_90_ball_card()
    card_85_id = test_create_85_ball_card()
    
    # Generar múltiples cartones
    multiple_cards = test_generate_multiple_cards()
    
    # Obtener cartones específicos
    if card_90_id:
        test_get_card(card_90_id)
        test_validate_card(card_90_id)
    
    if card_85_id:
        test_get_card(card_85_id)
        test_validate_card(card_85_id)
    
    # Listar cartones
    test_list_cards()
    
    # Estadísticas
    test_statistics()
    
    print("\n" + "=" * 60)
    print("Pruebas de API completadas!")

if __name__ == "__main__":
    main()
