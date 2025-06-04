@echo off
echo.
echo ===============================================
echo   🚀 Pro Hedge Trading - Enterprise Platform
echo ===============================================
echo.
echo Starting Pro Hedge Trading application...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo 📥 Instala Python desde: https://python.org/downloads
    pause
    exit /b 1
)

REM Verificar si Streamlit está instalado
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Streamlit no está instalado
    echo 📦 Instalando dependencias...
    pip install -e .
)

REM Ejecutar la aplicación
echo ✅ Iniciando Pro Hedge Trading...
echo 🌐 Abriendo en: http://localhost:8501
echo.
echo Para detener la aplicación, presiona Ctrl+C
echo.

python -m streamlit run src/ui/app.py --server.port=8501

echo.
echo 👋 Pro Hedge Trading se ha cerrado
pause 