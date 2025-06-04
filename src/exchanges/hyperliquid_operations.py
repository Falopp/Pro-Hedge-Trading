import math
import traceback
import json
import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from core.api_utils import api_request
# Hyperliquid constants
DEFAULT_TICK_SIZE = 0.1  # Tamaño de tick predeterminado para otros activos
BTC_TICK_SIZE = 1.0  # Tamaño de tick hardcoded para BTC (asset=0)

def get_funding_rate(coin):
    """
    Obtiene la tasa de funding para un símbolo en Hyperliquid.
    :param coin: Símbolo del activo (ej. BTC)
    :return: Diccionario con la tasa de funding
    """
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "metaAndAssetCtxs"}
    try:
        data = api_request(url, method='POST', payload=payload)
        # Imprimir la respuesta completa para depuración
        print(f"Respuesta completa de la API: {json.dumps(data, indent=2)}")
        
        if not isinstance(data, (list, tuple)) or len(data) < 2:
            print(f"Formato de datos inesperado: {data}")
            return {"rate": 0}
        
        meta, asset_ctxs = data[0], data[1]
        
        # Imprimir meta y asset_ctxs para inspección
        print(f"meta: {json.dumps(meta, indent=2)}")
        print(f"asset_ctxs: {json.dumps(asset_ctxs, indent=2)}")
        
        # Intentar encontrar el activo en meta['universe']
        if 'universe' in meta:
            for asset in meta['universe']:
                if asset.get('name') == coin:
                    asset_index = meta['universe'].index(asset)
                    if asset_index < len(asset_ctxs):
                        asset_data = asset_ctxs[asset_index]
                        return {"rate": float(asset_data.get('funding', 0))}
        
        print(f"No se encontró el activo {coin} en meta['universe']")
        return {"rate": 0}
    except Exception as e:
        print(f"Error al obtener funding rate de Hyperliquid: {e}")
        return {"rate": 0}
    
def get_hyperliquid_asset_metadata(hl_info, coin):
    try:
        data = hl_info.meta()
        for asset in data["universe"]:
            if asset["name"] == coin:
                return {
                    'sz_decimals': asset.get('szDecimals', 8),
                    'min_sz': float(asset.get('minSz', 0.001))
                }
        raise Exception(f"Activo {coin} no encontrado en el universo de Hyperliquid.")
    except Exception as e:
        raise Exception(f"Fallo al obtener metadatos del activo para {coin}: {e}")

def get_hyperliquid_asset_index(hl_info, coin):
    try:
        data = hl_info.meta()
        for idx, asset in enumerate(data["universe"]):
            if asset["name"] == coin:
                return idx
        raise Exception(f"Activo {coin} no encontrado en el universo de Hyperliquid.")
    except Exception as e:
        raise Exception(f"Fallo al obtener el índice del activo para {coin}: {e}")

def adjust_hyperliquid_size(hl_info, coin, sz):
    try:
        metadata = get_hyperliquid_asset_metadata(hl_info, coin)
        min_sz = metadata['min_sz']
        sz_decimals = metadata['sz_decimals']
        if sz < min_sz:
            print(f"Tamaño {sz} por debajo del mínimo {min_sz} para {coin}. Ajustando al mínimo.")
            sz = min_sz
        sz = math.floor(sz * 10**sz_decimals) / 10**sz_decimals  # Redondeo hacia abajo
        print(f"Tamaño ajustado para {coin}: {sz} (decimales: {sz_decimals}, mín: {min_sz})")
        return sz
    except Exception as e:
        print(f"Fallo al ajustar el tamaño de Hyperliquid: {e}")
        raise

def adjust_hyperliquid_price(hl_info, px, coin, is_buy):
    try:
        if px is None:
            return None
        asset_index = get_hyperliquid_asset_index(hl_info, coin)
        tick_size = BTC_TICK_SIZE if asset_index == 0 else DEFAULT_TICK_SIZE
        px_rounded = math.floor(px / tick_size) * tick_size if not is_buy else math.ceil(px / tick_size) * tick_size
        decimal_places = len(str(tick_size).split('.')[1]) if '.' in str(tick_size) else 0
        px_rounded = round(px_rounded, decimal_places)
        remainder = px_rounded % tick_size
        print(f"Ajuste de precio para {coin} (asset={asset_index}): Original={px}, Tamaño de Tick={tick_size}, Ajustado={px_rounded}, Resto (debe ser 0)={remainder}")
        if remainder != 0:
            print(f"El precio ajustado {px_rounded} no es divisible por el tamaño de tick {tick_size}.")
        return px_rounded
    except Exception as e:
        print(f"Fallo al ajustar el precio de Hyperliquid: {e}")
        raise

