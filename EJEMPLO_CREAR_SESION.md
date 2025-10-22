# 📝 Ejemplo: Crear Sesión y Obtener ID

## 🎯 Endpoint

```http
POST /api/multi-tenant/sessions/
Authorization: Bearer {token}
Content-Type: application/json
```

## 📤 Request Body

```json
{
  "operator": "uuid-operador",
  "name": "Bingo de la Tarde",
  "description": "Sesión de bingo con premios especiales",
  "bingo_type": "75",
  "max_players": 100,
  "entry_fee": 50,
  "total_cards": 200,
  "allow_card_reuse": true,
  "scheduled_start": "2024-10-22T18:00:00Z",
  "winning_patterns": [
    "horizontal_line",
    "vertical_line",
    "full_card",
    "four_corners"
  ]
}
```

## 📥 Response (201 Created)

```json
{
  "message": "Sesión creada exitosamente",
  "session_id": "22a7d060-ab2f-4118-9045-bb24885e316d",
  "session": {
    "id": "22a7d060-ab2f-4118-9045-bb24885e316d",
    "operator": "uuid-operador",
    "operator_name": "Mi Bingo",
    "name": "Bingo de la Tarde",
    "description": "Sesión de bingo con premios especiales",
    "bingo_type": "75",
    "bingo_type_display": "75 bolas",
    "max_players": 100,
    "entry_fee": "50.00",
    "total_cards": 200,
    "cards_generated": false,
    "allow_card_reuse": true,
    "scheduled_start": "2024-10-22T18:00:00Z",
    "actual_start": null,
    "actual_end": null,
    "status": "scheduled",
    "status_display": "Programada",
    "auto_start": false,
    "auto_draw_interval": 5,
    "winning_patterns": [
      "horizontal_line",
      "vertical_line",
      "full_card",
      "four_corners"
    ],
    "players_count": 0,
    "cards_count": 0,
    "available_cards_count": 0,
    "sold_cards_count": 0,
    "created_at": "2024-10-22T10:30:00Z",
    "updated_at": "2024-10-22T10:30:00Z",
    "created_by": ""
  }
}
```

## 💡 Campos Importantes en la Respuesta

### `session_id`
- **Tipo**: UUID (string)
- **Descripción**: ID único de la sesión creada
- **Uso**: Utilizar este ID para todas las operaciones posteriores (generar cartones, iniciar partida, etc.)

### `session`
- **Tipo**: Object
- **Descripción**: Objeto completo con todos los detalles de la sesión
- **Incluye**: Contadores de jugadores, cartones, estado, etc.

---

## 💻 Ejemplos de Integración

### Laravel

```php
// app/Services/BingoService.php

public function createSession(array $data)
{
    $token = $this->authService->getAccessToken();
    
    $response = Http::withHeaders([
        'Authorization' => "Bearer {$token}"
    ])->post($this->apiUrl . '/sessions/', $data);
    
    if ($response->successful()) {
        $result = $response->json();
        
        // Obtener el ID de la sesión creada
        $sessionId = $result['session_id'];
        
        // Guardar en base de datos local
        BingoSession::create([
            'django_session_id' => $sessionId,
            'name' => $result['session']['name'],
            'status' => $result['session']['status'],
            // ... otros campos
        ]);
        
        return [
            'success' => true,
            'session_id' => $sessionId,
            'session' => $result['session']
        ];
    }
    
    return ['success' => false, 'error' => $response->json()];
}

// Uso en controlador
public function store(Request $request)
{
    $result = $this->bingoService->createSession([
        'operator' => config('bingo.operator_id'),
        'name' => $request->name,
        'bingo_type' => $request->bingo_type,
        'total_cards' => $request->total_cards,
        'scheduled_start' => $request->scheduled_start,
        'winning_patterns' => $request->winning_patterns
    ]);
    
    if ($result['success']) {
        // Usar el session_id
        $sessionId = $result['session_id'];
        
        // Generar cartones
        $this->bingoService->generateCardsForSession($sessionId, 100);
        
        return response()->json([
            'message' => 'Sesión creada',
            'session_id' => $sessionId
        ]);
    }
    
    return response()->json(['error' => $result['error']], 400);
}
```

### Vue.js

