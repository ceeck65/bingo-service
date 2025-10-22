# 🎴 Propuesta: Sistema de Reutilización de Cartas

## 🎯 Problema Identificado

Actualmente, el sistema genera cartas **nuevas para cada sesión**, lo que impide:

❌ **Jugadores NO pueden reutilizar sus cartas favoritas**  
❌ **Operadores deben generar cartas cada vez**  
❌ **No hay concepto de "mi colección de cartas"**  
❌ **No se aprovecha el campo `allow_card_reuse`**

---

## 💡 Solución Propuesta

### 1. **Card Packs (Paquetes de Cartas)**

Crear un sistema de **packs de cartas reutilizables** que:

✅ Los operadores pueden crear **paquetes de cartas** (ej: "Pack Clásico 75", "Pack Premium 90")  
✅ Los jugadores pueden **comprar/recibir cartas** de estos packs  
✅ Las cartas se **reutilizan** en múltiples sesiones  
✅ Las sesiones pueden usar cartas de **packs existentes** o generar nuevas

---

## 🏗️ Arquitectura

### Modelo: `CardPack`

```python
class CardPack(models.Model):
    """Paquetes de cartas reutilizables"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    
    # Información básica
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    bingo_type = models.CharField(max_length=10, choices=BingoCard.BINGO_TYPES)
    
    # Configuración
    total_cards = models.IntegerField(default=100)
    cards_generated = models.BooleanField(default=False)
    
    # Precio y disponibilidad
    price_per_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)  # Visible para todos los jugadores
    
    # Categoría
    CATEGORY_CHOICES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='basic')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Modelo: `PlayerCard` (Nueva tabla intermedia)

```python
class PlayerCard(models.Model):
    """Cartas que pertenecen a los jugadores"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='owned_cards')
    card = models.ForeignKey(BingoCardExtended, on_delete=models.CASCADE, related_name='owners')
    pack = models.ForeignKey(CardPack, on_delete=models.SET_NULL, null=True)
    
    # Información de adquisición
    acquired_at = models.DateTimeField(auto_now_add=True)
    acquisition_type = models.CharField(max_length=20)  # 'purchase', 'gift', 'reward'
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Estadísticas
    times_used = models.IntegerField(default=0)
    times_won = models.IntegerField(default=0)
    total_prizes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Favoritos
    is_favorite = models.BooleanField(default=False)
    nickname = models.CharField(max_length=50, blank=True)  # "Mi carta de la suerte"
```

### Modelo: `SessionCard` (Tabla de relación)

```python
class SessionCard(models.Model):
    """Cartas activas en una sesión"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(BingoSession, on_delete=models.CASCADE, related_name='session_cards')
    card = models.ForeignKey(BingoCardExtended, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    # Estado en la sesión
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('playing', 'Jugando'),
        ('won', 'Ganadora'),
        ('finished', 'Finalizada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Números marcados en esta sesión
    marked_numbers = models.JSONField(default=list)
    
    # Resultado
    is_winner = models.BooleanField(default=False)
    winning_patterns = models.JSONField(default=list)
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session', 'card', 'player']
```

### Modificar: `BingoCardExtended`

```python
class BingoCardExtended(BingoCard):
    """Extensión del modelo BingoCard"""
    # Relación con pack (en lugar de sesión directa)
    pack = models.ForeignKey(CardPack, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    
    # DEPRECATED: session (ahora se usa SessionCard)
    # session = models.ForeignKey(BingoSession, ...)  # Mantener por compatibilidad
    
    # Información de la carta
    card_number = models.IntegerField(default=0)
    serial_number = models.CharField(max_length=50, unique=True)  # "PACK-001-CARD-0042"
    
    # Estadísticas globales
    total_sessions = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    
    # Metadatos
    is_reusable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Modificar: `BingoSession`

```python
class BingoSession(models.Model):
    # ... campos existentes ...
    
    # Configuración de cartas
    card_source = models.CharField(
        max_length=20,
        choices=[
            ('generate', 'Generar nuevas cartas'),
            ('pack', 'Usar cartas de un pack'),
            ('player_cards', 'Jugadores usan sus propias cartas'),
        ],
        default='player_cards'
    )
    
    # Si card_source='pack', especificar el pack
    card_pack = models.ForeignKey(CardPack, on_delete=models.SET_NULL, null=True, blank=True)
    
    # DEPRECATED: total_cards, cards_generated, allow_card_reuse
    # Mantener por compatibilidad pero marcar como obsoletos
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: **Operador crea Pack de Cartas**

```
1. POST /api/multi-tenant/card-packs/
   {
     "operator": "uuid",
     "name": "Pack Clásico 75",
     "bingo_type": "75",
     "total_cards": 500,
     "category": "free",
     "is_public": true
   }

2. POST /api/multi-tenant/card-packs/{pack_id}/generate-cards/
   → Genera 500 cartas con serial numbers únicos
   
3. Cartas disponibles para todos los jugadores del operador
```

### Flujo 2: **Jugador adquiere Cartas**

```
1. GET /api/multi-tenant/card-packs/
   → Lista packs disponibles

2. POST /api/multi-tenant/players/{player_id}/acquire-cards/
   {
     "pack_id": "uuid",
     "quantity": 3,
     "acquisition_type": "purchase"
   }
   
3. Sistema:
   - Selecciona 3 cartas del pack
   - Crea registros en PlayerCard
   - Jugador ahora "posee" esas 3 cartas
```

### Flujo 3: **Jugador se une a Sesión con sus Cartas**

```
1. GET /api/multi-tenant/players/{player_id}/cards/
   → Lista sus cartas disponibles

2. POST /api/multi-tenant/sessions/{session_id}/join/
   {
     "player_id": "uuid",
     "card_ids": ["card-uuid-1", "card-uuid-2"]
   }
   
3. Sistema:
   - Verifica que las cartas pertenecen al jugador
   - Verifica que las cartas son del tipo correcto (75/90)
   - Crea registros en SessionCard
   - Jugador listo para jugar con sus cartas
```

### Flujo 4: **Sesión con Pack Compartido**

```
1. POST /api/multi-tenant/sessions/
   {
     "card_source": "pack",
     "card_pack": "uuid-pack"
   }

2. POST /api/multi-tenant/sessions/{session_id}/join/
   {
     "player_id": "uuid",
     "cards_from_pack": 2  # Asignar 2 cartas del pack
   }
   
3. Sistema:
   - Asigna cartas del pack automáticamente
   - Las cartas se "alquilan" para esta sesión
   - Al terminar, vuelven al pool del pack
```

### Flujo 5: **Sesión con Cartas Generadas** (modo actual)

```
1. POST /api/multi-tenant/sessions/
   {
     "card_source": "generate",
     "total_cards": 100
   }

2. POST /api/multi-tenant/sessions/{session_id}/generate-cards/
   → Genera cartas desechables para esta sesión
   → Compatible con el sistema actual
```

---

## 📊 Ventajas del Nuevo Sistema

### Para Jugadores

✅ **Colección personal** de cartas  
✅ **Reutilizan sus cartas favoritas** en múltiples sesiones  
✅ **Estadísticas por carta** (veces usada, veces ganada)  
✅ **Apego emocional** ("mi carta de la suerte")  
✅ **Pueden regalar/intercambiar** cartas (futuro)

### Para Operadores

✅ **No generan cartas cada vez** (ahorro de recursos)  
✅ **Packs reutilizables** para múltiples sesiones  
✅ **Control de inventario** de cartas  
✅ **Pueden vender cartas premium**  
✅ **Diferentes categorías** (gratuitas, premium, VIP)

### Para el Sistema

✅ **Escalable**: Un pack de 1000 cartas sirve para miles de sesiones  
✅ **Flexible**: Soporta 3 modos (generar, pack, cartas propias)  
✅ **Retrocompatible**: Mantiene el sistema actual funcionando  
✅ **Optimizado**: No genera datos innecesarios

---

## 🚀 Plan de Implementación

### Fase 1: **Modelos y Migraciones** ⏱️ 30 min
- [x] Crear modelo `CardPack`
- [ ] Crear modelo `PlayerCard`
- [ ] Crear modelo `SessionCard`
- [ ] Modificar `BingoCardExtended`
- [ ] Modificar `BingoSession`
- [ ] Crear migraciones

### Fase 2: **Serializers y Validators** ⏱️ 20 min
- [ ] `CardPackSerializer`
- [ ] `PlayerCardSerializer`
- [ ] `SessionCardSerializer`
- [ ] Validators para adquisición de cartas

### Fase 3: **Endpoints Básicos** ⏱️ 40 min
- [ ] CRUD de `CardPack`
- [ ] Generar cartas para pack
- [ ] Listar packs disponibles
- [ ] Ver cartas de un pack

### Fase 4: **Sistema de Adquisición** ⏱️ 30 min
- [ ] Jugador adquiere cartas
- [ ] Listar cartas del jugador
- [ ] Marcar cartas como favoritas
- [ ] Estadísticas de cartas

### Fase 5: **Integración con Sesiones** ⏱️ 40 min
- [ ] Modificar endpoint de join
- [ ] Usar cartas propias en sesión
- [ ] Usar cartas de pack en sesión
- [ ] Actualizar estadísticas al terminar

### Fase 6: **Retrocompatibilidad** ⏱️ 20 min
- [ ] Mantener endpoint de generate-cards
- [ ] Migrar sesiones existentes
- [ ] Documentación de migración

### Fase 7: **Documentación y Tests** ⏱️ 30 min
- [ ] Documentar nuevos endpoints
- [ ] Ejemplos de integración
- [ ] Tests de flujos completos
- [ ] Guía de migración

**Tiempo Total Estimado:** ~3.5 horas

---

## 📝 Ejemplos de Uso

### Crear Pack Gratuito

```bash
curl -X POST http://localhost:8000/api/multi-tenant/card-packs/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operator": "uuid-operador",
    "name": "Pack Inicial Gratis",
    "bingo_type": "75",
    "total_cards": 100,
    "category": "free",
    "is_public": true
  }'
```

### Generar Cartas para Pack

```bash
curl -X POST http://localhost:8000/api/multi-tenant/card-packs/{pack_id}/generate-cards/ \
  -H "Authorization: Bearer $TOKEN"
```

### Jugador Adquiere Cartas

```bash
curl -X POST http://localhost:8000/api/multi-tenant/players/{player_id}/acquire-cards/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pack_id": "uuid-pack",
    "quantity": 5,
    "acquisition_type": "gift"
  }'
```

### Ver Mis Cartas

```bash
curl -X GET http://localhost:8000/api/multi-tenant/players/{player_id}/cards/ \
  -H "Authorization: Bearer $TOKEN"
```

### Unirse a Sesión con Mis Cartas

```bash
curl -X POST http://localhost:8000/api/multi-tenant/sessions/{session_id}/join/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "player_id": "uuid-player",
    "card_ids": ["uuid-card-1", "uuid-card-2"]
  }'
