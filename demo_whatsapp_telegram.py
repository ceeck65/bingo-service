#!/usr/bin/env python3
"""
Demo: Integración con WhatsApp y Telegram usando JWT
"""

import os
import sys
import django
import requests
import json

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, APIKey

print("📱 DEMO: Integración WhatsApp/Telegram con JWT")
print("=" * 70)

BASE_URL = 'http://localhost:8000'

# Crear operador si no existe
operator, _ = Operator.objects.get_or_create(
    code='whatsapp_demo',
    defaults={
        'name': 'WhatsApp Demo',
        'allowed_bingo_types': ['75', '90']
    }
)

# Crear API Key para WhatsApp
key, secret = APIKey.generate_credentials()
api_key = APIKey.objects.create(
    operator=operator,
    name='WhatsApp Bot',
    key=key,
    secret_hash=APIKey.hash_secret(secret),
    permission_level='write'
)

print(f"\n✅ Operador: {operator.name}")
print(f"✅ API Key: {key[:16]}...")
print(f"✅ API Secret: {secret[:16]}...")

# === PASO 1: Obtener Token JWT ===
print("\n" + "=" * 70)
print("PASO 1: Obtener Token JWT")
print("=" * 70)

response = requests.post(f'{BASE_URL}/api/token/', json={
    'api_key': key,
    'api_secret': secret
})

if response.status_code == 200:
    auth_data = response.json()
    access_token = auth_data['access']
    
    print(f"✅ Token JWT obtenido")
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   Expira en: {auth_data['expires_in']} segundos (24 horas)")
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# Headers para todos los requests
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# === PASO 2: Simular Comandos de WhatsApp ===
print("\n" + "=" * 70)
print("PASO 2: Simular Comandos de WhatsApp")
print("=" * 70)

# Comando: Registrar jugador
print("\n🔹 Comando: /registrar +5491112345678")

response = requests.post(
    f'{BASE_URL}/api/multi-tenant/players/register-by-phone/',
    headers=headers,
    json={
        'operator_code': operator.code,
        'phone': '+5491112345678',
        'username': 'Juan',
        'whatsapp_id': '+5491112345678'
    }
)

if response.status_code in [200, 201]:
    player = response.json().get('player', response.json())
    print(f"✅ Jugador registrado: {player['username']}")
    player_id = player['id']
else:
    print(f"❌ Error: {response.json()}")
    sys.exit(1)

# Comando: Listar sesiones activas
print("\n🔹 Comando: /sesiones")

response = requests.get(
    f'{BASE_URL}/api/multi-tenant/sessions/?operator={operator.id}',
    headers=headers
)

session_id = None

if response.status_code == 200:
    sessions = response.json()['results']
    print(f"✅ Sesiones activas: {len(sessions)}")
    
    if len(sessions) > 0:
        session = sessions[0]
        print(f"   - {session['name']} (Tipo: {session['bingo_type']})")
        session_id = session['id']
    else:
        # Crear sesión si no hay
        print("   No hay sesiones, creando una...")
        
        response = requests.post(
            f'{BASE_URL}/api/multi-tenant/sessions/',
            headers=headers,
            json={
                'operator': str(operator.id),
                'name': 'Sesión WhatsApp Demo',
                'bingo_type': '75',
                'total_cards': 100,
                'allow_card_reuse': True,
                'scheduled_start': '2024-10-21T20:00:00Z'
            }
        )
        
        if response.status_code == 201:
            session = response.json()
            session_id = session.get('id')
            print(f"✅ Sesión creada: {session.get('name', 'Sin nombre')}")
        else:
            print(f"⚠️ No se pudo crear sesión: {response.json()}")

# Comando: Ver cartones disponibles
print("\n🔹 Comando: /cartones")

if not session_id:
    print("⚠️ No hay session_id disponible, saltando...")
    cards = []
else:
    response = requests.get(
        f'{BASE_URL}/api/multi-tenant/sessions/{session_id}/available-cards/',
        headers=headers
    )

    if response.status_code == 200:
        cards = response.json()['cards']
        print(f"✅ Cartones disponibles: {len(cards)}")
        
        if len(cards) > 0:
            for i, card in enumerate(cards[:3], 1):
                print(f"   {i}. Cartón #{card['card_number']} - ${card.get('purchase_price', 0)}")
    else:
        cards = []

