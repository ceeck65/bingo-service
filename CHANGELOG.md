# 📝 Registro de Cambios (Changelog)

## Versión 2.5 - Sistema de Reutilización de Cartas (2024-10-22)

### 🎴 Nueva Arquitectura de Cartas

#### Modelos Implementados
- ✅ **`CardPack`**: Paquetes reutilizables de cartas
  - Operadores crean packs de cartas (50, 100, 500, etc.)
  - Categorías: free, basic, premium, vip, legacy
  - Generación única, uso infinito
  
- ✅ **`PlayerCard`**: Cartas propiedad de jugadores
  - Jugadores adquieren cartas de packs
  - Estadísticas por carta (veces usada, veces ganada, premios)
  - Personalización (favoritos, apodos)
  - Win rate tracking
  
- ✅ **`SessionCard`**: Cartas activas en sesiones
  - Relaciona sesión + jugador + carta
  - Números marcados por sesión
  - Resultados independientes por sesión
  - Permite reutilizar la misma carta en múltiples sesiones

#### Modificaciones a Modelos Existentes
- ✅ **`BingoCardExtended`**: Nuevos campos
  - `pack`: Relación con CardPack
  - `serial_number`: Identificador único (ej: OPERA-75-ABC12345-0042)
  - `is_reusable`: Indica si la carta puede reutilizarse
  - `total_sessions`: Contador de sesiones donde se usó
  - `total_wins`: Contador de victorias globales
  
- ✅ **`BingoSession`**: Sistema de fuentes de cartas
  - `card_source`: 'player_cards', 'pack', 'generate'
  - `card_pack`: Pack a usar (si card_source='pack')
  - Campos antiguos marcados como DEPRECATED

### 🔌 Nuevos Endpoints

#### Card Packs
- `POST /api/card-packs/packs/` - Crear pack
- `GET /api/card-packs/packs/` - Listar packs
- `GET /api/card-packs/packs/{id}/` - Detalle de pack
- `POST /api/card-packs/packs/{id}/generate-cards/` - Generar cartas
- `GET /api/card-packs/packs/{id}/cards/` - Ver cartas del pack

#### Player Cards
- `POST /api/card-packs/players/{id}/acquire-cards/` - Adquirir cartas
- `GET /api/card-packs/players/{id}/cards/` - Ver colección
- `PATCH /api/card-packs/players/{id}/cards/{card_id}/favorite/` - Marcar favorita
- `PATCH /api/card-packs/players/{id}/cards/{card_id}/nickname/` - Poner apodo

#### Session Cards
- `POST /api/card-packs/sessions/{id}/join-with-cards/` - Unirse con cartas
- `GET /api/card-packs/sessions/{id}/cards/` - Ver cartas en sesión
- `GET /api/card-packs/sessions/{id}/players/{player_id}/cards/` - Cartas de jugador
- `POST /api/card-packs/mark-number/` - Marcar número en carta

### 🎯 Modos de Operación

#### Modo 1: Jugadores con Cartas Propias (Recomendado)
```json
{
  "card_source": "player_cards"
}
```
- Jugadores usan sus cartas personales
- Reutilización completa
- Estadísticas por carta

#### Modo 2: Pack Compartido
```json
{
  "card_source": "pack",
  "card_pack": "uuid-pack"
}
```
- Sesión usa cartas de un pack
- Cartas se asignan temporalmente
- Vuelven al pool al terminar

#### Modo 3: Generar Nuevas (Legacy)
```json
{
  "card_source": "generate",
  "total_cards": 100
}
```
- Compatible con sistema anterior
- Cartas desechables

### 📊 Beneficios

**Para Jugadores:**
- ✅ Colección personal de cartas
- ✅ Reutilizan favoritas en múltiples sesiones
- ✅ Estadísticas detalladas (win rate, veces usada)
- ✅ Personalización (apodos, favoritos)

**Para Operadores:**
- ✅ No generan cartas cada vez
- ✅ Un pack sirve para miles de sesiones
- ✅ Control de inventario
- ✅ Pueden vender cartas premium

**Para el Sistema:**
- ✅ Escalable (menos datos generados)
- ✅ Flexible (3 modos de operación)
- ✅ Retrocompatible
- ✅ Optimizado

### 🗄️ Admin Interface
- ✅ Gestión de CardPacks con acción de generación masiva
- ✅ Visualización de PlayerCards con estadísticas
- ✅ Monitoreo de SessionCards activas

### 📝 Documentación
- ✅ `PROPUESTA_REUTILIZACION_CARTAS.md` - Diseño completo
- ✅ `demo_card_reuse.py` - Demo funcional del sistema

---

## Versión 2.4.1 - Mejora en Creación de Sesiones (2024-10-22)

### 🔧 Mejoras en API

