# 🚀 Inicio Rápido - Microservicio de Bingo

## ⚡ Configuración en 3 Pasos

### 1️⃣ Configurar PostgreSQL

```bash
./setup_postgresql.sh
```

O manualmente:
```bash
# Crear base de datos
createdb -U postgres bingo

# Aplicar migraciones
python3 manage.py migrate
```

### 2️⃣ Iniciar Servidor

```bash
python3 manage.py runserver
```

### 3️⃣ Probar el Sistema

```bash
python3 test_models.py
```

---

## 🎯 Primer Uso

### Crear un Operador

```bash
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Bingo App",
    "code": "mibingo",
    "allowed_bingo_types": ["75", "85", "90"]
  }'
```

**Respuesta:**
```json
{
  "id": "operator-uuid",
  "name": "Mi Bingo App",
  "code": "mibingo",
  ...
}
```

### Crear una Sesión con Cartones

```bash
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
```

### Generar Cartones

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "generate_now": true
  }'
```

**Respuesta:**
```json
{
  "message": "100 cartones generados exitosamente",
  "session": {
    "total_cards": 100,
    "cards_generated": true,
    "available_cards_count": 100
  }
}
```

### Ver Cartones Disponibles

```bash
curl http://localhost:8000/api/multi-tenant/sessions/session-uuid/available-cards/
```

---

## 🎮 Flujo Completo de Jugador

### 1. Registrar Jugador

```bash
curl -X POST http://localhost:8000/api/multi-tenant/players/register-by-phone/ \
  -H "Content-Type: application/json" \
  -d '{
    "operator_code": "mibingo",
    "phone": "+1234567890",
    "username": "juan123"
  }'
```

### 2. Unirse a Sesión

```bash
curl -X POST http://localhost:8000/api/multi-tenant/sessions/join/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "cards_count": 3
  }'
```

### 3. Ver Cartones Disponibles

```bash
curl http://localhost:8000/api/multi-tenant/sessions/session-uuid/available-cards/
```

### 4. Seleccionar Cartón

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/select/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "player_id": "player-uuid",
    "card_id": "card-uuid"
  }'
```

### 5. Confirmar Compra

```bash
curl -X POST http://localhost:8000/api/multi-tenant/cards/confirm-purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": "card-uuid"
  }'
```

---

## 🧹 Mantenimiento

### Limpiar Datos de Demo

```bash
python3 cleanup_duplicates.py
```

### Resetear Base de Datos

```bash
dropdb -U postgres bingo
createdb -U postgres bingo
python3 manage.py migrate
```

---

## 📚 Documentación

- **`DOCUMENTACION_COMPLETA.md`** - Documentación completa
- **`GUIA_SOLUCION_PROBLEMAS.md`** - Solución de problemas
- **`RESUMEN_PROYECTO.md`** - Resumen del proyecto

---

## 🎲 Scripts Útiles

```bash
# Configuración
./setup_postgresql.sh      # Setup de PostgreSQL
./start_server.sh          # Iniciar servidor

# Pruebas
python3 test_models.py          # Test de modelos
python3 test_pool_simple.py     # Test pool de cartones
python3 cleanup_duplicates.py   # Limpiar duplicados

# Demos
python3 demo_pool_cartones.py   # Demo pool de cartones
python3 demo_multi_tenant.py    # Demo multi-tenant
python3 demo_75_balls.py        # Demo 75 bolas
```

---

## ✅ Checklist de Verificación

- [x] PostgreSQL instalado y corriendo
- [x] Base de datos 'bingo' creada
- [x] Dependencias instaladas (`psycopg`)
- [x] Migraciones aplicadas
- [x] Servidor iniciado
- [x] APIs funcionando

---

## 🎉 ¡Listo!

El microservicio está configurado y funcionando con:
- ✅ PostgreSQL como base de datos
- ✅ Sistema multi-tenant operativo
- ✅ Pool de cartones funcionando
- ✅ APIs completas disponibles
- ✅ Documentación unificada

**Siguiente paso:** Leer `DOCUMENTACION_COMPLETA.md` para detalles de integración.

---

*¡Feliz desarrollo!* 🚀✨
