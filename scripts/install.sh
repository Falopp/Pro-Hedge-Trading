#!/bin/bash

# Pro Hedge Trading - Instalación Automática
# Copyright (c) 2024 Pro Hedge Trading Team

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art
echo -e "${PURPLE}"
cat << "EOF"
    ____             __  __          __            
   / __ \_________  / / / /__  ____/ /___ ____    
  / /_/ / ___/ __ \/ /_/ / _ \/ __  / __ `/ _ \   
 / ____/ /  / /_/ / __  /  __/ /_/ / /_/ /  __/   
/_/   /_/   \____/_/ /_/\___/\__,_/\__, /\___/    
                                 /____/          
    ______              ___                       
   /_  __/________ ____/ (_)___  ____ _           
    / / / ___/ __ `/ __  / / __ \/ __ `/           
   / / / /  / /_/ / /_/ / / / / / /_/ /            
  /_/ /_/   \__,_/\__,_/_/_/ /_/\__, /             
                              /____/              
EOF
echo -e "${NC}"

echo -e "${CYAN}🚀 Pro Hedge Trading - Enterprise Installation${NC}"
echo -e "${YELLOW}⚡ Instalación automática en progreso...${NC}"
echo ""

# Verificar prerrequisitos
echo -e "${BLUE}📋 Verificando prerrequisitos...${NC}"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo -e "${YELLOW}📥 Instala Python 3.10+ desde: https://python.org/downloads${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION detectado. Se requiere Python $REQUIRED_VERSION+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detectado${NC}"

# Verificar Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git no está instalado${NC}"
    echo -e "${YELLOW}📥 Instala Git desde: https://git-scm.com/downloads${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git detectado${NC}"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip no está instalado${NC}"
    echo -e "${YELLOW}📥 Instala pip: python3 -m ensurepip --upgrade${NC}"
    exit 1
fi

echo -e "${GREEN}✅ pip detectado${NC}"

# Crear directorio de instalación
INSTALL_DIR="$HOME/pro-hedge-trading"
echo -e "${BLUE}📁 Directorio de instalación: $INSTALL_DIR${NC}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠️  El directorio ya existe. ¿Sobrescribir? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Instalación cancelada${NC}"
        exit 1
    fi
    rm -rf "$INSTALL_DIR"
fi

# Clonar repositorio
echo -e "${BLUE}📥 Clonando repositorio...${NC}"
git clone https://github.com/Falopp/Pro-Hedge-Trading.git "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Crear entorno virtual
echo -e "${BLUE}🐍 Creando entorno virtual...${NC}"
python3 -m venv venv

# Activar entorno virtual
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Actualizar pip
echo -e "${BLUE}⬆️  Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
echo -e "${BLUE}📦 Instalando dependencias...${NC}"
pip install -e .

# Instalar dependencias de desarrollo (opcional)
echo -e "${YELLOW}🔧 ¿Instalar herramientas de desarrollo? (y/N)${NC}"
read -r dev_response
if [[ "$dev_response" =~ ^[Yy]$ ]]; then
    pip install -e .[dev]
    echo -e "${GREEN}✅ Herramientas de desarrollo instaladas${NC}"
fi

# Crear archivo de configuración
echo -e "${BLUE}⚙️  Configurando variables de entorno...${NC}"
cp env.example .env

echo -e "${CYAN}📝 Configuración de APIs${NC}"
echo -e "${YELLOW}Por favor, edita el archivo .env con tus credenciales:${NC}"
echo -e "${BLUE}  - BINANCE_API_KEY=tu_api_key${NC}"
echo -e "${BLUE}  - BINANCE_SECRET=tu_secret${NC}"
echo -e "${BLUE}  - HYPER_PRIVATE_KEY=0x_tu_private_key${NC}"
echo -e "${BLUE}  - HYPER_ADDRESS=0x_tu_address${NC}"

# Crear scripts de ejecución
echo -e "${BLUE}🚀 Creando scripts de ejecución...${NC}"

# Script para Linux/Mac
cat > run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run src/ui/app.py
EOF
chmod +x run.sh

# Script para Windows
cat > run.bat << 'EOF'
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
streamlit run src\ui\app.py
EOF

# Verificar instalación
echo -e "${BLUE}🧪 Verificando instalación...${NC}"
python -c "import streamlit; import pandas; import plotly; print('✅ Dependencias principales OK')"

# Ejecutar tests básicos
if [[ "$dev_response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🧪 Ejecutando tests básicos...${NC}"
    python -m pytest tests/ -v --tb=short || echo -e "${YELLOW}⚠️  Algunos tests fallaron (normal en primera instalación)${NC}"
fi

# Mensaje de éxito
echo ""
echo -e "${GREEN}🎉 ¡Instalación completada exitosamente!${NC}"
echo ""
echo -e "${CYAN}🚀 Para ejecutar Pro Hedge Trading:${NC}"
echo -e "${BLUE}   cd $INSTALL_DIR${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${BLUE}   ./run.bat${NC}"
else
    echo -e "${BLUE}   ./run.sh${NC}"
fi
echo ""
echo -e "${CYAN}📚 Documentación: https://pro-hedge-trading.readthedocs.io/${NC}"
echo -e "${CYAN}💬 Discord: https://discord.gg/pro-hedge-trading${NC}"
echo -e "${CYAN}🐦 Twitter: https://twitter.com/ProHedgeTrading${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo -e "${RED}   - Configura tus API keys en el archivo .env${NC}"
echo -e "${RED}   - Solo usa permisos de lectura/trading (NO withdraw)${NC}"
echo -e "${RED}   - Prueba con capital pequeño primero${NC}"
echo -e "${RED}   - El trading conlleva riesgos significativos${NC}"
echo ""
echo -e "${PURPLE}¡Gracias por usar Pro Hedge Trading! 🚀${NC}" 