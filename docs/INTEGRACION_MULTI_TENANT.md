# 🌐 Guía de Integración Multi-Tenant

## 📋 Resumen

Este microservicio de bingo ha sido diseñado específicamente para ser consumido por:
- **Laravel/Vue** (Web App)
- **WhatsApp Business API**
- **Telegram Bot API**
- **Sistemas Whitelabel** con múltiples operadores

## 🏗️ Arquitectura Multi-Tenant

### Conceptos Clave

1. **Operadores/Marcas**: Cada marca tiene su propio espacio aislado
2. **Jugadores**: Pertenecientes a un operador específico
3. **Sesiones**: Partidas organizadas por operador
4. **Aislamiento**: Cada operador solo ve sus propios datos

### Estructura de Datos

```
Operador (BingoMax)
├── Jugadores
│   ├── Juan (WhatsApp: +1234567890)
│   ├── María (Telegram: @maria_max)
│   └── Carlos (Email: carlos@bingomax.com)
├── Sesiones
│   ├── Sesión Matutina (75 bolas)
│   └── Gran Torneo (85 bolas)
└── Cartones
    ├── Cartones de Juan
    ├── Cartones de María
    └── Cartones de Carlos

Operador (LuckyBingo)
├── Jugadores
│   ├── Ana (WhatsApp: +2345678901)
│   └── Luis (Telegram: @luis_lucky)
├── Sesiones
│   └── Lucky Hour (75 bolas)
└── Cartones
    ├── Cartones de Ana
    └── Cartones de Luis
```

## 🔗 Integración con Laravel/Vue

### Configuración Base

```php
// config/bingo.php
return [
    'api_url' => env('BINGO_API_URL', 'http://localhost:8000/api/multi-tenant/'),
    'api_key' => env('BINGO_API_KEY'),
    'operator_code' => env('BINGO_OPERATOR_CODE', 'bingomax'),
];
```

### Servicio de Bingo

```php
// app/Services/BingoService.php
class BingoService
{
    protected $apiUrl;
    protected $operatorCode;
    
    public function __construct()
    {
        $this->apiUrl = config('bingo.api_url');
        $this->operatorCode = config('bingo.operator_code');
    }
    
    public function getActiveSessions()
    {
        $response = Http::get("{$this->apiUrl}sessions/", [
            'operator' => $this->getOperatorId(),
            'status' => 'active'
        ]);
        
        return $response->json();
    }
    
    public function createPlayer($data)
    {
        return Http::post("{$this->apiUrl}players/", [
            'operator' => $this->getOperatorId(),
            'username' => $data['username'],
            'email' => $data['email'],
            'phone' => $data['phone']
        ]);
    }
    
    public function joinSession($sessionId, $playerId, $cardsCount = 1)
    {
        return Http::post("{$this->apiUrl}sessions/join/", [
            'session_id' => $sessionId,
            'player_id' => $playerId,
            'cards_count' => $cardsCount
        ]);
    }
    
    private function getOperatorId()
    {
        // Obtener ID del operador basado en el código
        $response = Http::get("{$this->apiUrl}operators/", [
            'code' => $this->operatorCode
        ]);
        
        $operators = $response->json()['results'];
        return $operators[0]['id'] ?? null;
    }
}
```

### Componente Vue para Sesiones

```vue
<!-- resources/js/components/BingoSessions.vue -->
<template>
  <div class="bingo-sessions">
    <h2>Sesiones Activas</h2>
    <div v-for="session in sessions" :key="session.id" class="session-card">
      <h3>{{ session.name }}</h3>
      <p>{{ session.description }}</p>
      <p>Tipo: {{ session.bingo_type }} bolas</p>
      <p>Entrada: ${{ session.entry_fee }}</p>
      <p>Jugadores: {{ session.players_count }}/{{ session.max_players }}</p>
      <button @click="joinSession(session.id)" :disabled="!canJoin(session)">
        Unirse
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      sessions: [],
      player: null
    }
  },
  
  async mounted() {
    await this.loadSessions();
    await this.loadPlayer();
  },
  
  methods: {
    async loadSessions() {
      try {
        const response = await axios.get('/api/bingo/sessions');
        this.sessions = response.data.results;
      } catch (error) {
        console.error('Error cargando sesiones:', error);
      }
    },
    
    async joinSession(sessionId) {
      try {
        await axios.post('/api/bingo/sessions/join', {
          session_id: sessionId,
          player_id: this.player.id,
          cards_count: 3
        });
        
        this.$toast.success('Te has unido a la sesión exitosamente');
        await this.loadSessions();
      } catch (error) {
        this.$toast.error('Error al unirse a la sesión');
      }
    },
    
    canJoin(session) {
      return session.players_count < session.max_players && 
             session.status === 'scheduled';
    }
  }
}
</script>
```

## 📱 Integración con WhatsApp

