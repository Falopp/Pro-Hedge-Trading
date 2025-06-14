# Contributing to Pro Hedge Trading

🚀 ¡Gracias por tu interés en contribuir a Pro Hedge Trading! Este proyecto busca crear el sistema de arbitraje de funding rates más avanzado y confiable del ecosistema cripto.

## 🎯 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Proceso de Desarrollo](#proceso-de-desarrollo)
- [Estándares de Codificación](#estándares-de-codificación)
- [Pruebas](#pruebas)
- [Documentación](#documentación)
- [Seguridad](#seguridad)

## 📋 Código de Conducta

Nos comprometemos a crear un ambiente inclusivo y acogedor. Consulta nuestro [Código de Conducta](CODE_OF_CONDUCT.md) para más detalles.

## 🤝 Cómo Contribuir

### Reportar Bugs
- Usa nuestro [template de issues](https://github.com/Falopp/Pro-Hedge-Trading/issues/new?template=bug_report.md)
- Incluye pasos para reproducir el problema
- Proporciona logs relevantes (sin datos sensibles)
- Especifica versiones de Python, SO y dependencias

### Solicitar Features
- Usa nuestro [template de feature request](https://github.com/Falopp/Pro-Hedge-Trading/pro-hedge-trading/issues/new?template=feature_request.md)
- Describe claramente el caso de uso
- Explica el beneficio para la comunidad
- Considera la complejidad de implementación

### Pull Requests
1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/amazing-feature`)
3. Implementa tus cambios siguiendo nuestros estándares
4. Añade tests para nuevas funcionalidades
5. Asegúrate de que todos los tests pasen
6. Actualiza la documentación si es necesario
7. Commit tus cambios (`git commit -m 'Add amazing feature'`)
8. Push a la rama (`git push origin feature/amazing-feature`)
9. Abre un Pull Request

## 🛠️ Configuración del Entorno de Desarrollo

### Prerrequisitos
- Python 3.10+ 
- Git
- Docker (opcional, para containerización)

### Instalación
```bash
# Clona el repositorio
git clone https://github.com/Falopp/Pro-Hedge-Trading.git
cd pro-hedge-trading

# Crea entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala dependencias de desarrollo
pip install -e .[dev]

# Instala pre-commit hooks
pre-commit install
```

### Variables de Entorno
```bash
# Copia el archivo de ejemplo
cp env.example .env

# Configura tus API keys (opcional para desarrollo)
# BINANCE_API_KEY=tu_api_key
# BINANCE_SECRET=tu_secret
# HYPER_PRIVATE_KEY=0x_tu_private_key
# HYPER_ADDRESS=0x_tu_address
```

## 🔄 Proceso de Desarrollo

### Git Workflow
- `main`: Rama principal, siempre estable
- `develop`: Rama de desarrollo, integración continua
- `feature/*`: Nuevas funcionalidades
- `bugfix/*`: Corrección de bugs
- `hotfix/*`: Fixes críticos para producción

### Commits
Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for new exchange
fix: resolve price calculation bug
docs: update API documentation
test: add unit tests for trading operations
refactor: optimize order execution logic
```

### Branching Strategy
```bash
# Nueva feature
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# Bug fix
git checkout -b bugfix/issue-description

# Hotfix
git checkout main
git checkout -b hotfix/critical-fix
```

## 📝 Estándares de Codificación

### Python Style Guide
- Seguimos [PEP 8](https://pep8.org/) con modificaciones mínimas
- Línea máxima: 88 caracteres (configuración de Black)
- Usa `black` para formateo automático
- Usa `isort` para organizar imports
- Usa `mypy` para type checking

### Convenciones de Naming
```python
# Variables y funciones: snake_case
def calculate_funding_rate():
    trading_pair = "BTCUSDT"

# Clases: PascalCase
class TradingEngine:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_LEVERAGE = 125
DEFAULT_TIMEOUT = 30

# Archivos: snake_case.py
# api_utils.py, trading_operations.py
```

### Documentación de Código
```python
def execute_arbitrage_trade(
    pair: str, 
    capital: float, 
    leverage: int
) -> Dict[str, Any]:
    """
    Ejecuta una operación de arbitraje entre exchanges.
    
    Args:
        pair: Par de trading (ej. 'BTCUSDT')
        capital: Capital en USDT para la operación
        leverage: Nivel de apalancamiento (1-125)
        
    Returns:
        Diccionario con resultados de la operación
        
    Raises:
        ValueError: Si los parámetros son inválidos
        APIException: Si hay errores de API
        
    Example:
        >>> result = execute_arbitrage_trade("BTCUSDT", 100.0, 2)
        >>> print(result['status'])
        'success'
    """
    pass
```

## 🧪 Pruebas

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Solo unit tests
pytest -m unit

# Solo integration tests
pytest -m integration

# Tests específicos
pytest tests/test_trading_operations.py::TestTradingEngine::test_execute_order
```

### Escribir Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.core.trading_operations import TradingEngine

class TestTradingEngine:
    """Test suite for TradingEngine class."""
    
    @pytest.fixture
    def trading_engine(self):
        """Create a TradingEngine instance for testing."""
        return TradingEngine()
    
    def test_calculate_position_size(self, trading_engine):
        """Test position size calculation."""
        size = trading_engine.calculate_position_size(
            capital=100, 
            price=50000, 
            leverage=2
        )
        assert size == 0.004
    
    @patch('src.core.trading_operations.requests.get')
    def test_api_integration(self, mock_get, trading_engine):
        """Test API integration with mocked responses."""
        mock_get.return_value.json.return_value = {"price": 50000}
        
        price = trading_engine.get_current_price("BTCUSDT")
        assert price == 50000
```

### Test Categories
- **Unit Tests**: Funciones individuales, clases aisladas
- **Integration Tests**: Interacción entre componentes
- **E2E Tests**: Flujos completos de usuario
- **Performance Tests**: Benchmarks y optimización

## 📚 Documentación

### Actualizar Documentación
- README.md para información general
- Docstrings en el código
- Comentarios inline para lógica compleja
- Architecture docs en `/docs`

### Generar Docs
```bash
# Sphinx documentation
cd docs
make html

# Abrir en navegador
open _build/html/index.html
```

## 🔒 Seguridad

### Consideraciones de Seguridad
- **NUNCA** commits API keys o credenciales
- Usa variables de entorno para datos sensibles
- Implementa rate limiting adecuado
- Valida inputs de usuario
- Maneja errores sin exponer información sensible

### Reportar Vulnerabilidades
Para reportar vulnerabilidades de seguridad, envía un email a security@prohedgetrading.com en lugar de crear un issue público.

## 🏅 Reconocimientos

### Contributors
Todos los contribuidores son reconocidos en nuestro [Contributors Wall](https://github.com/ProHedgeTrading/pro-hedge-trading/graphs/contributors).

### Tipos de Contribución
- 💻 Código
- 🐛 Bug reports
- 📖 Documentación
- 🎨 Diseño
- 💡 Ideas y features
- 🧪 Testing
- 🌍 Traducciones
- 📢 Promoción

**¡Gracias por hacer Pro Hedge Trading mejor! 🚀** 