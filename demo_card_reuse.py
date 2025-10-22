#!/usr/bin/env python3
"""
Demo del Sistema de Reutilización de Cartas
Demuestra el flujo completo: crear pack, generar cartas, jugador adquiere cartas, usa en sesión
"""

import requests
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, Player, APIKey

print("🎴 DEMO: Sistema de Reutilización de Cartas")
print("=" * 80)

BASE_URL = 'http://localhost:8000'

# === SETUP ===
print("\n📋 SETUP: Preparando operador y jugador")
print("-" * 80)

operator, _ = Operator.objects.get_or_create(
    code='demo_reuse',
    defaults={
        'name': 'Demo Reutilización',
        'allowed_bingo_types': ['75', '90']
    }
)

player, _ = Player.objects.get_or_create(
    operator=operator,
    username='jugador_demo',
    defaults={
        'email': 'demo@example.com',
        'is_active': True
    }
)

# API Key
api_keys = APIKey.objects.filter(operator=operator, is_active=True)
if api_keys.exists():
    api_key_obj = api_keys.first()
    key = api_key_obj.key
    secret = 'demo_secret_123'
    api_key_obj.secret_hash = APIKey.hash_secret(secret)
    api_key_obj.save()
else:
    key, secret = APIKey.generate_credentials()
    api_key_obj = APIKey.objects.create(
        operator=operator,
        name='Demo Key',
        key=key,
        secret_hash=APIKey.hash_secret(secret),
        permission_level='write'
    )

print(f"✅ Operador: {operator.name} (ID: {operator.id})")
print(f"✅ Jugador: {player.username} (ID: {player.id})")

# Obtener token
response = requests.post(f'{BASE_URL}/api/token/', json={
    'api_key': key,
    'api_secret': secret
})
token = response.json()['access']
headers = {'Authorization': f'Bearer {token}'}

print(f"✅ Token JWT obtenido")

# === PASO 1: CREAR CARD PACK ===
print("\n1️⃣  CREAR CARD PACK")
print("-" * 80)

pack_data = {
    'operator': str(operator.id),
    'name': 'Pack Demo 75 Bolas',
    'description': 'Pack de demostración para reutilización de cartas',
    'bingo_type': '75',
    'total_cards': 50,
    'price_per_card': 0,
    'category': 'free',
    'is_active': True,
    'is_public': True
}

response = requests.post(
    f'{BASE_URL}/api/card-packs/packs/',
    headers=headers,
    json=pack_data
)

if response.status_code == 201:
    pack = response.json()
    pack_id = pack['id']
    print(f"✅ Pack creado: {pack['name']}")
    print(f"   ID: {pack_id}")
    print(f"   Tipo: {pack['bingo_type_display']}")
    print(f"   Total cartas: {pack['total_cards']}")
    print(f"   Categoría: {pack['category_display']}")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 2: GENERAR CARTAS PARA EL PACK ===
print("\n2️⃣  GENERAR CARTAS PARA EL PACK")
print("-" * 80)

response = requests.post(
    f'{BASE_URL}/api/card-packs/packs/{pack_id}/generate-cards/',
    headers=headers,
    json={}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"   Cartas generadas: {result['pack']['cards_count']}")
    print(f"   Cartas disponibles: {result['pack']['available_cards_count']}")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 3: VER CARTAS DEL PACK ===
print("\n3️⃣  VER CARTAS DEL PACK (primeras 5)")
print("-" * 80)

response = requests.get(
    f'{BASE_URL}/api/card-packs/packs/{pack_id}/cards/?page_size=5',
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Total de cartas: {result['pagination']['total']}")
    print(f"\nPrimeras 5 cartas:")
    for card in result['cards'][:5]:
        print(f"   • Carta #{card['card_number']} - Serial: {card['serial_number']}")
        print(f"     Tipo: {card['bingo_type_display']}")
        print(f"     Reutilizable: {'Sí' if card['is_reusable'] else 'No'}")
else:
    print(f"❌ Error: {response.json()}")

# === PASO 4: JUGADOR ADQUIERE CARTAS ===
print("\n4️⃣  JUGADOR ADQUIERE CARTAS DEL PACK")
print("-" * 80)

acquire_data = {
    'pack_id': pack_id,
    'quantity': 3,
    'acquisition_type': 'gift'
}

response = requests.post(
    f'{BASE_URL}/api/card-packs/players/{player.id}/acquire-cards/',
    headers=headers,
    json=acquire_data
)

if response.status_code == 201:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"\nCartas adquiridas:")
    for card in result['cards']:
        print(f"   • {card['card_details']['serial_number']}")
        print(f"     Pack: {card['pack_name']}")
        print(f"     Tipo de adquisición: {card['acquisition_type_display']}")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 5: VER CARTAS DEL JUGADOR ===
print("\n5️⃣  VER COLECCIÓN DE CARTAS DEL JUGADOR")
print("-" * 80)