#### Endpoint de Creación de Sesiones
- ✅ **`session_id` en respuesta**: Ahora retorna el ID directamente en el root de la respuesta
- ✅ **Respuesta mejorada**: Incluye `message`, `session_id` y `session` completo
- ✅ **Facilita integración**: No es necesario extraer el ID del objeto `session`

#### Ejemplo de Respuesta
```json
{
  "message": "Sesión creada exitosamente",
  "session_id": "uuid-de-la-sesion",
  "session": { ... }
}
```

#### Documentación
- ✅ `EJEMPLO_CREAR_SESION.md` - Guía completa con ejemplos
- ✅ Ejemplos de integración para Laravel, Vue.js, Python, Node.js

---

## Versión 2.4 - Sistema de Patrones de Victoria (2024-10-22)

### 🎯 Sistema de Patrones Configurables

#### Patrones Implementados
- ✅ **4 Patrones Clásicos**: Línea horizontal, vertical, diagonal, cartón lleno
- ✅ **5 Patrones Especiales**: Cuatro esquinas, X/Cruz, Letra L, Letra T, Jackpot rápido
- ✅ **Sistema de Jackpot Progresivo**: Premios especiales por velocidad
- ✅ **Multiplicadores de Premio**: Configurables por patrón
- ✅ **Compatibilidad por Tipo**: Patrones específicos para 75/85/90 bolas

#### Funcionalidades
- ✅ **Configuración por Sesión**: Operadores eligen patrones para cada partida
- ✅ **Verificación Automática**: Chequeo de ganadores después de cada bola
- ✅ **Múltiples Ganadores**: Soporte para varios patrones simultáneos
- ✅ **Patrones Personalizados**: Operadores pueden crear sus propios patrones

#### Endpoints de Patrones
- ✅ `GET /api/patterns/` - Listar todos los patrones
- ✅ `GET /api/patterns/available/{bingo_type}/` - Patrones por tipo
- ✅ `POST /api/patterns/sessions/{id}/configure/` - Configurar sesión
- ✅ `GET /api/patterns/sessions/{id}/patterns/` - Ver patrones de sesión
- ✅ `POST /api/patterns/check-winner/` - Verificar ganador
- ✅ `POST /api/patterns/games/{id}/check-all-cards/` - Verificar todos los cartones

#### Modelo y Lógica
- ✅ Modelo `WinningPattern` con validación de patrones
- ✅ 9 métodos de verificación implementados
- ✅ Integración con `BingoSession`
- ✅ Admin de Django configurado

#### Herramientas
- ✅ `initialize_patterns.py` - Script de inicialización
- ✅ `demo_patterns.py` - Demo completo del sistema

#### Documentación
- ✅ `PATRONES_VICTORIA.md` - Documentación completa
- ✅ Ejemplos de integración Laravel/Vue/WhatsApp

---

## Versión 2.3 - Autenticación JWT Bearer Token (2024-10-21)

### 🔐 Migración a JWT

#### Sistema JWT Implementado
- ✅ Autenticación con **Bearer Token** estándar
- ✅ Todos los endpoints protegidos por defecto
- ✅ Access Token (24h) + Refresh Token (7 días)
- ✅ Obtención de token con API Key + Secret
- ✅ Backend personalizado compatible con Operator
- ✅ Mensajes de error claros (401)

#### Endpoints JWT
- ✅ `POST /api/token/` - Obtener access + refresh token
- ✅ `POST /api/token/refresh/` - Renovar access token

#### Seguridad Mejorada
- ✅ Tokens firmados con HS256
- ✅ Expiración automática
- ✅ Renovación con refresh token
- ✅ Validación en cada request
- ✅ Claims personalizados (operator, permission_level)

#### Integraciones
- ✅ Ejemplos completos para Laravel/PHP
- ✅ Ejemplos completos para Vue.js
- ✅ Interceptores para refresh automático
- ✅ Manejo de cache de tokens

#### Documentación
- ✅ `AUTENTICACION_JWT.md` - Guía completa
- ✅ Ejemplos de código para Laravel
- ✅ Ejemplos de código para Vue.js
- ✅ Manejo de errores y best practices

#### Herramientas
- ✅ `create_api_key.py` - Script para crear credenciales sin autenticación
- ✅ `test_jwt.py` - Test automático del sistema JWT
- ✅ Solución al problema del "huevo y la gallina"

---

## Versión 2.2 - Sistema de Autenticación (2024-10-21)

### 🔐 Sistema de Autenticación con API Keys

#### Modelo y Autenticación
- ✅ Modelo `APIKey` para gestión de credenciales
- ✅ Generación automática de Key + Secret
- ✅ Hash seguro con SHA-256
- ✅ Verificación timing-safe con `secrets.compare_digest()`
- ✅ Middleware `APIKeyAuthentication`
- ✅ Permisos personalizados (read/write/admin)

