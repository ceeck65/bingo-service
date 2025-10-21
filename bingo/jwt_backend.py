"""
Backend de autenticación JWT personalizado
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from django.conf import settings

from .models import Operator, APIKey


class CustomJWTAuthentication(BaseAuthentication):
    """
    Autenticación JWT personalizada para el sistema de bingo
    """
    
    def authenticate(self, request):
        """
        Autentica el request usando el token JWT del header Authorization
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decodificar token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Verificar que sea un access token
            if payload.get('token_type') != 'access':
                raise exceptions.AuthenticationFailed('Token inválido')
            
            # Obtener operador
            operator_id = payload.get('operator_id')
            if not operator_id:
                raise exceptions.AuthenticationFailed('Token inválido - no contiene operator_id')
            
            operator = Operator.objects.get(id=operator_id, is_active=True)
            
            # Adjuntar información del token
            operator.token_permission_level = payload.get('permission_level', 'read')
            operator.api_key_id = payload.get('api_key_id')
            operator.is_authenticated = True
            
            # Retornar (user, auth) - user es el operator
            return (operator, payload)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token inválido')
        except Operator.DoesNotExist:
            raise exceptions.AuthenticationFailed('Operador no encontrado o inactivo')
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Error de autenticación: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Retorna el tipo de autenticación para el header WWW-Authenticate
        """
        return 'Bearer realm="api"'


