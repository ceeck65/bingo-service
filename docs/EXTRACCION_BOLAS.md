# 🎲 Sistema de Extracción de Bolas

## 📋 Resumen

El sistema de extracción de bolas está optimizado para:
- ✅ **Evitar duplicados automáticamente**
- ✅ **Detectar juego completado**
- ✅ **Marcar partida como finalizada**
- ✅ **Retornar progreso y estadísticas**

---

## 🎯 Funcionamiento

### Algoritmo de Extracción

```
1. Obtener bolas ya extraídas
   ↓
2. Verificar si todas fueron extraídas
   ├─ SÍ → Retornar "Juego Completado"
   └─ NO → Continuar
       ↓
3. Intentar extraer bola aleatoria (máx 10 intentos)
   ├─ ¿Bola no extraída? → Usar esa bola
   └─ ¿Todas extraídas? → Buscar bola disponible
       ↓
4. Seleccionar de bolas disponibles
   ├─ ¿Hay disponibles? → Seleccionar aleatoriamente
   └─ ¿No hay? → Juego Completado
       ↓
5. Guardar bola extraída
   ↓
6. Actualizar estadísticas
   ├─ Total extraídas
   ├─ Bolas restantes
   ├─ Porcentaje de progreso
   └─ Estado del juego
```

---

## 📡 Endpoint

### Extraer Bola

```bash
POST /api/multi-tenant/games/draw-ball/
{
  "game_id": "game-uuid"
}
```

### Respuestas Posibles

#### Bola Extraída Exitosamente

```json
{
  "message": "Bola I-26 extraída",
  "ball_number": 26,
  "letter": "I",
  "display_name": "I-26",
  "color": "#FF6B35",
  "total_drawn": 15,
  "remaining_balls": 60,
  "game_status": "active",
  "progress_percentage": 20.0,
  "game": {
    "id": "game-uuid",
    "name": "Partida Principal",
    "is_active": true,
    ...
  }
}
```

**Campos de visualización:**
- `letter`: Letra del BINGO ("B", "I", "N", "G", "O")
- `display_name`: Nombre completo ("I-26")
- `color`: Color CSS para la letra ("#FF6B35")

**Colores por letra:**
- **B**: #0066CC (Azul)
- **I**: #FF6B35 (Naranja)
- **N**: #4CAF50 (Verde)
- **G**: #9C27B0 (Púrpura)
- **O**: #F44336 (Rojo)

#### Juego Completado

```json
{
  "message": "Juego completado - Todas las bolas han sido extraídas",
  "status": "finished",
  "total_drawn": 75,
  "max_balls": 75,
  "game": {
    "id": "game-uuid",
    "is_active": false,
    ...
  }
}
```

---

## 🔄 Comportamiento Automático

### Evitación de Duplicados

**Problema resuelto:**
- Antes: Si la bola ya fue extraída, retornaba error
- Ahora: Selecciona automáticamente otra bola disponible

**Algoritmo:**
1. Genera bola aleatoria
2. Si ya fue extraída, intenta de nuevo (hasta 10 veces)
3. Si después de 10 intentos sigue duplicada, selecciona de las disponibles
4. Siempre retorna una bola nueva

### Detección de Finalización

**Automático:**
- Cuenta bolas extraídas vs máximo del tipo de juego
- Si `total_drawn >= max_balls`: Marca juego como `is_active = False`
- Retorna mensaje "Juego completado"

**Máximos por tipo:**
- Bingo 75 bolas: 75
- Bingo 85 bolas: 85
- Bingo 90 bolas: 90

---

## 📊 Estadísticas en Tiempo Real

Cada extracción retorna:

```json
{
  "ball_number": 42,           // Bola extraída
  "total_drawn": 15,           // Total de bolas extraídas
  "remaining_balls": 60,       // Bolas que faltan
  "game_status": "active",     // Estado: active/finished
  "progress_percentage": 20.0  // Progreso del juego (%)
}
```

---

## 🌐 Integración con Laravel

### Servicio de Extracción

```php
// app/Services/BingoGameService.php

public function drawBall($gameId)
{
    $response = Http::post($this->apiUrl . 'games/draw-ball/', [
        'game_id' => $gameId
    ])->json();
    
    // Verificar si el juego se completó
    if ($response['game_status'] === 'finished') {
        // Notificar a todos los jugadores
        $this->notifyGameFinished($gameId);
        
        // Verificar todos los ganadores
        $this->checkAllWinners($gameId);
    }
    
    return $response;
}

public function autoDrawBalls($gameId, $count = 1, $interval = 3)
{
    for ($i = 0; $i < $count; $i++) {
        $result = $this->drawBall($gameId);
        
        // Si el juego se completó, detener
        if ($result['game_status'] === 'finished') {
            break;
        }
        
        // Esperar antes de la siguiente extracción
        if ($i < $count - 1) {
            sleep($interval);
        }
    }
}
```