#### Características de Seguridad
- ✅ Secret nunca se almacena en texto plano
- ✅ Control por IP (opcional)
- ✅ Rate limiting configurado
- ✅ Expiración de keys
- ✅ Revocación de keys comprometidas
- ✅ Tracking de último uso

#### Endpoints de Autenticación
- ✅ `POST /api/auth/api-keys/create/` - Crear API Key
- ✅ `GET /api/auth/api-keys/` - Listar API Keys
- ✅ `POST /api/auth/api-keys/{id}/revoke/` - Revocar API Key
- ✅ `POST /api/auth/test/` - Probar autenticación

#### Documentación
- ✅ `AUTENTICACION.md` - Guía completa de autenticación
- ✅ Ejemplos de integración con Laravel/Vue
- ✅ Ejemplos de uso con curl

---

## Versión 2.1 - Múltiples Cartones por Jugador (2024-10-21)

### 🎮 Nuevas Funcionalidades

#### Múltiples Cartones por Jugador
- ✅ Jugador puede seleccionar múltiples cartones en una sesión
- ✅ Endpoint para selección múltiple: `/cards/select-multiple/`
- ✅ Endpoint para ver cartones del jugador: `/sessions/{id}/player/{id}/cards/`
- ✅ Confirmación en bloque: `/cards/confirm-multiple-purchase/`
- ✅ Validación automática de límites por operador
- ✅ Contador de cartones en `PlayerSession`

#### Validaciones
- ✅ Límite de cartones por jugador (configurable en Operator)
- ✅ Verificación de cartones disponibles
- ✅ Prevención de duplicados
- ✅ Validación de pertenencia a la sesión

#### Endpoints de Partidas Agregados
- ✅ `POST /games/draw-ball/` - Extraer bola con evitación de duplicados
  - Salta bolas duplicadas automáticamente
  - Selecciona bola disponible si hay duplicado
  - Detecta cuando todas las bolas fueron extraídas
  - Marca juego como finalizado automáticamente
  - Retorna progreso y estadísticas
  - **NUEVO**: Incluye letra (B-I-N-G-O), nombre completo y color CSS
- ✅ `GET /games/{id}/drawn-balls/` - Ver bolas extraídas
  - Incluye formato con letras para visualización
- ✅ `POST /games/check-winner/` - Verificar ganador
- ✅ `GET /sessions/{id}/game/` - Obtener partida activa de sesión

#### Visualización de Bolas
- ✅ Método `get_letter()` - Retorna letra (B, I, N, G, O)
- ✅ Método `get_display_name()` - Retorna nombre completo (ej: "I-26")
- ✅ Método `get_color()` - Retorna color CSS para cada letra
- ✅ Colores definidos:
  - B: #0066CC (Azul)
  - I: #FF6B35 (Naranja)
  - N: #4CAF50 (Verde)
  - G: #9C27B0 (Púrpura)
  - O: #F44336 (Rojo)

#### Scripts
- ✅ `demo_multiple_cards.py` - Demo completo de múltiples cartones
- ✅ `cleanup_duplicates.py` - Limpiar datos duplicados

#### Documentación Adicional
- ✅ `ENDPOINTS_API.md` - Referencia completa de todos los endpoints

---

## Versión 2.0 - Sistema Multi-Tenant con PostgreSQL (2024-10-21)

### 🎉 Características Principales Agregadas

#### 🐘 PostgreSQL
- ✅ Migración de SQLite a PostgreSQL
- ✅ Configuración de base de datos:
  - Database: `bingo`
  - User: `postgres`
  - Password: `123456`
- ✅ Dependencia `psycopg==3.1.18` agregada

#### 🏢 Sistema Multi-Tenant
- ✅ Modelo `Operator` para operadores/marcas
- ✅ Modelo `Player` para jugadores por operador
- ✅ Modelo `BingoSession` para sesiones organizadas
- ✅ Modelo `PlayerSession` para participación de jugadores
- ✅ Modelo `BingoCardExtended` para cartones con estados
- ✅ Modelo `BingoGameExtended` para partidas extendidas

#### 🎲 Pool de Cartones
- ✅ Operador define cantidad de cartones al crear sesión
- ✅ Cartones se generan una sola vez
- ✅ Jugadores seleccionan de cartones existentes
- ✅ Sistema de estados: available → reserved → sold
- ✅ Reutilización de cartones entre sesiones

#### 🎯 Bingo de 75 Bolas
- ✅ Soporte completo para bingo americano clásico
- ✅ Formato 5x5 con centro libre
- ✅ Validación de patrones ganadores
- ✅ Distribución B-I-N-G-O (1-15, 16-30, 31-45, 46-60, 61-75)

