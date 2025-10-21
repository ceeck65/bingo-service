"""
Serializers para el sistema multi-tenant
"""

from rest_framework import serializers
from .models import (
    Operator, Player, BingoSession, PlayerSession, 
    BingoCardExtended, BingoGameExtended
)


class OperatorSerializer(serializers.ModelSerializer):
    """Serializer para operadores/marcas"""
    allowed_bingo_types_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Operator
        fields = [
            'id', 'name', 'code', 'domain', 'logo_url', 
            'primary_color', 'secondary_color', 'is_active',
            'allowed_bingo_types', 'allowed_bingo_types_display',
            'max_cards_per_player', 'max_cards_per_game',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_allowed_bingo_types_display(self, obj):
        """Retorna los tipos de bingo permitidos con nombres descriptivos"""
        type_mapping = {
            '75': '75 bolas (Americano)',
            '85': '85 bolas (Americano Extendido)',
            '90': '90 bolas (Europeo)'
        }
        return [type_mapping.get(tipo, tipo) for tipo in obj.get_allowed_bingo_types()]


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer para jugadores"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'operator', 'operator_name', 'username', 'email', 'phone',
            'whatsapp_id', 'telegram_id', 'is_active', 'is_verified',
            'created_at', 'updated_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    def validate_username(self, value):
        """Validar que el username sea único por operador"""
        if self.instance:
            # Actualización
            if Player.objects.filter(
                operator=self.initial_data.get('operator'),
                username=value
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Este nombre de usuario ya existe para este operador")
        else:
            # Creación
            if Player.objects.filter(
                operator=self.initial_data.get('operator'),
                username=value
            ).exists():
                raise serializers.ValidationError("Este nombre de usuario ya existe para este operador")
        return value


class BingoSessionSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de bingo"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    bingo_type_display = serializers.CharField(source='get_bingo_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    players_count = serializers.SerializerMethodField()
    cards_count = serializers.SerializerMethodField()
    available_cards_count = serializers.SerializerMethodField()
    sold_cards_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BingoSession
        fields = [
            'id', 'operator', 'operator_name', 'name', 'description',
            'bingo_type', 'bingo_type_display', 'max_players', 'entry_fee',
            'total_cards', 'cards_generated', 'allow_card_reuse',
            'scheduled_start', 'actual_start', 'actual_end', 'status', 'status_display',
            'auto_start', 'auto_draw_interval', 'winning_patterns',
            'players_count', 'cards_count', 'available_cards_count', 'sold_cards_count',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'cards_generated', 'actual_start', 'actual_end', 'created_at', 'updated_at']
    
    def get_players_count(self, obj):
        """Retorna el número de jugadores inscritos"""
        return obj.player_sessions.filter(is_active=True).count()
    
    def get_cards_count(self, obj):
        """Retorna el número total de cartones en la sesión"""
        return obj.cards.count()
    
    def get_available_cards_count(self, obj):
        """Retorna el número de cartones disponibles"""
        return obj.cards.filter(status='available').count()
    
    def get_sold_cards_count(self, obj):
        """Retorna el número de cartones vendidos"""
        return obj.cards.filter(status='sold').count()


class PlayerSessionSerializer(serializers.ModelSerializer):
    """Serializer para participación de jugadores en sesiones"""
    player_username = serializers.CharField(source='player.username', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    
    class Meta:
        model = PlayerSession
        fields = [
            'id', 'session', 'session_name', 'player', 'player_username',
            'joined_at', 'cards_count', 'is_active', 'has_won',
            'winning_cards', 'prize_amount'
        ]
        read_only_fields = ['id', 'joined_at', 'has_won', 'winning_cards', 'prize_amount']


class BingoCardExtendedSerializer(serializers.ModelSerializer):
    """Serializer para cartones extendidos del sistema multi-tenant"""
    validation_result = serializers.SerializerMethodField()
    display_numbers = serializers.SerializerMethodField()
    player_username = serializers.CharField(source='player.username', read_only=True, allow_null=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    operator_name = serializers.CharField(source='player.operator.name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BingoCardExtended
        fields = [
            'id', 'player', 'player_username', 'session', 'session_name',
            'operator_name', 'bingo_type', 'numbers', 'card_number',
            'status', 'status_display', 'purchase_price',
            'is_winner', 'winning_patterns', 'prize_amount',
            'reserved_at', 'purchased_at',
            'validation_result', 'display_numbers', 'created_at'
        ]
        read_only_fields = ['id', 'card_number', 'is_winner', 'winning_patterns', 'prize_amount', 
                           'reserved_at', 'purchased_at', 'created_at']
    
    def get_validation_result(self, obj):
        """Retorna el resultado de la validación del cartón"""
        return obj.check_card_validity()
    
    def get_display_numbers(self, obj):
        """Retorna los números del cartón formateados para display"""
        return obj.get_display_numbers()


class BingoGameExtendedSerializer(serializers.ModelSerializer):
    """Serializer para partidas extendidas del sistema multi-tenant"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    drawn_balls_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BingoGameExtended
        fields = [
            'id', 'operator', 'operator_name', 'session', 'session_name',
            'game_type', 'name', 'is_active', 'auto_draw', 'draw_interval',
            'max_balls', 'drawn_balls_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_drawn_balls_count(self, obj):
        """Retorna el número de bolas extraídas"""
        return obj.drawn_balls.count()


# Serializers para creación específica

class CreatePlayerSerializer(serializers.ModelSerializer):
    """Serializer para crear jugadores"""
    class Meta:
        model = Player
        fields = ['operator', 'username', 'email', 'phone', 'whatsapp_id', 'telegram_id']
    
    def create(self, validated_data):
        """Crear jugador con validaciones específicas"""
        operator = validated_data['operator']
        
        # Verificar que el operador permita nuevos jugadores
        if not operator.is_active:
            raise serializers.ValidationError("El operador no está activo")
        
        return Player.objects.create(**validated_data)


class CreateBingoSessionSerializer(serializers.ModelSerializer):
    """Serializer para crear sesiones de bingo"""
    class Meta:
        model = BingoSession
        fields = [
            'operator', 'name', 'description', 'bingo_type', 'max_players',
            'entry_fee', 'scheduled_start', 'auto_start', 'auto_draw_interval',
            'winning_patterns', 'created_by'
        ]
    
    def validate_bingo_type(self, value):
        """Validar que el tipo de bingo esté permitido para el operador"""
        operator = self.initial_data.get('operator')
        if operator:
            operator_obj = Operator.objects.get(id=operator)
            if value not in operator_obj.get_allowed_bingo_types():
                raise serializers.ValidationError(
                    f"El operador {operator_obj.name} no permite bingo de {value} bolas"
                )
        return value


class JoinSessionSerializer(serializers.Serializer):
    """Serializer para que un jugador se una a una sesión"""
    session_id = serializers.UUIDField()
    player_id = serializers.UUIDField()
    cards_count = serializers.IntegerField(min_value=1, max_value=5, default=1)
    
    def validate(self, data):
        """Validaciones para unirse a una sesión"""
        session = BingoSession.objects.get(id=data['session_id'])
        player = Player.objects.get(id=data['player_id'])
        
        # Verificar que el jugador pertenezca al mismo operador
        if player.operator != session.operator:
            raise serializers.ValidationError(
                "El jugador no pertenece al operador de esta sesión"
            )
        
        # Verificar que la sesión esté abierta
        if session.status not in ['scheduled']:
            raise serializers.ValidationError(
                "La sesión no está abierta para nuevas inscripciones"
            )
        
        # Verificar límite de jugadores
        current_players = session.player_sessions.filter(is_active=True).count()
        if current_players >= session.max_players:
            raise serializers.ValidationError(
                "La sesión ha alcanzado el máximo de jugadores"
            )
        
        # Verificar límite de cartones por jugador
        if data['cards_count'] > session.operator.max_cards_per_player:
            raise serializers.ValidationError(
                f"Máximo {session.operator.max_cards_per_player} cartones por jugador"
            )
        
        return data


class GenerateCardsForSessionSerializer(serializers.Serializer):
    """Serializer para generar cartones cuando se crea una sesión"""
    session_id = serializers.UUIDField()
    generate_now = serializers.BooleanField(default=True)
    
    def validate(self, data):
        """Validaciones para generar cartones"""
        session = BingoSession.objects.get(id=data['session_id'])
        
        if session.cards_generated:
            raise serializers.ValidationError(
                "Los cartones ya fueron generados para esta sesión"
            )
        
        return data


class SelectCardSerializer(serializers.Serializer):
    """Serializer para que un jugador seleccione un cartón"""
    session_id = serializers.UUIDField()
    player_id = serializers.UUIDField()
    card_id = serializers.UUIDField()
    
    def validate(self, data):
        """Validaciones para seleccionar un cartón"""
        session = BingoSession.objects.get(id=data['session_id'])
        player = Player.objects.get(id=data['player_id'])
        card = BingoCardExtended.objects.get(id=data['card_id'])
        
        # Verificar que el jugador pertenezca al mismo operador
        if player.operator != session.operator:
            raise serializers.ValidationError(
                "El jugador no pertenece al operador de esta sesión"
            )
        
        # Verificar que el cartón pertenezca a la sesión
        if card.session != session:
            raise serializers.ValidationError(
                "El cartón no pertenece a esta sesión"
            )
        
        # Verificar que el cartón esté disponible
        if card.status != 'available':
            raise serializers.ValidationError(
                f"El cartón no está disponible (estado: {card.get_status_display()})"
            )
        
        # Verificar que el jugador esté inscrito en la sesión
        if not PlayerSession.objects.filter(
            session=session, player=player, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "El jugador no está inscrito en esta sesión"
            )
        
        return data


class SelectMultipleCardsSerializer(serializers.Serializer):
    """Serializer para que un jugador seleccione múltiples cartones"""
    session_id = serializers.UUIDField()
    player_id = serializers.UUIDField()
    card_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10,
        help_text="Lista de IDs de cartones a seleccionar"
    )
    
    def validate(self, data):
        """Validaciones para seleccionar múltiples cartones"""
        session = BingoSession.objects.get(id=data['session_id'])
        player = Player.objects.get(id=data['player_id'])
        
        # Verificar que el jugador pertenezca al mismo operador
        if player.operator != session.operator:
            raise serializers.ValidationError(
                "El jugador no pertenece al operador de esta sesión"
            )
        
        # Verificar que el jugador esté inscrito en la sesión
        if not PlayerSession.objects.filter(
            session=session, player=player, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "El jugador no está inscrito en esta sesión"
            )
        
        # Verificar límite de cartones por jugador
        current_cards = BingoCardExtended.objects.filter(
            session=session,
            player=player,
            status__in=['reserved', 'sold']
        ).count()
        
        total_requested = current_cards + len(data['card_ids'])
        max_allowed = session.operator.max_cards_per_player
        
        if total_requested > max_allowed:
            raise serializers.ValidationError(
                f"El jugador puede tener máximo {max_allowed} cartones. "
                f"Ya tiene {current_cards} y está intentando agregar {len(data['card_ids'])}"
            )
        
        # Verificar que todos los cartones existan, pertenezcan a la sesión y estén disponibles
        cards = BingoCardExtended.objects.filter(
            id__in=data['card_ids'],
            session=session
        )
        
        if cards.count() != len(data['card_ids']):
            raise serializers.ValidationError(
                "Algunos cartones no existen o no pertenecen a esta sesión"
            )
        
        # Verificar que todos estén disponibles
        unavailable = cards.exclude(status='available')
        if unavailable.exists():
            unavailable_numbers = [c.card_number for c in unavailable]
            raise serializers.ValidationError(
                f"Los siguientes cartones no están disponibles: {unavailable_numbers}"
            )
        
        return data


class ReuseCardsSerializer(serializers.Serializer):
    """Serializer para reutilizar cartones en una nueva sesión"""
    new_session_id = serializers.UUIDField()
    old_session_id = serializers.UUIDField()
    
    def validate(self, data):
        """Validaciones para reutilizar cartones"""
        new_session = BingoSession.objects.get(id=data['new_session_id'])
        old_session = BingoSession.objects.get(id=data['old_session_id'])
        
        # Verificar que la nueva sesión permita reutilizar cartones
        if not new_session.allow_card_reuse:
            raise serializers.ValidationError(
                "La nueva sesión no permite reutilizar cartones"
            )
        
        # Verificar que ambas sesiones tengan el mismo tipo de bingo
        if new_session.bingo_type != old_session.bingo_type:
            raise serializers.ValidationError(
                "Las sesiones deben tener el mismo tipo de bingo"
            )
        
        # Verificar que ambas sesiones pertenezcan al mismo operador
        if new_session.operator != old_session.operator:
            raise serializers.ValidationError(
                "Las sesiones deben pertenecer al mismo operador"
            )
        
        return data
