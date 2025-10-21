##🔐 Sistema de Autenticación - API Keys

## 📋 Resumen

El sistema utiliza autenticación basada en **API Key + Secret** para proteger los endpoints. Cada operador puede tener múltiples API Keys con diferentes niveles de permisos.

---

## 🔑 Credenciales

Cada API Key consiste en:

1. **API Key** - Clave pública (se envía en cada request)
2. **API Secret** - Clave privada (se envía en cada request, hash almacenado en BD)

### Formato

```
API Key:    iiGlpfVoThzR_bKGSWVgqs3u-70EECwDUvSTrFPSBZw
API Secret: GlzQVXxOXZdd98y5dH2hejQi1mFKezggFogWNzjbnTaR1CocCGk3qIAGtNqTJiSC
```

---

## 📡 Cómo Autenticarse

### Headers Requeridos

Incluir en cada request:

```
X-API-Key: tu-api-key
X-API-Secret: tu-api-secret
```

### Ejemplo con curl

```bash
curl http://localhost:8000/api/multi-tenant/sessions/ \
  -H "X-API-Key: iiGlpfVoThzR_bKGSWVgqs3u-70EECwDUvSTrFPSBZw" \
  -H "X-API-Secret: GlzQVXxOXZdd98y5dH2hejQi1mFKezggFogWNzjbnTaR1CocCGk3qIAGtNqTJiSC"
```

---

## 🎯 Niveles de Permisos

| Nivel | Descripción | Puede hacer |
|-------|-------------|-------------|
| **read** | Solo lectura | GET, HEAD, OPTIONS |
| **write** | Lectura y escritura | GET, POST, PUT, PATCH |
| **admin** | Administrador | Todo (incluyendo DELETE) |

---

## 🔧 Gestión de API Keys

### Crear API Key

```bash
POST /api/auth/api-keys/create/
{
  "operator": "operator-uuid",
  "name": "Laravel Production",
  "permission_level": "write",
  "rate_limit": 100
}
```

**Respuesta:**
```json
{
  "message": "API Key creada exitosamente",
  "api_key": {
    "id": "uuid",
    "name": "Laravel Production",
    "key": "iiGlpfVoThzR_bKGSWVgqs3u-70EECwDUvSTrFPSBZw",
    "secret": "GlzQVXxOXZdd98y5dH2hejQi1mFKezggFogWNzjbnTaR1CocCGk3qIAGtNqTJiSC",
    "permission_level": "write"
  },
  "warning": "Guarda el SECRET en un lugar seguro. No se volverá a mostrar."
}
```

⚠️ **IMPORTANTE**: El `secret` solo se muestra al crear la API Key. Guárdalo de forma segura.

### Listar API Keys

```bash
GET /api/auth/api-keys/
Headers:
  X-API-Key: tu-api-key
  X-API-Secret: tu-api-secret
```

### Revocar API Key

```bash
POST /api/auth/api-keys/{key-id}/revoke/
Headers:
  X-API-Key: tu-api-key
  X-API-Secret: tu-api-secret
```

### Test de Autenticación

```bash
POST /api/auth/test/
Headers:
  X-API-Key: tu-api-key
  X-API-Secret: tu-api-secret
```

**Respuesta:**
```json
{
  "message": "Autenticación exitosa",
  "authenticated": true,
  "operator": {
    "id": "operator-uuid",
    "name": "Mi Bingo",
    "code": "mibingo"
  },
  "api_key": {
    "name": "Laravel Production",
    "permission_level": "write",
    "last_used": "2024-01-15T10:30:00Z"
  }
}
```

---

## 🌐 Integración con Laravel

### Configuración

```php
// config/bingo.php
return [
    'api_url' => env('BINGO_API_URL'),
    'api_key' => env('BINGO_API_KEY'),
    'api_secret' => env('BINGO_API_SECRET'),
];

// .env
BINGO_API_URL=http://localhost:8000/api/multi-tenant/
BINGO_API_KEY=iiGlpfVoThzR_bKGSWVgqs3u-70EECwDUvSTrFPSBZw
BINGO_API_SECRET=GlzQVXxOXZdd98y5dH2hejQi1mFKezggFogWNzjbnTaR1CocCGk3qIAGtNqTJiSC
```

### Servicio con Autenticación

