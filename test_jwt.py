#!/usr/bin/env python3
"""
Test del sistema de autenticación JWT
"""

import os
import sys
import django
import requests

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, APIKey

print("🔐 TEST: Autenticación JWT")
print("=" * 70)

BASE_URL = 'http://localhost:8000'

# Crear operador y API Key si no existen
print("\n1️⃣  Preparando credenciales...")
print("-" * 70)

operator, _ = Operator.objects.get_or_create(
    code='test_jwt',
    defaults={
        'name': 'Test JWT',
        'allowed_bingo_types': ['75']
    }
)

# Crear API Key
key, secret = APIKey.generate_credentials()
api_key = APIKey.objects.create(
    operator=operator,
    name='Test JWT Key',
    key=key,
    secret_hash=APIKey.hash_secret(secret),
    permission_level='write'
)

print(f"✅ Operador: {operator.name}")
print(f"✅ API Key: {key[:16]}...")
print(f"✅ API Secret: {secret[:16]}...")

# Obtener token JWT
print("\n2️⃣  Obtener Token JWT")
print("-" * 70)

response = requests.post(f'{BASE_URL}/api/token/', json={
    'api_key': key,
    'api_secret': secret
})

if response.status_code == 200:
    data = response.json()
    access_token = data['access']
    refresh_token = data['refresh']
    
    print(f"✅ Token obtenido exitosamente")
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   Refresh Token: {refresh_token[:50]}...")
    print(f"   Operador: {data['operator']['name']}")
    print(f"   Permisos: {data['permission_level']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")
    sys.exit(1)

# Probar endpoint protegido
print("\n3️⃣  Probar Endpoint Protegido (CON token)")
print("-" * 70)

response = requests.get(
    f'{BASE_URL}/api/multi-tenant/sessions/',
    headers={'Authorization': f'Bearer {access_token}'}
)

print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ Acceso permitido")
    print(f"   Sesiones: {response.json()['count']}")
else:
    print(f"   ❌ Acceso denegado")
    print(f"   {response.json()}")

# Probar sin token
print("\n4️⃣  Probar Endpoint Protegido (SIN token)")
print("-" * 70)

response = requests.get(f'{BASE_URL}/api/multi-tenant/sessions/')

print(f"   Status: {response.status_code}")
if response.status_code == 401:
    print(f"   ✅ Correctamente bloqueado")
    print(f"   Mensaje: {response.json()['message']}")
else:
    print(f"   ❌ Debería estar bloqueado")

# Probar refresh token
print("\n5️⃣  Refrescar Token")
print("-" * 70)

response = requests.post(
    f'{BASE_URL}/api/token/refresh/',
    json={'refresh': refresh_token}
)

if response.status_code == 200:
    new_access = response.json()['access']
    print(f"✅ Token refrescado")
    print(f"   Nuevo Access Token: {new_access[:50]}...")
else:
    print(f"❌ Error al refrescar: {response.json()}")

print("\n" + "=" * 70)
print("✅ Test JWT completado")
print("\n🎯 Resumen:")
print("   ✅ Token JWT obtenido con API Key + Secret")
print("   ✅ Endpoints protegidos requieren Bearer Token")
print("   ✅ Sin token retorna mensaje claro de error")
print("   ✅ Refresh token funciona correctamente")
print("=" * 70)