### Webhook para Mensajes

```php
// routes/web.php
Route::post('/whatsapp/webhook', [WhatsAppController::class, 'webhook']);

// app/Http/Controllers/WhatsAppController.php
class WhatsAppController extends Controller
{
    public function webhook(Request $request)
    {
        $message = $request->input('messages.0');
        $phone = $message['from'];
        $text = $message['text']['body'] ?? '';
        
        // Registrar jugador si no existe
        $player = $this->registerOrGetPlayer($phone, $text);
        
        // Procesar comando
        $this->processCommand($player, $text);
    }
    
    private function registerOrGetPlayer($phone, $username)
    {
        $bingoService = app(BingoService::class);
        
        // Intentar obtener jugador existente
        $existingPlayer = $this->findPlayerByPhone($phone);
        if ($existingPlayer) {
            return $existingPlayer;
        }
        
        // Crear nuevo jugador
        $response = $bingoService->registerPlayerByPhone([
            'operator_code' => config('bingo.operator_code'),
            'phone' => $phone,
            'username' => $username ?: 'user_' . substr($phone, -4)
        ]);
        
        return $response->json()['player'];
    }
    
    private function processCommand($player, $text)
    {
        $command = strtolower(trim($text));
        
        switch ($command) {
            case 'sesiones':
                $this->sendActiveSessions($player);
                break;
            case 'unirme':
                $this->showJoinOptions($player);
                break;
            case 'mis cartones':
                $this->showPlayerCards($player);
                break;
            default:
                $this->sendWelcomeMessage($player);
        }
    }
    
    private function sendActiveSessions($player)
    {
        $sessions = app(BingoService::class)->getActiveSessions();
        
        $message = "🎯 *Sesiones Activas:*\n\n";
        foreach ($sessions['results'] as $session) {
            $message .= "🎲 *{$session['name']}*\n";
            $message .= "Tipo: {$session['bingo_type']} bolas\n";
            $message .= "Entrada: \${$session['entry_fee']}\n";
            $message .= "Jugadores: {$session['players_count']}/{$session['max_players']}\n\n";
        }
        
        $this->sendWhatsAppMessage($player['phone'], $message);
    }
}
```

### Comandos de WhatsApp

```
/sesiones - Ver sesiones activas
/unirme [id] - Unirse a una sesión
/mis cartones - Ver mis cartones
/estado - Ver mi estado
/ayuda - Mostrar ayuda
```

## 📱 Integración con Telegram

### Bot de Telegram

```php
// app/Services/TelegramBotService.php
class TelegramBotService
{
    protected $botToken;
    protected $apiUrl;
    
    public function __construct()
    {
        $this->botToken = config('telegram.bot_token');
        $this->apiUrl = "https://api.telegram.org/bot{$this->botToken}/";
    }
    
    public function handleUpdate($update)
    {
        $message = $update['message'];
        $chatId = $message['chat']['id'];
        $text = $message['text'] ?? '';
        $username = $message['from']['username'] ?? '';
        
        // Registrar jugador
        $player = $this->registerOrGetPlayer($chatId, $username);
        
        // Procesar comando
        $this->processCommand($player, $text, $chatId);
    }
    
    private function registerOrGetPlayer($telegramId, $username)
    {
        $bingoService = app(BingoService::class);
        
        // Buscar jugador existente
        $existingPlayer = $this->findPlayerByTelegram($telegramId);
        if ($existingPlayer) {
            return $existingPlayer;
        }
        
        // Crear nuevo jugador
        $response = $bingoService->registerPlayerByPhone([
            'operator_code' => config('bingo.operator_code'),
            'phone' => 'tg_' . $telegramId,
            'username' => $username ?: 'tg_user_' . $telegramId
        ]);
        
        // Vincular cuenta de Telegram
        $player = $response->json()['player'];
        $bingoService->linkSocialAccount([
            'player_id' => $player['id'],
            'telegram_id' => $telegramId
        ]);
        
        return $player;
    }
    
    private function processCommand($player, $text, $chatId)
    {
        $command = strtolower(trim($text));
        
        switch ($command) {
            case '/start':
                $this->sendWelcomeMessage($chatId);
                break;
            case '/sesiones':
                $this->sendActiveSessions($player, $chatId);
                break;
            case '/unirme':
                $this->showJoinOptions($player, $chatId);
                break;
            case '/micartones':
                $this->showPlayerCards($player, $chatId);
                break;
            default:
                $this->sendHelp($chatId);
        }
    }
    
    private function sendActiveSessions($player, $chatId)
    {
        $sessions = app(BingoService::class)->getActiveSessions();
        
        $message = "🎯 *Sesiones Activas:*\n\n";
        foreach ($sessions['results'] as $session) {
            $message .= "🎲 *{$session['name']}*\n";
            $message .= "Tipo: {$session['bingo_type']} bolas\n";
            $message .= "Entrada: \${$session['entry_fee']}\n";
            $message .= "Jugadores: {$session['players_count']}/{$session['max_players']}\n\n";
        }
        
        $this->sendMessage($chatId, $message);
    }
}
```

