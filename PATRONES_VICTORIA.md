# 🎯 Sistema de Patrones de Victoria

## 📋 Descripción

El sistema de patrones de victoria permite a los operadores configurar diferentes formas de ganar en sus partidas de bingo. Incluye patrones clásicos, especiales y la posibilidad de crear patrones personalizados.

---

## 🎲 Patrones Disponibles

### Patrones Clásicos

| Patrón | Código | Compatible | Premio | Descripción |
|--------|--------|------------|--------|-------------|
| **Línea Horizontal** | `horizontal_line` | Todos | x1.0 | Completar una fila horizontal |
| **Línea Vertical** | `vertical_line` | Todos | x1.0 | Completar una columna vertical |
| **Línea Diagonal** | `diagonal_line` | 75 bolas | x1.0 | Completar una diagonal |
| **Cartón Lleno** | `full_card` | Todos | x2.0 | Marcar todos los números |

### Patrones Especiales

| Patrón | Código | Compatible | Premio | Descripción |
|--------|--------|------------|--------|-------------|
| **Cuatro Esquinas** | `four_corners` | 75 bolas | x1.0 | Marcar las 4 esquinas |
| **X o Cruz** | `x_pattern` | 75 bolas | x1.5 | Formar una X con las diagonales |
| **Letra L** | `letter_l` | 75 bolas | x1.0 | Primera columna + última fila |
| **Letra T** | `letter_t` | 75 bolas | x1.0 | Primera fila + columna central |
| **Jackpot Rápido** | `blackout_jackpot` | 75 bolas | x5.0 | Bingo en < 50 bolas |

---

## 📡 API Endpoints

### Listar Patrones Disponibles

```http
GET /api/patterns/
GET /api/patterns/?category=classic
GET /api/patterns/?compatible_with=75
GET /api/patterns/?is_system=true
```

**Respuesta:**
```json
{
  "count": 9,
  "results": [
    {
      "id": "uuid",
      "name": "Línea Horizontal",
      "code": "horizontal_line",
      "description": "Completa una fila horizontal de números",
      "category": "classic",
      "category_display": "Clásico",
      "compatible_with": "all",
      "compatible_display": "Todos",
      "prize_multiplier": "1.00",
      "has_jackpot": false,
      "is_active": true,
      "is_system": true
    }
  ]
}
```

### Obtener Patrones para un Tipo de Bingo

```http
GET /api/patterns/available/75/
GET /api/patterns/available/90/
```

**Respuesta:**
```json
{
  "bingo_type": "75",
  "patterns": [...],
  "total": 9
}
```

### Configurar Patrones en una Sesión

```http
POST /api/patterns/sessions/{session_id}/configure/
Content-Type: application/json

{
  "pattern_codes": [
    "horizontal_line",
    "vertical_line",
    "full_card",
    "four_corners"
  ]
}
```

**Respuesta:**
```json
{
  "message": "Patrones configurados exitosamente",
  "session": {
    "id": "uuid",
    "name": "Bingo de la Tarde"
  },
  "patterns": [...]
}
```

### Obtener Patrones de una Sesión

```http
GET /api/patterns/sessions/{session_id}/patterns/
```

**Respuesta:**
```json
{
  "session": {
    "id": "uuid",
    "name": "Bingo de la Tarde",
    "bingo_type": "75"
  },
  "patterns": [...],
  "total_patterns": 4
}
```

### Verificar Ganador con Patrones

```http
POST /api/patterns/check-winner/
Content-Type: application/json

{
  "card_id": "uuid",
  "drawn_numbers": [1, 2, 3, 4, 5, ...],
  "check_all_patterns": false
}
```

**Respuesta:**
```json
{
  "is_winner": true,
  "winning_patterns": [
    {
      "is_winner": true,
      "pattern_name": "Línea Horizontal",
      "pattern_code": "horizontal_line",
      "prize_multiplier": 1.0,
      "is_jackpot": false,
      "balls_drawn": 25
    }
  ],
  "total_prize_multiplier": 1.0,
  "jackpot_won": false,
  "card_id": "uuid",
  "player_info": {
    "id": "uuid",
    "username": "Juan"
  },
  "balls_drawn": 25
}
```

### Verificar Todos los Cartones en una Partida

```http
POST /api/patterns/games/{game_id}/check-all-cards/
```

**Respuesta:**
```json
{
  "game_id": "uuid",
  "balls_drawn": 35,
  "winners_found": 2,
  "winners": [
    {
      "card_id": "uuid",
      "card_number": 1,
      "player": {
        "id": "uuid",
        "username": "Juan"
      },
      "pattern": {
        "is_winner": true,
        "pattern_name": "Línea Horizontal",
        "prize_multiplier": 1.0
      }
    }
  ]
}
```

---

## 💻 Ejemplos de Uso

### Laravel - Configurar Patrones en una Sesión

```php
// app/Services/BingoPatternService.php

public function configureSessionPatterns($sessionId, array $patterns)
{
    $token = $this->authService->getAccessToken();
    
    $response = Http::withHeaders([
        'Authorization' => "Bearer {$token}"
    ])->post(
        $this->apiUrl . "/patterns/sessions/{$sessionId}/configure/",
        ['pattern_codes' => $patterns]
    );
    
    return $response->json();
}

// Uso
$patterns = [
    'horizontal_line',
    'vertical_line',
    'full_card',
    'four_corners'
];

$result = $patternService->configureSessionPatterns(
    $sessionId,
    $patterns
);
```

### Vue.js - Seleccionar Patrones para una Sesión

