import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.api_utils import get_binance_best_price
from exchanges.hyperliquid_operations import get_hyperliquid_best_price, place_hyperliquid_order, get_hyperliquid_positions, get_hyperliquid_asset_metadata
from exchanges.binance_operations import ejecutar_binance_order, MIN_NOTIONAL
import math
import traceback
import time
from datetime import datetime
from exchanges.binance_operations import get_funding_rate as binance_fr
from exchanges.hyperliquid_operations import get_funding_rate as hyperliquid_fr

# Constants
FORCE_CLOSE_BUY_PRICE = 1e9  # Precio extremadamente alto para cierre forzado de compra
FORCE_CLOSE_SELL_PRICE = 0  # Precio extremadamente bajo para cierre forzado de venta

def verify_orders(client, hl_info, symbol, side, capital, leverage, direction):
    try:
        best_price_binance = get_binance_best_price(client, symbol, side)
        qty_binance = (capital * leverage) / best_price_binance
        notional = qty_binance * best_price_binance
        if qty_binance <= 0 or notional < MIN_NOTIONAL:
            raise ValueError(f"Binance: Notional (${notional:.2f}) debe ser ≥ {MIN_NOTIONAL} USDT.")
        coin = symbol.replace('USDT', '')
        is_buy = (direction == 'short')
        best_price_hyper, mark_price = get_hyperliquid_best_price(hl_info, coin, is_buy)
        qty_hyper = (capital * leverage) / best_price_hyper
        if qty_hyper <= 0:
            raise ValueError("Hyperliquid: La cantidad debe ser positiva.")
        print(f"Verificación de órdenes pasada: Precio Binance={best_price_binance}, qty={qty_binance}, Precio Hyperliquid={best_price_hyper}, qty={qty_hyper}, mark_price={mark_price}")
        return best_price_binance, best_price_hyper, qty_binance, qty_hyper, mark_price
    except Exception as e:
        print(f"Fallo en la verificación de órdenes: {e}")
        return None, None, None, None, None

def ejecutar_hyper_order(hl_info, hl_exchange, hyper_address, symbol, direction, capital, leverage, best_price):
    try:
        coin = symbol.replace('USDT', '')
        is_buy = (direction == 'short')
        # Obtener metadatos para redondeo
        metadata = get_hyperliquid_asset_metadata(hl_info, coin)
        sz_decimals = metadata['sz_decimals']
        min_sz = metadata['min_sz']
        # Calcular tamaño con redondeo hacia abajo
        qty = math.floor((capital * leverage) / best_price * 10**sz_decimals) / 10**sz_decimals
        if qty < min_sz:
            raise ValueError(f"Cantidad {qty} menor que el mínimo {min_sz} para {coin}.")
        
        print(f"Preparando orden en Hyperliquid: coin={coin}, is_buy={is_buy}, qty={qty}, px={best_price}")
        
        response = place_hyperliquid_order(
            hl_info=hl_info,
            hl_exchange=hl_exchange,
            hyper_address=hyper_address,
            coin=coin,
            is_buy=is_buy,
            sz=qty,
            leverage=leverage,
            reduce_only=False
        )
        
        return response, qty, best_price
    except Exception as e:
        raise Exception(f"Fallo en la orden de Hyperliquid: {e}")

def cerrar_posiciones(client, hl_info, hl_exchange, hyper_address, symbol, posicion, session_state, force_close=False):
    binance_closed = False
    hyperliquid_closed = False
    
    # Cerrar posición de Binance
    try:
        position_info = client.futures_position_information(symbol=symbol)
        if position_info:
            r1 = position_info[0]
            qty = abs(float(r1['positionAmt']))
            if qty > 0:
                close_side = 'SELL' if float(r1['positionAmt']) > 0 else 'BUY'
                close_order = client.futures_create_order(
                    symbol=symbol,
                    side=close_side,
                    type='MARKET',
                    quantity=qty
                )
                final_order = wait_for_binance_order(client, symbol, close_order['orderId'])
                if final_order['status'] != 'FILLED':
                    raise Exception(f"Fallo en la orden de cierre de Binance: {final_order}")
                position_info_after = client.futures_position_information(symbol=symbol)
                if position_info_after and abs(float(position_info_after[0]['positionAmt'])) < 1e-6:
                    session_state.positions['binance'][symbol] = {}
                    binance_closed = True
                else:
                    print("La posición de Binance no se cerró completamente.")
            else:
                binance_closed = True
        else:
            binance_closed = True
    except Exception as e:
        print(f"Error al cerrar la posición de Binance: {e}")
        traceback.print_exc()
    
    # Cerrar posición de Hyperliquid
    try:
        hyper_positions = get_hyperliquid_positions(hl_info, hyper_address)
        if symbol in hyper_positions and abs(hyper_positions[symbol]['size']) > 0:
            qty = abs(hyper_positions[symbol]['size'])
            coin = symbol.replace('USDT', '')
            is_buy = (hyper_positions[symbol]['size'] < 0)
            leverage = session_state.positions['hyperliquid'].get(symbol, {}).get('leverage', 2)
            print(f"Cerrando posición en Hyperliquid: coin={coin}, is_buy={is_buy}, qty={qty}, leverage={leverage}")
            response = place_hyperliquid_order(
                hl_info=hl_info,
                hl_exchange=hl_exchange,
                hyper_address=hyper_address,
                coin=coin,
                is_buy=is_buy,
                sz=qty,
                leverage=leverage,
                reduce_only=True
            )
            new_positions = get_hyperliquid_positions(hl_info, hyper_address)
            if symbol not in new_positions or abs(new_positions[symbol]['size']) < 1e-6:
                session_state.positions['hyperliquid'][symbol] = {}
                hyperliquid_closed = True
            else:
                print(f"La posición de Hyperliquid no se cerró completamente. Tamaño restante: {new_positions[symbol]['size']}")
        else:
            hyperliquid_closed = True
    except Exception as e:
        print(f"Error al cerrar la posición de Hyperliquid: {e}")
        traceback.print_exc()
    
    return binance_closed and hyperliquid_closed