### Comandos de Telegram

```
/start - Iniciar bot
/sesiones - Ver sesiones activas
/unirme - Unirse a una sesión
/micartones - Ver mis cartones
/estado - Ver mi estado
/ayuda - Mostrar ayuda
```

## 🔧 Configuración de Operadores

### Crear Operador

```bash
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Bingo App",
    "code": "mibingoapp",
    "domain": "mibingoapp.com",
    "logo_url": "https://mibingoapp.com/logo.png",
    "primary_color": "#FF6B35",
    "secondary_color": "#F7931E",
    "allowed_bingo_types": ["75", "85", "90"],
    "max_cards_per_player": 5,
    "max_cards_per_game": 100
  }'
```

### Configurar Sesión

```bash
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "name": "Sesión Matutina",
    "description": "Sesión matutina con premios especiales",
    "bingo_type": "75",
    "max_players": 50,
    "entry_fee": 5.00,
    "scheduled_start": "2024-01-15T10:00:00Z",
    "winning_patterns": ["line", "diagonal", "corners", "full_card"],
    "created_by": "admin"
  }'
```

## 📊 Monitoreo y Estadísticas

### Estadísticas de Operador

```bash
curl http://localhost:8000/api/multi-tenant/operators/{operator_id}/statistics/
```

Respuesta:
```json
{
  "operator": {
    "id": "uuid",
    "name": "BingoMax",
    "code": "bingomax",
    "is_active": true
  },
  "players": {
    "total": 150,
    "active": 120,
    "inactive": 30
  },
  "sessions": {
    "total": 25,
    "active": 3,
    "by_status": {
      "scheduled": 5,
      "active": 3,
      "finished": 15,
      "cancelled": 2
    }
  },
  "cards": {
    "total": 450,
    "by_type": {
      "75": 200,
      "85": 150,
      "90": 100
    }
  }
}
```

### Estadísticas de Sesión

```bash
curl http://localhost:8000/api/multi-tenant/sessions/{session_id}/statistics/
```

## 🔒 Seguridad y Aislamiento

### Principios de Seguridad

1. **Aislamiento por Operador**: Cada operador solo puede acceder a sus propios datos
2. **Validación de Entrada**: Todas las entradas son validadas
3. **Límites Configurables**: Cada operador puede configurar sus límites
4. **Auditoría**: Todas las acciones son registradas

### Filtros de Seguridad

```php
// Middleware para validar operador
class OperatorMiddleware
{
    public function handle($request, Closure $next)
    {
        $operatorCode = $request->header('X-Operator-Code');
        
        if (!$operatorCode) {
            return response()->json(['error' => 'Operator code required'], 401);
        }
        
        // Validar que el operador existe y está activo
        $operator = Operator::where('code', $operatorCode)
                          ->where('is_active', true)
                          ->first();
        
        if (!$operator) {
            return response()->json(['error' => 'Invalid operator'], 401);
        }
        
        $request->merge(['operator' => $operator]);
        
        return $next($request);
    }
}
```

## 🚀 Deployment

### Variables de Entorno

```bash
# .env
BINGO_API_URL=http://localhost:8000/api/multi-tenant/
BINGO_OPERATOR_CODE=bingomax
WHATSAPP_TOKEN=your_whatsapp_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### Docker Compose

```yaml
version: '3.8'
services:
  bingo-api:
    image: bingo-service:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/bingo
    depends_on:
      - db
  
  web-app:
    image: laravel-vue-app:latest
    ports:
      - "80:80"
    environment:
      - BINGO_API_URL=http://bingo-api:8000/api/multi-tenant/
    depends_on:
      - bingo-api
```

## 📈 Escalabilidad

### Consideraciones de Rendimiento

1. **Base de Datos**: Usar índices en campos de búsqueda frecuente
2. **Cache**: Implementar Redis para sesiones y estadísticas
3. **Load Balancing**: Usar múltiples instancias del API
4. **CDN**: Para assets estáticos como logos de operadores

### Métricas Recomendadas

- Tiempo de respuesta de API
- Número de jugadores activos por operador
- Sesiones concurrentes
- Uso de memoria y CPU
- Errores por endpoint

## 🎯 Próximos Pasos

1. **Implementar WebSockets** para actualizaciones en tiempo real
2. **Agregar Notificaciones Push** para WhatsApp y Telegram
3. **Implementar Sistema de Premios** con pagos
4. **Agregar Analytics Avanzados** por operador
5. **Implementar Multi-idioma** para operadores internacionales

---

¡El sistema está listo para integrarse con cualquier plataforma y soportar múltiples operadores de forma segura y escalable! 🚀
