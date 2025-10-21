# 🎲 Sistema de Pool de Cartones (Inventario)

## 📋 Resumen

El sistema de bingo ahora funciona con un **pool de cartones** o **inventario de cartones**, donde:

1. **El operador define la cantidad de cartones** al crear la sesión
2. **Los cartones se generan una sola vez** al crear la sesión
3. **Los jugadores seleccionan de los cartones existentes** (no se generan nuevos)
4. **Los cartones pueden reutilizarse** en múltiples sesiones

## 🎯 Flujo del Sistema

### 1. Operador Crea Sesión

Cuando un operador crea una sesión, define:
- Tipo de bingo (75, 85, 90 bolas)
- Número de jugadores máximos
- **Cantidad total de cartones** (ej: 100 cartones)
- Si permite reutilizar cartones de otras sesiones

```json
POST /api/multi-tenant/sessions/
{
  "operator": "operator-uuid",
  "name": "Sesión Matutina",
  "bingo_type": "75",
  "max_players": 50,
  "entry_fee": 5.00,
  "total_cards": 100,          // ← Cantidad de cartones a generar
  "allow_card_reuse": false,   // ← Permitir reutilizar cartones
  "scheduled_start": "2024-01-15T10:00:00Z"
}
```

### 2. Generación de Cartones

Los cartones se generan inmediatamente o bajo demanda:

```json
POST /api/multi-tenant/cards/generate-for-session/
{
  "session_id": "session-uuid",
  "generate_now": true
}
```

Esto crea 100 cartones con:
- Estado: `available` (disponible)
- Número único: 1, 2, 3, ..., 100
- Sin jugador asignado

### 3. Jugadores Seleccionan Cartones

Los jugadores ven los cartones disponibles y seleccionan el que desean:

**Ver cartones disponibles:**
```json
GET /api/multi-tenant/sessions/{session_id}/available-cards/

Respuesta:
{
  "session": {
    "id": "uuid",
    "name": "Sesión Matutina",
    "total_cards": 100,
    "available_count": 95
  },
  "cards": [
    {
      "id": "card-uuid-1",
      "card_number": 1,
      "status": "available",
      "numbers": [[1, 16, 31, 46, 61], ...]
    },
    ...
  ]
}
```

**Seleccionar un cartón:**
```json
POST /api/multi-tenant/cards/select/
{
  "session_id": "session-uuid",
  "player_id": "player-uuid",
  "card_id": "card-uuid-1"
}
```

El cartón cambia a estado `reserved` (reservado)

### 4. Confirmar Compra

Una vez que el jugador confirma el pago:

```json
POST /api/multi-tenant/cards/confirm-purchase/
{
  "card_id": "card-uuid-1"
}
```

El cartón cambia a estado `sold` (vendido)

### 5. Liberar Cartón (Opcional)

Si el jugador cancela antes de pagar:

```json
POST /api/multi-tenant/cards/release/
{
  "card_id": "card-uuid-1"
}
```

El cartón vuelve a estado `available`

## 🔄 Estados de los Cartones

### available (Disponible)
- El cartón está disponible para ser seleccionado
- No tiene jugador asignado
- Puede ser seleccionado por cualquier jugador

### reserved (Reservado)
- El cartón fue seleccionado por un jugador
- Tiene jugador asignado
- Esperando confirmación de pago
- Puede ser liberado si no se confirma la compra

### sold (Vendido)
- El cartón fue comprado y confirmado
- Tiene jugador asignado
- No puede ser liberado ni reasignado
- Participa en la partida

### cancelled (Cancelado)
- El cartón fue cancelado
- No puede ser usado en esta sesión

## 🔄 Reutilización de Cartones

### ¿Qué significa reutilizar cartones?

Cuando un operador crea una nueva sesión, puede optar por **reutilizar los mismos cartones** de una sesión anterior en lugar de generar nuevos.

**Ventajas:**
- ✅ No es necesario regenerar cartones
- ✅ Ahorra tiempo de procesamiento
- ✅ Los jugadores pueden usar los mismos cartones en diferentes horarios
- ✅ Permite crear múltiples sesiones con el mismo "set" de cartones

### Cómo Reutilizar Cartones

**Opción 1: Al crear la sesión**
```json
POST /api/multi-tenant/sessions/
{
  "operator": "operator-uuid",
  "name": "Sesión Vespertina",
  "bingo_type": "75",
  "total_cards": 100,
  "allow_card_reuse": true,  // ← Permite reutilizar
  "scheduled_start": "2024-01-15T18:00:00Z"
}
```

**Opción 2: Reutilizar de sesión específica**
```json
POST /api/multi-tenant/cards/reuse/
{
  "new_session_id": "new-session-uuid",
  "old_session_id": "old-session-uuid"
}
```

