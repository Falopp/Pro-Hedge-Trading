from binance.exceptions import BinanceAPIException
import time
import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.api_utils import get_binance_filters, round_down_by_step, wait_for_binance_order, get_binance_best_price
from core.api_utils import api_request

# Binance constants
MIN_NOTIONAL = 10  # Valor notional mínimo en USDT para Binance

def get_funding_rate(symbol, limit=1):
    """
    Obtiene el historial de tasas de funding para un símbolo en Binance.
    :param symbol: Símbolo del par (ej. BTCUSDT)
    :param limit: Número de registros a obtener (máx 1000)
    :return: Lista de tasas de funding
    """
    url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit={limit}"
    try:
        data = api_request(url)
        return data
    except Exception as e:
        print(f"Error al obtener funding rate de Binance: {e}")
        return []
    
def ejecutar_binance_order(client, symbol, side, capital, leverage, best_price):
    try:
        filters = get_binance_filters(client, symbol)
        tick_size = filters['tickSize']
        step_size = filters['stepSize']
        adjusted_price = round_down_by_step(best_price, tick_size)
        qty = round_down_by_step((capital * leverage) / best_price, step_size)
        notional = qty * best_price
        if qty <= 0:
            raise ValueError(f"Cantidad calculada es cero o negativa: {qty}")
        # Verificar margen disponible
        account_info = client.futures_account()
        available_balance = float(account_info['availableBalance'])
        margin_required = notional / leverage
        if margin_required > available_balance:
            raise Exception(f"Margen insuficiente. Requerido: {margin_required}, Disponible: {available_balance}")
        if margin_required > capital:
            raise ValueError(f"Margen requerido ({margin_required:.2f} USDT) excede el capital especificado ({capital} USDT).")
        # Configurar margen y apalancamiento
        try:
            client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')
        except BinanceAPIException as e:
            if 'No need to change margin type' not in str(e):
                raise e
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            quantity=qty,
            price=str(adjusted_price),
            timeInForce='GTC'
        )
        print(f"Orden colocada en Binance: {order}")
        final_order = wait_for_binance_order(client, symbol, order['orderId'])
        if final_order['status'] != 'FILLED':
            raise Exception(f"Fallo al llenar la orden de Binance: {final_order}")
        # Verificar posición
        position_info = client.futures_position_information(symbol=symbol)
        if position_info:
            position_info = position_info[0]
            actual_qty = abs(float(position_info['positionAmt']))
            expected_qty = qty if side == 'BUY' else -qty
            print(f"Verificación de posición: Qty esperada={expected_qty}, Qty actual={actual_qty}")
            if abs(actual_qty - abs(expected_qty)) > 1e-6:
                raise Exception(f"Discrepancia en el tamaño de la posición: Esperado {abs(expected_qty)}, obtenido {actual_qty}")
        else:
            print("No hay información de posición disponible. Asumiendo posición abierta.")
        return order, qty, best_price
    except Exception as e:
        raise Exception(f"Fallo en la orden de Binance: {e}")
