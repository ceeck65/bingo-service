from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import BingoCard, BingoGame, DrawnBall
from .serializers import (
    BingoCardSerializer, BingoCardCreateSerializer, BingoCardValidationSerializer,
    BingoCardWinnerSerializer, BingoGameSerializer, BingoGameCreateSerializer,
    DrawnBallSerializer, DrawBallSerializer
)


class BingoCardListView(generics.ListAPIView):
    """Lista todos los cartones de bingo"""
    queryset = BingoCard.objects.all()
    serializer_class = BingoCardSerializer
    
    def get_queryset(self):
        """Filtra los cartones por tipo y usuario si se especifica"""
        queryset = BingoCard.objects.all()
        bingo_type = self.request.query_params.get('bingo_type', None)
        user_id = self.request.query_params.get('user_id', None)
        
        if bingo_type:
            queryset = queryset.filter(bingo_type=bingo_type)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset


class BingoCardDetailView(generics.RetrieveAPIView):
    """Obtiene un cartón específico por ID"""
    queryset = BingoCard.objects.all()
    serializer_class = BingoCardSerializer
    lookup_field = 'id'


class BingoCardCreateView(APIView):
    """Crea un nuevo cartón de bingo"""
    
    def post(self, request):
        serializer = BingoCardCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            card = serializer.save()
            response_serializer = BingoCardSerializer(card)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BingoCardValidationView(APIView):
    """Valida un cartón existente"""
    
    def post(self, request):
        serializer = BingoCardValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            card_id = serializer.validated_data['card_id']
            card = get_object_or_404(BingoCard, id=card_id)
            validation_result = card.validate_card()
            
            return Response({
                'card_id': card_id,
                'validation_result': validation_result
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def generate_multiple_cards(request):
    """Genera múltiples cartones de bingo"""
    bingo_type = request.data.get('bingo_type')
    count = request.data.get('count', 1)
    user_id = request.data.get('user_id')
    
    if not bingo_type or bingo_type not in [choice[0] for choice in BingoCard.BINGO_TYPES]:
        return Response(
            {'error': 'bingo_type es requerido y debe ser "85" o "90"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        count = int(count)
        if count < 1 or count > 100:  # Límite de seguridad
            return Response(
                {'error': 'count debe estar entre 1 y 100'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response(
            {'error': 'count debe ser un número entero'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cards = []
    for _ in range(count):
        card = BingoCard.create_card(bingo_type=bingo_type, user_id=user_id)
        cards.append(card)
    
    serializer = BingoCardSerializer(cards, many=True)
    return Response({
        'count': len(cards),
        'bingo_type': bingo_type,
        'cards': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def card_statistics(request):
    """Obtiene estadísticas de los cartones"""
    total_cards = BingoCard.objects.count()
    cards_75 = BingoCard.objects.filter(bingo_type='75').count()
    cards_85 = BingoCard.objects.filter(bingo_type='85').count()
    cards_90 = BingoCard.objects.filter(bingo_type='90').count()
    
    return Response({
        'total_cards': total_cards,
        'cards_75_balls': cards_75,
        'cards_85_balls': cards_85,
        'cards_90_balls': cards_90,
        'cards_by_type': {
            '75': cards_75,
            '85': cards_85,
            '90': cards_90
        }
    }, status=status.HTTP_200_OK)


class BingoCardWinnerView(APIView):
    """Verifica si un cartón es ganador"""
    
    def post(self, request):
        serializer = BingoCardWinnerSerializer(data=request.data)
        
        if serializer.is_valid():
            card_id = serializer.validated_data['card_id']
            drawn_numbers = set(serializer.validated_data['drawn_numbers'])
            
            card = get_object_or_404(BingoCard, id=card_id)
            winner_result = card.check_winner(drawn_numbers)
            
            return Response({
                'card_id': card_id,
                'bingo_type': card.bingo_type,
                'winner_result': winner_result
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BingoGameListView(generics.ListCreateAPIView):
    """Lista y crea partidas de bingo"""
    queryset = BingoGame.objects.all()
    serializer_class = BingoGameSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BingoGameCreateSerializer
        return BingoGameSerializer


class BingoGameDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Obtiene, actualiza o elimina una partida específica"""
    queryset = BingoGame.objects.all()
    serializer_class = BingoGameSerializer


class DrawBallView(APIView):
    """Extrae una bola en una partida"""
    
    def post(self, request):
        serializer = DrawBallSerializer(data=request.data)
        
        if serializer.is_valid():
            game_id = serializer.validated_data['game_id']
            game = get_object_or_404(BingoGame, id=game_id)
            
            # Extraer bola
            drawn_number = game.draw_ball()
            
            # Verificar si ya fue extraída
            existing_ball = DrawnBall.objects.filter(game=game, number=drawn_number).first()
            if existing_ball:
                # Si ya fue extraída, intentar con otro número
                attempts = 0
                while existing_ball and attempts < 50:  # Máximo 50 intentos
                    drawn_number = game.draw_ball()
                    existing_ball = DrawnBall.objects.filter(game=game, number=drawn_number).first()
                    attempts += 1
                
                if existing_ball:
                    return Response(
                        {'error': 'No se pueden extraer más bolas únicas'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Crear la bola extraída
            drawn_ball = DrawnBall.objects.create(game=game, number=drawn_number)
            
            return Response({
                'game_id': game_id,
                'drawn_ball': DrawnBallSerializer(drawn_ball).data,
                'total_drawn': game.drawn_balls.count()
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrawnBallsListView(generics.ListAPIView):
    """Lista las bolas extraídas de una partida"""
    serializer_class = DrawnBallSerializer
    
    def get_queryset(self):
        game_id = self.kwargs['game_id']
        return DrawnBall.objects.filter(game_id=game_id)


@api_view(['POST'])
def check_winner_with_game(request):
    """Verifica si un cartón es ganador usando las bolas de una partida"""
    card_id = request.data.get('card_id')
    game_id = request.data.get('game_id')
    
    if not card_id or not game_id:
        return Response(
            {'error': 'card_id y game_id son requeridos'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        card = BingoCard.objects.get(id=card_id)
        game = BingoGame.objects.get(id=game_id)
        
        # Obtener números extraídos de la partida
        drawn_numbers = DrawnBall.get_drawn_numbers(game_id)
        
        # Verificar si es ganador
        winner_result = card.check_winner(drawn_numbers)
        
        return Response({
            'card_id': card_id,
            'game_id': game_id,
            'bingo_type': card.bingo_type,
            'drawn_numbers_count': len(drawn_numbers),
            'winner_result': winner_result
        }, status=status.HTTP_200_OK)
        
    except (BingoCard.DoesNotExist, BingoGame.DoesNotExist):
        return Response(
            {'error': 'Cartón o partida no encontrados'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def generate_card_with_game(request):
    """Genera un cartón y lo asocia a una partida"""
    game_id = request.data.get('game_id')
    user_id = request.data.get('user_id', '')
    
    if not game_id:
        return Response(
            {'error': 'game_id es requerido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        game = BingoGame.objects.get(id=game_id)
        
        # Crear cartón del tipo de la partida
        card = BingoCard.create_card(bingo_type=game.game_type, user_id=user_id)
        
        serializer = BingoCardSerializer(card)
        
        return Response({
            'game_id': game_id,
            'card': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except BingoGame.DoesNotExist:
        return Response(
            {'error': 'Partida no encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )