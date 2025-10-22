"""
Serializers para el sistema de reutilización de cartas
"""

from rest_framework import serializers
from .models import CardPack, PlayerCard, SessionCard, BingoCardExtended, Player, BingoSession


class CardPackSerializer(serializers.ModelSerializer):
    """Serializer para Card Packs"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    bingo_type_display = serializers.CharField(source='get_bingo_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    cards_count = serializers.SerializerMethodField()
    available_cards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CardPack
        fields = [
            'id', 'operator', 'operator_name', 'name', 'description',
            'bingo_type', 'bingo_type_display', 'total_cards', 'cards_generated',
            'price_per_card', 'is_active', 'is_public', 'category', 'category_display',
            'cards_count', 'available_cards_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'cards_generated', 'created_at', 'updated_at']
    
    def get_cards_count(self, obj):
        """Retorna el número de cartas generadas"""
        return obj.get_cards_count()
    
    def get_available_cards_count(self, obj):
        """Retorna el número de cartas disponibles (sin dueño)"""
        return obj.get_available_cards().count()


class BingoCardExtendedSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para cartas (sin toda la información)"""
    bingo_type_display = serializers.CharField(source='get_bingo_type_display', read_only=True)
    
    class Meta:
        model = BingoCardExtended
        fields = [
            'id', 'serial_number', 'card_number', 'bingo_type', 'bingo_type_display',
            'numbers', 'is_reusable', 'total_sessions', 'total_wins'
        ]
        read_only_fields = ['id', 'serial_number', 'card_number', 'numbers', 'total_sessions', 'total_wins']


class PlayerCardSerializer(serializers.ModelSerializer):
    """Serializer para cartas de jugadores"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    card_details = BingoCardExtendedSimpleSerializer(source='card', read_only=True)
    pack_name = serializers.CharField(source='pack.name', read_only=True)
    acquisition_type_display = serializers.CharField(source='get_acquisition_type_display', read_only=True)
    win_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = PlayerCard
        fields = [
            'id', 'player', 'player_username', 'card', 'card_details',
            'pack', 'pack_name', 'acquisition_type', 'acquisition_type_display',
            'purchase_price', 'acquired_at', 'times_used', 'times_won',
            'total_prizes', 'is_favorite', 'nickname', 'last_used_at',
            'win_rate'
        ]
        read_only_fields = [
            'id', 'acquired_at', 'times_used', 'times_won', 
            'total_prizes', 'last_used_at'
        ]
    
    def get_win_rate(self, obj):
        """Calcula el porcentaje de victorias"""
        if obj.times_used == 0:
            return 0
        return round((obj.times_won / obj.times_used) * 100, 2)


class SessionCardSerializer(serializers.ModelSerializer):
    """Serializer para cartas en sesiones"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    card_details = BingoCardExtendedSimpleSerializer(source='card', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    marked_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionCard
        fields = [
            'id', 'session', 'session_name', 'player', 'player_username',
            'card', 'card_details', 'status', 'status_display',
            'marked_numbers', 'marked_count', 'is_winner', 'winning_patterns',
            'prize_amount', 'joined_at', 'finished_at'
        ]
        read_only_fields = [
            'id', 'marked_numbers', 'is_winner', 'winning_patterns',
            'prize_amount', 'joined_at', 'finished_at'
        ]
    
    def get_marked_count(self, obj):
        """Retorna la cantidad de números marcados"""
        return len(obj.marked_numbers)


# === SERIALIZERS PARA ACCIONES ===

class GenerateCardsSerializer(serializers.Serializer):
    """Serializer para generar cartas de un pack"""
    # No requiere campos, solo se usa para validar la acción
    pass


class AcquireCardsSerializer(serializers.Serializer):
    """Serializer para que un jugador adquiera cartas"""
    pack_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1, max_value=50)
    acquisition_type = serializers.ChoiceField(
        choices=PlayerCard.ACQUISITION_TYPES,
        default='purchase'
    )
    
    def validate_quantity(self, value):
        """Valida que la cantidad sea razonable"""
        if value > 50:
            raise serializers.ValidationError("No puedes adquirir más de 50 cartas a la vez")
        return value


class JoinSessionWithCardsSerializer(serializers.Serializer):
    """Serializer para unirse a una sesión con cartas específicas"""
    player_id = serializers.UUIDField(required=True)
    card_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="IDs de las cartas que el jugador quiere usar"
    )
    cards_from_pack = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        help_text="Cantidad de cartas a asignar del pack de la sesión"
    )
    
    def validate(self, data):
        """Valida que se proporcione al menos una opción"""
        if not data.get('card_ids') and not data.get('cards_from_pack'):
            raise serializers.ValidationError(
                "Debes proporcionar 'card_ids' o 'cards_from_pack'"
            )
        
        if data.get('card_ids') and data.get('cards_from_pack'):
            raise serializers.ValidationError(
                "Solo puedes usar 'card_ids' o 'cards_from_pack', no ambos"
            )
        
        return data


class MarkNumberSerializer(serializers.Serializer):
    """Serializer para marcar un número en una carta de sesión"""
    session_card_id = serializers.UUIDField(required=True)
    number = serializers.IntegerField(required=True, min_value=1, max_value=90)
    
    def validate_number(self, value):
        """Valida que el número esté en el rango correcto"""
        if value < 1 or value > 90:
            raise serializers.ValidationError("El número debe estar entre 1 y 90")
        return value


class SetFavoriteSerializer(serializers.Serializer):
    """Serializer para marcar/desmarcar una carta como favorita"""
    is_favorite = serializers.BooleanField(required=True)


class SetNicknameSerializer(serializers.Serializer):
    """Serializer para establecer un apodo a una carta"""
    nickname = serializers.CharField(max_length=50, required=True, allow_blank=True)