```vue
<template>
  <div class="pattern-selector">
    <h3>Seleccionar Patrones de Victoria</h3>
    
    <div v-for="pattern in availablePatterns" :key="pattern.id">
      <label>
        <input 
          type="checkbox" 
          v-model="selectedPatterns"
          :value="pattern.code"
        />
        {{ pattern.name }}
        <span class="prize">x{{ pattern.prize_multiplier }}</span>
      </label>
      <p class="description">{{ pattern.description }}</p>
    </div>
    
    <button @click="savePatterns">Guardar Configuración</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      availablePatterns: [],
      selectedPatterns: []
    }
  },
  
  async mounted() {
    // Cargar patrones disponibles
    const { data } = await this.$http.get(
      `/api/patterns/available/${this.bingoType}/`
    )
    this.availablePatterns = data.patterns
  },
  
  methods: {
    async savePatterns() {
      await this.$http.post(
        `/api/patterns/sessions/${this.sessionId}/configure/`,
        { pattern_codes: this.selectedPatterns }
      )
      
      this.$message.success('Patrones configurados')
    }
  }
}
</script>
```

### WhatsApp Bot - Verificar Ganador

```python
def check_winner_after_ball_drawn(game_id):
    """Verifica ganadores después de cada bola extraída"""
    
    response = requests.post(
        f'{API_URL}/api/patterns/games/{game_id}/check-all-cards/',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    data = response.json()
    
    if data['winners_found'] > 0:
        for winner in data['winners']:
            player = winner['player']
            pattern = winner['pattern']
            
            # Enviar mensaje por WhatsApp
            message = f"""
🎉 ¡BINGO! ¡TENEMOS UN GANADOR!

🏆 Jugador: {player['username']}
🎯 Patrón: {pattern['pattern_name']}
💰 Premio: x{pattern['prize_multiplier']}
🎰 Jackpot: {'¡SÍ!' if pattern.get('is_jackpot') else 'No'}
            """.strip()
            
            send_whatsapp_message(player_phone, message)
    
    return data
```

---

## 🎮 Flujo Completo de Uso

### 1. Operador Crea Sesión y Configura Patrones

```bash
# Crear sesión
POST /api/multi-tenant/sessions/
{
  "operator": "uuid",
  "name": "Bingo de la Noche",
  "bingo_type": "75",
  "total_cards": 100
}

# Configurar patrones
POST /api/patterns/sessions/{session_id}/configure/
{
  "pattern_codes": [
    "horizontal_line",
    "vertical_line",
    "diagonal_line",
    "full_card",
    "four_corners",
    "x_pattern"
  ]
}
```

### 2. Durante el Juego - Verificar Ganadores

```bash
# Después de cada bola extraída
POST /api/patterns/games/{game_id}/check-all-cards/
```

### 3. Verificar Cartón Específico

```bash
POST /api/patterns/check-winner/
{
  "card_id": "uuid",
  "drawn_numbers": [1, 2, 3, ...]
}
```

---

## 🏆 Sistema de Premios

### Multiplicadores

Los patrones tienen multiplicadores de premio:

- **Línea Simple**: x1.0
- **X o Cruz**: x1.5
- **Cartón Lleno**: x2.0
- **Jackpot Rápido**: x5.0 (x10.0 con jackpot)

### Jackpot Progresivo

El patrón `blackout_jackpot` otorga un premio especial si se completa el cartón lleno en menos de 50 bolas:

- **< 50 bolas**: x10.0 (jackpot ganado)
- **≥ 50 bolas**: x5.0 (solo premio base)

### Múltiples Ganadores

Si se configura `check_all_patterns: true`, un cartón puede ganar con múltiples patrones simultáneamente, acumulando multiplicadores.

---

## 🛠️ Crear Patrones Personalizados

### Endpoint

```http
POST /api/patterns/create/
Content-Type: application/json

{
  "operator": "uuid",
  "name": "Patrón Especial",
  "code": "custom_special",
  "description": "Mi patrón personalizado",
  "category": "custom",
  "compatible_with": "75",
  "pattern_type": "custom",
  "pattern_data": {
    "positions": [[0,0], [1,1], [2,2]]
  },
  "prize_multiplier": 3.0
}
```

---

## 📊 Estructura del Modelo

```python
class WinningPattern:
    id: UUID
    operator: ForeignKey (opcional)
    name: str
    code: str (único)
    description: str
    category: 'classic' | 'special' | 'custom'
    compatible_with: 'all' | '75' | '85' | '90'
    pattern_type: str
    pattern_data: JSON
    prize_multiplier: Decimal
    has_jackpot: bool
    jackpot_max_balls: int (opcional)
    is_active: bool
    is_system: bool
```

---

## 🔒 Permisos y Limitaciones

- **Patrones del Sistema**: No se pueden modificar ni eliminar
- **Patrones Personalizados**: Solo el operador propietario puede modificarlos
- **Compatibilidad**: Patrones para 75 bolas no funcionan en bingos de 90 bolas

---

## 🧪 Testing

### Inicializar Patrones del Sistema

```bash
python initialize_patterns.py
```

### Probar Validación de Patrones

```bash
python demo_patterns.py
```

---

## ✅ Estado del Sistema

✅ **9 patrones predefinidos** creados  
✅ **4 patrones clásicos** implementados  
✅ **5 patrones especiales** implementados  
✅ **Sistema de jackpot** funcional  
✅ **Verificación automática** en partidas  
✅ **Endpoints REST** completos  
✅ **Integración con sesiones** lista  

---

¡El sistema de patrones está completamente implementado y listo para producción! 🎯✨