### Componente Vue en Tiempo Real

```vue
<template>
  <div class="game-board">
    <h2>Bolas Extraídas</h2>
    
    <div class="progress">
      <div class="progress-bar" :style="{width: progress + '%'}">
        {{ drawnBalls.length }}/{{ maxBalls }}
      </div>
    </div>
    
    <div class="balls-grid">
      <div 
        v-for="ball in drawnBalls" 
        :key="ball.number"
        class="ball"
        :class="getBallClass(ball.number)"
      >
        {{ ball.number }}
      </div>
    </div>
    
    <div v-if="gameFinished" class="game-finished">
      🏁 Juego Completado - Todas las bolas extraídas
    </div>
    
    <button 
      @click="drawBall"
      :disabled="gameFinished || isDrawing"
      class="btn-draw"
    >
      {{ isDrawing ? 'Extrayendo...' : 'Extraer Bola' }}
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      drawnBalls: [],
      maxBalls: 75,
      gameFinished: false,
      isDrawing: false
    }
  },
  
  computed: {
    progress() {
      return (this.drawnBalls.length / this.maxBalls) * 100;
    }
  },
  
  methods: {
    async drawBall() {
      this.isDrawing = true;
      
      try {
        const response = await axios.post('/api/bingo/games/draw-ball', {
          game_id: this.gameId
        });
        
        if (response.data.game_status === 'finished') {
          this.gameFinished = true;
          this.$toast.success('¡Juego completado!');
          this.loadDrawnBalls();
        } else {
          this.drawnBalls.push({
            number: response.data.ball_number,
            drawn_at: new Date()
          });
          
          // Reproducir sonido
          this.$audio.play('ball-draw');
        }
      } catch (error) {
        this.$toast.error('Error al extraer bola');
      } finally {
        this.isDrawing = false;
      }
    },
    
    getBallClass(number) {
      // Colorear por columna (B-I-N-G-O)
      if (number <= 15) return 'ball-b';
      if (number <= 30) return 'ball-i';
      if (number <= 45) return 'ball-n';
      if (number <= 60) return 'ball-g';
      return 'ball-o';
    }
  }
}
</script>
```

---

## 📱 Integración con WhatsApp

### Bot con Extracción Automática

```php
// app/Services/WhatsAppGameService.php

public function startAutoExtraction($gameId, $interval = 5)
{
    $continue = true;
    
    while ($continue) {
        $result = $this->bingoService->drawBall($gameId);
        
        // Notificar a todos los jugadores
        $this->notifyPlayers($gameId, $result['ball_number']);
        
        // Verificar si el juego terminó
        if ($result['game_status'] === 'finished') {
            $this->notifyGameFinished($gameId);
            $continue = false;
        } else {
            // Esperar antes de la siguiente extracción
            sleep($interval);
        }
    }
}

private function notifyPlayers($gameId, $ballNumber)
{
    $players = $this->getGamePlayers($gameId);
    
    foreach ($players as $player) {
        if ($player['whatsapp_id']) {
            $message = "🎲 Bola extraída: *{$ballNumber}*\n";
            $message .= "Verifica tus cartones!";
            
            $this->sendWhatsApp($player['phone'], $message);
        }
    }
}
```

---

## ⚙️ Características Técnicas

### Evitación de Duplicados

- **Método 1**: Intenta hasta 10 veces generar bola aleatoria no duplicada
- **Método 2**: Si falla, calcula bolas disponibles y selecciona una
- **Garantía**: Siempre retorna bola única o detecta fin del juego

### Detección de Finalización

- **Automática**: Compara `total_drawn >= max_balls`
- **Marca partida**: Actualiza `is_active = False`
- **Retorna estado**: `game_status: "finished"`

### Estadísticas en Cada Extracción

- `total_drawn`: Total de bolas extraídas
- `remaining_balls`: Bolas que faltan
- `progress_percentage`: Porcentaje completado
- `game_status`: Estado actual (active/finished)

---

## 💡 Casos de Uso

### Caso 1: Extracción Manual

Operador o sistema extrae una bola a la vez:

```bash
POST /games/draw-ball/ {"game_id": "..."}
# Bola 15 extraída

POST /games/draw-ball/ {"game_id": "..."}
# Bola 42 extraída

POST /games/draw-ball/ {"game_id": "..."}
# Bola 33 extraída
```

### Caso 2: Extracción Automática

Sistema extrae bolas automáticamente cada X segundos:

