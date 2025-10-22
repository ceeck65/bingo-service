#!/usr/bin/env python3
"""
Script para inicializar los patrones de victoria del sistema
"""

import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_service.settings')
django.setup()

from bingo.models import WinningPattern

print("🎯 INICIALIZAR PATRONES DE VICTORIA")
print("=" * 70)

# Crear patrones del sistema
created_count = WinningPattern.create_system_patterns()

print(f"\n✅ Patrones creados: {created_count}")

# Mostrar todos los patrones
all_patterns = WinningPattern.objects.all().order_by('category', 'name')

print(f"\n📋 PATRONES DISPONIBLES: {all_patterns.count()}")
print("=" * 70)

for pattern in all_patterns:
    print(f"\n🎲 {pattern.name}")
    print(f"   Código: {pattern.code}")
    print(f"   Categoría: {pattern.get_category_display()}")
    print(f"   Compatible: {pattern.get_compatible_with_display()}")
    print(f"   Multiplicador: x{pattern.prize_multiplier}")
    if pattern.has_jackpot:
        print(f"   🎰 Jackpot: Sí (máx {pattern.jackpot_max_balls} bolas)")
    print(f"   Descripción: {pattern.description}")

print("\n" + "=" * 70)
print("✅ Inicialización completada")

