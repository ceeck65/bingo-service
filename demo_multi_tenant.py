#!/usr/bin/env python3
"""
Demo del sistema multi-tenant para bingo
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
    Operator, Player, BingoSession, PlayerSession,
    BingoCardExtended, BingoGameExtended
)


def create_demo_operators():
    """Crear operadores de demostración"""
    print("🏢 CREANDO OPERADORES DE DEMOSTRACIÓN")
    print("=" * 50)
    
    operators_data = [
        {
            'name': 'BingoMax',
            'code': 'bingomax',
            'domain': 'bingomax.com',
            'primary_color': '#FF6B35',
            'secondary_color': '#F7931E',
            'allowed_bingo_types': ['75', '85', '90'],
            'max_cards_per_player': 5,
            'max_cards_per_game': 100
        },
        {
            'name': 'LuckyBingo',
            'code': 'luckybingo',
            'domain': 'luckybingo.net',
            'primary_color': '#4CAF50',
            'secondary_color': '#8BC34A',
            'allowed_bingo_types': ['75', '85'],
            'max_cards_per_player': 3,
            'max_cards_per_game': 50
        },
        {
            'name': 'EuroBingo',
            'code': 'eurobingo',
            'domain': 'eurobingo.eu',
            'primary_color': '#2196F3',
            'secondary_color': '#03DAC6',
            'allowed_bingo_types': ['90'],
            'max_cards_per_player': 10,
            'max_cards_per_game': 200
        }
    ]
    
    operators = []
    for data in operators_data:
        operator, created = Operator.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        status = "✅ Creado" if created else "📋 Existente"
        print(f"{status} {operator.name} ({operator.code})")
        operators.append(operator)
    
    return operators


def create_demo_players(operators):
    """Crear jugadores de demostración"""
    print("\n👥 CREANDO JUGADORES DE DEMOSTRACIÓN")
    print("=" * 50)
    
    players_data = [
        # BingoMax
        {'operator': operators[0], 'username': 'juan_max', 'email': 'juan@bingomax.com', 'phone': '+1234567890', 'whatsapp_id': '1234567890'},
        {'operator': operators[0], 'username': 'maria_max', 'email': 'maria@bingomax.com', 'phone': '+1234567891', 'telegram_id': 'maria_max_tg'},
        {'operator': operators[0], 'username': 'carlos_max', 'email': 'carlos@bingomax.com', 'phone': '+1234567892'},
        
        # LuckyBingo
        {'operator': operators[1], 'username': 'ana_lucky', 'email': 'ana@luckybingo.net', 'phone': '+2345678901', 'whatsapp_id': '2345678901'},
        {'operator': operators[1], 'username': 'luis_lucky', 'email': 'luis@luckybingo.net', 'phone': '+2345678902', 'telegram_id': 'luis_lucky_tg'},
        
        # EuroBingo
        {'operator': operators[2], 'username': 'sophie_euro', 'email': 'sophie@eurobingo.eu', 'phone': '+3456789012', 'whatsapp_id': '3456789012'},
        {'operator': operators[2], 'username': 'pierre_euro', 'email': 'pierre@eurobingo.eu', 'phone': '+3456789013', 'telegram_id': 'pierre_euro_tg'},
    ]
    
    players = []
    for data in players_data:
        player, created = Player.objects.get_or_create(
            operator=data['operator'],
            username=data['username'],
            defaults=data
        )
        status = "✅ Creado" if created else "📋 Existente"
        print(f"{status} {player.username} ({player.operator.name})")
        players.append(player)
    
    return players


def create_demo_sessions(operators):
    """Crear sesiones de demostración"""
    print("\n🎯 CREANDO SESIONES DE DEMOSTRACIÓN")
    print("=" * 50)
    
    sessions_data = [
        {
            'operator': operators[0],
            'name': 'Sesión Matutina BingoMax',
            'description': 'Sesión matutina de 75 bolas con premios especiales',
            'bingo_type': '75',
            'max_players': 20,
            'entry_fee': 5.00,
            'scheduled_start': datetime.now() + timedelta(hours=2),
            'winning_patterns': ['line', 'diagonal', 'corners', 'full_card'],
            'created_by': 'admin_bingomax'
        },
        {
            'operator': operators[0],
            'name': 'Gran Torneo BingoMax',
            'description': 'Torneo de 85 bolas con premio mayor',
            'bingo_type': '85',
            'max_players': 50,
            'entry_fee': 10.00,
            'scheduled_start': datetime.now() + timedelta(days=1),
            'winning_patterns': ['line', 'diagonal', 'full_card'],
            'created_by': 'admin_bingomax'
        },
        {
            'operator': operators[1],
            'name': 'Lucky Hour',
            'description': 'Hora de la suerte con bingo de 75 bolas',
            'bingo_type': '75',
            'max_players': 30,
            'entry_fee': 3.00,
            'scheduled_start': datetime.now() + timedelta(hours=3),
            'winning_patterns': ['line', 'corners'],
            'created_by': 'admin_luckybingo'
        },
        {
            'operator': operators[2],
            'name': 'Euro Classic',
            'description': 'Bingo europeo clásico de 90 bolas',
            'bingo_type': '90',
            'max_players': 100,
            'entry_fee': 7.50,
            'scheduled_start': datetime.now() + timedelta(days=2),
            'winning_patterns': ['line', 'two_lines', 'full_card'],
            'created_by': 'admin_eurobingo'
        }
    ]
    
    sessions = []
    for data in sessions_data:
        session, created = BingoSession.objects.get_or_create(
            operator=data['operator'],
            name=data['name'],
            defaults=data
        )
        status = "✅ Creado" if created else "📋 Existente"
        print(f"{status} {session.name} ({session.bingo_type} bolas)")
        sessions.append(session)
    
    return sessions


def simulate_player_registration(sessions, players):
    """Simular registro de jugadores en sesiones"""
    print("\n📝 SIMULANDO REGISTRO DE JUGADORES")
    print("=" * 50)
    
    # Registros de ejemplo
    registrations = [
        # Sesión 1: BingoMax Matutina (75 bolas)
        {'session': sessions[0], 'player': players[0], 'cards_count': 3},
        {'session': sessions[0], 'player': players[1], 'cards_count': 2},
        {'session': sessions[0], 'player': players[2], 'cards_count': 1},
        
        # Sesión 2: BingoMax Torneo (85 bolas)
        {'session': sessions[1], 'player': players[0], 'cards_count': 5},
        {'session': sessions[1], 'player': players[1], 'cards_count': 4},
        
        # Sesión 3: LuckyBingo Lucky Hour (75 bolas)
        {'session': sessions[2], 'player': players[3], 'cards_count': 2},
        {'session': sessions[2], 'player': players[4], 'cards_count': 3},
        
        # Sesión 4: EuroBingo Classic (90 bolas)
        {'session': sessions[3], 'player': players[5], 'cards_count': 5},
        {'session': sessions[3], 'player': players[6], 'cards_count': 3},
    ]
    
    player_sessions = []
    for reg in registrations:
        player_session, created = PlayerSession.objects.get_or_create(
            session=reg['session'],
            player=reg['player'],
            defaults={
                'cards_count': reg['cards_count'],
                'is_active': True
            }
        )
        status = "✅ Registrado" if created else "📋 Ya registrado"
        print(f"{status} {reg['player'].username} en {reg['session'].name} ({reg['cards_count']} cartones)")
        player_sessions.append(player_session)
    
    return player_sessions


def generate_cards_for_sessions(player_sessions):
    """Generar cartones para las sesiones"""
    print("\n🎲 GENERANDO CARTONES PARA LAS SESIONES")
    print("=" * 50)
    
    cards_generated = []
    for player_session in player_sessions:
        session = player_session.session
        player = player_session.player
        
        print(f"\n📋 Generando cartones para {player.username} en {session.name}:")
        
        # Generar cartones según la cantidad registrada
        for i in range(player_session.cards_count):
            card = BingoCardExtended.create_card(
                bingo_type=session.bingo_type,
                user_id=player.username
            )
            card.session = session
            card.player = player
            card.purchase_price = session.entry_fee / player_session.cards_count
            card.save()
            
            cards_generated.append(card)
            print(f"   ✅ Cartón {i+1}: {card.id}")
    
    return cards_generated


def demonstrate_api_endpoints():
    """Demostrar endpoints de la API multi-tenant"""
    print("\n🌐 ENDPOINTS DE LA API MULTI-TENANT")
    print("=" * 50)
    
    endpoints = [
        {
            'title': '🏢 Operadores',
            'endpoints': [
                'GET /api/multi-tenant/operators/ - Listar operadores',
                'POST /api/multi-tenant/operators/ - Crear operador',
                'GET /api/multi-tenant/operators/{id}/ - Detalle del operador',
                'GET /api/multi-tenant/operators/{id}/statistics/ - Estadísticas del operador'
            ]
        },
        {
            'title': '👥 Jugadores',
            'endpoints': [
                'GET /api/multi-tenant/players/ - Listar jugadores',
                'POST /api/multi-tenant/players/ - Crear jugador',
                'GET /api/multi-tenant/players/{id}/ - Detalle del jugador',
                'POST /api/multi-tenant/players/register-by-phone/ - Registrar por teléfono',
                'POST /api/multi-tenant/players/link-social/ - Vincular cuenta social'
            ]
        },
        {
            'title': '🎯 Sesiones',
            'endpoints': [
                'GET /api/multi-tenant/sessions/ - Listar sesiones',
                'POST /api/multi-tenant/sessions/ - Crear sesión',
                'GET /api/multi-tenant/sessions/{id}/ - Detalle de la sesión',
                'POST /api/multi-tenant/sessions/join/ - Unirse a sesión',
                'POST /api/multi-tenant/sessions/leave/ - Salir de sesión',
                'GET /api/multi-tenant/sessions/{id}/statistics/ - Estadísticas de la sesión'
            ]
        },
        {
            'title': '🎲 Cartones',
            'endpoints': [
                'GET /api/multi-tenant/cards/ - Listar cartones',
                'GET /api/multi-tenant/cards/{id}/ - Detalle del cartón',
                'POST /api/multi-tenant/cards/generate-for-session/ - Generar cartones para sesión'
            ]
        }
    ]
    
    for section in endpoints:
        print(f"\n{section['title']}")
        for endpoint in section['endpoints']:
            print(f"   {endpoint}")


def show_integration_examples():
    """Mostrar ejemplos de integración"""
    print("\n🔗 EJEMPLOS DE INTEGRACIÓN")
    print("=" * 50)
    
    print("\n📱 WhatsApp Integration:")
    print("""
