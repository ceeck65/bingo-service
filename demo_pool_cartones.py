#!/usr/bin/env python3
"""
Demo del sistema de pool de cartones (inventario de cartones)

En este sistema:
1. El operador crea una sesión y define la cantidad de cartones
2. Los cartones se generan al crear la sesión
3. Los jugadores seleccionan cartones existentes (no se generan nuevos)
4. Los cartones pueden reutilizarse en múltiples sesiones
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import (
    Operator, Player, BingoSession, BingoCardExtended
)


def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_crear_sesion_con_cartones():
    """Demo: Operador crea sesión y genera cartones"""
    print_section("1. OPERADOR CREA SESIÓN Y GENERA CARTONES")
    
    # Crear operador
    operator, _ = Operator.objects.get_or_create(
        code='demo_pool',
        defaults={
            'name': 'Demo Pool Cartones',
            'allowed_bingo_types': ['75', '85', '90'],
            'max_cards_per_player': 5
        }
    )
    print(f"✅ Operador: {operator.name}")
    
    # Crear sesión con 50 cartones
    session = BingoSession.objects.create(
        operator=operator,
        name='Sesión Matutina - Pool de Cartones',
        description='Sesión con cartones pre-generados',
        bingo_type='75',
        max_players=20,
        entry_fee=5.00,
        total_cards=50,  # *** Cantidad de cartones a generar ***
        scheduled_start=datetime.now() + timedelta(hours=2)
    )
    print(f"✅ Sesión creada: {session.name}")
    print(f"   - Tipo: {session.bingo_type} bolas")
    print(f"   - Cartones a generar: {session.total_cards}")
    print(f"   - Cartones generados: {session.cards_generated}")
    
    # Generar cartones
    print("\n🎲 Generando cartones...")
    success, message = session.generate_cards_for_session()
    print(f"   {message}")
    
    # Verificar cartones generados
    available = session.get_available_cards().count()
    print(f"\n📊 Estado de cartones:")
    print(f"   - Total: {session.cards.count()}")
    print(f"   - Disponibles: {available}")
    print(f"   - Reservados: {session.get_reserved_cards().count()}")
    print(f"   - Vendidos: {session.get_sold_cards().count()}")
    
    # Mostrar algunos cartones
    print("\n📋 Primeros 5 cartones generados:")
    for card in session.cards.all()[:5]:
        print(f"   - Cartón #{card.card_number}: {card.status.upper()}")
    
    return session, operator


def demo_jugadores_seleccionan_cartones(session, operator):
    """Demo: Jugadores seleccionan cartones del pool"""
    print_section("2. JUGADORES SELECCIONAN CARTONES DEL POOL")
    
    # Crear jugadores
    jugadores = []
    for i in range(1, 4):
        player, _ = Player.objects.get_or_create(
            operator=operator,
            username=f'jugador_pool_{i}',
            defaults={
                'email': f'jugador{i}@demopool.com'
            }
        )
        jugadores.append(player)
        print(f"✅ Jugador creado: {player.username}")
    
    # Ver cartones disponibles
    available_cards = session.get_available_cards()
    print(f"\n📋 Cartones disponibles: {available_cards.count()}")
    
    # Jugadores seleccionan cartones
    print("\n🎯 Jugadores seleccionan cartones:")
    
    for i, player in enumerate(jugadores):
        # Cada jugador selecciona 2 cartones
        cards_to_select = list(available_cards[i*2:(i+1)*2])
        
        print(f"\n   {player.username}:")
        for card in cards_to_select:
            success, message = card.reserve_for_player(player)
            if success:
                print(f"      ✅ Reservó cartón #{card.card_number}")
            else:
                print(f"      ❌ Error: {message}")
    
    # Ver estado actualizado
    print("\n📊 Estado actualizado de cartones:")
    print(f"   - Disponibles: {session.get_available_cards().count()}")
    print(f"   - Reservados: {session.get_reserved_cards().count()}")
    print(f"   - Vendidos: {session.get_sold_cards().count()}")
    
    return jugadores


def demo_confirmar_compra(session, jugadores):
    """Demo: Confirmar compra de cartones reservados"""
    print_section("3. CONFIRMAR COMPRA DE CARTONES RESERVADOS")
    
    # Confirmar compra de algunos cartones
    print("💳 Confirmando compras:")
    
    for player in jugadores[:2]:  # Solo los primeros 2 jugadores
        cards = session.cards.filter(player=player, status='reserved')
        print(f"\n   {player.username}:")
        
        for card in cards:
            success, message = card.mark_as_sold()
            if success:
                print(f"      ✅ Cartón #{card.card_number} vendido (${card.purchase_price})")
            else:
                print(f"      ❌ Error: {message}")
    
    # Ver estado actualizado
    print("\n📊 Estado actualizado de cartones:")
    print(f"   - Disponibles: {session.get_available_cards().count()}")
    print(f"   - Reservados: {session.get_reserved_cards().count()}")
    print(f"   - Vendidos: {session.get_sold_cards().count()}")


def demo_liberar_carton_reservado(session, jugadores):
    """Demo: Liberar un cartón reservado"""
    print_section("4. LIBERAR CARTÓN RESERVADO")
    
    # El último jugador cancela su reserva
    last_player = jugadores[-1]
    reserved_cards = session.cards.filter(player=last_player, status='reserved')
    
    print(f"🔓 {last_player.username} cancela su reserva:")
    for card in reserved_cards:
        success, message = card.release()
        if success:
            print(f"   ✅ Cartón #{card.card_number} liberado y disponible nuevamente")
        else:
            print(f"   ❌ Error: {message}")
    
    # Ver estado actualizado
    print("\n📊 Estado actualizado de cartones:")
    print(f"   - Disponibles: {session.get_available_cards().count()}")
    print(f"   - Reservados: {session.get_reserved_cards().count()}")
    print(f"   - Vendidos: {session.get_sold_cards().count()}")


def demo_reutilizar_cartones():
    """Demo: Reutilizar cartones en nueva sesión"""
    print_section("5. REUTILIZAR CARTONES EN NUEVA SESIÓN")
    
    # Obtener sesión anterior
    old_session = BingoSession.objects.filter(
        name__contains='Pool de Cartones'
    ).first()
    
    print(f"📋 Sesión original: {old_session.name}")
    print(f"   - Total cartones: {old_session.cards.count()}")
    
    # Crear nueva sesión que permite reutilizar cartones
    new_session = BingoSession.objects.create(
        operator=old_session.operator,
        name='Sesión Vespertina - Cartones Reutilizados',
        description='Sesión que reutiliza cartones de la sesión anterior',
        bingo_type='75',
        max_players=25,
        entry_fee=7.50,
        total_cards=50,
        allow_card_reuse=True,  # *** Permite reutilizar cartones ***
        scheduled_start=datetime.now() + timedelta(hours=5)
    )
    print(f"\n✅ Nueva sesión creada: {new_session.name}")
    print(f"   - Permite reutilizar cartones: {new_session.allow_card_reuse}")
    
    # Clonar cartones de la sesión anterior
    print("\n🔄 Reutilizando cartones de la sesión anterior...")
    old_cards = old_session.cards.all()
    cards_reused = 0
    
    for old_card in old_cards:
        new_card = BingoCardExtended.objects.create(
            session=new_session,
            bingo_type=old_card.bingo_type,
            numbers=old_card.numbers,  # *** Mismos números ***
            user_id=f"session_{new_session.id}_card_{old_card.card_number}",
            status='available',
            card_number=old_card.card_number
        )
        cards_reused += 1
    
    new_session.cards_generated = True
    new_session.save()
    
    print(f"✅ {cards_reused} cartones reutilizados exitosamente")
    
    # Comparar cartones
    print("\n🔍 Verificando que los cartones son idénticos:")
    for i in range(3):
        old_card = old_session.cards.filter(card_number=i+1).first()
        new_card = new_session.cards.filter(card_number=i+1).first()
        
        if old_card and new_card:
            same = old_card.numbers == new_card.numbers
            icon = "✅" if same else "❌"
            print(f"   {icon} Cartón #{i+1}: {'Idéntico' if same else 'Diferente'}")


def demo_api_examples():
    """Mostrar ejemplos de uso de la API"""
    print_section("6. EJEMPLOS DE USO DE LA API")
    
    print("\n📝 1. Crear sesión y generar cartones:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "operator": "operator-uuid",
    "name": "Sesión Matutina",
    "bingo_type": "75",
    "total_cards": 100,
    "max_players": 50,
    "entry_fee": 5.00,
    "scheduled_start": "2024-01-15T10:00:00Z"
  }'

# Luego generar los cartones:
curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "generate_now": true
  }'
""")
    
    print("\n📝 2. Ver cartones disponibles:")
    print("""
curl http://localhost:8000/api/multi-tenant/sessions/{session_id}/available-cards/
""")
    
    print("\n📝 3. Jugador selecciona un cartón:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/select/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "card_id": "card-uuid"
  }'
