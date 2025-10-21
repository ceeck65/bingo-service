#!/usr/bin/env python3
"""
Demo: Jugador puede jugar con múltiples cartones
"""

import os
import sys
import django
from datetime import datetime, timedelta

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import Operator, Player, BingoSession, BingoCardExtended, PlayerSession


def demo_jugador_multiples_cartones():
    """Demo de jugador con múltiples cartones"""
    print("🎲 DEMO: JUGADOR CON MÚLTIPLES CARTONES")
    print("=" * 70)
    
    # Limpiar datos anteriores
    print("🧹 Limpiando datos de prueba...")
    Player.objects.filter(username='jugador_multi').delete()
    BingoSession.objects.filter(name='Sesión Multi-Cartones').delete()
    Operator.objects.filter(code='demo_multi').delete()
    
    # 1. Crear operador
    print("\n1️⃣  CREAR OPERADOR")
    print("-" * 70)
    operator = Operator.objects.create(
        name='Demo Multi Cartones',
        code='demo_multi',
        allowed_bingo_types=['75'],
        max_cards_per_player=5  # ← Máximo 5 cartones por jugador
    )
    print(f"✅ Operador: {operator.name}")
    print(f"   Máximo cartones por jugador: {operator.max_cards_per_player}")
    
    # 2. Crear sesión con 20 cartones
    print("\n2️⃣  CREAR SESIÓN CON CARTONES")
    print("-" * 70)
    session = BingoSession.objects.create(
        operator=operator,
        name='Sesión Multi-Cartones',
        bingo_type='75',
        total_cards=20,  # ← 20 cartones disponibles
        max_players=10,
        entry_fee=5.00,
        scheduled_start=datetime.now() + timedelta(hours=2)
    )
    print(f"✅ Sesión: {session.name}")
    print(f"   Total cartones: {session.total_cards}")
    
    # Generar cartones
    success, message = session.generate_cards_for_session()
    print(f"   {message}")
    
    # 3. Crear jugador
    print("\n3️⃣  CREAR JUGADOR")
    print("-" * 70)
    player = Player.objects.create(
        operator=operator,
        username='jugador_multi',
        email='jugador@demo.com',
        phone='+9876543210'
    )
    print(f"✅ Jugador: {player.username}")
    
    # Inscribir jugador en sesión
    player_session = PlayerSession.objects.create(
        session=session,
        player=player,
        is_active=True
    )
    print(f"✅ Jugador inscrito en sesión")
    
    # 4. Jugador selecciona 3 cartones
    print("\n4️⃣  JUGADOR SELECCIONA 3 CARTONES")
    print("-" * 70)
    
    available_cards = session.get_available_cards()[:3]
    selected_cards = []
    
    for card in available_cards:
        success, message = card.reserve_for_player(player)
        if success:
            selected_cards.append(card)
            print(f"✅ Cartón #{card.card_number} reservado")
    
    # Actualizar contador
    player_session.cards_count = len(selected_cards)
    player_session.save()
    
    print(f"\n📊 Resumen de selección:")
    print(f"   - Cartones seleccionados: {len(selected_cards)}")
    print(f"   - Límite del operador: {operator.max_cards_per_player}")
    print(f"   - Puede seleccionar más: {operator.max_cards_per_player - len(selected_cards)}")
    
    # 5. Ver cartones del jugador
    print("\n5️⃣  CARTONES DEL JUGADOR")
    print("-" * 70)
    
    player_cards = BingoCardExtended.objects.filter(
        session=session,
        player=player
    ).order_by('card_number')
    
    print(f"📋 {player.username} tiene {player_cards.count()} cartones:")
    for card in player_cards:
        print(f"   - Cartón #{card.card_number}: {card.status.upper()}")
        # Mostrar primera fila del cartón
        if card.numbers:
            first_row = card.numbers[0]
            print(f"      B:{first_row[0]:2d} I:{first_row[1]:2d} N:{str(first_row[2]):>4} G:{first_row[3]:2d} O:{first_row[4]:2d}")
    
    # 6. Confirmar compra de todos los cartones
    print("\n6️⃣  CONFIRMAR COMPRA DE TODOS LOS CARTONES")
    print("-" * 70)
    
    total_cost = 0
    for card in selected_cards:
        success, message = card.mark_as_sold()
        if success:
            total_cost += float(card.purchase_price)
            print(f"✅ Cartón #{card.card_number} vendido (${card.purchase_price})")
    
    print(f"\n💰 Total a pagar: ${total_cost:.2f}")
    
    # 7. Estado final
    print("\n7️⃣  ESTADO FINAL DE LA SESIÓN")
    print("-" * 70)
    
    print(f"📊 Estadísticas de la sesión:")
    print(f"   - Total cartones: {session.cards.count()}")
    print(f"   - Disponibles: {session.get_available_cards().count()}")
    print(f"   - Reservados: {session.get_reserved_cards().count()}")
    print(f"   - Vendidos: {session.get_sold_cards().count()}")
    
    print(f"\n👤 Estadísticas del jugador:")
    print(f"   - Cartones del jugador: {player_session.cards_count}")
    print(f"   - Cartones vendidos: {player_cards.filter(status='sold').count()}")
    print(f"   - Cartones reservados: {player_cards.filter(status='reserved').count()}")


