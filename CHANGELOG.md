# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-19

### 🚀 Added
- **Nueva Arquitectura**: Reestructuración completa del proyecto con módulos separados
- **Enterprise DevOps**: CI/CD completo con GitHub Actions
- **Docker Support**: Containerización multi-stage optimizada
- **Testing Framework**: Suite de pruebas con pytest y 95%+ coverage
- **Type Safety**: Type hints completos y validación con mypy
- **Security Scanning**: Bandit integration para análisis de seguridad
- **Documentation**: Documentación completa estilo enterprise
- **Code Quality**: Pre-commit hooks, Black, isort, flake8
- **Monitoring**: Prometheus metrics y health checks
- **Package Management**: Soporte para pip install y PyPI

### 🔧 Changed
- **Estructura de Carpetas**: Organización modular en `/src`
- **Import System**: Imports relativos para mejor mantenimiento
- **Configuration**: pyproject.toml moderno en lugar de setup.py
- **Environment**: Mejor manejo de variables de entorno
- **Error Handling**: Manejo de errores más robusto

### 🐛 Fixed
- **Import Errors**: Corrección de todos los imports después de reestructuración
- **Path Issues**: Rutas relativas correctas en todos los módulos
- **Dependencies**: Versiones específicas para reproducibilidad

### 💔 Breaking Changes
- **File Structure**: Los archivos principales se movieron a `/src`
- **Import Paths**: Cambio en rutas de importación (usar imports relativos)
- **Entry Point**: Comando cambiado a `pro-hedge` o `streamlit run src/ui/app.py`

## [1.6.0] - 2024-12-18

### 🚀 Added
- **Funding Rate Analysis**: Evaluación automática de oportunidades
- **Real-time Dashboard**: Interface de Streamlit modernizada
- **Position Monitoring**: Tracking en vivo de P&L
- **Multi-Exchange Support**: Binance + Hyperliquid integration
- **Risk Management**: Validaciones y límites automáticos
- **Trade History**: Historial con export a CSV

### 🔧 Changed
- **UI/UX**: Interface completamente rediseñada
- **Performance**: Optimizaciones en API calls
- **Stability**: Mejor manejo de errores de conexión

### 🐛 Fixed
- **API Sync**: Sincronización de tiempo con Binance
- **Order Execution**: Validaciones mejoradas pre-trade
- **Memory Leaks**: Optimización de uso de memoria

## [1.0.0] - 2024-11-01

### 🚀 Added
- **Core Trading Engine**: Lógica básica de arbitraje
- **Binance Integration**: Soporte para Binance Futures
- **Hyperliquid Integration**: Soporte para Hyperliquid Perps
- **Manual Execution**: Sistema de trading manual
- **Basic UI**: Interface básica de Streamlit

---

## Tipos de Cambios

- `🚀 Added` - Nuevas funcionalidades
- `🔧 Changed` - Cambios en funcionalidades existentes
- `🐛 Fixed` - Corrección de bugs
- `💔 Breaking Changes` - Cambios que rompen compatibilidad
- `🗑️ Deprecated` - Funcionalidades obsoletas
- `🚫 Removed` - Funcionalidades eliminadas
- `🔒 Security` - Correcciones de seguridad 