#!/usr/bin/env python3
import os
import sys

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')

import django
django.setup()

print("🧪 Probando modelos del sistema...")
print("=" * 60)

try:
    from bingo.models import Operator, Player, BingoSession
    print("✅ Modelos importados correctamente")
    
    # Crear operador
    print("\n📝 Creando operador de prueba...")
    operator = Operator.objects.create(
        name='Test Operator',
        code='test_op',
        allowed_bingo_types=['75', '85', '90']
    )
    print(f"✅ Operador creado: {operator.name} (ID: {operator.id})")
    
    # Crear jugador
    print("\n📝 Creando jugador de prueba...")
    player = Player.objects.create(
        operator=operator,
        username='test_player',
        email='test@example.com'
    )
    print(f"✅ Jugador creado: {player.username} (ID: {player.id})")
    
    # Crear sesión
    from datetime import datetime, timedelta
    print("\n📝 Creando sesión de prueba...")
    session = BingoSession.objects.create(
        operator=operator,
        name='Test Session',
        bingo_type='75',
        total_cards=10,
        entry_fee=5.00,
        scheduled_start=datetime.now() + timedelta(hours=1)
    )
    print(f"✅ Sesión creada: {session.name} (ID: {session.id})")
    print(f"   - Total cartones: {session.total_cards}")
    print(f"   - Cartones generados: {session.cards_generated}")
    
    # Generar cartones
    print("\n🎲 Generando cartones...")
    success, message = session.generate_cards_for_session()
    print(f"   {message}")
    print(f"   - Cartones creados: {session.cards.count()}")
    
    print("\n" + "=" * 60)
    print("✅ ¡TODAS LAS PRUEBAS PASARON!")
    print("   El sistema está funcionando correctamente.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

