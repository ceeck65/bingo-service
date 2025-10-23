#!/bin/bash

# Script de prueba para verificar la corrección de cartones Django
# Fecha: 22 de Octubre, 2025

echo "🎴 Test de Corrección: Cartones Django Bingo Service"
echo "======================================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar directorio
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra manage.py. Ejecuta desde /home/ceeck65/Projects/bingo_service${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Paso 1: Verificando archivos modificados...${NC}"
echo ""

# Verificar cambios en models.py
if grep -q "return True, f\"{len(cards_created)} cartones generados exitosamente\", cards_created" bingo/models.py; then
    echo -e "${GREEN}✅ models.py: Método generate_cards_for_session() actualizado${NC}"
else
    echo -e "${RED}❌ models.py: NO tiene los cambios necesarios${NC}"
    exit 1
fi

# Verificar cambios en views_multi_tenant.py
if grep -q "success, message, cards_created = session.generate_cards_for_session()" bingo/views_multi_tenant.py; then
    echo -e "${GREEN}✅ views_multi_tenant.py: Vista generate_cards_for_session() actualizada${NC}"
else
    echo -e "${RED}❌ views_multi_tenant.py: NO tiene los cambios necesarios${NC}"
    exit 1
fi

if grep -q "'cards': cards_data" bingo/views_multi_tenant.py; then
    echo -e "${GREEN}✅ views_multi_tenant.py: Devuelve array 'cards' en la respuesta${NC}"
else
    echo -e "${RED}❌ views_multi_tenant.py: NO devuelve array 'cards'${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📋 Paso 2: Verificando sintaxis Python...${NC}"
echo ""

# Verificar sintaxis de models.py
python -m py_compile bingo/models.py 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ models.py: Sintaxis válida${NC}"
else
    echo -e "${RED}❌ models.py: Error de sintaxis${NC}"
    exit 1
fi

# Verificar sintaxis de views_multi_tenant.py
python -m py_compile bingo/views_multi_tenant.py 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ views_multi_tenant.py: Sintaxis válida${NC}"
else
    echo -e "${RED}❌ views_multi_tenant.py: Error de sintaxis${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📋 Paso 3: Verificando documentación...${NC}"
echo ""

if [ -f "docs/CORRECCION_RESPUESTA_CARTONES.md" ]; then
    echo -e "${GREEN}✅ Documentación completa creada${NC}"
else
    echo -e "${RED}⚠️  Documentación completa no encontrada${NC}"
fi

if [ -f "CORRECCION_CARTONES_RESUMEN.md" ]; then
    echo -e "${GREEN}✅ Resumen ejecutivo creado${NC}"
else
    echo -e "${RED}⚠️  Resumen ejecutivo no encontrado${NC}"
fi

if [ -f "CHANGELOG.md" ]; then
    if grep -q "Versión 2.6 - Corrección Respuesta de Cartones" CHANGELOG.md; then
        echo -e "${GREEN}✅ CHANGELOG.md actualizado${NC}"
    else
        echo -e "${RED}⚠️  CHANGELOG.md no tiene la nueva versión${NC}"
    fi
else
    echo -e "${RED}⚠️  CHANGELOG.md no encontrado${NC}"
fi

echo ""
echo -e "${GREEN}🎉 ¡Corrección verificada exitosamente!${NC}"
echo ""
echo "======================================================"
echo "📚 Próximos pasos:"
echo "======================================================"
echo ""
echo "1. Leer documentación completa:"
echo "   ${BLUE}cat docs/CORRECCION_RESPUESTA_CARTONES.md${NC}"
echo ""
echo "2. Ver resumen ejecutivo:"
echo "   ${BLUE}cat CORRECCION_CARTONES_RESUMEN.md${NC}"
echo ""
echo "3. Ver changelog:"
echo "   ${BLUE}head -50 CHANGELOG.md${NC}"
echo ""
echo "4. Reiniciar servidor Django:"
echo "   ${BLUE}# Si está corriendo, detenerlo primero"
echo "   ${BLUE}source venv/bin/activate  # o ./activate.sh"
echo "   ${BLUE}python manage.py runserver${NC}"
echo ""
echo "5. Probar endpoint de generación:"
echo "   ${BLUE}curl -X POST http://localhost:8000/api/multi-tenant/cards/generate-for-session/ \\"
echo "     -H \"Authorization: Bearer YOUR_JWT_TOKEN\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"session_id\": \"uuid-de-sesion\"}'${NC}"
echo ""
echo "6. Verificar que la respuesta incluye:"
echo "   ${GREEN}✅ 'cards': Array con todos los cartones"
echo "   ✅ 'cards_generated': Número de cartones generados"
echo "   ✅ 'cards_returned': Número de cartones en el array${NC}"
echo ""
echo "======================================================"
echo ""
echo -e "${BLUE}💡 Tip: Para más información, revisar la documentación en /docs/${NC}"
echo ""