def demo_api_multiple_cards():
    """Demo de APIs para múltiples cartones"""
    print("\n\n🌐 DEMO: APIs PARA MÚLTIPLES CARTONES")
    print("=" * 70)
    
    print("\n📝 1. Seleccionar múltiples cartones a la vez:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/select-multiple/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "card_ids": [
      "card-uuid-1",
      "card-uuid-2",
      "card-uuid-3"
    ]
  }'

Respuesta:
{
  "message": "3 cartones reservados exitosamente",
  "reserved_cards": [...],
  "total_cards": 3
}
""")
    
    print("\n📝 2. Ver todos los cartones de un jugador:")
    print("""
curl http://localhost:8000/api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/

Respuesta:
{
  "summary": {
    "total": 3,
    "available": 0,
    "reserved": 3,
    "sold": 0
  },
  "cards": [...]
}
""")
    
    print("\n📝 3. Confirmar compra de todos los cartones reservados:")
    print("""
curl -X POST http://localhost:8000/api/multi-tenant/cards/confirm-multiple-purchase/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid"
  }'

Respuesta:
{
  "message": "3 cartones confirmados exitosamente",
  "confirmed_cards": [...],
  "total_cost": 15.00,
  "total_cards": 3
}
""")


def demo_limites_cartones():
    """Demo de límites de cartones por jugador"""
    print("\n\n⚠️  DEMO: LÍMITES DE CARTONES")
    print("=" * 70)
    
    # Obtener datos de demo anterior
    operator = Operator.objects.filter(code='demo_multi').first()
    session = BingoSession.objects.filter(name='Sesión Multi-Cartones').first()
    player = Player.objects.filter(username='jugador_multi').first()
    
    if not all([operator, session, player]):
        print("❌ Ejecuta primero demo_jugador_multiples_cartones()")
        return
    
    print(f"📋 Configuración actual:")
    print(f"   - Operador: {operator.name}")
    print(f"   - Límite de cartones: {operator.max_cards_per_player}")
    print(f"   - Cartones actuales del jugador: {player.cards.filter(session=session).count()}")
    
    # Intentar seleccionar más cartones
    print(f"\n🎯 Intentando seleccionar más cartones...")
    
    current_count = BingoCardExtended.objects.filter(
        session=session,
        player=player,
        status__in=['reserved', 'sold']
    ).count()
    
    available = session.get_available_cards()
    can_select = operator.max_cards_per_player - current_count
    
    print(f"   - Cartones actuales: {current_count}")
    print(f"   - Límite del operador: {operator.max_cards_per_player}")
    print(f"   - Puede seleccionar: {can_select} más")
    
    if can_select > 0 and available.exists():
        print(f"\n✅ Seleccionando {min(can_select, 2)} cartones más...")
        cards_to_select = available[:min(can_select, 2)]
        
        for card in cards_to_select:
            success, message = card.reserve_for_player(player)
            if success:
                print(f"   ✅ Cartón #{card.card_number} reservado")
    else:
        print(f"\n⚠️  El jugador ya alcanzó el límite máximo de cartones")


def main():
    print("🎮 DEMO COMPLETO: JUGADOR CON MÚLTIPLES CARTONES")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar demos
    demo_jugador_multiples_cartones()
    demo_api_multiple_cards()
    demo_limites_cartones()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETADO")
    print("=" * 70)
    print("\n🎯 Funcionalidades demostradas:")
    print("   ✅ Jugador puede seleccionar múltiples cartones")
    print("   ✅ Límites de cartones por jugador (configurables)")
    print("   ✅ API para selección múltiple")
    print("   ✅ API para confirmación múltiple")
    print("   ✅ Ver todos los cartones de un jugador")
    print("   ✅ Validación automática de límites")
    print("\n💡 Ventajas:")
    print("   • Mayor probabilidad de ganar")
    print("   • Control de límites por operador")
    print("   • Transparencia total de cartones")
    print("   • Proceso de compra optimizado")
    print("=" * 70)


if __name__ == "__main__":
    main()

