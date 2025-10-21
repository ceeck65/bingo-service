"""
Vistas para gestión de API Keys
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import APIKey, Operator
from .serializers_auth import APIKeySerializer, APIKeyCreateSerializer
from .permissions import IsAuthenticated, HasAdminPermission


class APIKeyListView(generics.ListAPIView):
    """Lista API Keys del operador autenticado"""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna solo las API Keys del operador autenticado"""
        if self.request.auth:
            operator = self.request.user  # El operator autenticado
            return APIKey.objects.filter(operator=operator)
        return APIKey.objects.none()


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualización y eliminación de API Keys"""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated, HasAdminPermission]
    
    def get_queryset(self):
        """Solo API Keys del operador autenticado"""
        if self.request.auth:
            operator = self.request.user
            return APIKey.objects.filter(operator=operator)
        return APIKey.objects.none()


@api_view(['POST'])
def create_api_key(request):
    """Crea una nueva API Key para un operador"""
    serializer = APIKeyCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        operator_id = serializer.validated_data['operator']
        name = serializer.validated_data['name']
        permission_level = serializer.validated_data.get('permission_level', 'write')
        
        try:
            operator = Operator.objects.get(id=operator_id)
        except Operator.DoesNotExist:
            return Response({
                'error': 'Operador no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generar credenciales
        key, secret = APIKey.generate_credentials()
        secret_hash = APIKey.hash_secret(secret)
        
        # Crear API Key
        api_key = APIKey.objects.create(
            operator=operator,
            name=name,
            key=key,
            secret_hash=secret_hash,
            permission_level=permission_level
        )
        
        # IMPORTANTE: El secret solo se muestra esta vez
        return Response({
            'message': 'API Key creada exitosamente',
            'api_key': {
                'id': api_key.id,
                'name': api_key.name,
                'key': key,
                'secret': secret,  # ⚠️ Solo se muestra una vez
                'permission_level': api_key.permission_level,
                'operator': {
                    'id': operator.id,
                    'name': operator.name,
                    'code': operator.code
                }
            },
            'warning': 'Guarda el SECRET en un lugar seguro. No se volverá a mostrar.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def revoke_api_key(request, key_id):
    """Revoca (desactiva) una API Key"""
    try:
        api_key = APIKey.objects.get(id=key_id)
        
        # Verificar que pertenece al operador autenticado
        if request.auth and api_key.operator != request.user:
            return Response({
                'error': 'No tienes permiso para revocar esta API Key'
            }, status=status.HTTP_403_FORBIDDEN)
        
        api_key.is_active = False
        api_key.save()
        
        return Response({
            'message': 'API Key revocada exitosamente'
        }, status=status.HTTP_200_OK)
    
    except APIKey.DoesNotExist:
        return Response({
            'error': 'API Key no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def test_authentication(request):
    """Endpoint para probar autenticación"""
    if request.auth:
        api_key = request.auth
        operator = request.user
        
        return Response({
            'message': 'Autenticación exitosa',
            'authenticated': True,
            'operator': {
                'id': operator.id,
                'name': operator.name,
                'code': operator.code
            },
            'api_key': {
                'name': api_key.name,
                'permission_level': api_key.permission_level,
                'last_used': api_key.last_used
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'No autenticado',
            'authenticated': False
        }, status=status.HTTP_401_UNAUTHORIZED)

