"""
Vistas para el sistema multi-tenant
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone

from .models import (
    Operator, Player, BingoSession, PlayerSession, 
    BingoCardExtended, BingoGameExtended
)
from .serializers_multi_tenant import (
    OperatorSerializer, PlayerSerializer, BingoSessionSerializer,
    PlayerSessionSerializer, BingoCardExtendedSerializer, BingoGameExtendedSerializer,
    CreatePlayerSerializer, CreateBingoSessionSerializer, JoinSessionSerializer,
    GenerateCardsForSessionSerializer
)


# === VISTAS PARA OPERADORES ===

class OperatorListView(generics.ListCreateAPIView):
    """Lista y crea operadores"""
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    
    def get_queryset(self):
        """Filtrar operadores activos por defecto"""
        queryset = Operator.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class OperatorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de operadores"""
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


# === VISTAS PARA JUGADORES ===

class PlayerListView(generics.ListCreateAPIView):
    """Lista y crea jugadores"""
    serializer_class = PlayerSerializer
    
    def get_queryset(self):
        """Filtrar jugadores por operador"""
        queryset = Player.objects.all()
        operator_id = self.request.query_params.get('operator', None)
        
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer de creación para POST"""
        if self.request.method == 'POST':
            return CreatePlayerSerializer
        return PlayerSerializer


class PlayerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de jugadores"""
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


# === VISTAS PARA SESIONES ===

class BingoSessionListView(generics.ListCreateAPIView):
    """Lista y crea sesiones de bingo"""
    serializer_class = BingoSessionSerializer
    
    def get_queryset(self):
        """Filtrar sesiones por operador y estado"""
        queryset = BingoSession.objects.all()
        
        operator_id = self.request.query_params.get('operator', None)
        status_filter = self.request.query_params.get('status', None)
        
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer de creación para POST"""
        if self.request.method == 'POST':
            return CreateBingoSessionSerializer
        return BingoSessionSerializer


class BingoSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de sesiones"""
    queryset = BingoSession.objects.all()
    serializer_class = BingoSessionSerializer


# === VISTAS PARA PARTICIPACIÓN EN SESIONES ===

class PlayerSessionListView(generics.ListAPIView):
    """Lista participaciones de jugadores en sesiones"""
    serializer_class = PlayerSessionSerializer
    
    def get_queryset(self):
        """Filtrar participaciones por sesión o jugador"""
        queryset = PlayerSession.objects.all()
        
        session_id = self.request.query_params.get('session', None)
        player_id = self.request.query_params.get('player', None)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        
        return queryset


