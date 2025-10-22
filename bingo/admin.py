from django.contrib import admin
from .models import (
    BingoCard, BingoGame, DrawnBall,
    Operator, Player, BingoSession, PlayerSession,
    BingoCardExtended, BingoGameExtended, APIKey, WinningPattern,
    CardPack, PlayerCard, SessionCard
)


@admin.register(BingoCard)
class BingoCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'bingo_type', 'user_id', 'created_at']
    list_filter = ['bingo_type', 'created_at']
    search_fields = ['user_id']
    readonly_fields = ['id', 'created_at', 'numbers']
    
    def has_add_permission(self, request):
        # Los cartones se crean solo a través de la API
        return False
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['bingo_type', 'user_id']
        return self.readonly_fields


@admin.register(BingoGame)
class BingoGameAdmin(admin.ModelAdmin):
    list_display = ['id', 'game_type', 'name', 'is_active', 'created_at']
    list_filter = ['game_type', 'is_active', 'created_at']
    search_fields = ['name', 'id']
    readonly_fields = ['id', 'created_at']


@admin.register(DrawnBall)
class DrawnBallAdmin(admin.ModelAdmin):
    list_display = ['number', 'game', 'drawn_at']
    list_filter = ['game__game_type', 'drawn_at']
    search_fields = ['number', 'game__name']
    readonly_fields = ['id', 'drawn_at']


