#!/usr/bin/env python3
"""
Pro Hedge Trading - Enterprise Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path

# Agregar el directorio src al path para imports absolutos
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from core.api_utils import (
    init_binance_client, check_binance_api, get_current_price,
    validate_hyperliquid_credentials, init_hyperliquid_clients,
    check_hyperliquid_api, get_hyperliquid_pairs
)
from exchanges.hyperliquid_operations import get_hyperliquid_positions
from core.trading_operations import (
    verify_orders, ejecutar_binance_order, ejecutar_hyper_order,
    cerrar_posiciones, check_all_positions, evaluate_funding_opportunity
)

# Cargar variables de entorno
load_dotenv()

# Configuración de página
st.set_page_config(
    page_title="Pro Hedge Trading",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .main {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del estado de la sesión
if 'config' not in st.session_state:
    st.session_state.config = {
        'binance_api_key': '',
        'binance_secret': '',
        'hyper_private_key': '',
        'hyper_address': ''
    }

if 'positions' not in st.session_state:
    st.session_state.positions = {'binance': {}, 'hyperliquid': {}}

if 'history' not in st.session_state:
    st.session_state.history = []

# Título principal
st.title("🚀 Pro Hedge Trading Dashboard")
st.markdown("### *Enterprise-Grade Funding Rate Arbitrage System*")

# Sidebar - Configuración de APIs
with st.sidebar:
    st.header("⚙️ Configuración de APIs")
    
    st.subheader("🔑 Binance Futures")
    st.session_state.config['binance_api_key'] = st.text_input(
        "API Key", 
        value=st.session_state.config['binance_api_key'],
        type="password"
    )
    st.session_state.config['binance_secret'] = st.text_input(
        "Secret", 
        value=st.session_state.config['binance_secret'],
        type="password"
    )
    
    st.subheader("🌊 Hyperliquid")
    st.session_state.config['hyper_private_key'] = st.text_input(
        "Private Key", 
        value=st.session_state.config['hyper_private_key'],
        type="password"
    )
    st.session_state.config['hyper_address'] = st.text_input(
        "Address", 
        value=st.session_state.config['hyper_address']
    )

# Verificar configuración
config_complete = all(st.session_state.config.values())

if not config_complete:
    st.warning("⚠️ Por favor, configura todas las API keys en la barra lateral para continuar.")
    st.stop()

# Inicializar clientes
client = None
hl_info = None
hl_exchange = None

if config_complete:
    client = init_binance_client(
        st.session_state.config['binance_api_key'], 
        st.session_state.config['binance_secret']
    )
    hl_info, hl_exchange = init_hyperliquid_clients(
        st.session_state.config['hyper_private_key']
    )

# Panel principal
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Configuración de Trading")
    
    # Selección de par
    if client:
        pairs = get_hyperliquid_pairs(hl_info) if hl_info else ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        pair = st.selectbox("Par de Trading", pairs, index=0)
    else:
        pair = st.selectbox("Par de Trading", ['BTCUSDT'], index=0)
    
    # Configuración de trading
    col_config1, col_config2, col_config3 = st.columns(3)
    
    with col_config1:
        capital_usdt = st.number_input("Capital (USDT)", min_value=10.0, value=100.0, step=10.0)
    
    with col_config2:
        leverage = st.number_input("Apalancamiento", min_value=1, max_value=125, value=2, step=1)
    
    with col_config3:
        posicion = st.selectbox("Dirección", ["Long", "Short"])

    # Botón de evaluación de funding
    if st.button("📊 Evaluar Tasas de Funding", use_container_width=True):
        if client and hl_info:
            with st.spinner("Evaluando tasas de funding..."):
                result = evaluate_funding_opportunity(pair, threshold=0.001)
                if result['status'] == 'success':
                    st.success(f"✅ {result['message']}")
                    
                    # Mostrar detalles
                    col_rate1, col_rate2, col_rate3 = st.columns(3)
                    with col_rate1:
                        st.metric("Binance Funding", f"{result['binance_rate']:.4f}%")
                    with col_rate2:
                        st.metric("Hyperliquid Funding", f"{result['hyperliquid_rate']:.4f}%")
                    with col_rate3:
                        st.metric("Diferencia", f"{result['spread']:.4f}%")
                        
                    st.info(f"💡 Recomendación: {result['recommendation']}")
                else:
                    st.error(f"❌ {result['message']}")
        else:
            st.error("❌ No se pueden evaluar las tasas: APIs no configuradas")

    # Botones de trading
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🚀 Ejecutar Hedge", use_container_width=True):
            if client and hl_info:
                with st.spinner("Ejecutando hedge..."):
                    try:
                        side = 'BUY' if posicion == 'Long' else 'SELL'
                        best_price_binance, best_price_hyper, qty_binance, qty_hyper, mark_price = verify_orders(
                            client, hl_info, pair, side, capital_usdt, leverage, posicion.lower()
                        )
                        
                        if best_price_binance and best_price_hyper:
                            # Ejecutar órdenes
                            r2, qty_hyper, entry_price_hyper = ejecutar_hyper_order(
                                hl_info, hl_exchange, st.session_state.config['hyper_address'],
                                pair, posicion.lower(), capital_usdt, leverage, best_price_hyper
                            )
                            r1, qty_binance, entry_price_binance = ejecutar_binance_order(
                                client, pair, side, capital_usdt, leverage, best_price_binance
                            )
                            
                            # Guardar en historial
                            st.session_state.history.append({
                                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "Type": "Open",
                                "Pair": pair,
                                "Direction": posicion,
                                "Capital": capital_usdt,
                                "Leverage": leverage,
                                "Binance_Qty": qty_binance,
                                "Hyperliquid_Qty": qty_hyper
                            })
                            
                            st.success("✅ Hedge ejecutado exitosamente")
                        else:
                            st.error("❌ Error al verificar órdenes")
                    except Exception as e:
                        st.error(f"❌ Error al ejecutar hedge: {e}")
            else:
                st.error("❌ APIs no configuradas")
    
    with col_btn2:
        if st.button("🔒 Cerrar Hedge", use_container_width=True):
            if client and hl_info:
                with st.spinner("Cerrando hedge..."):
                    try:
                        success = cerrar_posiciones(
                            client, hl_info, hl_exchange, st.session_state.config['hyper_address'],
                            pair, posicion.lower(), st.session_state, force_close=False
                        )
                        if success:
                            st.success("✅ Hedge cerrado exitosamente")
                        else:
                            st.warning("⚠️ Cierre parcial o con errores")
                    except Exception as e:
                        st.error(f"❌ Error al cerrar hedge: {e}")
            else:
                st.error("❌ APIs no configuradas")

with col2:
    st.subheader("💰 Balance de Cuentas")
    
    if client and hl_info:
        try:
            # Balance Binance
            account = client.futures_account()
            binance_balance = float(account['totalWalletBalance'])
            st.metric("Binance", f"${binance_balance:,.2f}")
            
            # Balance Hyperliquid  
            user_state = hl_info.user_state(st.session_state.config['hyper_address'])
            if user_state and 'marginSummary' in user_state:
                hyper_balance = float(user_state['marginSummary'].get('accountValue', 0))
                st.metric("Hyperliquid", f"${hyper_balance:,.2f}")
            else:
                st.metric("Hyperliquid", "No disponible")
                
        except Exception as e:
            st.error(f"❌ Error al obtener balances: {e}")

# Posiciones abiertas
st.subheader("📊 Posiciones Abiertas")
tab1, tab2 = st.tabs(["Binance", "Hyperliquid"])

with tab1:
    if client:
        try:
            positions = client.futures_position_information(symbol=pair)
            open_positions = [pos for pos in positions if float(pos['positionAmt']) != 0]
            
            if open_positions:
                for pos in open_positions:
                    qty = float(pos['positionAmt'])
                    entry_price = float(pos['entryPrice'])
                    direction = 'Long' if qty > 0 else 'Short'
                    
                    col_pos1, col_pos2, col_pos3 = st.columns(3)
                    col_pos1.metric("Cantidad", f"{abs(qty):.4f}")
                    col_pos2.metric("Precio Entrada", f"${entry_price:,.2f}")
                    col_pos3.metric("Dirección", direction)
            else:
                st.info("No hay posiciones abiertas en Binance")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with tab2:
    if hl_info:
        try:
            positions = get_hyperliquid_positions(hl_info, st.session_state.config['hyper_address'])
            
            if positions:
                for symbol, pos in positions.items():
                    if pos['size'] != 0:
                        col_pos1, col_pos2, col_pos3 = st.columns(3)
                        col_pos1.metric("Cantidad", f"{abs(pos['size']):.4f}")
                        col_pos2.metric("Precio Entrada", f"${pos['entry_price']:,.2f}")
                        col_pos3.metric("Dirección", pos['direction'])
            else:
                st.info("No hay posiciones abiertas en Hyperliquid")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Historial de trades
if st.session_state.history:
    st.subheader("📜 Historial de Trades")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
    
    # Gráfico
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    fig = px.line(df, x='Timestamp', y='Capital', title="Capital por Trade")
    st.plotly_chart(fig, use_container_width=True)
    
    # Descarga
    csv = df.to_csv(index=False)
    st.download_button("📥 Descargar Historial", csv, "trade_history.csv", "text/csv")

# Footer
st.markdown("---")
st.markdown("Construido con ❤️ por Pro Hedge Trading | Versión 2.0 | [GitHub](https://github.com/falopp/pro-hedge-trading)")


def main():
    """Entry point para la aplicación Pro Hedge Trading."""
    pass


if __name__ == "__main__":
    main() 