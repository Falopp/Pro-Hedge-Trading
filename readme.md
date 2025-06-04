# 🚀 Pro Hedge Trading

### *Sistema de Arbitraje de Funding Rates para Criptomonedas*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 👨‍💻 **Creado por [@Falopp](https://github.com/Falopp)**

**🎯 Desarrollador full-stack • 🚀 Crypto-builder • 📊 On-chain analyst**

Especializado en bots de trading delta-neutral y herramientas cripto avanzadas.

### 🛠️ **Otros Proyectos**

| Proyecto | Descripción |
|----------|-------------|
| [**data_p2p**](https://github.com/Falopp/data_p2p) | CLI para análisis de transacciones P2P |
| [**P2P_Profit**](https://github.com/Falopp/P2P_Profit) | Sistema de seguimiento P2P con cálculo P&L |
| [**crypto_screener_dashboard**](https://github.com/Falopp/crypto_screener_dashboard) | Dashboard de monitoreo cripto en tiempo real |
| [**CS2_bot_dmarket**](https://github.com/Falopp/CS2_bot_dmarket) | Bot de trading para skins de CS2 |

---

## 📋 **¿Qué es Pro Hedge Trading?**

Sistema automatizado que aprovecha las diferencias en **tasas de funding** entre exchanges de criptomonedas (Binance y Hyperliquid) para generar ganancias con **bajo riesgo**.

### ⚡ **Funcionalidades Principales**

- **Arbitraje Delta-Neutral**: Posiciones opuestas en diferentes exchanges
- **Monitoring en Tiempo Real**: Dashboard web interactivo con Streamlit
- **Gestión de Riesgo**: Cálculo automático de cantidades y precios
- **Multi-Exchange**: Soporte para Binance Futures y Hyperliquid
- **Historial de Trades**: Seguimiento de operaciones y P&L

---

## 🛠️ **Instalación**

### **Prerrequisitos**
- Python 3.10 o superior
- Cuentas en Binance y Hyperliquid con APIs configuradas

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/Falopp/pro-hedge-trading.git
cd pro-hedge-trading
```

### **2. Instalar Dependencias**
```bash
# Instalar el paquete
pip install -e .

# O manualmente
pip install -r requirements.txt
```

### **3. Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con tus credenciales
nano .env
```

**Contenido del archivo `.env`:**
```env
# Binance Futures
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET=tu_secret_aqui

# Hyperliquid
HYPER_PRIVATE_KEY=0x_tu_private_key_aqui
HYPER_ADDRESS=0x_tu_address_aqui
```

---

## 🚀 **Cómo Usar**

### **Opción 1: Scripts de Ejecución (Recomendado)**

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### **Opción 2: Ejecución Manual**
```bash
python -m streamlit run src/ui/app.py
```

### **Opción 3: Docker**
```bash
# Construir imagen
docker build -t pro-hedge-trading .

# Ejecutar
docker run -p 8501:8501 \
  -e BINANCE_API_KEY=tu_key \
  -e BINANCE_SECRET=tu_secret \
  -e HYPER_PRIVATE_KEY=0x_tu_private_key \
  -e HYPER_ADDRESS=0x_tu_address \
  pro-hedge-trading
```

Luego abre: **http://localhost:8501**

---

## 📁 **Estructura del Proyecto**

```
Pro-Hedge-Trading/
├── src/
│   ├── core/                    # Lógica principal
│   │   ├── api_utils.py        # Utilidades de API
│   │   └── trading_operations.py # Operaciones de trading
│   ├── exchanges/               # Conectores de exchanges
│   │   ├── binance_operations.py
│   │   └── hyperliquid_operations.py
│   └── ui/
│       └── app.py              # Interfaz Streamlit
├── tests/                       # Tests automatizados
├── docs/                        # Documentación
├── scripts/                     # Scripts de instalación
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Containerización
├── run.bat                      # Script Windows
├── run.sh                       # Script Linux/Mac
└── README.md                    # Este archivo
```

---

## ⚙️ **Configuración de APIs**

### **Binance Futures**
1. Ve a [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Crea nueva API Key con permisos de **Futures**
3. Activa **Enable Futures** en los permisos
4. Copia API Key y Secret al archivo `.env`

### **Hyperliquid**
1. Conecta tu wallet a [Hyperliquid](https://app.hyperliquid.xyz/)
2. Exporta tu **Private Key** desde MetaMask u otra wallet
3. Copia la dirección de tu wallet y private key al `.env`

---

## 🎮 **Cómo Funciona**

### **1. Evaluación de Funding**
- El sistema compara tasas de funding entre Binance y Hyperliquid
- Identifica oportunidades donde las tasas difieren significativamente

### **2. Ejecución de Hedge**
- Abre posición **Long** en el exchange con funding negativo
- Abre posición **Short** en el exchange con funding positivo
- Las posiciones se cancelan mutuamente (delta-neutral)

### **3. Ganancia**
- Cobra funding positivo en una posición
- Paga funding negativo (menor) en la otra
- La diferencia es la ganancia neta

---

## 📊 **Dashboard**

El dashboard web incluye:

- **⚙️ Configuración**: Pares, capital, apalancamiento
- **📊 Evaluación**: Análisis de tasas de funding en tiempo real
- **🚀 Ejecución**: Botones para abrir/cerrar hedge
- **💰 Balances**: Saldos de ambos exchanges
- **📈 Posiciones**: Posiciones abiertas en cada exchange
- **📜 Historial**: Registro de trades y P&L

---

## 🔧 **Desarrollo**

### **Instalar para Desarrollo**
```bash
# Clonar e instalar en modo desarrollo
git clone https://github.com/Falopp/pro-hedge-trading.git
cd pro-hedge-trading
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/

# Linting
flake8 src/
black src/
```

### **Estructura de Tests**
```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_api_utils.py
pytest tests/test_trading_operations.py
```

---

## ⚠️ **Advertencias Importantes**

- **🚨 RIESGO**: El trading de criptomonedas conlleva riesgos. Usa solo capital que puedas permitirte perder.
- **🔑 SEGURIDAD**: Nunca compartas tus API keys. Usa credenciales con permisos mínimos necesarios.
- **📊 TESTNET**: Prueba primero en testnet antes de usar dinero real.
- **💰 CAPITAL**: Comienza con cantidades pequeñas hasta entender completamente el sistema.

---

## 🐛 **Problemas Comunes**

### **Error de Imports**
```bash
# Si hay errores de imports, instala el paquete
pip install -e .
```

### **Error de Conexión API**
- Verifica que las API keys sean correctas
- Revisa que tengas permisos de futures en Binance
- Confirma que tu IP esté en la whitelist

### **Error de Saldos Insuficientes**
- Asegúrate de tener fondos suficientes en ambos exchanges
- El sistema necesita margen para abrir posiciones

---

## 📞 **Soporte**

- **🐛 Issues**: [GitHub Issues](https://github.com/Falopp/pro-hedge-trading/issues)
- **💡 Mejoras**: [GitHub Discussions](https://github.com/Falopp/pro-hedge-trading/discussions)

---
**Hecho con ❤️ por [@Falopp](https://github.com/Falopp) | [⭐ Star este repo](https://github.com/Falopp/pro-hedge-trading) si te ayudó**