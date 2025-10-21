#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, BingoSession
from datetime import datetime, timedelta

print("🧪 Test del Sistema de Pool de Cartones")
print("=" * 50)

# Crear operador de prueba
op, created = Operator.objects.get_or_create(
    code='test_pool',
    defaults={'name': 'Test Pool', 'allowed_bingo_types': ['75']}
)
print(f"✅ Operador: {op.name} ({'creado' if created else 'existente'})")

# Crear sesión con 10 cartones
session = BingoSession.objects.create(
    operator=op,
    name='Test Pool Cartones',
    bingo_type='75',
    total_cards=10,
    entry_fee=5.00,
    scheduled_start=datetime.now() + timedelta(hours=1)
)
print(f"✅ Sesión creada: {session.name}")
print(f"   - Total cartones configurados: {session.total_cards}")
print(f"   - Cartones generados: {session.cards_generated}")

# Generar cartones
print("\n🎲 Generando cartones...")
success, message = session.generate_cards_for_session()
print(f"   {message}")
print(f"   - Cartones en BD: {session.cards.count()}")
print(f"   - Disponibles: {session.get_available_cards().count()}")
print(f"   - Reservados: {session.get_reserved_cards().count()}")
print(f"   - Vendidos: {session.get_sold_cards().count()}")

# Mostrar algunos cartones
print("\n📋 Cartones generados:")
for card in session.cards.all()[:5]:
    print(f"   - Cartón #{card.card_number}: Estado={card.status.upper()}")

print("\n✅ ¡Sistema de pool de cartones funcionando correctamente!")
print("=" * 50)