response = requests.get(
    f'{BASE_URL}/api/card-packs/players/{player.id}/cards/',
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Total de cartas: {result['total_cards']}")
    print(f"\nColección:")
    for card in result['cards']:
        print(f"   • Carta #{card['card_details']['card_number']}")
        print(f"     Serial: {card['card_details']['serial_number']}")
        print(f"     Veces usada: {card['times_used']}")
        print(f"     Veces ganada: {card['times_won']}")
        print(f"     Win rate: {card['win_rate']}%")
        print()
    
    # Guardar IDs de cartas para usar en sesión
    player_card_ids = [card['card_details']['id'] for card in result['cards']]
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 6: MARCAR UNA CARTA COMO FAVORITA ===
print("\n6️⃣  MARCAR CARTA COMO FAVORITA")
print("-" * 80)

first_player_card_id = result['cards'][0]['id']

response = requests.patch(
    f'{BASE_URL}/api/card-packs/players/{player.id}/cards/{first_player_card_id}/favorite/',
    headers=headers,
    json={'is_favorite': True}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"   Carta: {result['card']['card_details']['serial_number']}")
    print(f"   Es favorita: {'Sí' if result['card']['is_favorite'] else 'No'}")
else:
    print(f"❌ Error: {response.json()}")

# === PASO 7: PONER APODO A UNA CARTA ===
print("\n7️⃣  PONER APODO A UNA CARTA")
print("-" * 80)

response = requests.patch(
    f'{BASE_URL}/api/card-packs/players/{player.id}/cards/{first_player_card_id}/nickname/',
    headers=headers,
    json={'nickname': 'Mi carta de la suerte'}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"   Carta: {result['card']['card_details']['serial_number']}")
    print(f"   Apodo: '{result['card']['nickname']}'")
else:
    print(f"❌ Error: {response.json()}")

# === PASO 8: CREAR SESIÓN ===
print("\n8️⃣  CREAR SESIÓN DE BINGO")
print("-" * 80)

session_data = {
    'operator': str(operator.id),
    'name': 'Sesión Demo - Reutilización',
    'description': 'Sesión para demostrar reutilización de cartas',
    'bingo_type': '75',
    'max_players': 50,
    'entry_fee': 0,
    'card_source': 'player_cards',
    'scheduled_start': '2024-10-22T20:00:00Z',
    'winning_patterns': ['horizontal_line', 'vertical_line', 'full_card']
}

response = requests.post(
    f'{BASE_URL}/api/multi-tenant/sessions/',
    headers=headers,
    json=session_data
)

if response.status_code == 201:
    result = response.json()
    session_id = result['session_id']
    print(f"✅ Sesión creada: {result['session']['name']}")
    print(f"   ID: {session_id}")
    print(f"   Tipo: {result['session']['bingo_type_display']}")
    print(f"   Origen de cartas: {result['session']['card_source']}")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 9: JUGADOR SE UNE A SESIÓN CON SUS CARTAS ===
print("\n9️⃣  JUGADOR SE UNE A SESIÓN CON SUS CARTAS")
print("-" * 80)

join_data = {
    'player_id': str(player.id),
    'card_ids': player_card_ids
}

response = requests.post(
    f'{BASE_URL}/api/card-packs/sessions/{session_id}/join-with-cards/',
    headers=headers,
    json=join_data
)

if response.status_code == 201:
    result = response.json()
    print(f"✅ {result['message']}")
    print(f"\nCartas en la sesión:")
    for card in result['cards']:
        print(f"   • {card['card_details']['serial_number']}")
        print(f"     Estado: {card['status_display']}")
        print(f"     Números marcados: {card['marked_count']}")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# === PASO 10: VER CARTAS DEL JUGADOR EN LA SESIÓN ===
print("\n🔟 VER CARTAS DEL JUGADOR EN LA SESIÓN")
print("-" * 80)

response = requests.get(
    f'{BASE_URL}/api/card-packs/sessions/{session_id}/players/{player.id}/cards/',
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Sesión: {result['session']['name']}")
    print(f"   Jugador: {result['player']['username']}")
    print(f"   Total cartas: {len(result['cards'])}")
    print(f"\nCartas activas:")
    for card in result['cards']:
        print(f"   • {card['card_details']['serial_number']}")
        print(f"     Estado: {card['status_display']}")
else:
    print(f"❌ Error: {response.json()}")

# === RESUMEN ===
print("\n" + "=" * 80)
print("✅ DEMO COMPLETADO")
print("=" * 80)
print("\n📊 Resumen del flujo:")
print("   1. ✅ Creado pack de 50 cartas")
print("   2. ✅ Generadas cartas del pack")
print("   3. ✅ Jugador adquirió 3 cartas")
print("   4. ✅ Marcó una como favorita")
print("   5. ✅ Puso apodo a una carta")
print("   6. ✅ Creó sesión de bingo")
print("   7. ✅ Se unió con sus propias cartas")
print("   8. ✅ Cartas activas en la sesión")
print("\n🎯 Las cartas ahora pueden ser reutilizadas en múltiples sesiones!")
print("=" * 80)

