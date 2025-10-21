# 📡 Endpoints API - Referencia Completa

## Base URLs

- **APIs Multi-Tenant**: `http://localhost:8000/api/multi-tenant/`
- **APIs Básicas**: `http://localhost:8000/api/bingo/`

---

## 🏢 Operadores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/operators/` | Listar todos los operadores |
| POST | `/operators/` | Crear nuevo operador |
| GET | `/operators/{id}/` | Obtener operador específico |
| PUT | `/operators/{id}/` | Actualizar operador |
| DELETE | `/operators/{id}/` | Eliminar operador |
| GET | `/operators/{id}/statistics/` | Estadísticas del operador |

### Ejemplos

```bash
# Listar operadores
GET /api/multi-tenant/operators/

# Crear operador
POST /api/multi-tenant/operators/
{
  "name": "Mi Bingo",
  "code": "mibingo",
  "allowed_bingo_types": ["75", "85", "90"],
  "max_cards_per_player": 5
}

# Estadísticas
GET /api/multi-tenant/operators/{operator-id}/statistics/
```

---

## 👥 Jugadores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/players/` | Listar jugadores |
| GET | `/players/?operator={id}` | Filtrar por operador |
| POST | `/players/` | Crear jugador |
| GET | `/players/{id}/` | Obtener jugador específico |
| PUT | `/players/{id}/` | Actualizar jugador |
| DELETE | `/players/{id}/` | Eliminar jugador |
| POST | `/players/register-by-phone/` | Registrar por teléfono |
| POST | `/players/link-social/` | Vincular WhatsApp/Telegram |

### Ejemplos

```bash
# Registrar por teléfono (WhatsApp/Telegram)
POST /api/multi-tenant/players/register-by-phone/
{
  "operator_code": "mibingo",
  "phone": "+1234567890",
  "username": "juan123"
}

# Vincular WhatsApp
POST /api/multi-tenant/players/link-social/
{
  "player_id": "player-uuid",
  "whatsapp_id": "whatsapp-id"
}
```

---

## 🎯 Sesiones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/sessions/` | Listar sesiones |
| GET | `/sessions/?operator={id}` | Filtrar por operador |
| GET | `/sessions/?status={status}` | Filtrar por estado |
| POST | `/sessions/` | Crear sesión |
| GET | `/sessions/{id}/` | Obtener sesión específica |
| PUT | `/sessions/{id}/` | Actualizar sesión |
| DELETE | `/sessions/{id}/` | Eliminar sesión |
| GET | `/sessions/{id}/statistics/` | Estadísticas de la sesión |
| GET | `/sessions/{id}/available-cards/` | Ver cartones disponibles |
| GET | `/sessions/{id}/game/` | Obtener partida activa |
| POST | `/sessions/join/` | Unirse a sesión |
| POST | `/sessions/leave/` | Salir de sesión |

### Ejemplos

```bash
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

# Listar sesiones activas
GET /api/multi-tenant/sessions/?status=active

# Ver partida activa de una sesión
GET /api/multi-tenant/sessions/{session-id}/game/
```

---

## 🎲 Cartones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/cards/` | Listar cartones |
| GET | `/cards/?session={id}` | Filtrar por sesión |
| GET | `/cards/?player={id}` | Filtrar por jugador |
| GET | `/cards/{id}/` | Obtener cartón específico |
| POST | `/cards/generate-for-session/` | Generar cartones para sesión |
| POST | `/cards/select/` | Seleccionar un cartón |
| POST | `/cards/select-multiple/` | Seleccionar múltiples cartones |
| POST | `/cards/confirm-purchase/` | Confirmar compra de un cartón |
| POST | `/cards/confirm-multiple-purchase/` | Confirmar todos los cartones |
| POST | `/cards/release/` | Liberar cartón reservado |
| POST | `/cards/reuse/` | Reutilizar cartones en nueva sesión |
| GET | `/sessions/{sid}/player/{pid}/cards/` | Ver cartones del jugador |

