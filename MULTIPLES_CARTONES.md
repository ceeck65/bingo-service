# 🎲 Múltiples Cartones por Jugador

## 📋 Resumen

Los jugadores ahora pueden seleccionar y jugar con **múltiples cartones** en una misma sesión de bingo, aumentando sus probabilidades de ganar.

---

## ⚙️ Configuración

### Límite por Operador

Cada operador define el máximo de cartones que un jugador puede tener:

```python
operator.max_cards_per_player = 5  # Ejemplo: máximo 5 cartones
```

Este límite se valida automáticamente en cada selección.

---

## 🎯 Flujo de Uso

### 1. Jugador Ve Cartones Disponibles

```bash
GET /api/multi-tenant/sessions/{session-id}/available-cards/
```

**Respuesta:**
```json
{
  "session": {
    "name": "Sesión Matutina",
    "total_cards": 100,
    "available_count": 95
  },
  "cards": [
    {"id": "card-1", "card_number": 1, "numbers": [...]},
    {"id": "card-2", "card_number": 2, "numbers": [...]},
    ...
  ]
}
```

### 2. Jugador Selecciona Múltiples Cartones

**Opción A: Seleccionar uno por uno**

```bash
POST /api/multi-tenant/cards/select/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_id": "card-uuid-1"
}
```

**Opción B: Seleccionar varios a la vez (Recomendado)**

```bash
POST /api/multi-tenant/cards/select-multiple/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_ids": [
    "card-uuid-1",
    "card-uuid-2",
    "card-uuid-3"
  ]
}
```

**Respuesta:**
```json
{
  "message": "3 cartones reservados exitosamente",
  "reserved_cards": [...],
  "total_cards": 3
}
```

### 3. Ver Cartones del Jugador

```bash
GET /api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/
```

**Respuesta:**
```json
{
  "player": {
    "id": "player-uuid",
    "username": "juan123"
  },
  "summary": {
    "total": 3,
    "available": 0,
    "reserved": 3,
    "sold": 0
  },
  "cards": [
    {
      "id": "card-uuid-1",
      "card_number": 15,
      "status": "reserved",
      "numbers": [[7, 26, "FREE", 53, 66], ...]
    },
    ...
  ]
}
```

### 4. Confirmar Compra

**Opción A: Confirmar uno por uno**

```bash
POST /api/multi-tenant/cards/confirm-purchase/
{
  "card_id": "card-uuid-1"
}
```

**Opción B: Confirmar todos a la vez (Recomendado)**

```bash
POST /api/multi-tenant/cards/confirm-multiple-purchase/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid"
}
```

**Respuesta:**
```json
{
  "message": "3 cartones confirmados exitosamente",
  "confirmed_cards": [...],
  "total_cost": 15.00,
  "total_cards": 3
}
```

---

## 🔒 Validaciones

### Al Seleccionar Múltiples Cartones

✅ **Límite del operador** - No exceder `max_cards_per_player`  
✅ **Cartones disponibles** - Todos deben estar en estado `available`  
✅ **Pertenencia a sesión** - Todos deben ser de la misma sesión  
✅ **Jugador inscrito** - El jugador debe estar inscrito en la sesión  

### Ejemplo de Validación

```python
# Configuración
operator.max_cards_per_player = 5

# Jugador ya tiene 3 cartones
# Intenta seleccionar 3 más
# Total: 3 + 3 = 6 > 5 ❌

# Error:
{
  "error": "El jugador puede tener máximo 5 cartones. Ya tiene 3 y está intentando agregar 3"
}
```

---

## 💡 Casos de Uso

### Caso 1: Jugador Casual

```
Jugador selecciona: 1 cartón
Probabilidad de ganar: Baja
Inversión: $5.00
```

### Caso 2: Jugador Regular

```
Jugador selecciona: 3 cartones
Probabilidad de ganar: Media
Inversión: $15.00
```

### Caso 3: Jugador VIP

```
Jugador selecciona: 5 cartones (máximo)
Probabilidad de ganar: Alta
Inversión: $25.00
```

---