@api_view(['POST'])
def join_session(request):
    """Permite a un jugador unirse a una sesión"""
    serializer = JoinSessionSerializer(data=request.data)
    
    if serializer.is_valid():
        session_id = serializer.validated_data['session_id']
        player_id = serializer.validated_data['player_id']
        cards_count = serializer.validated_data['cards_count']
        
        session = BingoSession.objects.get(id=session_id)
        player = Player.objects.get(id=player_id)
        
        # Crear o actualizar participación
        player_session, created = PlayerSession.objects.get_or_create(
            session=session,
            player=player,
            defaults={
                'cards_count': cards_count,
                'is_active': True
            }
        )
        
        if not created:
            # Actualizar si ya existe
            player_session.cards_count = cards_count
            player_session.is_active = True
            player_session.save()
        
        return Response({
            'message': 'Jugador inscrito exitosamente en la sesión',
            'player_session': PlayerSessionSerializer(player_session).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def leave_session(request):
    """Permite a un jugador salir de una sesión"""
    session_id = request.data.get('session_id')
    player_id = request.data.get('player_id')
    
    if not session_id or not player_id:
        return Response({
            'error': 'session_id y player_id son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player_session = PlayerSession.objects.get(
            session_id=session_id,
            player_id=player_id
        )
        
        player_session.is_active = False
        player_session.save()
        
        return Response({
            'message': 'Jugador retirado exitosamente de la sesión'
        }, status=status.HTTP_200_OK)
    
    except PlayerSession.DoesNotExist:
        return Response({
            'error': 'El jugador no está inscrito en esta sesión'
        }, status=status.HTTP_404_NOT_FOUND)


# === VISTAS PARA CARTONES EXTENDIDOS ===

class BingoCardExtendedListView(generics.ListCreateAPIView):
    """Lista y crea cartones extendidos"""
    serializer_class = BingoCardExtendedSerializer
    
    def get_queryset(self):
        """Filtrar cartones por operador, sesión o jugador"""
        queryset = BingoCardExtended.objects.all()
        
        operator_id = self.request.query_params.get('operator', None)
        session_id = self.request.query_params.get('session', None)
        player_id = self.request.query_params.get('player', None)
        
        if operator_id:
            queryset = queryset.filter(player__operator_id=operator_id)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        
        return queryset


class BingoCardExtendedDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de cartones extendidos"""
    queryset = BingoCardExtended.objects.all()
    serializer_class = BingoCardExtendedSerializer


@api_view(['POST'])
def generate_cards_for_session(request):
    """Genera cartones cuando se crea una sesión"""
    serializer = GenerateCardsForSessionSerializer(data=request.data)
    
    if serializer.is_valid():
        session_id = serializer.validated_data['session_id']
        
        session = BingoSession.objects.get(id=session_id)
        
        # Generar cartones
        success, message = session.generate_cards_for_session()
        
        if not success:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'session': BingoSessionSerializer(session).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def select_card(request):
    """Permite a un jugador seleccionar un cartón disponible"""
    from .serializers_multi_tenant import SelectCardSerializer
    
    serializer = SelectCardSerializer(data=request.data)
    
    if serializer.is_valid():
        player_id = serializer.validated_data['player_id']
        card_id = serializer.validated_data['card_id']
        
        player = Player.objects.get(id=player_id)
        card = BingoCardExtended.objects.get(id=card_id)
        
        # Reservar el cartón
        success, message = card.reserve_for_player(player)
        
        if not success:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'card': BingoCardExtendedSerializer(card).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def select_multiple_cards(request):
    """Permite a un jugador seleccionar múltiples cartones a la vez"""
    from .serializers_multi_tenant import SelectMultipleCardsSerializer
    
    serializer = SelectMultipleCardsSerializer(data=request.data)
    
    if serializer.is_valid():
        session_id = serializer.validated_data['session_id']
        player_id = serializer.validated_data['player_id']
        card_ids = serializer.validated_data['card_ids']
        
        player = Player.objects.get(id=player_id)
        session = BingoSession.objects.get(id=session_id)
        
        # Reservar todos los cartones
        reserved_cards = []
        failed_cards = []
        
        for card_id in card_ids:
            try:
                card = BingoCardExtended.objects.get(id=card_id)
                success, message = card.reserve_for_player(player)
                
                if success:
                    reserved_cards.append(card)
                else:
                    failed_cards.append({
                        'card_number': card.card_number,
                        'error': message
                    })
            except BingoCardExtended.DoesNotExist:
                failed_cards.append({
                    'card_id': str(card_id),
                    'error': 'Cartón no encontrado'
                })
        
        # Actualizar contador en PlayerSession
        player_session = PlayerSession.objects.get(session=session, player=player)
        player_session.cards_count = BingoCardExtended.objects.filter(
            session=session,
            player=player,
            status__in=['reserved', 'sold']
        ).count()
        player_session.save()
        
        response_data = {
            'message': f'{len(reserved_cards)} cartones reservados exitosamente',
            'reserved_cards': BingoCardExtendedSerializer(reserved_cards, many=True).data,
            'total_cards': player_session.cards_count
        }
        
        if failed_cards:
            response_data['failed_cards'] = failed_cards
            response_data['warning'] = f'{len(failed_cards)} cartones no pudieron ser reservados'
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_player_cards(request, session_id, player_id):
    """Obtiene todos los cartones de un jugador en una sesión"""
    try:
        session = BingoSession.objects.get(id=session_id)
        player = Player.objects.get(id=player_id)
        
        # Obtener cartones del jugador
        cards = BingoCardExtended.objects.filter(
            session=session,
            player=player
        ).order_by('card_number')
        
        # Agrupar por estado
        available = cards.filter(status='available').count()
        reserved = cards.filter(status='reserved').count()
        sold = cards.filter(status='sold').count()
        
        return Response({
            'session': {
                'id': session.id,
                'name': session.name
            },
            'player': {
                'id': player.id,
                'username': player.username
            },
            'summary': {
                'total': cards.count(),
                'available': available,
                'reserved': reserved,
                'sold': sold
            },
            'cards': BingoCardExtendedSerializer(cards, many=True).data
        }, status=status.HTTP_200_OK)
    
    except BingoSession.DoesNotExist:
        return Response({
            'error': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except Player.DoesNotExist:
        return Response({
            'error': 'Jugador no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def confirm_card_purchase(request):
    """Confirma la compra de un cartón reservado"""
    card_id = request.data.get('card_id')
    
    if not card_id:
        return Response({
            'error': 'card_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        card = BingoCardExtended.objects.get(id=card_id)
        
        # Marcar como vendido
        success, message = card.mark_as_sold()
        
        if not success:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'card': BingoCardExtendedSerializer(card).data
        }, status=status.HTTP_200_OK)
    
    except BingoCardExtended.DoesNotExist:
        return Response({
            'error': 'Cartón no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def confirm_multiple_cards_purchase(request):
    """Confirma la compra de múltiples cartones reservados"""
    player_id = request.data.get('player_id')
    session_id = request.data.get('session_id')
    
    if not all([player_id, session_id]):
        return Response({
            'error': 'player_id y session_id son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player = Player.objects.get(id=player_id)
        session = BingoSession.objects.get(id=session_id)
        
        # Obtener todos los cartones reservados del jugador
        reserved_cards = BingoCardExtended.objects.filter(
            session=session,
            player=player,
            status='reserved'
        )
        
        if not reserved_cards.exists():
            return Response({
                'error': 'No hay cartones reservados para este jugador'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Confirmar todos los cartones
        confirmed_cards = []
        failed_cards = []
        
        for card in reserved_cards:
            success, message = card.mark_as_sold()
            if success:
                confirmed_cards.append(card)
            else:
                failed_cards.append({
                    'card_number': card.card_number,
                    'error': message
                })
        
        total_cost = sum(card.purchase_price for card in confirmed_cards)
        
        response_data = {
            'message': f'{len(confirmed_cards)} cartones confirmados exitosamente',
            'confirmed_cards': BingoCardExtendedSerializer(confirmed_cards, many=True).data,
            'total_cost': float(total_cost),
            'total_cards': len(confirmed_cards)
        }
        
        if failed_cards:
            response_data['failed_cards'] = failed_cards
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Player.DoesNotExist:
        return Response({
            'error': 'Jugador no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except BingoSession.DoesNotExist:
        return Response({
            'error': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def release_card(request):
    """Libera un cartón reservado para que esté disponible nuevamente"""
    card_id = request.data.get('card_id')
    
    if not card_id:
        return Response({
            'error': 'card_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        card = BingoCardExtended.objects.get(id=card_id)
        
        # Liberar el cartón
        success, message = card.release()
        
        if not success:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': message,
            'card': BingoCardExtendedSerializer(card).data
        }, status=status.HTTP_200_OK)
    
    except BingoCardExtended.DoesNotExist:
        return Response({
            'error': 'Cartón no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_available_cards(request, session_id):
    """Obtiene los cartones disponibles de una sesión"""
    try:
        session = BingoSession.objects.get(id=session_id)
        available_cards = session.get_available_cards()
        
        return Response({
            'session': {
                'id': session.id,
                'name': session.name,
                'total_cards': session.total_cards,
                'available_count': available_cards.count()
            },
            'cards': BingoCardExtendedSerializer(available_cards, many=True).data
        }, status=status.HTTP_200_OK)
    
    except BingoSession.DoesNotExist:
        return Response({
            'error': 'Sesión no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def reuse_cards_in_session(request):
    """Reutiliza cartones de una sesión anterior en una nueva sesión"""
    from .serializers_multi_tenant import ReuseCardsSerializer
    
    serializer = ReuseCardsSerializer(data=request.data)
    
    if serializer.is_valid():
        new_session_id = serializer.validated_data['new_session_id']
        old_session_id = serializer.validated_data['old_session_id']
        
        new_session = BingoSession.objects.get(id=new_session_id)
        old_session = BingoSession.objects.get(id=old_session_id)
        
        # Obtener cartones de la sesión anterior
        old_cards = old_session.cards.all()
        
        # Clonar cartones para la nueva sesión
        cards_reused = []
        for old_card in old_cards:
            new_card = BingoCardExtended.objects.create(
                session=new_session,
                bingo_type=old_card.bingo_type,
                numbers=old_card.numbers,
                user_id=old_card.user_id,
                status='available',
                card_number=old_card.card_number
            )
            cards_reused.append(new_card)
        
        new_session.cards_generated = True
        new_session.save()
        
        return Response({
            'message': f'{len(cards_reused)} cartones reutilizados exitosamente',
            'session': BingoSessionSerializer(new_session).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# === VISTAS PARA PARTIDAS EXTENDIDAS ===

class BingoGameExtendedListView(generics.ListCreateAPIView):
    """Lista y crea partidas extendidas"""
    serializer_class = BingoGameExtendedSerializer
    
    def get_queryset(self):
        """Filtrar partidas por operador o sesión"""
        queryset = BingoGameExtended.objects.all()
        
        operator_id = self.request.query_params.get('operator', None)
        session_id = self.request.query_params.get('session', None)
        
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset


class BingoGameExtendedDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de partidas extendidas"""
    queryset = BingoGameExtended.objects.all()
    serializer_class = BingoGameExtendedSerializer


# === VISTAS PARA ESTADÍSTICAS ===

@api_view(['GET'])
def operator_statistics(request, operator_id):
    """Estadísticas específicas de un operador"""
    operator = get_object_or_404(Operator, id=operator_id)
    
    # Estadísticas básicas
    total_players = operator.players.count()
    active_players = operator.players.filter(is_active=True).count()
    total_sessions = operator.sessions.count()
    active_sessions = operator.sessions.filter(status='active').count()
    
    # Estadísticas de cartones
    total_cards = BingoCardExtended.objects.filter(player__operator=operator).count()
    cards_by_type = {}
    for bingo_type, _ in BingoCardExtended.BINGO_TYPES:
        count = BingoCardExtended.objects.filter(
            player__operator=operator,
            bingo_type=bingo_type
        ).count()
        cards_by_type[bingo_type] = count
    
    # Estadísticas de sesiones por estado
    sessions_by_status = {}
    for status_code, _ in BingoSession.STATUS_CHOICES:
        count = operator.sessions.filter(status=status_code).count()
        sessions_by_status[status_code] = count
    
    return Response({
        'operator': {
            'id': operator.id,
            'name': operator.name,
            'code': operator.code,
            'is_active': operator.is_active
        },
        'players': {
            'total': total_players,
            'active': active_players,
            'inactive': total_players - active_players
        },
        'sessions': {
            'total': total_sessions,
            'active': active_sessions,
            'by_status': sessions_by_status
        },
        'cards': {
            'total': total_cards,
            'by_type': cards_by_type
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def session_statistics(request, session_id):
    """Estadísticas específicas de una sesión"""
    session = get_object_or_404(BingoSession, id=session_id)
    
    # Estadísticas de jugadores
    total_players = session.player_sessions.filter(is_active=True).count()
    winners_count = session.player_sessions.filter(has_won=True).count()
    
    # Estadísticas de cartones
    total_cards = session.cards.count()
    winning_cards = session.cards.filter(is_winner=True).count()
    
    # Cartones por jugador
    cards_by_player = session.player_sessions.filter(is_active=True).values(
        'player__username'
    ).annotate(
        cards_count=Count('cards_count')
    ).order_by('-cards_count')[:10]
    
    return Response({
        'session': {
            'id': session.id,
            'name': session.name,
            'status': session.status,
            'bingo_type': session.bingo_type
        },
        'players': {
            'total': total_players,
            'winners': winners_count
        },
        'cards': {
            'total': total_cards,
            'winning': winning_cards
        },
        'top_players': list(cards_by_player)
    }, status=status.HTTP_200_OK)


# === VISTAS PARA INTEGRACIÓN CON WHATSAPP/TELEGRAM ===

@api_view(['POST'])
def register_player_by_phone(request):
    """Registra un jugador usando número de teléfono (para WhatsApp/Telegram)"""
    operator_code = request.data.get('operator_code')
    phone = request.data.get('phone')
    username = request.data.get('username')
    
    if not all([operator_code, phone, username]):
        return Response({
            'error': 'operator_code, phone y username son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        operator = Operator.objects.get(code=operator_code, is_active=True)
    except Operator.DoesNotExist:
        return Response({
            'error': 'Operador no encontrado o inactivo'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Buscar jugador existente
    try:
        # Intentar encontrar por operador y teléfono
        player = Player.objects.filter(
            operator=operator,
            phone=phone
        ).first()  # Obtener el primero si hay múltiples
        
        if player:
            # Actualizar información si ya existe
            player.username = username
            player.is_verified = True
            player.save()
            created = False
        else:
            # Crear nuevo jugador
            player = Player.objects.create(
                operator=operator,
                phone=phone,
                username=username,
                is_verified=True
            )
            created = True
        
        return Response({
            'message': 'Jugador registrado exitosamente' if created else 'Jugador actualizado exitosamente',
            'player': PlayerSerializer(player).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error al registrar jugador: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def link_social_account(request):
    """Vincula una cuenta de WhatsApp o Telegram a un jugador"""
    player_id = request.data.get('player_id')
    whatsapp_id = request.data.get('whatsapp_id')
    telegram_id = request.data.get('telegram_id')
    
    if not player_id or (not whatsapp_id and not telegram_id):
        return Response({
            'error': 'player_id y al menos uno de whatsapp_id o telegram_id son requeridos'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        player = Player.objects.get(id=player_id)
        
        if whatsapp_id:
            player.whatsapp_id = whatsapp_id
        if telegram_id:
            player.telegram_id = telegram_id
        
        player.save()
        
        return Response({
            'message': 'Cuenta social vinculada exitosamente',
            'player': PlayerSerializer(player).data
        }, status=status.HTTP_200_OK)
    
    except Player.DoesNotExist:
        return Response({
            'error': 'Jugador no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