### Ejemplos

```bash
# Generar cartones
POST /api/multi-tenant/cards/generate-for-session/
{
  "session_id": "session-uuid",
  "generate_now": true
}

# Ver cartones disponibles
GET /api/multi-tenant/sessions/{session-id}/available-cards/

# Seleccionar múltiples cartones
POST /api/multi-tenant/cards/select-multiple/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_ids": ["card-1", "card-2", "card-3"]
}

# Ver cartones de un jugador
GET /api/multi-tenant/sessions/{session-id}/player/{player-id}/cards/

# Confirmar todos los cartones
POST /api/multi-tenant/cards/confirm-multiple-purchase/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid"
}
```

---

## 🎮 Partidas y Juegos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/games/` | Listar partidas |
| GET | `/games/?operator={id}` | Filtrar por operador |
| GET | `/games/?session={id}` | Filtrar por sesión |
| POST | `/games/` | Crear partida |
| GET | `/games/{id}/` | Obtener partida específica |
| POST | `/games/draw-ball/` | Extraer una bola (body: game_id) |
| POST | `/games/{id}/draw-ball/` | Extraer una bola (game_id en URL) |
| GET | `/games/{id}/drawn-balls/` | Ver bolas extraídas |
| POST | `/games/check-winner/` | Verificar si un cartón es ganador |

### Ejemplos

```bash
# Crear partida
POST /api/multi-tenant/games/
{
  "operator": "operator-uuid",
  "session": "session-uuid",
  "game_type": "75",
  "name": "Partida Matutina"
}

# Listar partidas de una sesión
GET /api/multi-tenant/games/?session={session-id}

# Obtener partida activa de sesión
GET /api/multi-tenant/sessions/{session-id}/game/

# Extraer bola (Opción 1: game_id en body)
POST /api/multi-tenant/games/draw-ball/
{
  "game_id": "game-uuid"
}

# Extraer bola (Opción 2: game_id en URL - Recomendado)
POST /api/multi-tenant/games/{game-uuid}/draw-ball/

# También acepta GET para compatibilidad
GET /api/multi-tenant/games/{game-uuid}/draw-ball/

# Ver bolas extraídas
GET /api/multi-tenant/games/{game-id}/drawn-balls/

# Verificar ganador
POST /api/multi-tenant/games/check-winner/
{
  "game_id": "game-uuid",
  "card_id": "card-uuid"
}
```

---

## 📊 Estadísticas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/operators/{id}/statistics/` | Estadísticas del operador |
| GET | `/sessions/{id}/statistics/` | Estadísticas de la sesión |

### Ejemplos

```bash
# Estadísticas de operador
GET /api/multi-tenant/operators/{operator-id}/statistics/

Respuesta:
{
  "operator": {...},
  "players": {
    "total": 150,
    "active": 120
  },
  "sessions": {
    "total": 25,
    "active": 3
  },
  "cards": {
    "total": 450,
    "by_type": {"75": 200, "85": 150, "90": 100}
  }
}

# Estadísticas de sesión
GET /api/multi-tenant/sessions/{session-id}/statistics/

Respuesta:
{
  "session": {...},
  "players": {
    "total": 30,
    "winners": 1
  },
  "cards": {
    "total": 100,
    "winning": 1
  }
}
```

---

## 🔗 Participación en Sesiones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/player-sessions/` | Listar participaciones |
| GET | `/player-sessions/?session={id}` | Filtrar por sesión |
| GET | `/player-sessions/?player={id}` | Filtrar por jugador |
| POST | `/sessions/join/` | Unirse a sesión |
| POST | `/sessions/leave/` | Salir de sesión |

### Ejemplos

```bash
# Unirse a sesión
POST /api/multi-tenant/sessions/join/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "cards_count": 3
}

# Ver participaciones de una sesión
GET /api/multi-tenant/player-sessions/?session={session-id}
```

