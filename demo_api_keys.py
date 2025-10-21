#!/usr/bin/env python3
"""
Demo del sistema de autenticación con API Keys
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, APIKey

print("🔐 DEMO: Sistema de Autenticación con API Keys")
print("=" * 70)

# Limpiar datos de prueba
print("🧹 Limpiando API Keys de prueba...")
APIKey.objects.filter(name__startswith='Demo').delete()
Operator.objects.filter(code='demo_auth').delete()

# Crear operador
print("\n1️⃣  CREAR OPERADOR")
print("-" * 70)

operator = Operator.objects.create(
    name='Demo Auth',
    code='demo_auth',
    allowed_bingo_types=['75', '85', '90']
)
print(f"✅ Operador creado: {operator.name}")

# Generar API Key
print("\n2️⃣  GENERAR API KEY")
print("-" * 70)

key, secret = APIKey.generate_credentials()
secret_hash = APIKey.hash_secret(secret)

api_key = APIKey.objects.create(
    operator=operator,
    name='Demo API Key - Laravel',
    key=key,
    secret_hash=secret_hash,
    permission_level='write'
)

print(f"✅ API Key creada: {api_key.name}")
print(f"\n🔑 Credenciales (guárdalas en un lugar seguro):")
print(f"   API Key:    {key}")
print(f"   API Secret: {secret}")
print(f"\n⚠️  IMPORTANTE: El secret solo se muestra una vez!")

# Verificar secret
print("\n3️⃣  VERIFICAR SECRET")
print("-" * 70)

# Verificar con secret correcto
is_valid = api_key.verify_secret(secret)
print(f"   Secret correcto: {'✅ Válido' if is_valid else '❌ Inválido'}")

# Verificar con secret incorrecto
is_valid_wrong = api_key.verify_secret('wrong_secret')
print(f"   Secret incorrecto: {'✅ Válido' if is_valid_wrong else '❌ Inválido'}")

# Verificar estado de la API Key
print("\n4️⃣  VERIFICAR ESTADO DE API KEY")
print("-" * 70)

is_valid, message = api_key.is_valid()
print(f"   Estado: {'✅ Válida' if is_valid else '❌ Inválida'}")
print(f"   Mensaje: {message}")
print(f"   Permisos: {api_key.permission_level}")
print(f"   Rate limit: {api_key.rate_limit} req/min")

# Generar más API Keys con diferentes permisos
print("\n5️⃣  GENERAR MÚLTIPLES API KEYS")
print("-" * 70)

api_keys_config = [
    {'name': 'Demo API Key - WhatsApp', 'permission': 'write'},
    {'name': 'Demo API Key - Telegram', 'permission': 'write'},
    {'name': 'Demo API Key - Admin', 'permission': 'admin'},
    {'name': 'Demo API Key - ReadOnly', 'permission': 'read'},
]

created_keys = []

for config in api_keys_config:
    key, secret = APIKey.generate_credentials()
    secret_hash = APIKey.hash_secret(secret)
    
    api_key_obj = APIKey.objects.create(
        operator=operator,
        name=config['name'],
        key=key,
        secret_hash=secret_hash,
        permission_level=config['permission']
    )
    
    created_keys.append({
        'name': config['name'],
        'key': key,
        'secret': secret,
        'permission': config['permission']
    })
    
    print(f"   ✅ {config['name']}: {key[:16]}...")

# Mostrar resumen
print("\n6️⃣  RESUMEN DE API KEYS CREADAS")
print("-" * 70)

all_keys = APIKey.objects.filter(operator=operator)
print(f"\n📊 Total de API Keys para {operator.name}: {all_keys.count()}")

for api_key in all_keys:
    print(f"\n   📋 {api_key.name}")
    print(f"      Key: {api_key.key[:16]}...")
    print(f"      Permisos: {api_key.get_permission_level_display()}")
    print(f"      Estado: {'✅ Activa' if api_key.is_active else '❌ Inactiva'}")

# Ejemplo de uso en curl
print("\n7️⃣  EJEMPLO DE USO CON CURL")
print("-" * 70)

example_key = created_keys[0]
print(f"""
# Usar la primera API Key creada ({example_key['name']})

curl http://localhost:8000/api/multi-tenant/sessions/ \\
  -H "X-API-Key: {example_key['key']}" \\
  -H "X-API-Secret: {example_key['secret']}"

# Para crear una sesión (requiere write permission)
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \\
  -H "X-API-Key: {example_key['key']}" \\
  -H "X-API-Secret: {example_key['secret']}" \\
  -H "Content-Type: application/json" \\
  -d '{{"operator": "{operator.id}", "name": "Test Session", ...}}'
""")

# Ejemplo de integración Laravel
print("\n8️⃣  EJEMPLO DE INTEGRACIÓN LARAVEL")
print("-" * 70)

print(f"""
// config/bingo.php
return [
    'api_url' => env('BINGO_API_URL', 'http://localhost:8000/api/multi-tenant/'),
    'api_key' => env('BINGO_API_KEY', '{example_key['key']}'),
    'api_secret' => env('BINGO_API_SECRET', '{example_key['secret']}'),
];

// app/Services/BingoService.php
protected function makeRequest($method, $endpoint, $data = null)
{{
    $response = Http::withHeaders([
        'X-API-Key' => config('bingo.api_key'),
        'X-API-Secret' => config('bingo.api_secret'),
    ])->$method(config('bingo.api_url') . $endpoint, $data);
    
    return $response->json();
}}
""")

print("\n" + "=" * 70)
print("✅ Demo completado")
print("\n🎯 Sistema de autenticación implementado:")
print("   ✅ Modelo de API Key creado")
print("   ✅ Generación automática de key + secret")
print("   ✅ Hash seguro del secret (SHA-256)")
print("   ✅ Verificación con compare_digest (timing-safe)")
print("   ✅ Niveles de permisos (read/write/admin)")
print("   ✅ Control por IP (opcional)")
print("   ✅ Rate limiting configurado")
print("   ✅ Expiración de keys")
print("=" * 70)

