"""
Sistema de autenticación con API Key + Secret
"""

from rest_framework import authentication, exceptions
from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Autenticación basada en API Key + Secret
    
    Headers requeridos:
    - X-API-Key: La API Key pública
    - X-API-Secret: El secret privado
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        api_secret = request.META.get('HTTP_X_API_SECRET')
        
        if not api_key or not api_secret:
            return None  # No se proporcionaron credenciales
        
        try:
            # Buscar API Key
            api_key_obj = APIKey.objects.select_related('operator').get(
                key=api_key,
                is_active=True
            )
            
            # Verificar que la API Key no haya expirado
            is_valid, message = api_key_obj.is_valid()
            if not is_valid:
                raise exceptions.AuthenticationFailed(message)
            
            # Verificar el secret
            if not api_key_obj.verify_secret(api_secret):
                raise exceptions.AuthenticationFailed('Secret inválido')
            
            # Verificar IP si está configurado
            if api_key_obj.allowed_ips:
                client_ip = self.get_client_ip(request)
                if client_ip not in api_key_obj.allowed_ips:
                    raise exceptions.AuthenticationFailed(
                        f'IP {client_ip} no autorizada'
                    )
            
            # Actualizar último uso
            api_key_obj.update_last_used()
            
            # Retornar (user=None, auth=api_key_obj)
            # Django REST Framework usa esto para identificar la autenticación
            return (api_key_obj.operator, api_key_obj)
        
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('API Key inválida')
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class OptionalAPIKeyAuthentication(APIKeyAuthentication):
    """
    Autenticación opcional - no falla si no hay credenciales
    Útil para endpoints públicos que pueden tener funcionalidad adicional con auth
    """
    
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except exceptions.AuthenticationFailed:
            return None  # Permitir acceso sin autenticación