Esto copia todos los cartones de la sesión antigua a la nueva, manteniendo los mismos números pero con estado `available`.

## 📊 Información de la Sesión

Al consultar una sesión, se puede ver el estado de los cartones:

```json
GET /api/multi-tenant/sessions/{id}/

Respuesta:
{
  "id": "uuid",
  "name": "Sesión Matutina",
  "total_cards": 100,
  "cards_generated": true,
  "cards_count": 100,
  "available_cards_count": 85,
  "sold_cards_count": 15,
  "allow_card_reuse": false,
  ...
}
```

## 🎮 Escenarios de Uso

### Escenario 1: Bingo Online Web

1. **Operador configura sesión** en el panel de administración
   - Define 200 cartones para la sesión de las 20:00
   - Sistema genera los 200 cartones inmediatamente

2. **Jugadores entran al sitio web**
   - Ven galería de cartones disponibles
   - Cada cartón muestra su preview
   - Seleccionan el cartón que más les gusta

3. **Proceso de compra**
   - Cartón se reserva durante el proceso de pago
   - Si el pago falla, se libera automáticamente
   - Si el pago es exitoso, se marca como vendido

### Escenario 2: Bingo por WhatsApp

1. **Operador crea sesión** para las 21:00 con 100 cartones

2. **Jugador envía comando** `/cartones`
   - Bot muestra: "Hay 95 cartones disponibles"
   - Bot envía imagen con primeros 10 cartones

3. **Jugador selecciona** `/seleccionar 42`
   - Bot: "Cartón #42 reservado. Tienes 10 minutos para pagar"

4. **Jugador confirma pago**
   - Bot: "✅ Cartón #42 confirmado. ¡Suerte!"

### Escenario 3: Múltiples Sesiones Mismo Día

1. **Operador crea "Set de Cartones A"**
   - 150 cartones de 75 bolas
   - Los genera una sola vez

2. **Crea 3 sesiones diferentes**
   - Sesión 10:00 - Reutiliza Set A
   - Sesión 15:00 - Reutiliza Set A
   - Sesión 20:00 - Reutiliza Set A

3. **Mismo cartón, diferentes partidas**
   - El Cartón #42 puede ser comprado por diferentes jugadores en cada sesión
   - Cada sesión tiene su propia partida independiente

## 🔒 Reglas y Validaciones

### Al Seleccionar un Cartón

✅ El cartón debe estar `available`  
✅ El cartón debe pertenecer a la sesión  
✅ El jugador debe estar inscrito en la sesión  
✅ El jugador debe pertenecer al mismo operador  

### Al Reutilizar Cartones

✅ La nueva sesión debe permitir reutilización  
✅ Ambas sesiones deben ser del mismo tipo de bingo  
✅ Ambas sesiones deben ser del mismo operador  

### Límites

- Un cartón solo puede estar en una sesión a la vez
- Un cartón `sold` no puede ser liberado
- Un cartón `cancelled` no puede ser reactivado

## 💡 Ventajas del Sistema

### Para el Operador

✅ **Control total** sobre cuántos cartones existen  
✅ **Evita duplicados** en la misma sesión  
✅ **Optimiza recursos** - genera una sola vez  
✅ **Reutilización** en múltiples sesiones  
✅ **Transparencia** - los jugadores ven todos los cartones disponibles  

### Para los Jugadores

✅ **Pueden elegir** su cartón favorito  
✅ **Ven todos** los cartones disponibles  
✅ **Transparencia** en la selección  
✅ **No hay duplicados** en la misma sesión  

### Para el Sistema

✅ **Más eficiente** - genera cartones una sola vez  
✅ **Mejor control** del inventario  
✅ **Trazabilidad** completa (quién seleccionó qué y cuándo)  
✅ **Escalable** - puede manejar miles de cartones  

## 🚀 Próximas Mejoras

### Sugerencias para Futuras Versiones

1. **Sistema de Expiración de Reservas**
   - Liberar automáticamente reservas después de X minutos
   - Cola de espera para cartones populares

2. **Filtros y Búsqueda**
   - Buscar cartones por números específicos
   - Filtrar por patrones favoritos

3. **Cartones Favoritos**
   - Jugadores pueden marcar cartones como favoritos
   - Notificación cuando un cartón favorito está disponible

4. **Analytics**
   - Cartones más populares
   - Tiempo promedio de selección
   - Tasa de conversión reserva→venta

---

## 📞 Soporte

Para más información sobre el sistema, consultar:
- `README.md` - Documentación principal
- `INTEGRACION_MULTI_TENANT.md` - Guía de integración
- `demo_pool_cartones.py` - Demo funcional del sistema

¡El sistema de pool de cartones optimiza la experiencia tanto para operadores como para jugadores! 🎲✨