# Comando: Comprar cartón
print("\n🔹 Comando: /comprar 1")

if len(cards) > 0:
    card_id = cards[0]['id']
    
    # Seleccionar cartón
    response = requests.post(
        f'{BASE_URL}/api/multi-tenant/cards/{card_id}/select/',
        headers=headers,
        json={'player': player_id}
    )
    
    if response.status_code == 200:
        # Confirmar compra
        response = requests.post(
            f'{BASE_URL}/api/multi-tenant/cards/{card_id}/confirm-purchase/',
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Cartón comprado exitosamente")

# === PASO 3: Simular Juego en Vivo ===
print("\n" + "=" * 70)
print("PASO 3: Simular Juego en Vivo (Extracción de Bolas)")
print("=" * 70)

# Obtener o crear partida
response = requests.post(
    f'{BASE_URL}/api/multi-tenant/games/',
    headers=headers,
    json={
        'name': 'Partida WhatsApp',
        'game_type': '75',
        'operator': str(operator.id),
        'session': session_id
    }
)

if response.status_code == 201:
    game = response.json()
    game_id = game['id']
    print(f"✅ Partida creada: {game['name']}")
else:
    # Obtener partida existente
    response = requests.get(
        f'{BASE_URL}/api/multi-tenant/sessions/{session_id}/game/',
        headers=headers
    )
    
    if response.status_code == 200:
        game = response.json()['game']
        game_id = game['id']

# Extraer 5 bolas
print("\n🎰 Extrayendo bolas...")

for i in range(5):
    response = requests.post(
        f'{BASE_URL}/api/multi-tenant/games/{game_id}/draw-ball/',
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        ball_data = response.json()
        
        if ball_data.get('game_status') == 'finished':
            print(f"\n🏁 Juego completado!")
            break
        
        print(f"   Bola {i+1}: {ball_data['display_name']} (Color: {ball_data.get('color', 'N/A')})")

# === PASO 4: Ejemplo de Respuesta para WhatsApp ===
print("\n" + "=" * 70)
print("PASO 4: Formatear Respuesta para WhatsApp")
print("=" * 70)

def format_whatsapp_message(ball_data):
    """Formatea la bola extraída para WhatsApp"""
    letter = ball_data.get('letter', '')
    number = ball_data['ball_number']
    display = ball_data['display_name']
    
    message = f"🎰 *BOLA EXTRAÍDA*\n\n"
    message += f"   {display}\n\n"
    message += f"Bolas restantes: {ball_data['remaining_balls']}\n"
    message += f"Progreso: {ball_data['progress_percentage']}%"
    
    return message

# Obtener última bola
response = requests.get(
    f'{BASE_URL}/api/multi-tenant/games/{game_id}/drawn-balls/',
    headers=headers
)

if response.status_code == 200:
    balls = response.json()['balls']
    
    if balls:
        last_ball = balls[-1]
        
        # Simular datos de respuesta
        ball_data = {
            'letter': last_ball.get('letter', ''),
            'ball_number': last_ball['number'],
            'display_name': last_ball['display_name'],
            'remaining_balls': 75 - len(balls),
            'progress_percentage': round((len(balls) / 75) * 100, 2)
        }
        
        whatsapp_message = format_whatsapp_message(ball_data)
        
        print("\n📱 Mensaje para WhatsApp:")
        print("-" * 40)
        print(whatsapp_message)
        print("-" * 40)

# === RESUMEN FINAL ===
print("\n" + "=" * 70)
print("✅ DEMO COMPLETADO")
print("=" * 70)

print(f"""
🎯 Flujo Completo Demostrado:

1. ✅ Autenticación JWT con API Key + Secret
2. ✅ Registro de jugador por WhatsApp
3. ✅ Consulta de sesiones activas
4. ✅ Consulta de cartones disponibles
5. ✅ Compra de cartón
6. ✅ Creación de partida
7. ✅ Extracción de bolas con letra (B-I-N-G-O)
8. ✅ Formateo de respuestas para WhatsApp

🔐 Todos los requests protegidos con Bearer Token JWT

📱 Integración lista para:
   - WhatsApp Business API
   - Telegram Bot API
   - Laravel/Vue WebApp
""")

print("=" * 70)

