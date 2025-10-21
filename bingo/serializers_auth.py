"""
Serializers para el sistema de autenticación
"""

from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer para API Keys (sin mostrar el secret)"""
    operator_name = serializers.CharField(source='operator.name', read_only=True)
    key_preview = serializers.SerializerMethodField()
    is_valid_status = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'operator', 'operator_name', 'name', 'key_preview',
            'permission_level', 'is_active', 'allowed_ips', 'rate_limit',
            'created_at', 'last_used', 'expires_at', 'is_valid_status'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']
    
    def get_key_preview(self, obj):
        """Muestra solo los primeros 8 caracteres de la key"""
        return f"{obj.key[:8]}..." if obj.key else ""
    
    def get_is_valid_status(self, obj):
        """Retorna el estado de validez"""
        is_valid, message = obj.is_valid()
        return {
            'valid': is_valid,
            'message': message
        }


class APIKeyCreateSerializer(serializers.Serializer):
    """Serializer para crear nuevas API Keys"""
    operator = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    permission_level = serializers.ChoiceField(
        choices=['read', 'write', 'admin'],
        default='write'
    )
    allowed_ips = serializers.ListField(
        child=serializers.IPAddressField(),
        required=False,
        default=list
    )
    rate_limit = serializers.IntegerField(default=100, min_value=1, max_value=10000)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_operator(self, value):
        """Validar que el operador exista"""
        from .models import Operator
        try:
            Operator.objects.get(id=value)
        except Operator.DoesNotExist:
            raise serializers.ValidationError("Operador no encontrado")
        return value

