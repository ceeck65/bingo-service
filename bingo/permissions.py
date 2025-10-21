"""
Permisos personalizados para el sistema multi-tenant
"""

from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """Requiere que el request esté autenticado con API Key"""
    
    def has_permission(self, request, view):
        return request.auth is not None


class HasWritePermission(permissions.BasePermission):
    """Requiere permiso de escritura o superior"""
    
    def has_permission(self, request, view):
        if not request.auth:
            return False
        
        # Verificar nivel de permiso
        allowed_levels = ['write', 'admin']
        return request.auth.permission_level in allowed_levels


class HasAdminPermission(permissions.BasePermission):
    """Requiere permiso de administrador"""
    
    def has_permission(self, request, view):
        if not request.auth:
            return False
        
        return request.auth.permission_level == 'admin'


class IsOperatorOwner(permissions.BasePermission):
    """Verifica que el recurso pertenezca al operador autenticado"""
    
    def has_object_permission(self, request, view, obj):
        if not request.auth:
            return False
        
        # Obtener el operador del request
        operator = request.user  # request.user es el Operator gracias a authentication
        
        # Verificar según el tipo de objeto
        if hasattr(obj, 'operator'):
            return obj.operator == operator
        elif hasattr(obj, 'player') and hasattr(obj.player, 'operator'):
            return obj.player.operator == operator
        elif hasattr(obj, 'session') and hasattr(obj.session, 'operator'):
            return obj.session.operator == operator
        
        return False


class IsReadOnly(permissions.BasePermission):
    """Permite solo métodos de lectura (GET, HEAD, OPTIONS)"""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