# Registrar jugador desde WhatsApp
curl -X POST http://localhost:8000/api/multi-tenant/players/register-by-phone/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "operator_code": "bingomax",
    "phone": "+1234567890",
    "username": "juan_whatsapp"
  }'

# Vincular cuenta de WhatsApp
curl -X POST http://localhost:8000/api/multi-tenant/players/link-social/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "player_id": "player-uuid",
    "whatsapp_id": "whatsapp-user-id"
  }'
""")
    
    print("\n📱 Telegram Integration:")
    print("""
# Vincular cuenta de Telegram
curl -X POST http://localhost:8000/api/multi-tenant/players/link-social/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "player_id": "player-uuid",
    "telegram_id": "telegram-user-id"
  }'
""")
    
    print("\n🌐 Laravel/Vue Integration:")
    print("""
# Obtener sesiones activas de un operador
curl -X GET "http://localhost:8000/api/multi-tenant/sessions/?operator=operator-uuid&status=active"

# Unirse a una sesión
curl -X POST http://localhost:8000/api/multi-tenant/sessions/join/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "cards_count": 3
  }'

# Generar cartones para una sesión
curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "count": 3
  }'
""")


def main():
    print("🎲 DEMO SISTEMA MULTI-TENANT PARA BINGO")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Limpiar datos de demo anteriores
    print("🧹 Limpiando datos de demo anteriores...")
    BingoCardExtended.objects.filter(player__username__endswith='_max').delete()
    BingoCardExtended.objects.filter(player__username__endswith='_lucky').delete()
    BingoCardExtended.objects.filter(player__username__endswith='_euro').delete()
    PlayerSession.objects.all().delete()
    BingoSession.objects.filter(name__startswith='Sesión').delete()
    BingoSession.objects.filter(name__startswith='Lucky').delete()
    BingoSession.objects.filter(name__startswith='Euro').delete()
    BingoSession.objects.filter(name__startswith='Gran').delete()
    Player.objects.filter(username__endswith='_max').delete()
    Player.objects.filter(username__endswith='_lucky').delete()
    Player.objects.filter(username__endswith='_euro').delete()
    Operator.objects.filter(code__in=['bingomax', 'luckybingo', 'eurobingo']).delete()
    
    # Crear datos de demo
    operators = create_demo_operators()
    players = create_demo_players(operators)
    sessions = create_demo_sessions(operators)
    player_sessions = simulate_player_registration(sessions, players)
    cards = generate_cards_for_sessions(player_sessions)
    
    # Mostrar información de integración
    demonstrate_api_endpoints()
    show_integration_examples()
    
    print("\n" + "=" * 60)
    print("✅ DEMO MULTI-TENANT COMPLETADO")
    print("=" * 60)
    print("🎯 Sistema listo para integración con:")
    print("   - Laravel/Vue (Web App)")
    print("   - WhatsApp Business API")
    print("   - Telegram Bot API")
    print("   - Sistemas whitelabel")
    print("\n🚀 El microservicio soporta múltiples operadores con:")
    print("   - Aislamiento completo de datos")
    print("   - Configuraciones personalizadas")
    print("   - Branding personalizado")
    print("   - Límites configurables")
    print("   - Integración con redes sociales")
    print("=" * 60)


if __name__ == "__main__":
    main()
