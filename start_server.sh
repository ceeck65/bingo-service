#!/bin/bash
# Script para iniciar el servidor de bingo

echo "🎲 Iniciando Microservicio de Bingo..."
echo "======================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encontró manage.py"
    echo "   Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Verificar que Django está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado"

# Aplicar migraciones si es necesario
echo "🔄 Aplicando migraciones..."
python3 manage.py migrate

# Iniciar el servidor
echo "🚀 Iniciando servidor en http://localhost:8000"
echo "   Presiona Ctrl+C para detener el servidor"
echo "======================================"

python3 manage.py runserver
