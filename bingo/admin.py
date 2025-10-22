from django.contrib import admin
from .models import (
    BingoCard, BingoGame, DrawnBall,
    Operator, Player, BingoSession, PlayerSession,
    BingoCardExtended, BingoGameExtended, APIKey, WinningPattern
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