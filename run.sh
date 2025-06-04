#!/bin/bash

# Pro Hedge Trading - Enterprise Platform
# Execution script for Linux/Mac

echo ""
echo "==============================================="
echo "  🚀 Pro Hedge Trading - Enterprise Platform"
echo "==============================================="
echo ""
echo "Starting Pro Hedge Trading application..."
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo -e "${YELLOW}📥 Instala Python 3.10+ desde: https://python.org/downloads${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python detectado${NC}"

# Verificar si Streamlit está instalado
if ! python3 -c "import streamlit" &> /dev/null; then
    echo -e "${YELLOW}❌ Streamlit no está instalado${NC}"
    echo -e "${BLUE}📦 Instalando dependencias...${NC}"
    pip3 install -e .
fi

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Ejecutar la aplicación
echo -e "${GREEN}✅ Iniciando Pro Hedge Trading...${NC}"
echo -e "${BLUE}🌐 Abriendo en: http://localhost:8501${NC}"
echo ""
echo -e "${YELLOW}Para detener la aplicación, presiona Ctrl+C${NC}"
echo ""

python3 -m streamlit run src/ui/app.py --server.port=8501

echo ""
echo -e "${GREEN}👋 Pro Hedge Trading se ha cerrado${NC}" 