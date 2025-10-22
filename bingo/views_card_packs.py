"""
Vistas para el sistema de reutilización de cartas
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import CardPack, PlayerCard, SessionCard, BingoCardExtended, Player, BingoSession, Operator
from .serializers_card_packs import (
    CardPackSerializer, PlayerCardSerializer, SessionCardSerializer,
    GenerateCardsSerializer, AcquireCardsSerializer, JoinSessionWithCardsSerializer,
    MarkNumberSerializer, SetFavoriteSerializer, SetNicknameSerializer,
    BingoCardExtendedSimpleSerializer
)


# ============================================================================
# CARD PACKS - Gestión de paquetes de cartas
# ============================================================================

class CardPackListView(generics.ListCreateAPIView):
    """Lista y crea card packs"""
    serializer_class = CardPackSerializer
    
    def get_queryset(self):
        """Filtrar packs por operador y estado"""
        queryset = CardPack.objects.all()
        
        operator_id = self.request.query_params.get('operator', None)
        bingo_type = self.request.query_params.get('bingo_type', None)
        category = self.request.query_params.get('category', None)
        is_active = self.request.query_params.get('is_active', None)
        is_public = self.request.query_params.get('is_public', None)
        
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)
        
        if bingo_type:
            queryset = queryset.filter(bingo_type=bingo_type)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        return queryset


class CardPackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de card packs"""
    queryset = CardPack.objects.all()
    serializer_class = CardPackSerializer


