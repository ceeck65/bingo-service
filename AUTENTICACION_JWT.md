# 🔐 Autenticación JWT con Bearer Token

## 📋 Resumen

El sistema utiliza **JWT (JSON Web Tokens)** con autenticación **Bearer Token** para proteger todos los endpoints. Los tokens se obtienen usando las credenciales de API Key + Secret.

---

## 🎯 Características

✅ **JWT estándar** - Compatible con cualquier cliente HTTP  
✅ **Bearer Token** - Header `Authorization: Bearer {token}`  
✅ **Basado en API Key + Secret** - Sin necesidad de usuarios  
✅ **Access + Refresh tokens** - Renovación automática  
✅ **Multi-tenant** - Cada operador tiene sus tokens  
✅ **Permisos incluidos** - read/write/admin en el token  
✅ **Mensajes claros** - Errores 401 descriptivos  

---

## 🔑 Obtener Token JWT

### 1. Endpoint

```
POST /api/token/
```

### 2. Body

```json
{
  "api_key": "tu-api-key-aqui",
  "api_secret": "tu-api-secret-aqui"
}
```

### 3. Respuesta Exitosa (200)

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "operator": {
    "id": "uuid-operador",
    "name": "Mi Bingo",
    "code": "mibingo"
  },
  "permission_level": "write"
}
```

### 4. Ejemplo curl

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "tu-api-key",
    "api_secret": "tu-api-secret"
  }'
```

---

## 🌐 Usar el Token en Requests

### Header Required

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Ejemplo curl

