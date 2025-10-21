"""
Utilidades del sistema
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para mensajes más claros
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Personalizar mensajes de autenticación
        if response.status_code == 401:
            response.data = {
                'error': 'No autorizado',
                'message': 'No tienes permisos para acceder a este recurso. Proporciona un token Bearer válido.',
                'detail': response.data.get('detail', 'Credenciales de autenticación no proporcionadas.')
            }
        elif response.status_code == 403:
            response.data = {
                'error': 'Prohibido',
                'message': 'No tienes permisos suficientes para realizar esta acción.',
                'detail': response.data.get('detail', 'No tienes permiso para realizar esta acción.')
            }
    
    return response

