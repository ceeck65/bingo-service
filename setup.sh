#!/bin/bash
# Script de configuración inicial del microservicio de bingo

echo "🎲 Configurando Microservicio de Bingo..."
echo "========================================="

# Verificar si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Aplicar migraciones
echo "🗄️  Aplicando migraciones de base de datos..."
python manage.py migrate

echo ""
echo "🎉 ¡Configuración completada!"
echo "========================================="
echo ""
echo "📋 Para usar el proyecto:"
echo "   1. Activar entorno: source venv/bin/activate"
echo "   2. Iniciar servidor: python manage.py runserver"
echo "   3. Ejecutar demo: python demo.py"
echo ""
echo "🚀 O usar el script de activación: ./activate.sh"
echo "========================================="
