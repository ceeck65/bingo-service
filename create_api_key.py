#!/usr/bin/env python3
"""
Script para crear API Keys sin necesidad de autenticación
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, APIKey

print("🔑 CREAR API KEY")
print("=" * 70)

# Listar operadores existentes
operators = Operator.objects.all()

if not operators.exists():
    print("\n⚠️  No hay operadores registrados.")
    print("Primero debes crear un operador.")
    
    create = input("\n¿Crear un nuevo operador? (s/n): ").lower()
    
    if create == 's':
        name = input("Nombre del operador: ")
        code = input("Código del operador (ej: mibingo): ").lower()
        
        operator = Operator.objects.create(
            name=name,
            code=code,
            allowed_bingo_types=['75', '85', '90']
        )
        
        print(f"✅ Operador creado: {operator.name} ({operator.code})")
    else:
        print("❌ Cancelado")
        sys.exit(0)
else:
    print("\n📋 Operadores disponibles:")
    for i, op in enumerate(operators, 1):
        print(f"   {i}. {op.name} ({op.code})")
    
    selection = input("\nSelecciona un operador (número): ")
    
    try:
        operator = list(operators)[int(selection) - 1]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        sys.exit(1)

# Datos de la API Key
print(f"\n🔐 Crear API Key para: {operator.name}")
print("-" * 70)

name = input("Nombre de la API Key (ej: Laravel Production): ")
permission = input("Nivel de permisos (read/write/admin) [write]: ").lower() or 'write'

if permission not in ['read', 'write', 'admin']:
    print("⚠️  Nivel inválido, usando 'write'")
    permission = 'write'

# Generar credenciales
key, secret = APIKey.generate_credentials()
secret_hash = APIKey.hash_secret(secret)

api_key = APIKey.objects.create(
    operator=operator,
    name=name,
    key=key,
    secret_hash=secret_hash,
    permission_level=permission
)

# Mostrar resultado
print("\n" + "=" * 70)
print("✅ API KEY CREADA EXITOSAMENTE")
print("=" * 70)

print(f"""
📋 Información de la API Key:
   ID: {api_key.id}
   Nombre: {api_key.name}
   Operador: {operator.name} ({operator.code})
   Permisos: {api_key.get_permission_level_display()}

🔑 CREDENCIALES (guárdalas en un lugar seguro):

   API Key:    {key}
   API Secret: {secret}

⚠️  IMPORTANTE: El secret solo se muestra esta vez. Si lo pierdes,
   deberás crear una nueva API Key.

📝 Uso:

1. Obtener token JWT:
   
   curl -X POST http://localhost:8000/api/token/ \\
     -H "Content-Type: application/json" \\
     -d '{{
       "api_key": "{key}",
       "api_secret": "{secret}"
     }}'

2. Usar en requests:
   
   curl http://localhost:8000/api/multi-tenant/sessions/ \\
     -H "Authorization: Bearer {{TOKEN}}"

""")

print("=" * 70)

# Preguntar si quiere guardar en archivo
save = input("\n¿Guardar credenciales en archivo? (s/n): ").lower()

if save == 's':
    filename = f"credentials_{operator.code}_{api_key.id}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"API KEY CREDENTIALS\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Operator: {operator.name} ({operator.code})\n")
        f.write(f"API Key Name: {api_key.name}\n")
        f.write(f"Permission Level: {api_key.get_permission_level_display()}\n")
        f.write(f"Created: {api_key.created_at}\n\n")
        f.write(f"API Key:    {key}\n")
        f.write(f"API Secret: {secret}\n\n")
        f.write(f"IMPORTANT: Keep this file secure and delete it after storing\n")
        f.write(f"the credentials in a safe place (password manager, .env, etc.)\n")
    
    print(f"✅ Credenciales guardadas en: {filename}")
    print(f"⚠️  Recuerda eliminar este archivo después de guardar las credenciales")

print("\n🎉 ¡Listo! Ya puedes usar estas credenciales para obtener tokens JWT.")