""")
    
    print("\n📝 4. Confirmar compra del cartón:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/confirm-purchase/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "card_id": "card-uuid"
  }'
""")
    
    print("\n📝 5. Liberar cartón reservado:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/release/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "card_id": "card-uuid"
  }'
""")
    
    print("\n📝 6. Reutilizar cartones en nueva sesión:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/reuse/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "new_session_id": "new-session-uuid",
    "old_session_id": "old-session-uuid"
  }'
""")


def main():
    print("🎲 DEMO: SISTEMA DE POOL DE CARTONES")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nEste demo muestra el nuevo sistema donde:")
    print("  1️⃣  El operador define la cantidad de cartones al crear la sesión")
    print("  2️⃣  Los cartones se generan al crear la sesión")
    print("  3️⃣  Los jugadores seleccionan de los cartones disponibles")
    print("  4️⃣  Los cartones pueden reutilizarse en múltiples sesiones")
    
    # Limpiar datos anteriores
    print("\n🧹 Limpiando datos de demos anteriores...")
    BingoCardExtended.objects.filter(session__name__contains='Pool de Cartones').delete()
    BingoCardExtended.objects.filter(session__name__contains='Cartones Reutilizados').delete()
    BingoSession.objects.filter(name__contains='Pool de Cartones').delete()
    BingoSession.objects.filter(name__contains='Cartones Reutilizados').delete()
    Player.objects.filter(username__startswith='jugador_pool').delete()
    Operator.objects.filter(code='demo_pool').delete()
    
    # Ejecutar demos
    session, operator = demo_crear_sesion_con_cartones()
    jugadores = demo_jugadores_seleccionan_cartones(session, operator)
    demo_confirmar_compra(session, jugadores)
    demo_liberar_carton_reservado(session, jugadores)
    demo_reutilizar_cartones()
    demo_api_examples()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADO")
    print("=" * 70)
    print("\n🎯 Resumen del sistema:")
    print("   ✅ Operador define cantidad de cartones al crear sesión")
    print("   ✅ Cartones se generan una sola vez")
    print("   ✅ Jugadores seleccionan cartones existentes")
    print("   ✅ Sistema de estados: disponible → reservado → vendido")
    print("   ✅ Cartones pueden liberarse si no se confirma la compra")
    print("   ✅ Cartones pueden reutilizarse en múltiples sesiones")
    print("\n💡 Ventajas:")
    print("   • Mayor control del operador sobre los cartones")
    print("   • Evita duplicados en la misma sesión")
    print("   • Optimiza recursos (genera una sola vez)")
    print("   • Permite reutilización en múltiples partidas")
    print("=" * 70)


if __name__ == "__main__":
    main()
