"""
Sistema de autenticación JWT personalizado usando API Keys
"""

import uuid
import jwt
from datetime import datetime, timedelta
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings

from .models import APIKey, Operator


@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_token(request):
    """
    Obtiene un token JWT usando API Key + Secret
    
    Body:
    {
        "api_key": "your-api-key",
        "api_secret": "your-api-secret"
    }
    """
    api_key = request.data.get('api_key')
    api_secret = request.data.get('api_secret')
    
    if not api_key or not api_secret:
        return Response({
            'error': 'Credenciales requeridas',
            'message': 'api_key y api_secret son obligatorios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar API Key
        api_key_obj = APIKey.objects.select_related('operator').get(
            key=api_key,
            is_active=True
        )
        
        # Verificar validez
        is_valid, message = api_key_obj.is_valid()
        if not is_valid:
            return Response({
                'error': 'API Key inválida',
                'message': message
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar secret
        if not api_key_obj.verify_secret(api_secret):
            return Response({
                'error': 'Credenciales inválidas',
                'message': 'El API Secret no coincide'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Actualizar último uso
        api_key_obj.update_last_used()
        
        # Obtener operador
        operator = api_key_obj.operator
        
        # Generar tokens
        now = datetime.utcnow()
        
        # Access Token (24 horas)
        access_payload = {
            'token_type': 'access',
            'exp': now + timedelta(hours=24),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'operator_id': str(operator.id),
            'operator_code': operator.code,
            'operator_name': operator.name,
            'api_key_id': str(api_key_obj.id),
            'permission_level': api_key_obj.permission_level,
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # Refresh Token (7 días)
        refresh_payload = access_payload.copy()
        refresh_payload['token_type'] = 'refresh'
        refresh_payload['exp'] = now + timedelta(days=7)
        refresh_payload['jti'] = str(uuid.uuid4())
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400,  # 24 horas en segundos
            'operator': {
                'id': str(operator.id),
                'name': operator.name,
                'code': operator.code
            },
            'permission_level': api_key_obj.permission_level
        }, status=status.HTTP_200_OK)
    
    except APIKey.DoesNotExist:
        return Response({
            'error': 'Credenciales inválidas',
            'message': 'API Key no encontrada o inactiva'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresca un access token usando el refresh token
    
    Body:
    {
        "refresh": "your-refresh-token"
    }
    """
    refresh_token_str = request.data.get('refresh')
    
    if not refresh_token_str:
        return Response({
            'error': 'Refresh token requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Decodificar refresh token
        payload = jwt.decode(
            refresh_token_str,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Verificar que sea un refresh token
        if payload.get('token_type') != 'refresh':
            return Response({
                'error': 'Token inválido',
                'message': 'Este no es un refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generar nuevo access token
        now = datetime.utcnow()
        
        access_payload = {
            'token_type': 'access',
            'exp': now + timedelta(hours=24),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'operator_id': payload['operator_id'],
            'operator_code': payload['operator_code'],
            'operator_name': payload['operator_name'],
            'api_key_id': payload['api_key_id'],
            'permission_level': payload['permission_level'],
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return Response({
            'access': access_token,
            'token_type': 'Bearer',
            'expires_in': 86400
        }, status=status.HTTP_200_OK)
    
    except jwt.ExpiredSignatureError:
        return Response({
            'error': 'Token expirado',
            'message': 'El refresh token ha expirado'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError as e:
        return Response({
            'error': 'Token inválido',
            'message': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
