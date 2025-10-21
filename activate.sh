#!/bin/bash
# Script para activar el entorno virtual del microservicio de bingo

echo "🎲 Activando entorno virtual del Microservicio de Bingo..."
echo "=================================================="

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Error: El entorno virtual no existe."
    echo "   Ejecuta: python3 -m venv venv"
    exit 1
fi

# Activar el entorno virtual
source venv/bin/activate

echo "✅ Entorno virtual activado"
echo "📍 Directorio: $(pwd)"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"
echo ""
echo "📋 Comandos útiles:"
echo "   python manage.py runserver     # Iniciar servidor"
echo "   python manage.py migrate       # Aplicar migraciones"
echo "   python demo.py                 # Ejecutar demo"
echo "   python demo_winner.py          # Demo de ganadores"
echo ""
echo "🚀 Para salir del entorno virtual: deactivate"
echo "=================================================="