---

## 🔍 Filtros Disponibles

### Operadores
- `?is_active=true` - Solo operadores activos

### Jugadores
- `?operator={operator-id}` - Por operador

### Sesiones
- `?operator={operator-id}` - Por operador
- `?status=active` - Por estado (scheduled, active, finished, etc.)

### Cartones
- `?session={session-id}` - Por sesión
- `?player={player-id}` - Por jugador
- `?operator={operator-id}` - Por operador

### Partidas
- `?operator={operator-id}` - Por operador
- `?session={session-id}` - Por sesión

---

## 📝 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Error en los datos enviados |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 🎯 Flujo Completo de una Partida

### 1. Configuración (Operador)

```bash
# 1.1 Crear sesión
POST /sessions/
{
  "name": "Sesión de las 20:00",
  "total_cards": 100,
  ...
}

# 1.2 Generar cartones
POST /cards/generate-for-session/
{"session_id": "...", "generate_now": true}

# 1.3 Crear partida
POST /games/
{
  "session": "session-uuid",
  "game_type": "75",
  ...
}
```

### 2. Inscripción (Jugadores)

```bash
# 2.1 Jugador se une
POST /sessions/join/
{"session_id": "...", "player_id": "...", "cards_count": 3}

# 2.2 Selecciona cartones
POST /cards/select-multiple/
{"session_id": "...", "player_id": "...", "card_ids": [...]}

# 2.3 Confirma compra
POST /cards/confirm-multiple-purchase/
{"session_id": "...", "player_id": "..."}
```

### 3. Partida en Curso

```bash
# 3.1 Extraer bolas
POST /games/draw-ball/
{"game_id": "..."}

# 3.2 Ver bolas extraídas
GET /games/{game-id}/drawn-balls/

# 3.3 Verificar ganadores
POST /games/check-winner/
{"game_id": "...", "card_id": "..."}
```

---

## 💡 Tips y Mejores Prácticas

### Performance

- Usar filtros para reducir respuestas grandes
- Paginar resultados en listados grandes
- Cachear datos que no cambian frecuentemente

### Seguridad

- Validar siempre que el jugador pertenece al operador correcto
- Verificar estados de las sesiones antes de operaciones
- Usar HTTPS en producción

### Manejo de Errores

- Siempre verificar códigos de estado HTTP
- Manejar errores 404 y 400 adecuadamente
- Implementar retry logic para errores temporales

---

## 🧪 Probar Endpoints

### Con curl

```bash
# Crear operador
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "code": "test", "allowed_bingo_types": ["75"]}'

# Listar sesiones
curl http://localhost:8000/api/multi-tenant/sessions/

# Extraer bola
curl -X POST http://localhost:8000/api/multi-tenant/games/draw-ball/ \
  -H "Content-Type: application/json" \
  -d '{"game_id": "game-uuid"}'
```

### Con Python (requests)

```python
import requests

BASE_URL = 'http://localhost:8000/api/multi-tenant/'

# Crear sesión
response = requests.post(BASE_URL + 'sessions/', json={
    'operator': operator_id,
    'name': 'Test Session',
    'bingo_type': '75',
    'total_cards': 50,
    'entry_fee': 5.00,
    'scheduled_start': '2024-01-15T20:00:00Z'
})

session = response.json()

# Listar partidas
response = requests.get(BASE_URL + f'games/?session={session["id"]}')
games = response.json()
```

---

## 📚 Documentación Relacionada

- **[DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md)** - Guía completa
- **[MULTIPLES_CARTONES.md](MULTIPLES_CARTONES.md)** - Múltiples cartones
- **[GUIA_SOLUCION_PROBLEMAS.md](GUIA_SOLUCION_PROBLEMAS.md)** - Troubleshooting

---

*Última actualización: 2024-10-21*
