#!/usr/bin/env python3
"""
Script para limpiar datos duplicados de demos
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, Player, BingoSession, BingoCardExtended, PlayerSession

print("🧹 Limpiando datos de demos...")
print("=" * 60)

# Limpiar jugadores de demos
demo_players = Player.objects.filter(
    username__in=[
        'test_player', 'demo_winner_75', 'demo_winner_85', 'demo_winner_90'
    ]
) | Player.objects.filter(
    username__startswith='jugador_pool_'
) | Player.objects.filter(
    username__startswith='demo_75_user_'
) | Player.objects.filter(
    username__startswith='jugador_75_'
) | Player.objects.filter(
    username__endswith='_max'
) | Player.objects.filter(
    username__endswith='_lucky'
) | Player.objects.filter(
    username__endswith='_euro'
)

count = demo_players.count()
if count > 0:
    demo_players.delete()
    print(f"✅ Eliminados {count} jugadores de demo")
else:
    print("📋 No hay jugadores de demo para eliminar")

# Limpiar cartones sin sesión o sin jugador
orphan_cards = BingoCardExtended.objects.filter(session__isnull=True)
count = orphan_cards.count()
if count > 0:
    orphan_cards.delete()
    print(f"✅ Eliminados {count} cartones huérfanos")
else:
    print("📋 No hay cartones huérfanos")

# Limpiar sesiones de demo
demo_sessions = BingoSession.objects.filter(
    name__icontains='demo'
) | BingoSession.objects.filter(
    name__icontains='test'
) | BingoSession.objects.filter(
    name__icontains='pool de cartones'
)

count = demo_sessions.count()
if count > 0:
    demo_sessions.delete()
    print(f"✅ Eliminadas {count} sesiones de demo")
else:
    print("📋 No hay sesiones de demo para eliminar")

# Limpiar operadores de demo
demo_operators = Operator.objects.filter(
    code__in=['test_pool', 'demo_pool', 'testbingo', 'test_op']
) | Operator.objects.filter(
    code__in=['bingomax', 'luckybingo', 'eurobingo']
)

count = demo_operators.count()
if count > 0:
    demo_operators.delete()
    print(f"✅ Eliminados {count} operadores de demo")
else:
    print("📋 No hay operadores de demo para eliminar")

# Limpiar jugadores duplicados por teléfono
print("\n🔍 Buscando jugadores duplicados por teléfono...")
from django.db.models import Count

duplicates = Player.objects.values('operator', 'phone').annotate(
    count=Count('id')
).filter(count__gt=1)

for dup in duplicates:
    # Mantener el más reciente, eliminar los demás
    players = Player.objects.filter(
        operator_id=dup['operator'],
        phone=dup['phone']
    ).order_by('-created_at')
    
    # Mantener el primero (más reciente), eliminar el resto
    to_delete = players[1:]
    count = len(to_delete)
    for p in to_delete:
        p.delete()
    
    if count > 0:
        print(f"✅ Eliminados {count} duplicados del teléfono {dup['phone']}")

print("\n" + "=" * 60)
print("✅ Limpieza completada")
print("=" * 60)

# Mostrar estadísticas finales
print("\n📊 Estadísticas del sistema:")
print(f"   - Operadores: {Operator.objects.count()}")
print(f"   - Jugadores: {Player.objects.count()}")
print(f"   - Sesiones: {BingoSession.objects.count()}")
print(f"   - Cartones: {BingoCardExtended.objects.count()}")

print("\n✅ Sistema limpio y listo para usar")