# === ADMIN PARA SISTEMA MULTI-TENANT ===

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'domain']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'domain', 'is_active')
        }),
        ('Branding', {
            'fields': ('logo_url', 'primary_color', 'secondary_color')
        }),
        ('Configuración de Bingo', {
            'fields': ('allowed_bingo_types', 'max_cards_per_player', 'max_cards_per_game')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['username', 'operator', 'email', 'is_active', 'is_verified', 'created_at']
    list_filter = ['operator', 'is_active', 'is_verified', 'created_at']
    search_fields = ['username', 'email', 'phone', 'whatsapp_id', 'telegram_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    fieldsets = (
        ('Información Básica', {
            'fields': ('operator', 'username', 'email', 'phone')
        }),
        ('Cuentas Sociales', {
            'fields': ('whatsapp_id', 'telegram_id')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        })
    )


@admin.register(BingoSession)
class BingoSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'bingo_type', 'status', 'scheduled_start', 'created_at']
    list_filter = ['operator', 'bingo_type', 'status', 'scheduled_start', 'created_at']
    search_fields = ['name', 'description', 'created_by']
    readonly_fields = ['id', 'actual_start', 'actual_end', 'created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('operator', 'name', 'description')
        }),
        ('Configuración', {
            'fields': ('bingo_type', 'max_players', 'entry_fee')
        }),
        ('Horarios', {
            'fields': ('scheduled_start', 'actual_start', 'actual_end')
        }),
        ('Estado y Configuración', {
            'fields': ('status', 'auto_start', 'auto_draw_interval', 'winning_patterns')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PlayerSession)
class PlayerSessionAdmin(admin.ModelAdmin):
    list_display = ['player', 'session', 'joined_at', 'cards_count', 'has_won', 'is_active']
    list_filter = ['session__operator', 'session__bingo_type', 'has_won', 'is_active', 'joined_at']
    search_fields = ['player__username', 'session__name']
    readonly_fields = ['id', 'joined_at', 'has_won', 'winning_cards', 'prize_amount']
    fieldsets = (
        ('Participación', {
            'fields': ('session', 'player', 'joined_at')
        }),
        ('Estado', {
            'fields': ('cards_count', 'is_active')
        }),
        ('Resultados', {
            'fields': ('has_won', 'winning_cards', 'prize_amount')
        }),
        ('Metadatos', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )


@admin.register(BingoCardExtended)
class BingoCardExtendedAdmin(admin.ModelAdmin):
    list_display = ['id', 'bingo_type', 'player', 'session', 'is_winner', 'created_at']
    list_filter = ['bingo_type', 'player__operator', 'session', 'is_winner', 'created_at']
    search_fields = ['player__username', 'session__name']
    readonly_fields = ['id', 'numbers', 'is_winner', 'winning_patterns', 'prize_amount', 'created_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('player', 'session', 'bingo_type')
        }),
        ('Cartón', {
            'fields': ('numbers',)
        }),
        ('Transacción', {
            'fields': ('purchase_price',)
        }),
        ('Resultados', {
            'fields': ('is_winner', 'winning_patterns', 'prize_amount')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False  # Los cartones se crean via API


@admin.register(BingoGameExtended)
class BingoGameExtendedAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'session', 'game_type', 'is_active', 'created_at']
    list_filter = ['operator', 'session', 'game_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('operator', 'session', 'name')
        }),
        ('Configuración', {
            'fields': ('game_type', 'is_active')
        }),
        ('Configuración Avanzada', {
            'fields': ('auto_draw', 'draw_interval', 'max_balls')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'key_preview', 'permission_level', 'is_active', 'last_used', 'created_at']
    list_filter = ['operator', 'permission_level', 'is_active', 'created_at']
    search_fields = ['name', 'key']
    readonly_fields = ['id', 'key', 'secret_hash', 'created_at', 'last_used']
    fieldsets = (
        ('Información Básica', {
            'fields': ('operator', 'name')
        }),
        ('Credenciales', {
            'fields': ('key', 'secret_hash'),
            'classes': ('collapse',)
        }),
        ('Permisos', {
            'fields': ('permission_level', 'is_active')
        }),
        ('Configuración', {
            'fields': ('allowed_ips', 'rate_limit', 'expires_at')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'last_used'),
            'classes': ('collapse',)
        })
    )
    
    def key_preview(self, obj):
        """Muestra preview de la key"""
        return f"{obj.key[:8]}..." if obj.key else ""
    key_preview.short_description = 'API Key'


@admin.register(WinningPattern)
class WinningPatternAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'compatible_with', 'prize_multiplier', 'has_jackpot', 'is_active', 'is_system']
    list_filter = ['category', 'compatible_with', 'is_active', 'is_system', 'has_jackpot']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'description', 'category')
        }),
        ('Configuración', {
            'fields': ('compatible_with', 'pattern_type', 'pattern_data')
        }),
        ('Premio', {
            'fields': ('prize_multiplier', 'has_jackpot', 'jackpot_max_balls')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_system', 'operator')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Los patrones del sistema no se pueden modificar"""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and obj.is_system:
            readonly.extend(['code', 'pattern_type', 'is_system'])
        return readonly


# === ADMIN PARA SISTEMA DE REUTILIZACIÓN DE CARTAS ===

@admin.register(CardPack)
class CardPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'operator', 'bingo_type', 'category', 'total_cards', 'cards_generated', 'is_active', 'created_at']
    list_filter = ['operator', 'bingo_type', 'category', 'is_active', 'cards_generated', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'cards_generated', 'created_at', 'updated_at', 'cards_count_display']
    fieldsets = (
        ('Información Básica', {
            'fields': ('operator', 'name', 'description', 'bingo_type')
        }),
        ('Configuración', {
            'fields': ('total_cards', 'cards_generated', 'cards_count_display', 'category')
        }),
        ('Precio y Disponibilidad', {
            'fields': ('price_per_card', 'is_active', 'is_public')
        }),
        ('Metadatos', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def cards_count_display(self, obj):
        """Muestra el conteo actual de cartas"""
        return f"{obj.get_cards_count()} / {obj.total_cards}"
    cards_count_display.short_description = 'Cartas Generadas'
    
    actions = ['generate_cards_action']
    
    def generate_cards_action(self, request, queryset):
        """Acción para generar cartas para packs seleccionados"""
        success_count = 0
        for pack in queryset:
            if not pack.cards_generated:
                success, message = pack.generate_cards()
                if success:
                    success_count += 1
        
        self.message_user(request, f"{success_count} packs procesados exitosamente")
    generate_cards_action.short_description = "Generar cartas para los packs seleccionados"


@admin.register(PlayerCard)
class PlayerCardAdmin(admin.ModelAdmin):
    list_display = ['player', 'card_serial', 'pack', 'acquisition_type', 'times_used', 'times_won', 'is_favorite', 'acquired_at']
    list_filter = ['player__operator', 'pack', 'acquisition_type', 'is_favorite', 'acquired_at']
    search_fields = ['player__username', 'card__serial_number', 'nickname']
    readonly_fields = ['id', 'acquired_at', 'last_used_at', 'times_used', 'times_won', 'total_prizes']
    fieldsets = (
        ('Relaciones', {
            'fields': ('player', 'card', 'pack')
        }),
        ('Adquisición', {
            'fields': ('acquisition_type', 'purchase_price', 'acquired_at')
        }),
        ('Personalización', {
            'fields': ('is_favorite', 'nickname')
        }),
        ('Estadísticas', {
            'fields': ('times_used', 'times_won', 'total_prizes', 'last_used_at')
        }),
        ('Metadatos', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )
    
    def card_serial(self, obj):
        """Muestra el serial number de la carta"""
        return obj.card.serial_number or f"#{obj.card.card_number}"
    card_serial.short_description = 'Carta'


@admin.register(SessionCard)
class SessionCardAdmin(admin.ModelAdmin):
    list_display = ['session', 'player', 'card_serial', 'status', 'is_winner', 'prize_amount', 'joined_at']
    list_filter = ['session__operator', 'status', 'is_winner', 'joined_at']
    search_fields = ['session__name', 'player__username', 'card__serial_number']
    readonly_fields = ['id', 'joined_at', 'finished_at', 'marked_numbers', 'is_winner', 'winning_patterns', 'prize_amount']
    fieldsets = (
        ('Relaciones', {
            'fields': ('session', 'player', 'card')
        }),
        ('Estado', {
            'fields': ('status', 'joined_at', 'finished_at')
        }),
        ('Juego', {
            'fields': ('marked_numbers',)
        }),
        ('Resultados', {
            'fields': ('is_winner', 'winning_patterns', 'prize_amount')
        }),
        ('Metadatos', {
            'fields': ('id',),
            'classes': ('collapse',)
        })
    )
    
    def card_serial(self, obj):
        """Muestra el serial number de la carta"""
        return obj.card.serial_number or f"#{obj.card.card_number}"
    card_serial.short_description = 'Carta'
    
    def has_add_permission(self, request):
        return False  # Las SessionCard se crean via API