```php
// Laravel - Comando artisan
public function handle()
{
    $game = BingoGame::find($this->argument('game_id'));
    
    while (true) {
        $result = $this->bingoService->drawBall($game->id);
        
        if ($result['game_status'] === 'finished') {
            $this->info('Juego completado!');
            break;
        }
        
        $this->info("Bola {$result['ball_number']} - {$result['progress_percentage']}%");
        
        sleep(5); // Esperar 5 segundos
    }
}
```

### Caso 3: Extracción por Lotes

Extraer múltiples bolas a la vez:

```php
public function drawMultipleBalls($gameId, $count = 10)
{
    $results = [];
    
    for ($i = 0; $i < $count; $i++) {
        $result = $this->bingoService->drawBall($gameId);
        
        if ($result['game_status'] === 'finished') {
            $results[] = $result;
            break;
        }
        
        $results[] = $result;
    }
    
    return $results;
}
```

---

## 🧪 Probar el Sistema

```bash
# Test manual (ejecutar el demo)
python3 demo_multiple_cards.py

# Test con curl
curl -X POST http://localhost:8000/api/multi-tenant/games/draw-ball/ \
  -H "Content-Type: application/json" \
  -d '{"game_id": "game-uuid"}'
```

---

## ✅ Ventajas del Sistema

### Robustez
- ✅ Nunca retorna bolas duplicadas
- ✅ Maneja correctamente el final del juego
- ✅ No requiere intervención manual

### Información
- ✅ Progreso en tiempo real
- ✅ Bolas restantes
- ✅ Porcentaje completado
- ✅ Estado del juego

### Automatización
- ✅ Detección automática de finalización
- ✅ Marcado automático de estado
- ✅ Listo para extracción automática

---

## 🎨 Visualización en HTML/Canvas

### Ejemplo HTML/CSS

```html
<!-- Mostrar bola extraída -->
<div class="ball-display" style="background-color: {{ color }}">
  <span class="ball-letter">{{ letter }}</span>
  <span class="ball-number">{{ number }}</span>
</div>

<!-- CSS -->
<style>
.ball-display {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.ball-letter {
  font-size: 20px;
  margin-bottom: 5px;
}

.ball-number {
  font-size: 28px;
}
</style>
```

### Ejemplo Vue Component

```vue
<template>
  <div class="balls-board">
    <!-- Última bola extraída -->
    <div class="current-ball">
      <div 
        class="ball-circle" 
        :style="{ backgroundColor: currentBall.color }"
      >
        <div class="ball-letter">{{ currentBall.letter }}</div>
        <div class="ball-number">{{ currentBall.number }}</div>
      </div>
      <div class="ball-display-name">{{ currentBall.display_name }}</div>
    </div>
    
    <!-- Historial de bolas -->
    <div class="balls-history">
      <div 
        v-for="ball in drawnBalls" 
        :key="ball.number"
        class="ball-small"
        :style="{ backgroundColor: ball.color }"
      >
        {{ ball.display_name }}
      </div>
    </div>
    
    <!-- Agrupadas por letra -->
    <div class="balls-by-letter">
      <div v-for="letter in ['B','I','N','G','O']" :key="letter" class="letter-group">
        <h3>{{ letter }}</h3>
        <div class="balls-grid">
          <div 
            v-for="ball in getBallsByLetter(letter)" 
            :key="ball.number"
            class="ball-item"
          >
            {{ ball.number }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentBall: null,
      drawnBalls: []
    }
  },
  
  methods: {
    async drawBall() {
      const response = await axios.post('/api/bingo/games/draw-ball', {
        game_id: this.gameId
      });
      
      this.currentBall = {
        number: response.data.ball_number,
        letter: response.data.letter,
        display_name: response.data.display_name,
        color: response.data.color
      };
      
      this.drawnBalls.push(this.currentBall);
    },
    
    getBallsByLetter(letter) {
      return this.drawnBalls.filter(b => b.letter === letter);
    }
  }
}
</script>
```

### Ejemplo Canvas

```javascript
// Dibujar bola en canvas
function drawBall(ctx, ball, x, y, radius) {
  // Fondo con color
  ctx.fillStyle = ball.color;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();
  
  // Borde
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 3;
  ctx.stroke();
  
  // Letra
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 24px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(ball.letter, x, y - 10);
  
  // Número
  ctx.font = 'bold 32px Arial';
  ctx.fillText(ball.number, x, y + 20);
}

// Uso
const canvas = document.getElementById('bingo-canvas');
const ctx = canvas.getContext('2d');

// Datos de la API
const ball = {
  number: 26,
  letter: 'I',
  display_name: 'I-26',
  color: '#FF6B35'
};

drawBall(ctx, ball, 100, 100, 40);
```