```javascript
// services/bingoService.js
export default {
  async createSession(sessionData) {
    try {
      const response = await this.$http.post('/api/multi-tenant/sessions/', sessionData)
      
      // Extraer el session_id de la respuesta
      const { session_id, session } = response.data
      
      // Guardar en Vuex store
      this.$store.commit('bingo/SET_CURRENT_SESSION', {
        id: session_id,
        ...session
      })
      
      return { success: true, sessionId: session_id, session }
    } catch (error) {
      return { success: false, error: error.response.data }
    }
  }
}

// Componente Vue
<script>
export default {
  methods: {
    async createNewSession() {
      const sessionData = {
        operator: this.operatorId,
        name: this.form.name,
        bingo_type: this.form.bingoType,
        total_cards: this.form.totalCards,
        scheduled_start: this.form.scheduledStart,
        winning_patterns: this.form.selectedPatterns
      }
      
      const result = await bingoService.createSession(sessionData)
      
      if (result.success) {
        this.$message.success('Sesión creada exitosamente')
        
        // Usar el ID de la sesión
        const sessionId = result.sessionId
        
        // Redirigir a la página de la sesión
        this.$router.push({ 
          name: 'session-detail', 
          params: { id: sessionId } 
        })
        
        // O generar cartones automáticamente
        await this.generateCards(sessionId)
      } else {
        this.$message.error('Error creando sesión')
      }
    },
    
    async generateCards(sessionId) {
      await this.$http.post(
        `/api/multi-tenant/sessions/${sessionId}/generate-cards/`,
        { quantity: 100 }
      )
    }
  }
}
</script>
```

### Python (WhatsApp Bot)

```python
import requests

def create_bingo_session(operator_id, name, bingo_type, total_cards):
    """Crea una sesión de bingo y retorna el ID"""
    
    # Obtener token
    token = get_jwt_token()
    
    # Datos de la sesión
    session_data = {
        'operator': operator_id,
        'name': name,
        'bingo_type': bingo_type,
        'total_cards': total_cards,
        'scheduled_start': datetime.now().isoformat(),
        'winning_patterns': [
            'horizontal_line',
            'vertical_line',
            'full_card'
        ]
    }
    
    # Crear sesión
    response = requests.post(
        f'{API_URL}/api/multi-tenant/sessions/',
        headers={'Authorization': f'Bearer {token}'},
        json=session_data
    )
    
    if response.status_code == 201:
        result = response.json()
        
        # Obtener el ID de la sesión
        session_id = result['session_id']
        
        print(f"✅ Sesión creada: {session_id}")
        print(f"   Nombre: {result['session']['name']}")
        print(f"   Tipo: {result['session']['bingo_type_display']}")
        
        return session_id
    else:
        print(f"❌ Error: {response.json()}")
        return None

# Uso
session_id = create_bingo_session(
    operator_id='uuid-operador',
    name='Bingo WhatsApp',
    bingo_type='75',
    total_cards=50
)

if session_id:
    # Generar cartones
    generate_cards_for_session(session_id, 50)
    
    # Notificar jugadores
    notify_players_new_session(session_id)
```

### JavaScript/Node.js

```javascript
// services/bingoApi.js
const axios = require('axios');

class BingoAPI {
  constructor(apiUrl, apiKey, apiSecret) {
    this.apiUrl = apiUrl;
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
    this.token = null;
  }
  
  async getToken() {
    if (this.token) return this.token;
    
    const response = await axios.post(`${this.apiUrl}/api/token/`, {
      api_key: this.apiKey,
      api_secret: this.apiSecret
    });
    
    this.token = response.data.access;
    return this.token;
  }
  
  async createSession(sessionData) {
    const token = await this.getToken();
    
    const response = await axios.post(
      `${this.apiUrl}/api/multi-tenant/sessions/`,
      sessionData,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    
    // Retornar el ID y los datos completos
    return {
      sessionId: response.data.session_id,
      session: response.data.session,
      message: response.data.message
    };
  }
}

// Uso
const bingoApi = new BingoAPI(
  'http://localhost:8000',
  'api-key',
  'api-secret'
);

const result = await bingoApi.createSession({
  operator: 'uuid-operador',
  name: 'Bingo Node.js',
  bingo_type: '75',
  total_cards: 100,
  scheduled_start: new Date().toISOString(),
  winning_patterns: ['horizontal_line', 'full_card']
});

console.log('Session ID:', result.sessionId);
console.log('Session:', result.session);
```

---

## ✅ Resumen

Ahora cuando creas una sesión, la respuesta incluye:

1. **`message`**: Mensaje de confirmación
2. **`session_id`**: ⭐ **ID de la sesión** (usar para operaciones posteriores)
3. **`session`**: Objeto completo con todos los detalles

Este cambio facilita la integración y evita tener que extraer el ID del objeto `session`.

---

**Documentación actualizada:** Versión 2.4
