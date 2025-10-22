#!/usr/bin/env python3
"""
Test de creación de sesión y obtención del ID
"""

import requests
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, APIKey

print("🧪 TEST: Creación de Sesión con Retorno de ID")
print("=" * 70)

BASE_URL = 'http://localhost:8000'

# Obtener o crear operador y API Key
operator, _ = Operator.objects.get_or_create(
    code='test_session',
    defaults={
        'name': 'Test Session',
        'allowed_bingo_types': ['75', '90']
    }
)

# Obtener API Key existente o crear una nueva
api_keys = APIKey.objects.filter(operator=operator, is_active=True)
if api_keys.exists():
    api_key_obj = api_keys.first()
    key = api_key_obj.key
    # Para test, usamos un secret conocido
    secret = 'test_secret_12345'
    # Actualizar el hash
    api_key_obj.secret_hash = APIKey.hash_secret(secret)
    api_key_obj.save()
else:
    key, secret = APIKey.generate_credentials()
    api_key_obj = APIKey.objects.create(
        operator=operator,
        name='Test Session Key',
        key=key,
        secret_hash=APIKey.hash_secret(secret),
        permission_level='write'
    )

print(f"✅ Operador: {operator.name} (ID: {operator.id})")
print(f"✅ API Key configurada")

# Obtener token JWT
print("\n1️⃣  Obtener Token JWT")
print("-" * 70)

response = requests.post(f'{BASE_URL}/api/token/', json={
    'api_key': key,
    'api_secret': secret
})

if response.status_code == 200:
    token = response.json()['access']
    print(f"✅ Token obtenido")
else:
    print(f"❌ Error obteniendo token: {response.json()}")
    sys.exit(1)

# Crear sesión
print("\n2️⃣  Crear Sesión de Bingo")
print("-" * 70)

session_data = {
    'operator': str(operator.id),
    'name': 'Test Session - Verificar ID',
    'description': 'Sesión de prueba para verificar retorno de ID',
    'bingo_type': '75',
    'max_players': 50,
    'entry_fee': 100,
    'total_cards': 100,
    'allow_card_reuse': True,
    'scheduled_start': '2024-10-22T20:00:00Z',
    'winning_patterns': ['horizontal_line', 'vertical_line', 'full_card']
}

response = requests.post(
    f'{BASE_URL}/api/multi-tenant/sessions/',
    headers={'Authorization': f'Bearer {token}'},
    json=session_data
)

print(f"Status: {response.status_code}")

if response.status_code == 201:
    result = response.json()
    
    print(f"\n✅ Sesión creada exitosamente")
    print("\n📋 Respuesta:")
    print(f"   Mensaje: {result.get('message')}")
    print(f"   🆔 Session ID: {result.get('session_id')}")
    
    if 'session' in result:
        session = result['session']
        print(f"\n📊 Detalles de la Sesión:")
        print(f"   ID: {session.get('id')}")
        print(f"   Nombre: {session.get('name')}")
        print(f"   Tipo: {session.get('bingo_type_display')}")
        print(f"   Estado: {session.get('status_display')}")
        print(f"   Total cartones: {session.get('total_cards')}")
        print(f"   Patrones: {', '.join(session.get('winning_patterns', []))}")
    
    # Verificar que el session_id existe
    if result.get('session_id'):
        print(f"\n✅ El campo 'session_id' está presente en la respuesta")
        print(f"   Valor: {result.get('session_id')}")
    else:
        print(f"\n❌ ERROR: El campo 'session_id' NO está en la respuesta")
    
    # Verificar que el ID también está en session
    if result.get('session', {}).get('id'):
        print(f"✅ El campo 'session.id' también está presente")
        
        # Verificar que ambos IDs coinciden
        if result.get('session_id') == result.get('session', {}).get('id'):
            print(f"✅ Los IDs coinciden correctamente")
        else:
            print(f"⚠️  Los IDs NO coinciden")
    
else:
    print(f"\n❌ Error creando sesión:")
    print(f"   {response.json()}")

print("\n" + "=" * 70)
print("✅ Test completado")

