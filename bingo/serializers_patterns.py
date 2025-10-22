"""
Serializers para el sistema de patrones de victoria
"""

from rest_framework import serializers
from .models import WinningPattern, BingoSession


class WinningPatternSerializer(serializers.ModelSerializer):
    """Serializer para patrones de victoria"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    compatible_display = serializers.CharField(source='get_compatible_with_display', read_only=True)
    
    class Meta:
        model = WinningPattern
        fields = [
            'id', 'name', 'code', 'description', 'category', 'category_display',
            'compatible_with', 'compatible_display', 'pattern_type', 'pattern_data',
            'prize_multiplier', 'has_jackpot', 'jackpot_max_balls',
            'is_active', 'is_system', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']


class WinningPatternCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear patrones personalizados"""
    
    class Meta:
        model = WinningPattern
        fields = [
            'operator', 'name', 'code', 'description', 'category',
            'compatible_with', 'pattern_type', 'pattern_data',
            'prize_multiplier', 'has_jackpot', 'jackpot_max_balls'
        ]
    
    def validate_code(self, value):
        """Validar que el código sea único"""
        if WinningPattern.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ya existe un patrón con este código")
        return value
    
    def validate_pattern_type(self, value):
        """Validar que el tipo de patrón sea válido"""
        valid_types = [
            'horizontal_line', 'vertical_line', 'diagonal_line', 'full_card',
            'four_corners', 'x_pattern', 'letter_l', 'letter_t', 'custom'
        ]
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo de patrón inválido. Opciones: {', '.join(valid_types)}")
        return value


class SessionPatternConfigSerializer(serializers.Serializer):
    """Serializer para configurar patrones en una sesión"""
    pattern_codes = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de códigos de patrones a usar en la sesión"
    )
    
    def validate_pattern_codes(self, value):
        """Validar que todos los patrones existan y estén activos"""
        if not value:
            raise serializers.ValidationError("Debe seleccionar al menos un patrón")
        
        patterns = WinningPattern.objects.filter(code__in=value, is_active=True)
        
        if patterns.count() != len(value):
            found_codes = [p.code for p in patterns]
            missing = [code for code in value if code not in found_codes]
            raise serializers.ValidationError(f"Patrones no encontrados o inactivos: {', '.join(missing)}")
        
        return value


class CheckWinnerWithPatternsSerializer(serializers.Serializer):
    """Serializer para verificar ganador con múltiples patrones"""
    card_id = serializers.UUIDField(help_text="ID del cartón a verificar")
    drawn_numbers = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de números extraídos"
    )
    check_all_patterns = serializers.BooleanField(
        default=False,
        help_text="Si es True, verifica todos los patrones de la sesión"
    )


class WinnerResultSerializer(serializers.Serializer):
    """Serializer para el resultado de verificación de ganador"""
    is_winner = serializers.BooleanField()
    winning_patterns = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de patrones ganados"
    )
    total_prize_multiplier = serializers.DecimalField(max_digits=10, decimal_places=2)
    jackpot_won = serializers.BooleanField()
    card_id = serializers.UUIDField()
    player_info = serializers.DictField()