@api_view(['POST'])
def generate_cards_for_pack(request, pack_id):
    """Genera las cartas para un pack específico"""
    pack = get_object_or_404(CardPack, id=pack_id)
    
    serializer = GenerateCardsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    success, message = pack.generate_cards()
    
    if success:
        return Response({
            'success': True,
            'message': message,
            'pack': CardPackSerializer(pack).data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_pack_cards(request, pack_id):
    """Lista las cartas de un pack"""
    pack = get_object_or_404(CardPack, id=pack_id)
    
    # Filtros opcionales
    available_only = request.query_params.get('available_only', 'false').lower() == 'true'
    
    if available_only:
        cards = pack.get_available_cards()
    else:
        cards = pack.cards.all()
    
    # Paginación simple
    page_size = int(request.query_params.get('page_size', 50))
    page = int(request.query_params.get('page', 1))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    cards_page = cards[start:end]
    total_count = cards.count()
    
    serializer = BingoCardExtendedSimpleSerializer(cards_page, many=True)
    
    return Response({
        'pack': CardPackSerializer(pack).data,
        'cards': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_count,
            'total_pages': (total_count + page_size - 1) // page_size
        }
    })


# ============================================================================
# PLAYER CARDS - Cartas de los jugadores
# ============================================================================

@api_view(['POST'])
def acquire_cards(request, player_id):
    """Permite a un jugador adquirir cartas de un pack"""
    player = get_object_or_404(Player, id=player_id)
    
    serializer = AcquireCardsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    pack_id = serializer.validated_data['pack_id']
    quantity = serializer.validated_data['quantity']
    acquisition_type = serializer.validated_data.get('acquisition_type', 'purchase')
    
    pack = get_object_or_404(CardPack, id=pack_id)
    
    # Verificar que el pack pertenece al mismo operador
    if pack.operator != player.operator:
        return Response({
            'success': False,
            'message': 'El pack no pertenece al operador del jugador'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar que el pack está activo
    if not pack.is_active:
        return Response({
            'success': False,
            'message': 'El pack no está activo'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Obtener cartas disponibles
    available_cards = pack.get_available_cards()[:quantity]
    
    if len(available_cards) < quantity:
        return Response({
            'success': False,
            'message': f'Solo hay {len(available_cards)} cartas disponibles, solicitaste {quantity}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Crear PlayerCard para cada carta
    player_cards = []
    for card in available_cards:
        player_card = PlayerCard.objects.create(
            player=player,
            card=card,
            pack=pack,
            acquisition_type=acquisition_type,
            purchase_price=pack.price_per_card if acquisition_type == 'purchase' else 0
        )
        player_cards.append(player_card)
    
    return Response({
        'success': True,
        'message': f'{len(player_cards)} cartas adquiridas exitosamente',
        'cards': PlayerCardSerializer(player_cards, many=True).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_player_cards(request, player_id):
    """Lista las cartas de un jugador"""
    player = get_object_or_404(Player, id=player_id)
    
    # Filtros opcionales
    is_favorite = request.query_params.get('is_favorite', None)
    pack_id = request.query_params.get('pack', None)
    bingo_type = request.query_params.get('bingo_type', None)
    
    queryset = player.owned_cards.all()
    
    if is_favorite is not None:
        queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')
    
    if pack_id:
        queryset = queryset.filter(pack_id=pack_id)
    
    if bingo_type:
        queryset = queryset.filter(card__bingo_type=bingo_type)
    
    serializer = PlayerCardSerializer(queryset, many=True)
    
    return Response({
        'player': {
            'id': player.id,
            'username': player.username,
            'operator': player.operator.name
        },
        'total_cards': queryset.count(),
        'cards': serializer.data
    })


@api_view(['PATCH'])
def set_card_favorite(request, player_id, player_card_id):
    """Marca/desmarca una carta como favorita"""
    player = get_object_or_404(Player, id=player_id)
    player_card = get_object_or_404(PlayerCard, id=player_card_id, player=player)
    
    serializer = SetFavoriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    player_card.is_favorite = serializer.validated_data['is_favorite']
    player_card.save()
    
    return Response({
        'success': True,
        'message': 'Favorito actualizado',
        'card': PlayerCardSerializer(player_card).data
    })


@api_view(['PATCH'])
def set_card_nickname(request, player_id, player_card_id):
    """Establece un apodo a una carta"""
    player = get_object_or_404(Player, id=player_id)
    player_card = get_object_or_404(PlayerCard, id=player_card_id, player=player)
    
    serializer = SetNicknameSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    player_card.nickname = serializer.validated_data['nickname']
    player_card.save()
    
    return Response({
        'success': True,
        'message': 'Apodo actualizado',
        'card': PlayerCardSerializer(player_card).data
    })


# ============================================================================
# SESSION CARDS - Cartas en sesiones
# ============================================================================

@api_view(['POST'])
def join_session_with_cards(request, session_id):
    """Permite a un jugador unirse a una sesión con sus cartas"""
    session = get_object_or_404(BingoSession, id=session_id)
    
    serializer = JoinSessionWithCardsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    player_id = serializer.validated_data['player_id']
    card_ids = serializer.validated_data.get('card_ids', [])
    cards_from_pack = serializer.validated_data.get('cards_from_pack', 0)
    
    player = get_object_or_404(Player, id=player_id)
    
    # Verificar que el jugador pertenece al mismo operador
    if player.operator != session.operator:
        return Response({
            'success': False,
            'message': 'El jugador no pertenece al operador de la sesión'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar que la sesión permite unirse
    if session.status not in ['scheduled', 'active']:
        return Response({
            'success': False,
            'message': f'No puedes unirte a una sesión en estado: {session.get_status_display()}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    session_cards = []
    
    # Opción 1: Jugador usa sus propias cartas
    if card_ids:
        for card_id in card_ids:
            # Verificar que el jugador posee la carta
            player_card = PlayerCard.objects.filter(
                player=player,
                card_id=card_id
            ).first()
            
            if not player_card:
                return Response({
                    'success': False,
                    'message': f'El jugador no posee la carta {card_id}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que la carta es del tipo correcto
            if player_card.card.bingo_type != session.bingo_type:
                return Response({
                    'success': False,
                    'message': f'La carta {card_id} es de tipo {player_card.card.bingo_type}, pero la sesión requiere {session.bingo_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que la carta no está ya en esta sesión
            existing = SessionCard.objects.filter(
                session=session,
                card=player_card.card,
                player=player
            ).exists()
            
            if existing:
                continue  # Saltar cartas duplicadas
            
            # Crear SessionCard
            session_card = SessionCard.objects.create(
                session=session,
                card=player_card.card,
                player=player,
                status='active'
            )
            session_cards.append(session_card)
    
    # Opción 2: Asignar cartas del pack de la sesión
    elif cards_from_pack:
        if not session.card_pack:
            return Response({
                'success': False,
                'message': 'La sesión no tiene un pack de cartas asignado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener cartas disponibles del pack
        available_cards = session.card_pack.cards.filter(
            bingo_type=session.bingo_type
        ).exclude(
            session_instances__session=session
        )[:cards_from_pack]
        
        if len(available_cards) < cards_from_pack:
            return Response({
                'success': False,
                'message': f'Solo hay {len(available_cards)} cartas disponibles en el pack'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        for card in available_cards:
            session_card = SessionCard.objects.create(
                session=session,
                card=card,
                player=player,
                status='active'
            )
            session_cards.append(session_card)
    
    # Actualizar o crear PlayerSession
    from .models import PlayerSession
    player_session, created = PlayerSession.objects.get_or_create(
        session=session,
        player=player,
        defaults={'cards_count': len(session_cards)}
    )
    
    if not created:
        player_session.cards_count += len(session_cards)
        player_session.save()
    
    return Response({
        'success': True,
        'message': f'Unido a la sesión con {len(session_cards)} cartas',
        'session': {
            'id': session.id,
            'name': session.name,
            'status': session.status
        },
        'cards': SessionCardSerializer(session_cards, many=True).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_session_cards(request, session_id):
    """Lista las cartas activas en una sesión"""
    session = get_object_or_404(BingoSession, id=session_id)
    
    # Filtros opcionales
    player_id = request.query_params.get('player', None)
    status_filter = request.query_params.get('status', None)
    is_winner = request.query_params.get('is_winner', None)
    
    queryset = session.session_cards.all()
    
    if player_id:
        queryset = queryset.filter(player_id=player_id)
    
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if is_winner is not None:
        queryset = queryset.filter(is_winner=is_winner.lower() == 'true')
    
    serializer = SessionCardSerializer(queryset, many=True)
    
    return Response({
        'session': {
            'id': session.id,
            'name': session.name,
            'status': session.status,
            'bingo_type': session.bingo_type
        },
        'total_cards': queryset.count(),
        'cards': serializer.data
    })


@api_view(['POST'])
def mark_number_on_card(request):
    """Marca un número en una carta de sesión"""
    serializer = MarkNumberSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    session_card_id = serializer.validated_data['session_card_id']
    number = serializer.validated_data['number']
    
    session_card = get_object_or_404(SessionCard, id=session_card_id)
    
    # Verificar que la sesión está activa
    if session_card.session.status != 'active':
        return Response({
            'success': False,
            'message': 'La sesión no está activa'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Marcar el número
    marked = session_card.mark_number(number)
    
    if not marked:
        return Response({
            'success': False,
            'message': 'El número ya estaba marcado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si es ganador
    winner_result = session_card.check_winner()
    
    return Response({
        'success': True,
        'message': 'Número marcado',
        'marked_count': len(session_card.marked_numbers),
        'is_winner': winner_result['is_winner'],
        'winner_details': winner_result if winner_result['is_winner'] else None,
        'card': SessionCardSerializer(session_card).data
    })


@api_view(['GET'])
def get_player_session_cards(request, session_id, player_id):
    """Obtiene las cartas de un jugador específico en una sesión"""
    session = get_object_or_404(BingoSession, id=session_id)
    player = get_object_or_404(Player, id=player_id)
    
    session_cards = SessionCard.objects.filter(
        session=session,
        player=player
    )
    
    serializer = SessionCardSerializer(session_cards, many=True)
    
    return Response({
        'session': {
            'id': session.id,
            'name': session.name
        },
        'player': {
            'id': player.id,
            'username': player.username
        },
        'cards': serializer.data
    })