## 🌐 Integración con Laravel

### Servicio de Bingo

```php
// app/Services/BingoService.php

public function selectMultipleCards($sessionId, $playerId, array $cardIds)
{
    return Http::post($this->apiUrl . 'cards/select-multiple/', [
        'session_id' => $sessionId,
        'player_id' => $playerId,
        'card_ids' => $cardIds
    ])->json();
}

public function getPlayerCards($sessionId, $playerId)
{
    return Http::get(
        $this->apiUrl . "sessions/{$sessionId}/player/{$playerId}/cards/"
    )->json();
}

public function confirmAllCards($sessionId, $playerId)
{
    return Http::post($this->apiUrl . 'cards/confirm-multiple-purchase/', [
        'session_id' => $sessionId,
        'player_id' => $playerId
    ])->json();
}
```

### Componente Vue

```vue
<template>
  <div class="card-selector">
    <h2>Selecciona tus Cartones ({{ selectedCards.length }}/{{ maxCards }})</h2>
    
    <div class="cards-grid">
      <div 
        v-for="card in availableCards" 
        :key="card.id"
        class="card-item"
        :class="{ 
          selected: isSelected(card.id),
          disabled: !canSelect
        }"
        @click="toggleCard(card)"
      >
        <div class="card-number">#{{ card.card_number }}</div>
        <div class="card-preview">
          <!-- Preview del cartón -->
        </div>
        <div class="card-checkbox">
          <input 
            type="checkbox" 
            :checked="isSelected(card.id)"
            :disabled="!canSelect && !isSelected(card.id)"
          />
        </div>
      </div>
    </div>
    
    <div class="summary">
      <p>Cartones seleccionados: {{ selectedCards.length }}</p>
      <p>Total: ${{ totalCost }}</p>
    </div>
    
    <button 
      @click="confirmSelection"
      :disabled="selectedCards.length === 0"
      class="btn-confirm"
    >
      Confirmar {{ selectedCards.length }} Cartones
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      availableCards: [],
      selectedCards: [],
      maxCards: 5
    }
  },
  
  computed: {
    canSelect() {
      return this.selectedCards.length < this.maxCards;
    },
    totalCost() {
      return this.selectedCards.length * this.session.entry_fee;
    }
  },
  
  methods: {
    toggleCard(card) {
      const index = this.selectedCards.findIndex(c => c.id === card.id);
      
      if (index >= 0) {
        // Deseleccionar
        this.selectedCards.splice(index, 1);
      } else {
        // Seleccionar si no se alcanzó el límite
        if (this.canSelect) {
          this.selectedCards.push(card);
        }
      }
    },
    
    isSelected(cardId) {
      return this.selectedCards.some(c => c.id === cardId);
    },
    
    async confirmSelection() {
      try {
        const cardIds = this.selectedCards.map(c => c.id);
        
        await axios.post('/api/bingo/cards/select-multiple', {
          session_id: this.session.id,
          player_id: this.$auth.user.id,
          card_ids: cardIds
        });
        
        this.$toast.success('Cartones reservados. Procede al pago');
        this.$router.push('/checkout');
      } catch (error) {
        this.$toast.error('Error al seleccionar cartones');
      }
    }
  }
}
</script>
```

---

## 📱 Integración con WhatsApp

### Comandos

```
/cartones - Ver cartones disponibles
/seleccionar 5,12,23 - Seleccionar cartones #5, #12 y #23
/miscartas - Ver mis cartones
/confirmar - Confirmar compra de todos los cartones
```

### Implementación