```

---

## ⚠️ Consideraciones

### Migración de Datos Existentes

```python
# Script de migración
def migrate_existing_sessions():
    """Migra sesiones existentes al nuevo sistema"""
    for session in BingoSession.objects.filter(cards_generated=True):
        # Crear un pack "legacy" para esta sesión
        pack = CardPack.objects.create(
            operator=session.operator,
            name=f"Pack Legacy - {session.name}",
            bingo_type=session.bingo_type,
            total_cards=session.total_cards,
            category='basic',
            is_public=False,
            cards_generated=True
        )
        
        # Asociar cartas existentes al pack
        session.cards.update(pack=pack)
        
        # Actualizar sesión
        session.card_source = 'pack'
        session.card_pack = pack
        session.save()
```

### Validaciones Importantes

✅ Verificar que la carta es del tipo correcto (75/90)  
✅ Verificar que el jugador posee la carta  
✅ Verificar que la carta no está en otra sesión activa  
✅ Limitar cantidad de cartas por jugador/sesión  
✅ Prevenir duplicados en la misma sesión

---

## 🎯 Conclusión

Este sistema proporciona:

1. **Flexibilidad**: 3 modos de operación (generar, pack, cartas propias)
2. **Reutilización**: Las cartas se pueden usar infinitas veces
3. **Colección**: Jugadores tienen su propia colección
4. **Estadísticas**: Tracking por carta y por jugador
5. **Escalabilidad**: Un pack sirve para miles de sesiones
6. **Retrocompatibilidad**: El sistema actual sigue funcionando

**¿Procedemos con la implementación?**