### Ejemplo WhatsApp (con emojis)

```php
// Mapeo de letras a emojis de colores
private function getBallEmoji($letter)
{
    $emojis = [
        'B' => '🔵',  // Círculo azul
        'I' => '🟠',  // Círculo naranja
        'N' => '🟢',  // Círculo verde
        'G' => '🟣',  // Círculo púrpura
        'O' => '🔴',  // Círculo rojo
    ];
    
    return $emojis[$letter] ?? '⚪';
}

private function notifyBallDrawn($gameId, $ball)
{
    $players = $this->getGamePlayers($gameId);
    
    $emoji = $this->getBallEmoji($ball['letter']);
    $message = "{$emoji} *Bola Extraída*\n\n";
    $message .= "🎲 {$ball['display_name']}\n";
    $message .= "📊 Extraídas: {$ball['total_drawn']}\n";
    $message .= "⏳ Restantes: {$ball['remaining_balls']}\n\n";
    $message .= "¡Marca tus cartones!";
    
    foreach ($players as $player) {
        $this->sendWhatsApp($player['phone'], $message);
    }
}
```

### Ejemplo Tablero Visual (HTML)

```html
<!-- Tablero con bolas agrupadas por letra -->
<div class="bingo-board">
  <div class="column" data-letter="B">
    <div class="column-header" style="background: #0066CC">B</div>
    <div class="numbers">
      <!-- Números 1-15 -->
      <div class="number" data-drawn="true">7</div>
      <div class="number" data-drawn="true">12</div>
      <div class="number">3</div>
      ...
    </div>
  </div>
  
  <div class="column" data-letter="I">
    <div class="column-header" style="background: #FF6B35">I</div>
    <div class="numbers">
      <!-- Números 16-30 -->
      <div class="number" data-drawn="true">26</div>
      <div class="number">18</div>
      ...
    </div>
  </div>
  
  <!-- ... Continúa para N, G, O -->
</div>

<style>
.bingo-board {
  display: flex;
  gap: 10px;
}

.column {
  flex: 1;
}

.column-header {
  color: white;
  text-align: center;
  padding: 10px;
  font-size: 24px;
  font-weight: bold;
}

.number {
  padding: 8px;
  margin: 4px;
  border: 1px solid #ddd;
  text-align: center;
  border-radius: 4px;
}

.number[data-drawn="true"] {
  background: var(--letter-color);
  color: white;
  font-weight: bold;
}
</style>
```

### JavaScript para Actualizar Tablero

```javascript
// Función para actualizar tablero cuando se extrae una bola
function updateBoard(ball) {
  // Actualizar bola actual
  document.getElementById('current-ball').innerHTML = `
    <div class="ball" style="background: ${ball.color}">
      <span class="letter">${ball.letter}</span>
      <span class="number">${ball.number}</span>
    </div>
  `;
  
  // Marcar número en el tablero
  const numberElement = document.querySelector(
    `[data-letter="${ball.letter}"] [data-number="${ball.number}"]`
  );
  
  if (numberElement) {
    numberElement.classList.add('drawn');
    numberElement.style.background = ball.color;
  }
  
  // Agregar al historial
  const historyHTML = `
    <span class="ball-mini" style="background: ${ball.color}">
      ${ball.display_name}
    </span>
  `;
  
  document.getElementById('history').insertAdjacentHTML('beforeend', historyHTML);
}

// Uso con WebSocket o polling
socket.on('ball_drawn', (ball) => {
  updateBoard(ball);
  
  // Animación
  playBallAnimation(ball);
  
  // Verificar cartones del jugador
  checkPlayerCards(ball);
});
```

---

## 📊 Endpoint con Todas las Bolas

```bash
GET /api/multi-tenant/games/{game-id}/drawn-balls/
```

**Respuesta:**
```json
{
  "game": {
    "id": "game-uuid",
    "name": "Partida Principal",
    "game_type": "75"
  },
  "total_drawn": 10,
  "balls": [7, 26, 41, 53, 66, 12, 18, 35, 60, 75],
  "balls_with_letters": [
    {
      "number": 7,
      "letter": "B",
      "display_name": "B-7",
      "color": "#0066CC",
      "drawn_at": "2024-01-15T10:05:00Z"
    },
    {
      "number": 26,
      "letter": "I",
      "display_name": "I-26",
      "color": "#FF6B35",
      "drawn_at": "2024-01-15T10:05:15Z"
    },
    ...
  ]
}
```

---

¡El sistema de extracción de bolas ahora incluye letras, colores y nombres completos para una visualización perfecta! 🎨✨
