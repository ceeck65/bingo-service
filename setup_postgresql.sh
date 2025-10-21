#!/bin/bash
# Script para configurar PostgreSQL para el microservicio de bingo

echo "🐘 Configuración de PostgreSQL para Microservicio de Bingo"
echo "=========================================================="

# Verificar que PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL no está instalado"
    echo "   Instalar con: sudo dnf install postgresql postgresql-server"
    exit 1
fi

echo "✅ PostgreSQL instalado"

# Verificar que PostgreSQL está corriendo
if ! sudo systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL no está corriendo"
    echo "   Intentando iniciar..."
    sudo systemctl start postgresql
    
    if sudo systemctl is-active --quiet postgresql; then
        echo "✅ PostgreSQL iniciado"
    else
        echo "❌ No se pudo iniciar PostgreSQL"
        exit 1
    fi
else
    echo "✅ PostgreSQL está corriendo"
fi

# Crear base de datos
echo ""
echo "📁 Creando base de datos 'bingo'..."

sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = 'bingo'" | grep -q 1

if [ $? -eq 0 ]; then
    echo "📋 La base de datos 'bingo' ya existe"
else
    sudo -u postgres createdb bingo
    if [ $? -eq 0 ]; then
        echo "✅ Base de datos 'bingo' creada"
    else
        echo "❌ Error al crear la base de datos"
        exit 1
    fi
fi

# Configurar usuario y contraseña
echo ""
echo "👤 Configurando usuario postgres..."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '123456';"

if [ $? -eq 0 ]; then
    echo "✅ Contraseña del usuario postgres configurada"
else
    echo "⚠️  No se pudo configurar la contraseña"
fi

# Aplicar migraciones
echo ""
echo "🔄 Aplicando migraciones..."
python3 manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Migraciones aplicadas correctamente"
else
    echo "❌ Error al aplicar migraciones"
    exit 1
fi

echo ""
echo "=========================================================="
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=========================================================="
echo ""
echo "Base de datos: bingo"
echo "Usuario: postgres"
echo "Contraseña: 123456"
echo "Host: localhost"
echo "Puerto: 5432"
echo ""
echo "🚀 Para iniciar el servidor:"
echo "   python3 manage.py runserver"
echo ""
echo "=========================================================="