def check_hyperliquid_margin(hl_info, hyper_address, notional_value, leverage):
    try:
        user_state = hl_info.user_state(hyper_address)
        withdrawable = float(user_state.get('withdrawable', 0))
        required_margin = notional_value / leverage
        print(f"Verificación de margen: Notional={notional_value}, Apalancamiento={leverage}, Margen Requerido={required_margin}")
        print(f"Retirable={withdrawable}")
        if required_margin > withdrawable:
            raise Exception(f"Margen insuficiente para colocar la orden. Requerido: {required_margin}, Disponible: {withdrawable}")
        return True
    except Exception as e:
        print(f"Error al verificar el margen de Hyperliquid: {e}")
        raise

def place_hyperliquid_order(hl_info, hl_exchange, hyper_address, coin, is_buy, sz, leverage, reduce_only):
    try:
        if not hl_exchange:
            raise Exception("Cliente de intercambio de Hyperliquid no inicializado.")
        
        sz_adjusted = adjust_hyperliquid_size(hl_info, coin, sz)
        order_type = {"limit": {"tif": "Gtc"}}
        
        # Usar precio de mercado ajustado
        _, mark_price = get_hyperliquid_best_price(hl_info, coin, is_buy)
        adjusted_mark_price = mark_price * (1.0005 if is_buy else 0.9995)
        px_adjusted = adjust_hyperliquid_price(hl_info, adjusted_mark_price, coin, is_buy)
        
        # Verificar margen para órdenes no reduce_only
        if not reduce_only:
            notional_value = sz_adjusted * px_adjusted
            check_hyperliquid_margin(hl_info, hyper_address, notional_value, leverage)
        else:
            print("Órden reduce_only detectada. Omitiendo verificación de margen.")
        
        # Configurar apalancamiento
        try:
            hl_exchange.update_leverage(name=coin, leverage=leverage, is_cross=True)
            print(f"Apalancamiento establecido a {leverage}x para {coin}")
        except Exception as e:
            print(f"Fallo al establecer apalancamiento: {e}. Usando predeterminado.")
        
        order_details = {
            "coin": coin,
            "is_buy": is_buy,
            "original_size": sz,
            "adjusted_size": sz_adjusted,
            "adjusted_price": px_adjusted,
            "order_type": order_type,
            "reduce_only": reduce_only,
            "leverage": leverage
        }
        print(f"Intentando orden en Hyperliquid: {order_details}")
        
        response = hl_exchange.order(
            name=coin,
            is_buy=is_buy,
            sz=sz_adjusted,
            limit_px=px_adjusted,
            order_type=order_type,
            reduce_only=reduce_only
        )
        
        print(f"Respuesta de Hyperliquid: {response}")
        
        statuses = response.get('response', {}).get('data', {}).get('statuses', [])
        for status in statuses:
            if 'error' in status:
                raise Exception(f"Orden rechazada: {status['error']}")
        
        return response
    except Exception as e:
        print(f"Fallo en la orden de Hyperliquid: {e}")
        traceback.print_exc()
        raise

def get_hyperliquid_best_price(hl_info, coin, is_buy):
    try:
        data = hl_info.meta_and_asset_ctxs()
        meta = data[0]
        asset_ctxs = data[1]
        asset_index = None
        for idx, asset in enumerate(meta["universe"]):
            if asset["name"] == coin:
                asset_index = idx
                break
        if asset_index is None:
            raise Exception(f"Activo {coin} no encontrado en Hyperliquid")
        asset_data = asset_ctxs[asset_index]
        mark_price = float(asset_data["markPx"])
        best_price = mark_price * (0.999 if is_buy else 1.001)
        print(f"Cálculo del mejor precio en Hyperliquid: mark_price={mark_price}, is_buy={is_buy}, best_price={best_price}")
        return best_price, mark_price
    except Exception as e:
        print(f"Error al obtener el mejor precio de Hyperliquid: {e}")
        raise

def get_hyperliquid_positions(hl_info, hyper_address):
    try:
        user_state = hl_info.user_state(hyper_address)
        positions = user_state.get('assetPositions', [])
        formatted_positions = {}
        for pos in positions:
            position_data = pos.get('position', {})
            coin = position_data.get('coin') + 'USDT'
            size = float(position_data.get('szi', 0))
            formatted_positions[coin] = {
                'size': size,
                'entry_price': float(position_data.get('entryPx', 0)),
                'direction': 'Long' if size > 0 else 'Short'
            }
        return formatted_positions
    except Exception as e:
        print(f"Error al obtener posiciones de Hyperliquid: {e}")
        traceback.print_exc()
        return {}