#### 📡 Nuevas APIs
- ✅ `/api/multi-tenant/operators/` - Gestión de operadores
- ✅ `/api/multi-tenant/players/` - Gestión de jugadores
- ✅ `/api/multi-tenant/sessions/` - Gestión de sesiones
- ✅ `/api/multi-tenant/cards/` - Gestión de cartones
- ✅ Endpoints para selección y compra de cartones
- ✅ Endpoints para reutilización de cartones
- ✅ Endpoints para WhatsApp/Telegram

#### 📱 Integración Social
- ✅ Registro por teléfono para WhatsApp
- ✅ Vinculación de cuentas de Telegram
- ✅ APIs específicas para bots

### 🔧 Correcciones de Bugs

#### Bug #1: MultipleObjectsReturned
- **Problema**: `register_by_phone` fallaba con jugadores duplicados
- **Solución**: Cambiado de `get_or_create()` a `filter().first()`
- **Archivo**: `bingo/views_multi_tenant.py`

#### Bug #2: AttributeError en BingoCardExtended
- **Problema**: `check_card_validity()` no accesible
- **Solución**: Implementado método directamente en la clase
- **Archivo**: `bingo/models.py`

#### Bug #3: Migraciones no aplicadas
- **Problema**: Tabla `bingo_operator` no existía
- **Solución**: Recrear BD y aplicar migraciones
- **Script**: `setup_postgresql.sh`

### 📚 Documentación

#### Documentación Unificada
- ✅ `DOCUMENTACION_COMPLETA.md` - Guía completa unificada
- ✅ `INICIO_RAPIDO.md` - Configuración en 3 pasos
- ✅ `GUIA_SOLUCION_PROBLEMAS.md` - Soluciones a errores
- ✅ `RESUMEN_PROYECTO.md` - Vista general
- ✅ `README.md` - Actualizado y simplificado

#### Documentación Antigua
- ✅ 9 archivos movidos a `docs_old/`
- ✅ Mantenidos como respaldo

### 🧪 Scripts Nuevos

- ✅ `cleanup_duplicates.py` - Limpiar datos duplicados
- ✅ `test_models.py` - Test de modelos multi-tenant
- ✅ `test_pool_simple.py` - Test de pool de cartones
- ✅ `demo_pool_cartones.py` - Demo del pool de cartones
- ✅ `demo_multi_tenant.py` - Demo multi-tenant
- ✅ `setup_postgresql.sh` - Configuración automática de PostgreSQL

### 📊 Estadísticas

- **Modelos**: 9 modelos (6 nuevos)
- **Endpoints**: 30+ APIs REST
- **Migraciones**: 3 migraciones aplicadas
- **Documentación**: 5 archivos principales
- **Scripts**: 10+ scripts de prueba y demo

---

## Versión 1.0 - Sistema Base (2024-10-20)

### Características Iniciales

- ✅ Generación de cartones de bingo
- ✅ Bingo de 90 bolas (Europeo)
- ✅ Bingo de 85 bolas (Americano)
- ✅ Validación de cartones
- ✅ Sistema de validación de ganadores
- ✅ API REST básica
- ✅ Extracción de bolas
- ✅ SQLite como base de datos

---

## 🔮 Próximas Versiones (Roadmap)

### Versión 2.1 (Planeada)

- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Sistema de notificaciones push
- [ ] Sistema de pagos integrado
- [ ] Analytics avanzados por operador
- [ ] Dashboard de administración web

### Versión 2.2 (Planeada)

- [ ] Multi-idioma (i18n)
- [ ] Sistema de torneos
- [ ] Rankings y leaderboards
- [ ] Sistema de premios automatizado
- [ ] Integración con pasarelas de pago

### Versión 3.0 (Futura)

- [ ] Machine Learning para detección de patrones
- [ ] Streaming de video de las partidas
- [ ] Chat en vivo durante partidas
- [ ] Sistema de afiliados
- [ ] App móvil nativa

---

## 🤝 Contribuciones

### Cómo Contribuir

1. Fork del repositorio
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Reporte de Bugs

Para reportar bugs, incluir:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Logs de error
- Versión del sistema

---

## 📄 Licencia

Este proyecto es un microservicio desarrollado para uso interno.

---

## 👥 Equipo de Desarrollo

- **Backend**: Django + PostgreSQL
- **APIs**: Django REST Framework
- **Base de Datos**: PostgreSQL
- **Integraciones**: WhatsApp, Telegram, Laravel/Vue

---

## 📞 Soporte

Para soporte técnico:
1. Revisar `GUIA_SOLUCION_PROBLEMAS.md`
2. Ejecutar scripts de prueba
3. Revisar logs de Django
4. Contactar al equipo de desarrollo

---

*Última actualización: 2024-10-21*  
*Versión actual: 2.0*  
*Estado: ✅ Producción Ready*
