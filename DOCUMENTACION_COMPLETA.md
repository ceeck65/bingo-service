# 🎲 Microservicio de Bingo - Documentación Completa

> **Sistema Multi-Tenant con Pool de Cartones para Laravel/Vue, WhatsApp y Telegram**

---

## 📑 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Características del Sistema](#características-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Tipos de Bingo](#tipos-de-bingo)
5. [Arquitectura Multi-Tenant](#arquitectura-multi-tenant)
6. [Sistema de Pool de Cartones](#sistema-de-pool-de-cartones)
7. [API REST - Endpoints](#api-rest---endpoints)
8. [Integración con Laravel/Vue](#integración-con-laravelvue)
9. [Integración con WhatsApp](#integración-con-whatsapp)
10. [Integración con Telegram](#integración-con-telegram)
11. [Patrones Ganadores](#patrones-ganadores)
12. [Scripts de Prueba](#scripts-de-prueba)
13. [Solución de Problemas](#solución-de-problemas)
14. [Estructura del Proyecto](#estructura-del-proyecto)

---

## 📖 Introducción

Este microservicio Django proporciona una solución completa para gestionar juegos de bingo en línea. Está diseñado específicamente para ser consumido por:

- **Web Apps (Laravel/Vue)** - Interfaz web completa
- **WhatsApp Business API** - Bots y comandos por WhatsApp
- **Telegram Bot API** - Bots y comandos por Telegram
- **Sistemas Whitelabel** - Múltiples operadores/marcas

### ¿Qué lo hace especial?

✅ **Multi-Tenant** - Cada operador tiene su espacio aislado  
✅ **Pool de Cartones** - Los jugadores seleccionan cartones pre-generados  
✅ **3 Tipos de Bingo** - Soporta 75, 85 y 90 bolas  
✅ **Validación Automática** - Detecta ganadores automáticamente  
✅ **Reutilización** - Los cartones pueden usarse en múltiples sesiones  
✅ **APIs Completas** - REST API para todas las funcionalidades  

---

## 🎯 Características del Sistema

### Funcionalidades Core

- ✅ Generación automática de cartones válidos
- ✅ Validación completa de reglas de bingo
- ✅ Sistema de validación de ganadores con múltiples patrones
- ✅ Sistema de partidas con extracción de bolas
- ✅ API REST completa y documentada
- ✅ Soporte para tres tipos de bingo (75, 85, 90 bolas)
- ✅ Generación de múltiples cartones simultáneos
- ✅ Estadísticas detalladas del sistema

### Sistema Multi-Tenant

- ✅ Operadores/marcas con aislamiento completo de datos
- ✅ Jugadores únicos por operador
- ✅ Sesiones de bingo organizadas y configurables
- ✅ Branding personalizado (colores, logos, dominios)
- ✅ Configuraciones flexibles por operador
- ✅ Límites configurables (cartones por jugador/partida)
- ✅ Integración con WhatsApp y Telegram

### Sistema de Pool de Cartones

- ✅ Operador define cantidad de cartones al crear sesión
- ✅ Cartones se generan una sola vez
- ✅ Jugadores seleccionan de cartones existentes
- ✅ Sistema de estados (disponible/reservado/vendido)
- ✅ Reutilización de cartones entre sesiones
- ✅ Trazabilidad completa de selecciones

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

### Configuración Rápida

```bash
# 1. Clonar o navegar al proyecto
cd /home/ceeck65/Projects/bingo_service

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos PostgreSQL
# La configuración está en bingo_service/settings.py:
# - Database: bingo
# - User: postgres
# - Password: 123456
# - Host: localhost
# - Port: 5432

# 4. Aplicar migraciones
python3 manage.py migrate

# 5. Crear superusuario (opcional)
python3 manage.py createsuperuser

# 6. Iniciar servidor
python3 manage.py runserver
```

### Variables de Entorno

El proyecto usa las siguientes configuraciones:

```python
# Base de Datos
DATABASE_NAME = 'bingo'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = '123456'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
```

### Dependencias

```
Django==5.2.7
djangorestframework==3.16.1
django-cors-headers==4.6.0
psycopg==3.1.18
```

---

## 🎲 Tipos de Bingo

### Bingo de 75 Bolas (Americano Clásico)

- **Formato**: 5x5 con centro libre (FREE)
- **Distribución por columnas**:
  - **B**: números 1-15
  - **I**: números 16-30
  - **N**: números 31-45 (centro libre)
  - **G**: números 46-60
  - **O**: números 61-75

**Ejemplo de cartón:**
```
  B    I    N    G    O
  7   26  FREE  53   66
 15   28   44   60   65
 11   24   41   47   72
  5   16   38   59   73
  2   29   31   50   64
```

### Bingo de 85 Bolas (Americano Extendido)

- **Formato**: 5x5 con centro libre
- **Distribución por columnas**:
  - **B**: números 1-16
  - **I**: números 17-32
  - **N**: números 33-48 (centro libre)
  - **G**: números 49-64
  - **O**: números 65-80

### Bingo de 90 Bolas (Europeo)

- **Formato**: 3x9 (3 filas, 9 columnas)
- **Números por fila**: Exactamente 5 números y 4 espacios vacíos
- **Distribución por columnas**:
  - Columna 1: números 1-9
  - Columna 2: números 10-19
  - ...
  - Columna 9: números 80-90

**Ejemplo de cartón:**
```
  5  --  23  --  45  --  67  82  --
 --  12  --  34  --  56  --  --  89
  9  --  29  --  48  --  71  --  90
```

---

## 🏢 Arquitectura Multi-Tenant

### Estructura Jerárquica

```
Operador (BingoMax)
├── Configuración
│   ├── Branding (logo, colores)
│   ├── Tipos de bingo permitidos
│   └── Límites configurables
├── Jugadores
│   ├── Juan (WhatsApp: +1234567890)
│   ├── María (Telegram: @maria_max)
│   └── Carlos (Email: carlos@bingomax.com)
├── Sesiones
│   ├── Sesión Matutina (75 bolas, 100 cartones)
│   └── Gran Torneo (85 bolas, 200 cartones)
└── Estadísticas
    ├── Jugadores activos
    ├── Sesiones realizadas
    └── Cartones vendidos
```

### Modelos Principales

#### 1. Operator (Operador/Marca)

```python
{
  "id": "uuid",
  "name": "BingoMax",
  "code": "bingomax",
  "domain": "bingomax.com",
  "logo_url": "https://bingomax.com/logo.png",
  "primary_color": "#FF6B35",
  "secondary_color": "#F7931E",
  "allowed_bingo_types": ["75", "85", "90"],
  "max_cards_per_player": 5,
  "max_cards_per_game": 100
}
```

#### 2. Player (Jugador)

```python
{
  "id": "uuid",
  "operator": "operator-uuid",
  "username": "juan_max",
  "email": "juan@bingomax.com",
  "phone": "+1234567890",
  "whatsapp_id": "1234567890",
  "telegram_id": "juan_max_tg",
  "is_active": true,
  "is_verified": true
}
```

#### 3. BingoSession (Sesión)

```python
{
  "id": "uuid",
  "operator": "operator-uuid",
  "name": "Sesión Matutina",
  "bingo_type": "75",
  "total_cards": 100,
  "max_players": 50,
  "entry_fee": 5.00,
  "scheduled_start": "2024-01-15T10:00:00Z",
  "status": "scheduled"
}
```

---

## 🎮 Sistema de Pool de Cartones

### Concepto

En lugar de generar un cartón nuevo cada vez que un jugador se une, el sistema funciona con un **pool (inventario) de cartones pre-generados** que los jugadores pueden seleccionar.

### Flujo Completo

```
1. OPERADOR CREA SESIÓN
   ├─> Define: nombre, tipo bingo, fecha/hora
   └─> Define: total_cards = 100

2. SISTEMA GENERA CARTONES
   ├─> Crea 100 cartones únicos
   ├─> Estado inicial: "available"
   └─> Numerados: #1, #2, #3, ..., #100

3. JUGADOR VE CARTONES DISPONIBLES
   ├─> GET /sessions/{id}/available-cards/
   └─> Ve todos los cartones con preview

4. JUGADOR SELECCIONA CARTÓN
   ├─> POST /cards/select/
   ├─> Estado cambia a: "reserved"
   └─> Tiene 10 min para confirmar

5. JUGADOR CONFIRMA COMPRA
   ├─> POST /cards/confirm-purchase/
   ├─> Estado cambia a: "sold"
   └─> Cartón listo para jugar

6. ALTERNATIVA: LIBERAR CARTÓN
   ├─> POST /cards/release/
   ├─> Estado vuelve a: "available"
   └─> Otro jugador puede seleccionarlo
```

### Estados de los Cartones

| Estado | Descripción | Acción Permitida |
|--------|-------------|------------------|
| **available** | Disponible para selección | Puede ser reservado |
| **reserved** | Reservado por un jugador | Puede confirmar o liberar |
| **sold** | Comprado y confirmado | Participa en la partida |
| **cancelled** | Cancelado por operador | No puede usarse |

### Ventajas

✅ **Control**: Operador define exactamente cuántos cartones existen  
✅ **Transparencia**: Jugadores ven todos los cartones disponibles  
✅ **Eficiencia**: Se generan una sola vez  
✅ **Elección**: Jugadores pueden elegir su cartón favorito  
✅ **Múltiples Cartones**: Jugadores pueden jugar con varios cartones simultáneamente  
✅ **Reutilización**: Mismos cartones en múltiples sesiones  

### Jugador con Múltiples Cartones

Un jugador puede seleccionar y jugar con múltiples cartones en la misma sesión:

#### Límites Configurables

Cada operador define el máximo de cartones por jugador:

```python
operator.max_cards_per_player = 5  # Máximo 5 cartones
```

#### Selección Múltiple

**Opción 1: Seleccionar uno por uno**
```bash
# Seleccionar cartón #1
POST /api/multi-tenant/cards/select/
{"session_id": "...", "player_id": "...", "card_id": "card-1"}

# Seleccionar cartón #2
POST /api/multi-tenant/cards/select/
{"session_id": "...", "player_id": "...", "card_id": "card-2"}
```

**Opción 2: Seleccionar múltiples a la vez (Recomendado)**
```bash
POST /api/multi-tenant/cards/select-multiple/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_ids": ["card-1", "card-2", "card-3"]
}
```

#### Ver Cartones del Jugador

```bash
GET /api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/

Respuesta:
{
  "summary": {
    "total": 3,
    "reserved": 3,
    "sold": 0
  },
  "cards": [
    {
      "id": "card-uuid-1",
      "card_number": 1,
      "status": "reserved",
      "numbers": [...]
    },
    ...
  ]
}
```

#### Confirmación en Bloque

Confirmar todos los cartones reservados de un jugador:

```bash
POST /api/multi-tenant/cards/confirm-multiple-purchase/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid"
}

Respuesta:
{
  "message": "3 cartones confirmados exitosamente",
  "total_cost": 15.00,
  "total_cards": 3
}
```

#### Ventajas de Múltiples Cartones

✅ **Mayor probabilidad de ganar** - Más cartones = más chances  
✅ **Control de límites** - Operador define máximo  
✅ **Proceso optimizado** - Selección y compra en bloque  
✅ **Transparencia** - El jugador ve todos sus cartones  

---

## 📡 API REST - Endpoints

### Base URLs

- **APIs Básicas**: `http://localhost:8000/api/bingo/`
- **APIs Multi-Tenant**: `http://localhost:8000/api/multi-tenant/`

### Operadores

```bash
# Listar operadores
GET /api/multi-tenant/operators/

# Crear operador
POST /api/multi-tenant/operators/
{
  "name": "Mi Bingo",
  "code": "mibingo",
  "allowed_bingo_types": ["75", "85", "90"]
}

# Obtener operador específico
GET /api/multi-tenant/operators/{id}/

# Estadísticas del operador
GET /api/multi-tenant/operators/{id}/statistics/
```

### Jugadores

```bash
# Listar jugadores
GET /api/multi-tenant/players/?operator={operator-id}

# Crear jugador
POST /api/multi-tenant/players/
{
  "operator": "operator-uuid",
  "username": "juan123",
  "email": "juan@example.com",
  "phone": "+1234567890"
}

# Registrar por teléfono (WhatsApp/Telegram)
POST /api/multi-tenant/players/register-by-phone/
{
  "operator_code": "mibingo",
  "phone": "+1234567890",
  "username": "juan_whatsapp"
}

# Vincular cuenta social
POST /api/multi-tenant/players/link-social/
{
  "player_id": "player-uuid",
  "whatsapp_id": "whatsapp-user-id"
}
```

### Sesiones

```bash
# Listar sesiones
GET /api/multi-tenant/sessions/?operator={operator-id}

# Crear sesión
POST /api/multi-tenant/sessions/
{
  "operator": "operator-uuid",
  "name": "Sesión Matutina",
  "bingo_type": "75",
  "total_cards": 100,
  "max_players": 50,
  "entry_fee": 5.00,
  "scheduled_start": "2024-01-15T10:00:00Z"
}

# Obtener sesión específica
GET /api/multi-tenant/sessions/{id}/

# Estadísticas de la sesión
GET /api/multi-tenant/sessions/{id}/statistics/

# Unirse a una sesión
POST /api/multi-tenant/sessions/join/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "cards_count": 3
}
```

### Cartones

```bash
# Generar cartones para sesión
POST /api/multi-tenant/cards/generate-for-session/
{
  "session_id": "session-uuid",
  "generate_now": true
}

# Ver cartones disponibles
GET /api/multi-tenant/sessions/{session-id}/available-cards/

# Seleccionar un cartón
POST /api/multi-tenant/cards/select/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_id": "card-uuid"
}

# ⭐ NUEVO: Seleccionar múltiples cartones a la vez
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

# ⭐ NUEVO: Ver todos los cartones de un jugador
GET /api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/

# Confirmar compra de un cartón
POST /api/multi-tenant/cards/confirm-purchase/
{
  "card_id": "card-uuid"
}

# ⭐ NUEVO: Confirmar compra de todos los cartones reservados
POST /api/multi-tenant/cards/confirm-multiple-purchase/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid"
}

# Liberar cartón
POST /api/multi-tenant/cards/release/
{
  "card_id": "card-uuid"
}

# Reutilizar cartones en nueva sesión
POST /api/multi-tenant/cards/reuse/
{
  "new_session_id": "new-session-uuid",
  "old_session_id": "old-session-uuid"
}
```

### Partidas

```bash
# Listar partidas
GET /api/multi-tenant/games/?operator={operator-id}
GET /api/multi-tenant/games/?session={session-id}

# Crear partida
POST /api/multi-tenant/games/
{
  "operator": "operator-uuid",
  "session": "session-uuid",
  "game_type": "75",
  "name": "Partida Principal",
  "auto_draw": false
}

# Obtener partida específica
GET /api/multi-tenant/games/{game-id}/

# Obtener partida activa de una sesión
GET /api/multi-tenant/sessions/{session-id}/game/

Respuesta:
{
  "game": {
    "id": "game-uuid",
    "name": "Partida Principal",
    "game_type": "75",
    "is_active": true
  },
  "session": {
    "id": "session-uuid",
    "name": "Sesión Matutina",
    "status": "active"
  },
  "stats": {
    "balls_drawn": 15,
    "total_cards": 45,
    "players": 12
  }
}

# Extraer bola
POST /api/multi-tenant/games/draw-ball/
{
  "game_id": "game-uuid"
}

Respuesta:
{
  "message": "Bola 42 extraída",
  "ball_number": 42,
  "total_drawn": 15
}

# Ver bolas extraídas
GET /api/multi-tenant/games/{game-id}/drawn-balls/

Respuesta:
{
  "game": {...},
  "total_drawn": 15,
  "balls": [5, 12, 23, 34, 42, ...],
  "details": [
    {"number": 5, "drawn_at": "2024-01-15T10:05:00Z"},
    ...
  ]
}

# Verificar ganador (un cartón)
POST /api/multi-tenant/games/check-winner/
{
  "card_id": "card-uuid",
  "game_id": "game-uuid"
}

Respuesta:
{
  "card": {...},
  "winner_result": {
    "is_winner": true,
    "winning_patterns": ["Línea horizontal (fila 1)"],
    "marked_numbers": [7, 26, 41, 53, 66]
  },
  "drawn_balls_count": 25
}
```

---

## 🌐 Integración con Laravel/Vue

### Servicio de Bingo en Laravel

```php
// app/Services/BingoService.php
namespace App\Services;

use Illuminate\Support\Facades\Http;

class BingoService
{
    protected $apiUrl;
    protected $operatorId;
    
    public function __construct()
    {
        $this->apiUrl = config('bingo.api_url');
        $this->operatorId = config('bingo.operator_id');
    }
    
    // Crear sesión
    public function createSession($data)
    {
        return Http::post($this->apiUrl . 'sessions/', [
            'operator' => $this->operatorId,
            'name' => $data['name'],
            'bingo_type' => $data['type'],
            'total_cards' => $data['total_cards'],
            'max_players' => $data['max_players'],
            'entry_fee' => $data['price'],
            'scheduled_start' => $data['start_time']
        ])->json();
    }
    
    // Generar cartones
    public function generateCards($sessionId)
    {
        return Http::post($this->apiUrl . 'cards/generate-for-session/', [
            'session_id' => $sessionId,
            'generate_now' => true
        ])->json();
    }
    
    // Obtener cartones disponibles
    public function getAvailableCards($sessionId)
    {
        return Http::get(
            $this->apiUrl . "sessions/{$sessionId}/available-cards/"
        )->json();
    }
    
    // Seleccionar cartón
    public function selectCard($sessionId, $playerId, $cardId)
    {
        return Http::post($this->apiUrl . 'cards/select/', [
            'session_id' => $sessionId,
            'player_id' => $playerId,
            'card_id' => $cardId
        ])->json();
    }
    
    // Confirmar compra
    public function confirmPurchase($cardId)
    {
        return Http::post($this->apiUrl . 'cards/confirm-purchase/', [
            'card_id' => $cardId
        ])->json();
    }
}
```

### Componente Vue para Selección de Cartones

```vue
<!-- resources/js/components/CardSelector.vue -->
<template>
  <div class="card-selector">
    <h2>Selecciona tu Cartón</h2>
    
    <div class="cards-grid">
      <div 
        v-for="card in availableCards" 
        :key="card.id"
        class="card-item"
        :class="{ selected: selectedCard === card.id }"
        @click="selectCard(card)"
      >
        <div class="card-number">#{{ card.card_number }}</div>
        <div class="card-preview">
          <table>
            <thead>
              <tr>
                <th>B</th>
                <th>I</th>
                <th>N</th>
                <th>G</th>
                <th>O</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in card.numbers" :key="i">
                <td v-for="(num, j) in row" :key="j">
                  {{ num === 'FREE' ? '★' : num }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <button 
      @click="confirmSelection"
      :disabled="!selectedCard"
      class="btn-confirm"
    >
      Confirmar Selección
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      availableCards: [],
      selectedCard: null,
      session: null
    }
  },
  
  async mounted() {
    await this.loadAvailableCards();
  },
  
  methods: {
    async loadAvailableCards() {
      try {
        const response = await axios.get(
          `/api/bingo/sessions/${this.$route.params.sessionId}/available-cards`
        );
        this.availableCards = response.data.cards;
        this.session = response.data.session;
      } catch (error) {
        this.$toast.error('Error cargando cartones');
      }
    },
    
    selectCard(card) {
      this.selectedCard = card.id;
    },
    
    async confirmSelection() {
      try {
        await axios.post('/api/bingo/cards/select', {
          session_id: this.session.id,
          player_id: this.$auth.user.id,
          card_id: this.selectedCard
        });
        
        this.$toast.success('Cartón reservado. Procede al pago');
        this.$router.push('/checkout');
      } catch (error) {
        this.$toast.error('Error al seleccionar cartón');
      }
    }
  }
}
</script>
```

---

## 📱 Integración con WhatsApp

### Comandos Disponibles

```
/sesiones - Ver sesiones activas
/cartones - Ver cartones disponibles
/seleccionar {número} - Seleccionar un cartón
/miscartas - Ver mis cartones
/estado - Ver estado de mi cuenta
/ayuda - Mostrar ayuda
```

### Implementación en Laravel

```php
// app/Services/WhatsAppBingoService.php
namespace App\Services;

class WhatsAppBingoService
{
    protected $bingoService;
    
    public function __construct(BingoService $bingoService)
    {
        $this->bingoService = $bingoService;
    }
    
    public function processCommand($phone, $message)
    {
        $player = $this->getOrCreatePlayer($phone);
        
        switch (trim(strtolower($message))) {
            case '/sesiones':
                return $this->sendActiveSessions($player);
                
            case '/cartones':
                return $this->sendAvailableCards($player);
                
            case '/miscartas':
                return $this->sendPlayerCards($player);
                
            case '/ayuda':
                return $this->sendHelp($player);
                
            default:
                if (preg_match('/\/seleccionar (\d+)/', $message, $matches)) {
                    return $this->selectCard($player, $matches[1]);
                }
                return $this->sendHelp($player);
        }
    }
    
    private function sendActiveSessions($player)
    {
        $sessions = $this->bingoService->getActiveSessions();
        
        $message = "🎯 *Sesiones Activas:*\n\n";
        
        foreach ($sessions['results'] as $session) {
            $message .= "🎲 *{$session['name']}*\n";
            $message .= "Tipo: {$session['bingo_type']} bolas\n";
            $message .= "Entrada: \${$session['entry_fee']}\n";
            $message .= "Disponibles: {$session['available_cards_count']}/{$session['total_cards']}\n";
            $message .= "------------------------\n";
        }
        
        $message .= "\n📝 Usa /cartones para ver los cartones disponibles";
        
        return $this->sendWhatsApp($player['phone'], $message);
    }
    
    private function sendAvailableCards($player)
    {
        $session = $this->bingoService->getActiveSession();
        $cards = $this->bingoService->getAvailableCards($session['id']);
        
        $message = "🎲 *Cartones Disponibles: {$cards['session']['available_count']}*\n\n";
        
        // Mostrar primeros 10 cartones
        foreach (array_slice($cards['cards'], 0, 10) as $card) {
            $message .= "📋 *Cartón #{$card['card_number']}*\n";
            $message .= "B: {$card['numbers'][0][0]} | ";
            $message .= "I: {$card['numbers'][0][1]} | ";
            $message .= "N: {$card['numbers'][0][2]} | ";
            $message .= "G: {$card['numbers'][0][3]} | ";
            $message .= "O: {$card['numbers'][0][4]}\n";
        }
        
        $message .= "\n✅ Usa /seleccionar {número} para elegir tu cartón";
        
        return $this->sendWhatsApp($player['phone'], $message);
    }
    
    private function selectCard($player, $cardNumber)
    {
        try {
            $session = $this->bingoService->getActiveSession();
            $card = $this->findCardByNumber($session['id'], $cardNumber);
            
            $result = $this->bingoService->selectCard(
                $session['id'],
                $player['id'],
                $card['id']
            );
            
            $message = "✅ *Cartón #{$cardNumber} Reservado*\n\n";
            $message .= "Tienes 10 minutos para completar el pago.\n";
            $message .= "Precio: \${$session['entry_fee']}\n\n";
            $message .= "💳 Envía el comprobante para confirmar.";
            
            return $this->sendWhatsApp($player['phone'], $message);
            
        } catch (\Exception $e) {
            return $this->sendWhatsApp(
                $player['phone'],
                "❌ Error: " . $e->getMessage()
            );
        }
    }
}
```

---

## 📱 Integración con Telegram

### Bot de Telegram

```php
// app/Services/TelegramBingoBot.php
namespace App\Services;

use Telegram\Bot\Api;
use Telegram\Bot\Keyboard\Keyboard;

class TelegramBingoBot
{
    protected $telegram;
    protected $bingoService;
    
    public function __construct(BingoService $bingoService)
    {
        $this->telegram = new Api(config('telegram.bot_token'));
        $this->bingoService = $bingoService;
    }
    
    public function handleUpdate($update)
    {
        $message = $update->getMessage();
        $chatId = $message->getChat()->getId();
        $text = $message->getText();
        $username = $message->getFrom()->getUsername();
        
        $player = $this->getOrCreatePlayer($chatId, $username);
        
        $this->processCommand($chatId, $text, $player);
    }
    
    private function processCommand($chatId, $text, $player)
    {
        switch ($text) {
            case '/start':
                $this->sendWelcome($chatId);
                break;
                
            case '/sesiones':
                $this->sendSessions($chatId);
                break;
                
            case '/cartones':
                $this->sendCards($chatId, $player);
                break;
                
            default:
                $this->sendHelp($chatId);
        }
    }
    
    private function sendWelcome($chatId)
    {
        $keyboard = Keyboard::make()
            ->inline()
            ->row([
                Keyboard::inlineButton([
                    'text' => '🎯 Ver Sesiones',
                    'callback_data' => 'view_sessions'
                ])
            ])
            ->row([
                Keyboard::inlineButton([
                    'text' => '🎲 Ver Cartones',
                    'callback_data' => 'view_cards'
                ])
            ]);
        
        $this->telegram->sendMessage([
            'chat_id' => $chatId,
            'text' => "¡Bienvenido al Bingo! 🎲\n\nSelecciona una opción:",
            'reply_markup' => $keyboard
        ]);
    }
    
    private function sendSessions($chatId)
    {
        $sessions = $this->bingoService->getActiveSessions();
        
        $text = "🎯 *Sesiones Activas:*\n\n";
        
        foreach ($sessions['results'] as $session) {
            $text .= "🎲 *{$session['name']}*\n";
            $text .= "Tipo: {$session['bingo_type']} bolas\n";
            $text .= "Entrada: \${$session['entry_fee']}\n";
            $text .= "Disponibles: {$session['available_cards_count']}\n";
            $text .= "─────────────\n";
        }
        
        $this->telegram->sendMessage([
            'chat_id' => $chatId,
            'text' => $text,
            'parse_mode' => 'Markdown'
        ]);
    }
}
```

---

## 🏆 Patrones Ganadores

### Bingo de 75 Bolas (Americano)

- ✅ **Línea Horizontal** - Una fila completa
- ✅ **Línea Vertical** - Una columna completa (B, I, N, G, O)
- ✅ **Diagonal Principal** - De esquina superior izquierda a inferior derecha
- ✅ **Diagonal Secundaria** - De esquina superior derecha a inferior izquierda
- ✅ **Cuatro Esquinas** - Las cuatro esquinas del cartón
- ✅ **Cartón Completo** - Todo el cartón marcado

### Bingo de 85 Bolas (Americano Extendido)

- ✅ **Línea Horizontal** - Una fila completa
- ✅ **Línea Vertical** - Una columna completa
- ✅ **Diagonal Principal**
- ✅ **Diagonal Secundaria**
- ✅ **Cuatro Esquinas**
- ✅ **Cartón Completo**

### Bingo de 90 Bolas (Europeo)

- ✅ **Línea** - Una fila completa
- ✅ **Dos Líneas** - Dos filas completas
- ✅ **Cartón Completo** - Las tres filas completas
- ✅ **Columna** - Una columna completa (menos común)

---

## 🧪 Scripts de Prueba

### Probar Sistema Completo

```bash
# Test de modelos
python3 test_models.py

# Demo de pool de cartones
python3 demo_pool_cartones.py

# Demo de 75 bolas
python3 demo_75_balls.py

# Demo multi-tenant
python3 demo_multi_tenant.py

# Test simple
python3 test_pool_simple.py
```

### Ejemplos con curl

```bash
# Crear operador
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Bingo",
    "code": "testbingo",
    "allowed_bingo_types": ["75"]
  }'

# Crear sesión
curl -X POST http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "operator-uuid",
    "name": "Sesión de Prueba",
    "bingo_type": "75",
    "total_cards": 50,
    "entry_fee": 5.00,
    "scheduled_start": "2024-01-15T20:00:00Z"
  }'

# Generar cartones
curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "generate_now": true
  }'

# Ver cartones disponibles
curl http://localhost:8000/api/multi-tenant/sessions/session-uuid/available-cards/
```

---

## 🔧 Solución de Problemas

### Error: "MultipleObjectsReturned"

**Problema:**
```
MultipleObjectsReturned at /api/multi-tenant/players/register-by-phone/
get() returned more than one Player
```

**Solución:**
```bash
# Limpiar datos duplicados
python3 cleanup_duplicates.py
```

### Error: "no such table: bingo_operator"

**Problema:**
```
OperationalError: no such table: bingo_operator
```

**Solución:**
```bash
python3 manage.py migrate
```

### Error: PostgreSQL Connection Failed

**Problema:**
```
could not connect to server
```

**Soluciones:**

1. Verificar PostgreSQL:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

2. Crear base de datos:
```bash
createdb -U postgres bingo
```

3. Usar script de configuración:
```bash
./setup_postgresql.sh
```

### Migraciones Desincronizadas

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Puerto Ya en Uso

```bash
# Cambiar puerto
python3 manage.py runserver 8001

# O matar proceso
pkill -f runserver
```

### Instalar psycopg

```bash
pip install psycopg==3.1.18
```

### Limpiar Sistema Completo

```bash
# Limpiar datos de demos
python3 cleanup_duplicates.py

# Resetear base de datos
python3 manage.py flush
python3 manage.py migrate
```

**Ver más soluciones en:** `GUIA_SOLUCION_PROBLEMAS.md`

---

## 📁 Estructura del Proyecto

```
bingo_service/
├── bingo/                          # App principal
│   ├── migrations/                 # Migraciones de base de datos
│   ├── models.py                   # Modelos de datos
│   ├── views.py                    # Vistas básicas
│   ├── views_multi_tenant.py       # Vistas multi-tenant
│   ├── serializers.py              # Serializers básicos
│   ├── serializers_multi_tenant.py # Serializers multi-tenant
│   ├── urls.py                     # URLs básicas
│   ├── urls_multi_tenant.py        # URLs multi-tenant
│   └── admin.py                    # Configuración del admin
│
├── bingo_service/                  # Configuración del proyecto
│   ├── settings.py                 # Configuración Django
│   ├── urls.py                     # URLs principales
│   └── wsgi.py                     # WSGI config
│
├── requirements.txt                # Dependencias
├── manage.py                       # Django management
│
├── demo_pool_cartones.py          # Demo pool de cartones
├── demo_multi_tenant.py           # Demo multi-tenant
├── demo_75_balls.py               # Demo 75 bolas
├── test_models.py                 # Test de modelos
├── test_pool_simple.py            # Test simple
│
└── DOCUMENTACION_COMPLETA.md      # Esta documentación
```

---

## 📞 Soporte y Contacto

Para más información o soporte:

1. Revisar esta documentación completa
2. Ejecutar los scripts de demo
3. Revisar logs en caso de errores
4. Verificar configuración de PostgreSQL

---

## 🎉 Conclusión

Este microservicio proporciona una solución completa y robusta para gestionar juegos de bingo en línea con las siguientes ventajas:

✅ **Multi-Tenant** - Múltiples operadores aislados  
✅ **Pool de Cartones** - Sistema eficiente de selección  
✅ **3 Tipos de Bingo** - Máxima flexibilidad  
✅ **APIs Completas** - Integración fácil  
✅ **PostgreSQL** - Base de datos robusta  
✅ **Documentado** - Guías completas  

**¡El sistema está listo para producción!** 🎲✨

---

*Documentación actualizada: 2024*
*Versión del Sistema: 2.0*
*Base de Datos: PostgreSQL*