```php
// app/Services/BingoService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;

class BingoService
{
    protected $apiUrl;
    protected $apiKey;
    protected $apiSecret;
    
    public function __construct()
    {
        $this->apiUrl = config('bingo.api_url');
        $this->apiKey = config('bingo.api_key');
        $this->apiSecret = config('bingo.api_secret');
    }
    
    protected function makeRequest($method, $endpoint, $data = null)
    {
        $http = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'X-API-Secret' => $this->apiSecret,
            'Content-Type' => 'application/json',
        ]);
        
        $response = $http->$method($this->apiUrl . $endpoint, $data);
        
        if ($response->failed()) {
            throw new \Exception('API request failed: ' . $response->body());
        }
        
        return $response->json();
    }
    
    public function getSessions()
    {
        return $this->makeRequest('get', 'sessions/');
    }
    
    public function createSession($data)
    {
        return $this->makeRequest('post', 'sessions/', $data);
    }
    
    public function drawBall($gameId)
    {
        return $this->makeRequest('post', "games/{$gameId}/draw-ball/");
    }
}
```

---

## 📱 Integración con WhatsApp/Telegram

```php
// app/Services/WhatsAppBingoService.php

class WhatsAppBingoService extends BingoService
{
    public function processCommand($phone, $message)
    {
        // Las credenciales se manejan automáticamente por la clase padre
        $sessions = $this->getSessions();
        
        // ... procesar comando
    }
}
```

---

## 🔒 Seguridad

### Características de Seguridad

✅ **Secret Hasheado** - SHA-256, nunca se almacena en texto plano  
✅ **Timing-Safe Comparison** - Usa `secrets.compare_digest()`  
✅ **Control por IP** - Opcional, lista blanca de IPs  
✅ **Rate Limiting** - Límite de requests por minuto  
✅ **Expiración** - API Keys pueden tener fecha de expiración  
✅ **Revocación** - Desactivar API Keys comprometidas  

### Mejores Prácticas

1. **Nunca compartir el secret** - Es como una contraseña
2. **Usar HTTPS en producción** - Las credenciales viajan en headers
3. **Rotar keys regularmente** - Generar nuevas cada cierto tiempo
4. **Un key por servicio** - Laravel, WhatsApp, Telegram tienen keys separadas
5. **Monitorear uso** - Revisar `last_used` para detectar uso sospechoso
6. **Límites por IP** - Configurar IPs permitidas en producción

---

## ⚙️ Configuración Avanzada

### API Key con Restricción de IP

```bash
POST /api/auth/api-keys/create/
{
  "operator": "operator-uuid",
  "name": "Laravel Production",
  "permission_level": "write",
  "allowed_ips": ["192.168.1.100", "10.0.0.50"],
  "rate_limit": 200
}
```

### API Key con Expiración

```bash
POST /api/auth/api-keys/create/
{
  "operator": "operator-uuid",
  "name": "API Key Temporal",
  "permission_level": "read",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

---

## 📊 Monitoreo

### Ver Uso de API Keys

```bash
GET /api/auth/api-keys/
```

**Respuesta:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Laravel Production",
      "key_preview": "iiGlpfVo...",
      "permission_level": "write",
      "is_active": true,
      "last_used": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🧪 Probar Autenticación

### Endpoint de Prueba

```bash
POST /api/auth/test/
Headers:
  X-API-Key: tu-api-key
  X-API-Secret: tu-api-secret
```

**Respuesta exitosa:**
```json
{
  "message": "Autenticación exitosa",
  "authenticated": true,
  "operator": {...},
  "api_key": {...}
}
```

**Respuesta fallida:**
```json
{
  "detail": "API Key inválida"
}
```

---

## ❌ Errores Comunes

### Error: "API Key inválida"

**Causa**: La API Key no existe o está desactivada  
**Solución**: Verificar que la key sea correcta y esté activa

### Error: "Secret inválido"

**Causa**: El secret no coincide  
**Solución**: Verificar que el secret sea el correcto

### Error: "API Key expirada"

**Causa**: La key tiene fecha de expiración vencida  
**Solución**: Crear una nueva API Key

### Error: "IP no autorizada"

**Causa**: La IP del cliente no está en la lista de IPs permitidas  
**Solución**: Agregar la IP a `allowed_ips` o dejar el campo vacío

---

## 🎯 Endpoints de Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/api-keys/create/` | Crear nueva API Key |
| GET | `/api/auth/api-keys/` | Listar API Keys |
| GET | `/api/auth/api-keys/{id}/` | Detalle de API Key |
| POST | `/api/auth/api-keys/{id}/revoke/` | Revocar API Key |
| POST | `/api/auth/test/` | Probar autenticación |

---

¡El sistema de autenticación está completamente implementado y listo para producción! 🔐✨