```bash
curl http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ejemplo JavaScript/Fetch

```javascript
fetch('http://localhost:8000/api/multi-tenant/sessions/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

### Ejemplo Axios

```javascript
axios.get('http://localhost:8000/api/multi-tenant/sessions/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
```

---

## 🔄 Refrescar Token

Cuando el access token expire (24 horas), usa el refresh token para obtener uno nuevo.

### Endpoint

```
POST /api/token/refresh/
```

### Body

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Respuesta

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

---

## 📱 Integración con Laravel

### 1. Configuración

```php
// config/bingo.php
return [
    'api_url' => env('BINGO_API_URL'),
    'api_key' => env('BINGO_API_KEY'),
    'api_secret' => env('BINGO_API_SECRET'),
];

// .env
BINGO_API_URL=http://localhost:8000/api/multi-tenant/
BINGO_API_KEY=tu-api-key
BINGO_API_SECRET=tu-api-secret
```

### 2. Servicio de Autenticación

```php
// app/Services/BingoAuthService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Cache;

class BingoAuthService
{
    protected $apiUrl;
    protected $apiKey;
    protected $apiSecret;
    
    public function __construct()
    {
        $this->apiUrl = rtrim(config('bingo.api_url'), '/');
        $this->apiKey = config('bingo.api_key');
        $this->apiSecret = config('bingo.api_secret');
    }
    
    public function getAccessToken()
    {
        // Intentar obtener token del cache
        $token = Cache::get('bingo_access_token');
        
        if ($token) {
            return $token;
        }
        
        // Obtener nuevo token
        $response = Http::post($this->apiUrl . '/../token/', [
            'api_key' => $this->apiKey,
            'api_secret' => $this->apiSecret
        ]);
        
        if ($response->successful()) {
            $data = $response->json();
            $token = $data['access'];
            
            // Cachear token por 23 horas (expira en 24)
            Cache::put('bingo_access_token', $token, now()->addHours(23));
            Cache::put('bingo_refresh_token', $data['refresh'], now()->addDays(6));
            
            return $token;
        }
        
        throw new \Exception('No se pudo obtener token de autenticación');
    }
    
    public function refreshToken()
    {
        $refreshToken = Cache::get('bingo_refresh_token');
        
        if (!$refreshToken) {
            // Si no hay refresh token, obtener uno nuevo
            return $this->getAccessToken();
        }
        
        $response = Http::post($this->apiUrl . '/../token/refresh/', [
            'refresh' => $refreshToken
        ]);
        
        if ($response->successful()) {
            $data = $response->json();
            $token = $data['access'];
            
            Cache::put('bingo_access_token', $token, now()->addHours(23));
            
            return $token;
        }
        
        // Si falla el refresh, obtener token nuevo
        Cache::forget('bingo_access_token');
        Cache::forget('bingo_refresh_token');
        
        return $this->getAccessToken();
    }
}
```

### 3. Servicio para hacer Requests

```php
// app/Services/BingoApiService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;

class BingoApiService
{
    protected $authService;
    protected $apiUrl;
    
    public function __construct(BingoAuthService $authService)
    {
        $this->authService = $authService;
        $this->apiUrl = rtrim(config('bingo.api_url'), '/');
    }
    
    protected function makeRequest($method, $endpoint, $data = null)
    {
        $token = $this->authService->getAccessToken();
        
        $http = Http::withHeaders([
            'Authorization' => "Bearer {$token}",
            'Accept' => 'application/json',
        ]);
        
        $response = $method === 'get' 
            ? $http->get($this->apiUrl . $endpoint)
            : $http->$method($this->apiUrl . $endpoint, $data);
        
        // Si el token expiró, refrescar y reintentar
        if ($response->status() === 401) {
            $token = $this->authService->refreshToken();
            
            $http = Http::withHeaders([
                'Authorization' => "Bearer {$token}",
                'Accept' => 'application/json',
            ]);
            
            $response = $method === 'get' 
                ? $http->get($this->apiUrl . $endpoint)
                : $http->$method($this->apiUrl . $endpoint, $data);
        }
        
        if ($response->failed()) {
            throw new \Exception('API request failed: ' . $response->body());
        }
        
        return $response->json();
    }
    
    public function getSessions()
    {
        return $this->makeRequest('get', '/sessions/');
    }
    
    public function createSession($data)
    {
        return $this->makeRequest('post', '/sessions/', $data);
    }
    
    public function drawBall($gameId)
    {
        return $this->makeRequest('post', "/games/{$gameId}/draw-ball/");
    }
}
```

### 4. Uso en Controladores

```php
// app/Http/Controllers/BingoController.php
namespace App\Http\Controllers;

use App\Services\BingoApiService;

class BingoController extends Controller
{
    protected $bingoApi;
    
    public function __construct(BingoApiService $bingoApi)
    {
        $this->bingoApi = $bingoApi;
    }
    
    public function index()
    {
        $sessions = $this->bingoApi->getSessions();
        return view('bingo.sessions', compact('sessions'));
    }
    
    public function drawBall($gameId)
    {
        $result = $this->bingoApi->drawBall($gameId);
        return response()->json($result);
    }
}
```

---

## 📱 Integración con Vue.js

### 1. Configuración Axios

```javascript
// src/plugins/axios.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.VUE_APP_BINGO_API_URL || 'http://localhost:8000/api/multi-tenant/',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para agregar el token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('bingo_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Interceptor para manejar errores 401
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('bingo_refresh_token')
        const { data } = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken
        })
        
        localStorage.setItem('bingo_access_token', data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh falló, redirigir a login
        localStorage.removeItem('bingo_access_token')
        localStorage.removeItem('bingo_refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

### 2. Servicio de Autenticación

```javascript
// src/services/auth.service.js
import axios from 'axios'

const API_URL = process.env.VUE_APP_BINGO_API_URL || 'http://localhost:8000'

class AuthService {
  async login(apiKey, apiSecret) {
    const response = await axios.post(`${API_URL}/api/token/`, {
      api_key: apiKey,
      api_secret: apiSecret
    })
    
    if (response.data.access) {
      localStorage.setItem('bingo_access_token', response.data.access)
      localStorage.setItem('bingo_refresh_token', response.data.refresh)
      localStorage.setItem('bingo_operator', JSON.stringify(response.data.operator))
    }
    
    return response.data
  }
  
  logout() {
    localStorage.removeItem('bingo_access_token')
    localStorage.removeItem('bingo_refresh_token')
    localStorage.removeItem('bingo_operator')
  }
  
  getOperator() {
    const operator = localStorage.getItem('bingo_operator')
    return operator ? JSON.parse(operator) : null
  }
  
  isAuthenticated() {
    return !!localStorage.getItem('bingo_access_token')
  }
}

export default new AuthService()
```

### 3. Uso en Componentes

```vue
<template>
  <div>
    <h2>Sesiones de Bingo</h2>
    <div v-for="session in sessions" :key="session.id">
      {{ session.name }}
    </div>
  </div>
</template>

<script>
import apiClient from '@/plugins/axios'

export default {
  data() {
    return {
      sessions: []
    }
  },
  async mounted() {
    try {
      const response = await apiClient.get('/sessions/')
      this.sessions = response.data.results
    } catch (error) {
      console.error('Error loading sessions:', error)
    }
  }
}
</script>
```

---

## ❌ Errores de Autenticación

### Sin Token (401)

```json
{
  "error": "No autorizado",
  "message": "No tienes permisos para acceder a este recurso. Proporciona un token Bearer válido.",
  "detail": "Credenciales de autenticación no proporcionadas."
}
```

### Token Inválido (401)

```json
{
  "error": "No autorizado",
  "message": "No tienes permisos para acceder a este recurso. Proporciona un token Bearer válido.",
  "detail": "Token inválido"
}
```

### Token Expirado (401)

```json
{
  "error": "No autorizado",
  "message": "No tienes permisos para acceder a este recurso. Proporciona un token Bearer válido.",
  "detail": "Token expirado"
}
```

---

## 📊 Estructura del Token JWT

### Payload del Access Token

```json
{
  "token_type": "access",
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "uuid-unico",
  "operator_id": "uuid-operador",
  "operator_code": "mibingo",
  "operator_name": "Mi Bingo",
  "api_key_id": "uuid-api-key",
  "permission_level": "write"
}
```

### Duración de Tokens

| Token | Duración |
|-------|----------|
| Access Token | 24 horas |
| Refresh Token | 7 días |

---

## 🔒 Seguridad

### Mejores Prácticas

✅ **Almacenar tokens de forma segura**  
   - Laravel: Cache con TTL  
   - Vue: localStorage o Vuex  
   - WhatsApp/Telegram: Variables de sesión

✅ **Usar HTTPS en producción**  
   - Los tokens viajan en headers HTTP

✅ **Renovar tokens antes de expirar**  
   - Implementar refresh automático

✅ **Manejar errores 401**  
   - Refresh token automático  
   - Logout si el refresh falla

✅ **No compartir access tokens**  
   - Cada cliente tiene su propio token

---

## ✅ Estado del Sistema

✅ **JWT configurado** - djangorestframework-simplejwt  
✅ **Todos los endpoints protegidos** - Requieren Bearer Token  
✅ **Mensajes claros de error** - 401 con explicación  
✅ **Refresh token implementado** - Renovación automática  
✅ **Backend personalizado** - Compatible con modelo Operator  

---

¡El sistema de autenticación JWT está completamente funcional y listo para producción! 🔐✨
