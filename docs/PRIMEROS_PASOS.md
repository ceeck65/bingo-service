# 🚀 Primeros Pasos - Sistema de Bingo

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL
- pip

---

## ⚡ Instalación Rápida (5 minutos)

### 1. Clonar/Descargar el Proyecto

```bash
cd /home/ceeck65/Projects/bingo_service
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Base de Datos PostgreSQL

```bash
# Crear base de datos (si no existe)
sudo -u postgres psql -c "CREATE DATABASE bingo;"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD '123456';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bingo TO postgres;"

# Aplicar migraciones
python manage.py migrate
```

### 4. Iniciar Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

---

## 🔑 Crear tu Primera API Key

### Ejecutar Script de Creación

```bash
python create_api_key.py
```

**El script te preguntará:**

1. ¿Crear un nuevo operador? → `s`
2. Nombre del operador → `Mi Bingo`
3. Código del operador → `mibingo`
4. Nombre de la API Key → `Laravel Production`
5. Nivel de permisos → `write`

**Resultado:**
```
✅ API KEY CREADA EXITOSAMENTE
====================================

🔑 CREDENCIALES (guárdalas):

   API Key:    iiGlpfVoThzR_bKGSWVgqs3u-70EECwDUvSTrFPSBZw
   API Secret: GlzQVXxOXZdd98y5dH2hejQi1mFKezggFogWNzjbnTaR...
```

⚠️ **IMPORTANTE**: Guarda estas credenciales en un lugar seguro (`.env`, gestor de contraseñas, etc.)

---

## 🧪 Probar la API

### 1. Obtener Token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "tu-api-key-aqui",
    "api_secret": "tu-api-secret-aqui"
  }'
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

### 2. Usar el Token

```bash
# Guardar token en variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Hacer request
curl http://localhost:8000/api/multi-tenant/operators/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📱 Integrar con tu Aplicación

### Laravel

```php
// .env
BINGO_API_URL=http://localhost:8000/api/multi-tenant/
BINGO_API_KEY=tu-api-key
BINGO_API_SECRET=tu-api-secret

// Obtener token
$response = Http::post('http://localhost:8000/api/token/', [
    'api_key' => config('bingo.api_key'),
    'api_secret' => config('bingo.api_secret')
]);

$token = $response->json()['access'];

// Usar en requests
$sessions = Http::withHeaders([
    'Authorization' => "Bearer {$token}"
])->get(config('bingo.api_url') . 'sessions/');
```

### Vue.js

```javascript
// Obtener token
const { data } = await axios.post('http://localhost:8000/api/token/', {
  api_key: 'tu-api-key',
  api_secret: 'tu-api-secret'
})

const token = data.access

// Usar en requests
const sessions = await axios.get('http://localhost:8000/api/multi-tenant/sessions/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

---

## 🎯 Flujo Completo de Ejemplo

### 1. Crear Sesión de Bingo

```bash
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "name": "Bingo de la Tarde",
    "bingo_type": "75",
    "total_cards": 100,
    "scheduled_start": "2024-10-21T18:00:00Z"
  }'
```

### 2. Generar Cartones

```bash
curl -X POST http://localhost:8000/api/multi-tenant/sessions/{session-id}/generate-cards/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 100
  }'
```

### 3. Registrar Jugador

```bash
curl -X POST http://localhost:8000/api/multi-tenant/players/register-by-phone/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operator_code": "mibingo",
    "phone": "+5491112345678",
    "username": "Juan",
    "whatsapp_id": "+5491112345678"
  }'
```

### 4. Jugador Selecciona Cartón

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/{card-id}/select/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "player": "player-uuid"
  }'
```

### 5. Confirmar Compra

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/{card-id}/confirm-purchase/ \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Crear Partida

```bash
curl -X POST http://localhost:8000/api/multi-tenant/games/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Partida 1",
    "game_type": "75",
    "operator": "operator-uuid",
    "session": "session-uuid"
  }'
```

### 7. Extraer Bolas

```bash
curl -X POST http://localhost:8000/api/multi-tenant/games/{game-id}/draw-ball/ \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta:**
```json
{
  "ball_number": 26,
  "letter": "I",
  "display_name": "I-26",
  "color": "#FF6B35",
  "total_drawn": 1,
  "remaining_balls": 74,
  "game_status": "active"
}
```

---

## 🆘 Problemas Comunes

### Error: "API Key inválida"

**Solución:** Verifica que copiaste correctamente el api_key y api_secret del script de creación.

### Error: "Token expirado"

**Solución:** El access token dura 24 horas. Usa el refresh token:

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "tu-refresh-token"
  }'
```

### Error: "No autorizado"

**Solución:** Asegúrate de incluir el header `Authorization: Bearer {token}` en todos los requests.

### Error de conexión a PostgreSQL

**Solución:** Verifica las credenciales en `bingo_service/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bingo',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📚 Siguiente Paso

Lee la documentación completa:

- **[AUTENTICACION_JWT.md](AUTENTICACION_JWT.md)** - Sistema de autenticación
- **[ENDPOINTS_API.md](ENDPOINTS_API.md)** - Todos los endpoints disponibles
- **[DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md)** - Guía completa

---

¡Listo! Ya tienes el sistema funcionando 🎉
