"""
Vistas para el sistema de patrones de victoria
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import WinningPattern, BingoSession, BingoCardExtended, BingoGameExtended, DrawnBall
from .serializers_patterns import (
    WinningPatternSerializer, WinningPatternCreateSerializer,
    SessionPatternConfigSerializer, CheckWinnerWithPatternsSerializer,
    WinnerResultSerializer
)


# === CRUD de Patrones ===

class WinningPatternListView(generics.ListAPIView):
    """Lista todos los patrones de victoria disponibles"""
    serializer_class = WinningPatternSerializer
    
    def get_queryset(self):
        queryset = WinningPattern.objects.filter(is_active=True)
        
        # Filtros opcionales
        category = self.request.query_params.get('category')
        compatible_with = self.request.query_params.get('compatible_with')
        is_system = self.request.query_params.get('is_system')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if compatible_with:
            queryset = queryset.filter(compatible_with__in=['all', compatible_with])
        
        if is_system is not None:
            is_system_bool = is_system.lower() == 'true'
            queryset = queryset.filter(is_system=is_system_bool)
        
        return queryset


class WinningPatternDetailView(generics.RetrieveAPIView):
    """Detalle de un patrón de victoria"""
    queryset = WinningPattern.objects.all()
    serializer_class = WinningPatternSerializer


class WinningPatternCreateView(generics.CreateAPIView):
    """Crear un patrón personalizado"""
    serializer_class = WinningPatternCreateSerializer
    
    def perform_create(self, serializer):
        # El patrón personalizado no es del sistema
        serializer.save(is_system=False)


class WinningPatternUpdateView(generics.UpdateAPIView):
    """Actualizar un patrón (solo personalizados)"""
    serializer_class = WinningPatternSerializer
    
    def get_queryset(self):
        # Solo permitir actualizar patrones no del sistema
        return WinningPattern.objects.filter(is_system=False)


class WinningPatternDeleteView(generics.DestroyAPIView):
    """Eliminar un patrón (solo personalizados)"""
    
    def get_queryset(self):
        # Solo permitir eliminar patrones no del sistema
        return WinningPattern.objects.filter(is_system=False)


# === Configuración de Patrones en Sesiones ===

@api_view(['POST'])
def configure_session_patterns(request, session_id):
    """
    Configura los patrones de victoria para una sesión
    
    POST /api/patterns/sessions/{session_id}/configure/
    {
        "pattern_codes": ["horizontal_line", "full_card", "four_corners"]
    }
    """
    session = get_object_or_404(BingoSession, id=session_id)
    
    serializer = SessionPatternConfigSerializer(data=request.data)
    
    if serializer.is_valid():
        pattern_codes = serializer.validated_data['pattern_codes']
        
        # Actualizar la sesión
        session.winning_patterns = pattern_codes
        session.save()
        
        # Obtener los patrones configurados
        patterns = WinningPattern.objects.filter(code__in=pattern_codes)
        
        return Response({
            'message': 'Patrones configurados exitosamente',
            'session': {
                'id': session.id,
                'name': session.name
            },
            'patterns': WinningPatternSerializer(patterns, many=True).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_session_patterns(request, session_id):
    """
    Obtiene los patrones configurados para una sesión
    
    GET /api/patterns/sessions/{session_id}/patterns/
    """
    session = get_object_or_404(BingoSession, id=session_id)
    
    patterns = session.get_winning_patterns()
    
    return Response({
        'session': {
            'id': session.id,
            'name': session.name,
            'bingo_type': session.bingo_type
        },
        'patterns': WinningPatternSerializer(patterns, many=True).data,
        'total_patterns': patterns.count()
    }, status=status.HTTP_200_OK)


# === Verificación de Ganadores con Patrones ===

@api_view(['POST'])
def check_winner_with_patterns(request):
    """
    Verifica si un cartón es ganador según los patrones de la sesión
    
    POST /api/patterns/check-winner/
    {
        "card_id": "uuid",
        "drawn_numbers": [1, 2, 3, ...],
        "check_all_patterns": false
    }
    """
    serializer = CheckWinnerWithPatternsSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    card_id = serializer.validated_data['card_id']
    drawn_numbers = serializer.validated_data['drawn_numbers']
    check_all = serializer.validated_data.get('check_all_patterns', False)
    
    # Obtener el cartón
    try:
        card = BingoCardExtended.objects.select_related('session', 'player').get(id=card_id)
    except BingoCardExtended.DoesNotExist:
        return Response({
            'error': 'Cartón no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Obtener patrones de la sesión
    patterns = card.session.get_winning_patterns()
    
    # Verificar cada patrón
    winning_patterns = []
    total_multiplier = 0
    jackpot_won = False
    
    for pattern in patterns:
        result = pattern.check_pattern(
            marked_numbers=drawn_numbers,
            card_numbers=card.numbers,
            bingo_type=card.bingo_type,
            balls_drawn=len(drawn_numbers)
        )
        
        if result['is_winner']:
            winning_patterns.append(result)
            total_multiplier += result['prize_multiplier']
            
            if result.get('is_jackpot'):
                jackpot_won = True
            
            # Si no se solicita verificar todos, salir al primer ganador
            if not check_all:
                break
    
    is_winner = len(winning_patterns) > 0
    
    # Si es ganador, actualizar el cartón
    if is_winner:
        card.is_winner = True
        card.winning_patterns = [p['pattern_code'] for p in winning_patterns]
        card.save()
    
    return Response({
        'is_winner': is_winner,
        'winning_patterns': winning_patterns,
        'total_prize_multiplier': total_multiplier,
        'jackpot_won': jackpot_won,
        'card_id': str(card.id),
        'player_info': {
            'id': str(card.player.id) if card.player else None,
            'username': card.player.username if card.player else None
        },
        'balls_drawn': len(drawn_numbers)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_all_cards_in_game(request, game_id):
    """
    Verifica todos los cartones de una partida después de extraer una bola
    
    POST /api/patterns/games/{game_id}/check-all-cards/
    """
    try:
        game = BingoGameExtended.objects.select_related('session').get(id=game_id)
    except BingoGameExtended.DoesNotExist:
        return Response({
            'error': 'Partida no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Obtener números extraídos
    drawn_balls = DrawnBall.objects.filter(game=game).values_list('number', flat=True)
    drawn_numbers = list(drawn_balls)
    
    if not drawn_numbers:
        return Response({
            'message': 'No hay bolas extraídas aún'
        }, status=status.HTTP_200_OK)
    
    # Obtener todos los cartones de la sesión que están vendidos
    cards = BingoCardExtended.objects.filter(
        session=game.session,
        status='sold',
        is_winner=False  # Solo verificar los que aún no han ganado
    ).select_related('player')
    
    # Patrones de la sesión
    patterns = game.session.get_winning_patterns()
    
    winners = []
    
    for card in cards:
        for pattern in patterns:
            result = pattern.check_pattern(
                marked_numbers=drawn_numbers,
                card_numbers=card.numbers,
                bingo_type=card.bingo_type,
                balls_drawn=len(drawn_numbers)
            )
            
            if result['is_winner']:
                # Marcar como ganador
                card.is_winner = True
                card.winning_patterns = card.winning_patterns or []
                if result['pattern_code'] not in card.winning_patterns:
                    card.winning_patterns.append(result['pattern_code'])
                card.save()
                
                winners.append({
                    'card_id': str(card.id),
                    'card_number': card.card_number,
                    'player': {
                        'id': str(card.player.id) if card.player else None,
                        'username': card.player.username if card.player else None
                    },
                    'pattern': result
                })
    
    return Response({
        'game_id': str(game.id),
        'balls_drawn': len(drawn_numbers),
        'winners_found': len(winners),
        'winners': winners
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_available_patterns_for_bingo_type(request, bingo_type):
    """
    Obtiene los patrones compatibles con un tipo de bingo
    
    GET /api/patterns/available/{bingo_type}/
    """
    if bingo_type not in ['75', '85', '90']:
        return Response({
            'error': 'Tipo de bingo inválido. Debe ser 75, 85 o 90'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    patterns = WinningPattern.objects.filter(
        is_active=True,
        compatible_with__in=['all', bingo_type]
    )
    
    return Response({
        'bingo_type': bingo_type,
        'patterns': WinningPatternSerializer(patterns, many=True).data,
        'total': patterns.count()
    }, status=status.HTTP_200_OK)