```php
// app/Services/WhatsAppBingoService.php

private function handleSelectCommand($player, $message)
{
    // Ejemplo: /seleccionar 5,12,23
    preg_match('/\/seleccionar (.+)/', $message, $matches);
    $numbers = explode(',', trim($matches[1]));
    
    $session = $this->getActiveSession();
    $cards = $this->findCardsByNumbers($session['id'], $numbers);
    
    if (count($cards) !== count($numbers)) {
        return $this->sendWhatsApp(
            $player['phone'],
            "❌ Algunos cartones no están disponibles"
        );
    }
    
    $cardIds = array_column($cards, 'id');
    
    $result = $this->bingoService->selectMultipleCards(
        $session['id'],
        $player['id'],
        $cardIds
    );
    
    $message = "✅ *{$result['total_cards']} Cartones Reservados*\n\n";
    
    foreach ($result['reserved_cards'] as $card) {
        $message .= "📋 Cartón #{$card['card_number']}\n";
    }
    
    $message .= "\n💰 Total: \${$result['total_cost']}\n";
    $message .= "\n💳 Envía el comprobante para confirmar";
    
    return $this->sendWhatsApp($player['phone'], $message);
}

private function confirmAllCards($player)
{
    $session = $this->getActiveSession();
    
    $result = $this->bingoService->confirmAllCards(
        $session['id'],
        $player['id']
    );
    
    $message = "✅ *Compra Confirmada*\n\n";
    $message .= "Cartones confirmados: {$result['total_cards']}\n";
    $message .= "Total pagado: \${$result['total_cost']}\n\n";
    $message .= "🎲 ¡Buena suerte en la partida!";
    
    return $this->sendWhatsApp($player['phone'], $message);
}
```

---

## 📊 Estadísticas

### Por Jugador

```bash
GET /api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/
```

```json
{
  "summary": {
    "total": 5,
    "available": 0,
    "reserved": 0,
    "sold": 5
  },
  "cards": [...]
}
```

### Por Sesión

```bash
GET /api/multi-tenant/sessions/{session-id}/statistics/
```

Incluye información sobre cuántos jugadores tienen múltiples cartones.

---

## 🧪 Probar la Funcionalidad

```bash
# Demo completo
python3 demo_multiple_cards.py

# Test de la API
curl -X POST http://localhost:8000/api/multi-tenant/cards/select-multiple/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "card_ids": ["card-1", "card-2", "card-3"]
  }'
```

---

## 💡 Ventajas

### Para Jugadores
- ✅ Mayor probabilidad de ganar
- ✅ Más diversión con múltiples cartones
- ✅ Selección en un solo paso
- ✅ Confirmación de compra en bloque

### Para Operadores
- ✅ Mayor ingreso por jugador
- ✅ Control de límites
- ✅ Mejor experiencia de usuario
- ✅ Optimización del proceso

### Para el Sistema
- ✅ APIs eficientes
- ✅ Validaciones robustas
- ✅ Escalable
- ✅ Trazabilidad completa

---

## 🎮 Ejemplo Completo

```python
# 1. Operador configura límite
operator.max_cards_per_player = 5

# 2. Jugador selecciona 3 cartones
select_multiple_cards(
    session_id="...",
    player_id="...",
    card_ids=["card-1", "card-2", "card-3"]
)

# 3. Sistema valida
# ✅ 3 cartones < 5 (límite) ✓
# ✅ Todos los cartones están disponibles ✓
# ✅ Jugador está inscrito ✓

# 4. Cartones reservados
# Estado: available → reserved

# 5. Jugador confirma compra
confirm_multiple_cards_purchase(
    session_id="...",
    player_id="..."
)

# 6. Cartones confirmados
# Estado: reserved → sold
# Total: $15.00 (3 × $5.00)
```

---

## 🔧 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/cards/select-multiple/` | Seleccionar múltiples cartones |
| GET | `/sessions/{id}/player/{id}/cards/` | Ver cartones del jugador |
| POST | `/cards/confirm-multiple-purchase/` | Confirmar todos los cartones |

---

## ✅ Checklist de Implementación

- [x] Endpoint de selección múltiple
- [x] Validación de límites por operador
- [x] Endpoint para ver cartones del jugador
- [x] Confirmación en bloque
- [x] Contador de cartones en PlayerSession
- [x] Demo funcional
- [x] Documentación actualizada
- [x] Ejemplos de integración (Laravel, WhatsApp)

---

¡Los jugadores ahora pueden disfrutar con múltiples cartones y aumentar sus probabilidades de ganar! 🎲✨
