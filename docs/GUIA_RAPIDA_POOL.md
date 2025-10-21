# 🚀 Guía Rápida - Sistema de Pool de Cartones

## ✅ Migraciones Aplicadas

Las migraciones han sido creadas y aplicadas exitosamente:

```bash
python3 manage.py makemigrations
# Migrations for 'bingo':
#   - Create model Operator
#   - Create model BingoSession
#   - Create model Player
#   - Create model BingoCardExtended
#   - Create model PlayerSession

python3 manage.py migrate
# Migraciones aplicadas correctamente
```

## 🎯 Flujo de Uso Rápido

### 1. Crear Operador y Sesión

```bash
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Bingo",
    "code": "mibingo",
    "allowed_bingo_types": ["75", "85", "90"]
  }'

# Respuesta: { "id": "operator-uuid", ... }

curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "name": "Sesión de las 20:00",
    "bingo_type": "75",
    "total_cards": 100,
    "max_players": 50,
    "entry_fee": 5.00,
    "scheduled_start": "2024-01-15T20:00:00Z"
  }'

# Respuesta: { "id": "session-uuid", "total_cards": 100, "cards_generated": false, ... }
```

### 2. Generar Cartones

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "generate_now": true
  }'

# Respuesta: { "message": "100 cartones generados exitosamente", ... }
```

### 3. Ver Cartones Disponibles

```bash
curl http://localhost:8000/api/multi-tenant/sessions/session-uuid/available-cards/

# Respuesta:
# {
#   "session": {
#     "id": "session-uuid",
#     "name": "Sesión de las 20:00",
#     "total_cards": 100,
#     "available_count": 100
#   },
#   "cards": [
#     {
#       "id": "card-uuid-1",
#       "card_number": 1,
#       "status": "available",
#       "numbers": [[7, 26, 41, 53, 66], [15, 28, 44, 60, 65], ...]
#     },
#     ...
#   ]
# }
```

### 4. Jugador Selecciona Cartón

```bash
# Primero crear/obtener jugador
curl -X POST http://localhost:8000/api/multi-tenant/players/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "username": "juan123",
    "email": "juan@example.com"
  }'

# Respuesta: { "id": "player-uuid", ... }

# Luego seleccionar cartón
curl -X POST http://localhost:8000/api/multi-tenant/cards/select/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "card_id": "card-uuid-1"
  }'

# Respuesta: { "message": "Cartón reservado exitosamente", "card": {...} }
```

### 5. Confirmar Compra

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/confirm-purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "card-uuid-1"
  }'

# Respuesta: { "message": "Cartón vendido exitosamente", "card": {...} }
```

## 📊 Consultar Estado de Sesión

```bash
curl http://localhost:8000/api/multi-tenant/sessions/session-uuid/

# Respuesta:
# {
#   "id": "session-uuid",
#   "name": "Sesión de las 20:00",
#   "total_cards": 100,
#   "cards_generated": true,
#   "cards_count": 100,
#   "available_cards_count": 95,
#   "sold_cards_count": 5,
#   ...
# }
```

## 🔄 Reutilizar Cartones

```bash
# Crear nueva sesión que permite reutilización
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "name": "Sesión de las 22:00",
    "bingo_type": "75",
    "total_cards": 100,
    "allow_card_reuse": true,
    "scheduled_start": "2024-01-15T22:00:00Z"
  }'

# Reutilizar cartones de sesión anterior
curl -X POST http://localhost:8000/api/multi-tenant/cards/reuse/ \
  -H "Content-Type: application/json" \
  -d '{
    "new_session_id": "new-session-uuid",
    "old_session_id": "old-session-uuid"
  }'

# Respuesta: { "message": "100 cartones reutilizados exitosamente", ... }
```

## 🎮 Integración con Laravel

```php
// app/Services/BingoService.php

// Crear sesión
public function createSession($operatorId, $data) {
    return Http::post($this->apiUrl . 'sessions/', [
        'operator' => $operatorId,
        'name' => $data['name'],
        'bingo_type' => $data['type'],
        'total_cards' => $data['total_cards'],
        'entry_fee' => $data['price'],
        'scheduled_start' => $data['start_time']
    ])->json();
}

// Generar cartones
public function generateCards($sessionId) {
    return Http::post($this->apiUrl . 'cards/generate-for-session/', [
        'session_id' => $sessionId,
        'generate_now' => true
    ])->json();
}

// Obtener cartones disponibles
public function getAvailableCards($sessionId) {
    return Http::get($this->apiUrl . "sessions/{$sessionId}/available-cards/")
        ->json();
}

// Seleccionar cartón
public function selectCard($sessionId, $playerId, $cardId) {
    return Http::post($this->apiUrl . 'cards/select/', [
        'session_id' => $sessionId,
        'player_id' => $playerId,
        'card_id' => $cardId
    ])->json();
}

// Confirmar compra
public function confirmPurchase($cardId) {
    return Http::post($this->apiUrl . 'cards/confirm-purchase/', [
        'card_id' => $cardId
    ])->json();
}
```

## 📱 Integración con WhatsApp

```php
// app/Services/WhatsAppBingoService.php

public function processCommand($phone, $message) {
    $player = $this->getOrCreatePlayer($phone);
    
    if ($message === '/cartones') {
        $session = $this->getActiveSession();
        $cards = $this->bingoService->getAvailableCards($session['id']);
        
        $response = "🎲 Cartones disponibles: {$cards['session']['available_count']}\n\n";
        
        foreach (array_slice($cards['cards'], 0, 5) as $card) {
            $response .= "#{$card['card_number']} - ";
            $response .= "B: {$card['numbers'][0][0]}, ";
            $response .= "I: {$card['numbers'][0][1]}, ";
            $response .= "N: {$card['numbers'][0][2]}, ";
            $response .= "G: {$card['numbers'][0][3]}, ";
            $response .= "O: {$card['numbers'][0][4]}\n";
        }
        
        $response .= "\nEnvía /seleccionar {número} para elegir tu cartón";
        
        return $this->sendWhatsApp($phone, $response);
    }
    
    if (preg_match('/\/seleccionar (\d+)/', $message, $matches)) {
        $cardNumber = $matches[1];
        // Buscar el cartón por número
        // Reservarlo para el jugador
        // Enviar confirmación
    }
}
```

## 🧪 Probar el Sistema

```bash
# 1. Iniciar servidor
python3 manage.py runserver

# 2. Ejecutar demo
python3 demo_pool_cartones.py

# 3. Ejecutar test simple
python3 test_pool_simple.py
```

## 📚 Documentación Completa

- `SISTEMA_POOL_CARTONES.md` - Documentación detallada del sistema
- `INTEGRACION_MULTI_TENANT.md` - Guía de integración completa
- `README.md` - Documentación general

## ✅ Verificación

Para verificar que todo está funcionando:

```bash
# 1. Verificar migraciones
python3 manage.py showmigrations bingo

# 2. Verificar modelos en admin
python3 manage.py createsuperuser
# Luego accede a http://localhost:8000/admin/

# 3. Ver endpoints disponibles
curl http://localhost:8000/api/multi-tenant/
```

---

¡El sistema está listo para usar! 🎲✨

**Características principales:**
- ✅ Operador define cantidad de cartones
- ✅ Cartones pre-generados
- ✅ Jugadores seleccionan cartones existentes
- ✅ Sistema de estados (disponible/reservado/vendido)
- ✅ Reutilización de cartones entre sesiones
- ✅ APIs completas para integración
