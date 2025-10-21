# 🔧 Guía de Solución de Problemas

## ❌ Error: "AttributeError: 'BingoCardExtended' object has no attribute 'check_card_validity'"

### Problema
```
AttributeError at /api/multi-tenant/sessions/.../available-cards/
'BingoCardExtended' object has no attribute 'check_card_validity'
```

### Causa
Problema de herencia en Django cuando se usa herencia de modelos Multi-Table.

### Solución
✅ **Ya corregido** - El método `check_card_validity()` ahora está implementado directamente en `BingoCardExtended`.

Si encuentras este error, asegúrate de tener la última versión del código.

---

## ❌ Error: "MultipleObjectsReturned"

### Problema
```
MultipleObjectsReturned at /api/multi-tenant/players/register-by-phone/
get() returned more than one Player -- it returned 3!
```

### Causa
Hay múltiples jugadores con el mismo teléfono en la base de datos (generalmente de demos o pruebas).

### Solución

**Opción 1: Limpiar datos duplicados**
```bash
python3 cleanup_duplicates.py
```

**Opción 2: Limpiar manualmente**
```bash
python3 manage.py shell
```
```python
from bingo.models import Player
# Ver duplicados
Player.objects.values('operator', 'phone').annotate(count=Count('id')).filter(count__gt=1)
# Eliminar duplicados manualmente
```

**Opción 3: Recrear base de datos**
```bash
python3 manage.py flush
python3 manage.py migrate
```

### ✅ Corrección Aplicada

El código fue actualizado para usar `.filter().first()` en lugar de `.get()`, lo que evita el error.

---

## ❌ Error: "no such table: bingo_operator"

### Problema
```
OperationalError at /api/multi-tenant/operators/
no such table: bingo_operator
```

### Causa
Las migraciones no han sido aplicadas a la base de datos.

### Solución

```bash
# Aplicar migraciones
python3 manage.py migrate

# Si no funciona, crear migraciones primero
python3 manage.py makemigrations
python3 manage.py migrate
```

---

## ❌ Error: PostgreSQL Connection Failed

### Problema
```
django.db.utils.OperationalError: could not connect to server
```

### Solución

**1. Verificar que PostgreSQL está corriendo**
```bash
sudo systemctl status postgresql
```

**2. Iniciar PostgreSQL si está detenido**
```bash
sudo systemctl start postgresql
```

**3. Verificar que la base de datos existe**
```bash
psql -U postgres -l | grep bingo
```

**4. Crear base de datos si no existe**
```bash
createdb -U postgres bingo
```

**5. Configurar contraseña del usuario**
```bash
sudo -u postgres psql
# Dentro de psql:
ALTER USER postgres WITH PASSWORD '123456';
\q
```

**6. Usar script de configuración automática**
```bash
./setup_postgresql.sh
```

---

## ❌ Error: Puerto en Uso

### Problema
```
Error: That port is already in use.
```

### Solución

**Opción 1: Usar otro puerto**
```bash
python3 manage.py runserver 8001
```

**Opción 2: Matar proceso en el puerto**
```bash
# Encontrar proceso
lsof -i :8000

# Matar proceso
kill -9 [PID]
```

**Opción 3: Usar pkill**
```bash
pkill -f runserver
```

---

## ❌ Error: psycopg no instalado

### Problema
```
django.core.exceptions.ImproperlyConfigured: 
Error loading psycopg2 or psycopg module
```

### Solución

```bash
pip install psycopg==3.1.18
```

Si falla, probar con:
```bash
pip install psycopg2-binary
```

---

## ❌ Error: Migraciones Desincronizadas

### Problema
```
Your models have changes that are not yet reflected in a migration
```

### Solución

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

---

## 🔄 Resetear Sistema Completo

Si quieres empezar desde cero:

```bash
# 1. Eliminar base de datos PostgreSQL
dropdb -U postgres bingo

# 2. Crear nueva base de datos
createdb -U postgres bingo

# 3. Aplicar migraciones
python3 manage.py migrate

# 4. Crear superusuario
python3 manage.py createsuperuser

# 5. Iniciar servidor
python3 manage.py runserver
```

---

## 🧹 Limpiar Datos de Demo

```bash
# Limpiar datos duplicados y de demos
python3 cleanup_duplicates.py

# Limpiar completamente la base de datos
python3 manage.py flush
```

---

## 🔍 Verificar Estado del Sistema

### Verificar Migraciones

```bash
python3 manage.py showmigrations bingo
```

Deberías ver todas con `[X]`:
```
bingo
 [X] 0001_initial
 [X] 0002_bingogame_drawnball
 [X] 0003_operator_alter_bingocard_bingo_type_and_more
```

### Verificar Base de Datos

```bash
python3 manage.py dbshell
```
```sql
\dt bingo_*
\q
```

### Verificar Modelos

```bash
python3 test_models.py
```

---

## 📞 Ayuda Adicional

Si ninguna de estas soluciones funciona:

1. **Revisar logs de Django**
   - Los errores detallados aparecen en la consola

2. **Revisar configuración**
   - `bingo_service/settings.py` - Configuración de base de datos
   - `requirements.txt` - Dependencias instaladas

3. **Ejecutar scripts de prueba**
   - `test_models.py`
   - `test_pool_simple.py`
   - `test_register_phone.py`

4. **Leer documentación completa**
   - `DOCUMENTACION_COMPLETA.md`

---

## ✅ Checklist de Troubleshooting

- [ ] PostgreSQL está corriendo
- [ ] Base de datos 'bingo' existe
- [ ] Usuario 'postgres' tiene contraseña configurada
- [ ] Dependencia `psycopg` está instalada
- [ ] Migraciones aplicadas (`python3 manage.py migrate`)
- [ ] No hay datos duplicados (`cleanup_duplicates.py`)
- [ ] Puerto 8000 está disponible
- [ ] Configuración correcta en `settings.py`

---

¡Con esta guía deberías poder resolver cualquier problema que surja! 🚀
