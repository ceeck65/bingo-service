# 🎲 Microservicio de Bingo

> **Sistema Multi-Tenant con Pool de Cartones para Laravel/Vue, WhatsApp y Telegram**

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

```bash
python manage.py migrate
```

### 3. Crear Credenciales de API

```bash
python create_api_key.py
```

Este script te guiará para crear tu primera API Key y mostrará las credenciales.

### 4. Obtener Token JWT

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "tu-api-key",
    "api_secret": "tu-api-secret"
  }'
```

### 5. Usar la API

```bash
curl http://localhost:8000/api/multi-tenant/sessions/ \
  -H "Authorization: Bearer tu-token-jwt"
```

---

## 🚀 Inicio Rápido (Detallado)

### Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar PostgreSQL
# Database: bingo
# User: postgres
# Password: 123456

# 3. Aplicar migraciones
python3 manage.py migrate

# 4. Iniciar servidor
python3 manage.py runserver
```

### Primer Uso

```bash
# Crear operador
curl -X POST http://localhost:8000/api/multi-tenant/operators/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Bingo",
    "code": "mibingo",
    "allowed_bingo_types": ["75", "85", "90"]
  }'

# Crear sesión con 50 cartones
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
```

---

## 📚 Documentación

| Documento | Contenido |
|-----------|-----------|
| **[PRIMEROS_PASOS.md](PRIMEROS_PASOS.md)** | 🚀 Guía completa desde cero (EMPIEZA AQUÍ) |
| **[INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md)** | 📑 Índice completo de documentación |
| **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** | ⚡ Configuración en 3 pasos |
| **[DOCUMENTACION_COMPLETA.md](DOCUMENTACION_COMPLETA.md)** | 📚 Guía completa del sistema |
| **[ENDPOINTS_API.md](ENDPOINTS_API.md)** | 📡 Referencia de 48+ endpoints |
| **[MULTIPLES_CARTONES.md](MULTIPLES_CARTONES.md)** | 🎲 Múltiples cartones por jugador |
| **[EXTRACCION_BOLAS.md](EXTRACCION_BOLAS.md)** | 🎯 Sistema de extracción de bolas |
| **[AUTENTICACION_JWT.md](AUTENTICACION_JWT.md)** | 🔐 Sistema de autenticación JWT Bearer Token |
| **[RESUMEN_JWT.md](RESUMEN_JWT.md)** | ⚡ Resumen rápido de JWT |
| **[GUIA_SOLUCION_PROBLEMAS.md](GUIA_SOLUCION_PROBLEMAS.md)** | 🔧 Soluciones a errores comunes |
| **[RESUMEN_PROYECTO.md](RESUMEN_PROYECTO.md)** | 🎯 Vista general del proyecto |
| **[CHANGELOG.md](CHANGELOG.md)** | 📝 Registro de cambios |

---

## 🎯 Características Principales

### Sistema Multi-Tenant
- 🏢 Múltiples operadores con datos aislados
- 👥 Jugadores únicos por operador
- 🎨 Branding personalizado
- ⚙️ Configuraciones flexibles

### Pool de Cartones
- 🎲 Operador define cantidad de cartones
- 📊 Jugadores seleccionan cartones existentes
- 🔄 Reutilización entre sesiones
- 📈 Trazabilidad completa

### 3 Tipos de Bingo
- 🇺🇸 75 bolas (Americano clásico)
- 🇺🇸 85 bolas (Americano extendido)
- 🇪🇺 90 bolas (Europeo)

### Integración
- 🌐 Laravel/Vue
- 📱 WhatsApp Business API
- 📱 Telegram Bot API

---

## 🗄️ Base de Datos

### PostgreSQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bingo',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📡 Endpoints Principales

### Operadores
- `GET /api/multi-tenant/operators/`
- `POST /api/multi-tenant/operators/`

### Jugadores
- `GET /api/multi-tenant/players/`
- `POST /api/multi-tenant/players/`
- `POST /api/multi-tenant/players/register-by-phone/`

### Sesiones
- `GET /api/multi-tenant/sessions/`
- `POST /api/multi-tenant/sessions/`
- `GET /api/multi-tenant/sessions/{id}/available-cards/`

### Cartones
- `POST /api/multi-tenant/cards/generate-for-session/`
- `POST /api/multi-tenant/cards/select/`
- `POST /api/multi-tenant/cards/confirm-purchase/`

**[Ver API completa en la documentación](DOCUMENTACION_COMPLETA.md#-api-rest---endpoints)**

---

## 🧪 Scripts de Prueba

```bash
# Test de modelos
python3 test_models.py

# Demo pool de cartones
python3 demo_pool_cartones.py

# Demo multi-tenant
python3 demo_multi_tenant.py
```

---

## 🔧 Solución de Problemas

### Migraciones

```bash
python3 manage.py migrate
```

### PostgreSQL

```bash
# Verificar estado
sudo systemctl status postgresql

# Crear base de datos
createdb -U postgres bingo
```

**[Ver más soluciones](DOCUMENTACION_COMPLETA.md#-solución-de-problemas)**

---

## 📁 Estructura

```
bingo_service/
├── bingo/                      # App principal
├── bingo_service/              # Configuración
├── requirements.txt            # Dependencias
├── DOCUMENTACION_COMPLETA.md   # Documentación unificada
└── README.md                   # Este archivo
```

---

## 🎉 ¡Listo para Producción!

✅ Sistema multi-tenant completo  
✅ Pool de cartones optimizado  
✅ 3 tipos de bingo soportados  
✅ APIs completas para integración  
✅ PostgreSQL como base de datos  
✅ Documentación exhaustiva  

**[👉 Leer Documentación Completa](DOCUMENTACION_COMPLETA.md)**

---

*Microservicio de Bingo v2.0 - Con PostgreSQL*