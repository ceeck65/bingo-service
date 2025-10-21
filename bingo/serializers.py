from rest_framework import serializers
from .models import BingoCard, BingoGame, DrawnBall


class BingoCardSerializer(serializers.ModelSerializer):
    validation_result = serializers.SerializerMethodField()
    display_numbers = serializers.SerializerMethodField()
    
    class Meta:
        model = BingoCard
        fields = ['id', 'user_id', 'bingo_type', 'numbers', 'created_at', 'validation_result', 'display_numbers']
        read_only_fields = ['id', 'created_at', 'validation_result', 'display_numbers']
    
    def get_validation_result(self, obj):
        """Retorna el resultado de la validación del cartón"""
        return obj.validate_card()
    
    def get_display_numbers(self, obj):
        """Retorna los números formateados para mostrar"""
        return obj.get_display_numbers()


class BingoCardCreateSerializer(serializers.Serializer):
    bingo_type = serializers.ChoiceField(choices=BingoCard.BINGO_TYPES)
    user_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Crea un nuevo cartón de bingo"""
        bingo_type = validated_data['bingo_type']
        user_id = validated_data.get('user_id')
        
        return BingoCard.create_card(bingo_type=bingo_type, user_id=user_id)


class BingoCardValidationSerializer(serializers.Serializer):
    """Serializer para validar un cartón existente"""
    card_id = serializers.UUIDField()
    
    def validate_card_id(self, value):
        """Verifica que el cartón existe"""
        try:
            BingoCard.objects.get(id=value)
        except BingoCard.DoesNotExist:
            raise serializers.ValidationError("El cartón no existe")
        return value


class BingoCardWinnerSerializer(serializers.Serializer):
    """Serializer para verificar si un cartón es ganador"""
    card_id = serializers.UUIDField()
    drawn_numbers = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de números extraídos"
    )
    
    def validate_card_id(self, value):
        """Verifica que el cartón existe"""
        try:
            BingoCard.objects.get(id=value)
        except BingoCard.DoesNotExist:
            raise serializers.ValidationError("El cartón no existe")
        return value


class BingoGameSerializer(serializers.ModelSerializer):
    """Serializer para partidas de bingo"""
    drawn_balls_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BingoGame
        fields = ['id', 'game_type', 'name', 'created_at', 'is_active', 'drawn_balls_count']
        read_only_fields = ['id', 'created_at', 'drawn_balls_count']
    
    def get_drawn_balls_count(self, obj):
        """Retorna la cantidad de bolas extraídas"""
        return obj.drawn_balls.count()


class DrawnBallSerializer(serializers.ModelSerializer):
    """Serializer para bolas extraídas"""
    
    class Meta:
        model = DrawnBall
        fields = ['id', 'number', 'drawn_at']
        read_only_fields = ['id', 'drawn_at']


class BingoGameCreateSerializer(serializers.Serializer):
    """Serializer para crear una nueva partida"""
    game_type = serializers.ChoiceField(choices=BingoCard.BINGO_TYPES)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Crea una nueva partida de bingo"""
        return BingoGame.objects.create(**validated_data)


class DrawBallSerializer(serializers.Serializer):
    """Serializer para extraer una bola"""
    game_id = serializers.UUIDField()
    
    def validate_game_id(self, value):
        """Verifica que el juego existe y está activo"""
        try:
            game = BingoGame.objects.get(id=value)
            if not game.is_active:
                raise serializers.ValidationError("El juego no está activo")
        except BingoGame.DoesNotExist:
            raise serializers.ValidationError("El juego no existe")
        return value
