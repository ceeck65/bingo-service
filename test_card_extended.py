#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, BingoSession, BingoCardExtended
from datetime import datetime, timedelta

print("🧪 Test de BingoCardExtended")
print("=" * 60)

# Limpiar datos de prueba
print("🧹 Limpiando datos de prueba...")
BingoSession.objects.filter(name='Test Card Extended').delete()
Operator.objects.filter(code='test_card_ext').delete()

# Crear operador
print("\n📝 Creando operador...")
operator = Operator.objects.create(
    name='Test Card Extended',
    code='test_card_ext',
    allowed_bingo_types=['75']
)
print(f"✅ Operador: {operator.name}")

# Crear sesión
print("\n📝 Creando sesión...")
session = BingoSession.objects.create(
    operator=operator,
    name='Test Card Extended',
    bingo_type='75',
    total_cards=5,
    entry_fee=5.00,
    scheduled_start=datetime.now() + timedelta(hours=1)
)
print(f"✅ Sesión: {session.name}")

# Generar cartones
print("\n🎲 Generando cartones...")
success, message = session.generate_cards_for_session()
print(f"   {message}")

# Obtener primer cartón
print("\n📋 Probando métodos de BingoCardExtended...")
card = session.cards.first()

if card:
    print(f"✅ Cartón #{card.card_number} encontrado")
    
    # Probar check_card_validity
    try:
        validation = card.check_card_validity()
        print(f"✅ check_card_validity() funciona: {validation['is_valid']}")
    except AttributeError as e:
        print(f"❌ check_card_validity() falló: {e}")
    
    # Probar get_display_numbers
    try:
        display = card.get_display_numbers()
        print(f"✅ get_display_numbers() funciona: {len(display)} filas")
    except AttributeError as e:
        print(f"❌ get_display_numbers() falló: {e}")
    
    print(f"\n📊 Información del cartón:")
    print(f"   - ID: {card.id}")
    print(f"   - Número: #{card.card_number}")
    print(f"   - Tipo: {card.bingo_type}")
    print(f"   - Estado: {card.status}")
    print(f"   - Sesión: {card.session.name}")
else:
    print("❌ No se encontró ningún cartón")

print("\n" + "=" * 60)
print("✅ Test completado")

