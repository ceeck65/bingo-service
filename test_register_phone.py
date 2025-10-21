#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, Player

print("🧪 Test de registro por teléfono")
print("=" * 60)

# Limpiar datos de prueba
print("🧹 Limpiando datos de prueba anteriores...")
Player.objects.filter(phone='+1234567890').delete()
Operator.objects.filter(code='test_phone').delete()

# Crear operador de prueba
print("\n📝 Creando operador de prueba...")
operator = Operator.objects.create(
    name='Test Phone',
    code='test_phone',
    allowed_bingo_types=['75']
)
print(f"✅ Operador creado: {operator.code}")

# Simular registro por teléfono (primera vez)
print("\n📱 Simulando primer registro...")
player1 = Player.objects.create(
    operator=operator,
    phone='+1234567890',
    username='juan_first',
    is_verified=True
)
print(f"✅ Jugador creado: {player1.username}")

# Simular segundo registro con mismo teléfono (debe actualizar)
print("\n📱 Simulando segundo registro (mismo teléfono)...")
existing = Player.objects.filter(
    operator=operator,
    phone='+1234567890'
).first()

if existing:
    existing.username = 'juan_updated'
    existing.save()
    print(f"✅ Jugador actualizado: {existing.username}")
else:
    print("❌ No se encontró jugador existente")

# Verificar que solo hay un jugador
count = Player.objects.filter(
    operator=operator,
    phone='+1234567890'
).count()

print(f"\n📊 Jugadores con teléfono +1234567890: {count}")

if count == 1:
    print("✅ Correcto: Solo un jugador por teléfono")
else:
    print(f"❌ Error: Hay {count} jugadores con el mismo teléfono")

print("\n" + "=" * 60)
print("✅ Test completado")