def check_all_positions(binance_client, hl_exchange, hl_info, hyper_address):
    try:
        if not binance_client or not hl_exchange or not hl_info:
            return "❌ No se pueden verificar posiciones: Clientes no inicializados."

        # Verificar posiciones en Binance
        binance_positions = []
        try:
            positions = binance_client.futures_position_information()
            binance_positions = [p for p in positions if float(p['positionAmt']) != 0]
        except Exception as e:
            print(f"❌ Error al obtener posiciones de Binance: {e}")

        # Verificar posiciones en Hyperliquid
        hyper_positions = []
        try:
            user_state = hl_info.user_state(hyper_address)
            if user_state and 'assetPositions' in user_state:
                hyper_positions = [p for p in user_state['assetPositions'] if float(p['position']) != 0]
        except Exception as e:
            print(f"❌ Error al obtener posiciones de Hyperliquid: {e}")

        # Preparar mensaje de respuesta
        if not binance_positions and not hyper_positions:
            return "✅ No hay posiciones abiertas en ningún exchange."

        mensaje = "📊 Posiciones Actuales:\n\n"
        
        if binance_positions:
            mensaje += "Binance:\n"
            for pos in binance_positions:
                mensaje += f"- {pos['symbol']}: {pos['positionAmt']} @ {pos['entryPrice']}\n"
        
        if hyper_positions:
            mensaje += "\nHyperliquid:\n"
            for pos in hyper_positions:
                mensaje += f"- {pos['coin']}: {pos['position']} @ {pos['entryPrice']}\n"

        return mensaje

    except Exception as e:
        return f"❌ Error al verificar posiciones: {str(e)}"

def evaluate_funding_opportunity(symbol, threshold=0.001):
    """
    Evalúa las tasas de funding entre Binance y Hyperliquid y recomienda una acción manual.
    :param symbol: Símbolo del par (ej. BTCUSDT)
    :param threshold: Umbral mínimo para considerar una oportunidad (ej. 0.001, que es 0.1%)
    :return: Diccionario con la recomendación y detalles
    """
    try:
        # Obtener tasas de funding
        binance_data = binance_fr(symbol)
        if not binance_data:
            return {"status": "error", "message": "No se pudo obtener la tasa de funding de Binance"}
        
        binance_rate = float(binance_data[-1]["fundingRate"]) * 100  # Convertir a porcentaje
        hyperliquid_data = hyperliquid_fr(symbol.replace("USDT", ""))
        hyperliquid_rate = float(hyperliquid_data.get("rate", 0)) * 100  # Convertir a porcentaje

        # Calcular diferencia en porcentaje
        diff = binance_rate - hyperliquid_rate

        # Ajustar el umbral a porcentaje (por ejemplo, 0.001 * 100 = 0.1%)
        if abs(diff) > threshold * 100:
            if diff > 0:
                recommendation = "Abrir Long en Binance, Short en Hyperliquid"
                opportunity = "Tasa de funding más alta en Binance"
            else:
                recommendation = "Abrir Short en Binance, Long en Hyperliquid"
                opportunity = "Tasa de funding más alta en Hyperliquid"
            
            return {
                "status": "opportunity",
                "recommendation": recommendation,
                "opportunity": opportunity,
                "binance_rate": binance_rate,
                "hyperliquid_rate": hyperliquid_rate,
                "difference": diff
            }
        else:
            return {
                "status": "no_opportunity",
                "message": f"Diferencia de tasas ({abs(diff):.6f}%) menor que el umbral ({threshold * 100}%)",
                "binance_rate": binance_rate,
                "hyperliquid_rate": hyperliquid_rate,
                "difference": diff
            }
    except Exception as e:
        return {"status": "error", "message": f"Error al evaluar tasas de funding: {e}"}