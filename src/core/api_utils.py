import requests
import time
import math
import traceback
from binance.client import Client
from binance.exceptions import BinanceAPIException
from eth_account import Account
from hyperliquid.utils import constants
import hyperliquid.info as hyperliquid_info
import hyperliquid.exchange as hyperliquid_exchange
import requests
import time
from ratelimit import limits, sleep_and_retry

# Configuración de límites de tasa y caché
CALLS_PER_MINUTE = 1200
PERIOD = 60
CACHE_TTL = 60  # Tiempo de vida del caché en segundos
api_cache = {}

@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=PERIOD)
def api_request(url, method='GET', payload=None, retries=3, delay=5, use_cache=True):
    """
    Realiza una solicitud HTTP con reintentos, control de límites de tasa y caché.
    :param url: URL de la API
    :param method: Método HTTP ('GET' o 'POST')
    :param payload: Datos para solicitudes POST
    :param retries: Número de reintentos
    :param delay: Retraso entre reintentos (segundos)
    :param use_cache: Si se debe usar el caché para esta solicitud
    :return: Respuesta JSON
    """
    cache_key = f"{method}:{url}:{str(payload)}"
    current_time = time.time()

    # Verificar caché si está habilitado
    if use_cache and method.upper() == 'GET':
        if cache_key in api_cache:
            cached_data, timestamp = api_cache[cache_key]
            if current_time - timestamp < CACHE_TTL:
                return cached_data

    # Realizar solicitud con reintentos
    for attempt in range(retries):
        try:
            if method.upper() == 'POST':
                response = requests.post(url, json=payload, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Actualizar caché si está habilitado
            if use_cache and method.upper() == 'GET':
                api_cache[cache_key] = (data, current_time)
            
            return data
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            raise Exception(f"Fallo tras {retries} intentos: {e}")
        except Exception as e:
            raise Exception(f"Error inesperado: {e}")
def round_down_by_step(value, step):
    return math.floor(value / step) * step

# Binance utilities
def sync_binance_time():
    try:
        url = 'https://fapi.binance.com/fapi/v1/time'
        response = requests.get(url)
        response.raise_for_status()
        server_time = response.json()['serverTime']
        local_time = int(time.time() * 1000)
        offset = server_time - local_time
        Client.FUTURES_TIME_OFFSET = offset
        # Agregar un pequeño retraso para asegurar la sincronización
        time.sleep(0.5)
        return offset
    except Exception as e:
        print(f"Error al sincronizar tiempo con Binance: {e}")
        return None

def init_binance_client(api_key, api_secret, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Sincronizar tiempo primero
            offset = sync_binance_time()
            if offset is None:
                raise Exception("No se pudo sincronizar el tiempo con Binance")
                
            # Inicializar el cliente con el offset de tiempo
            client = Client(api_key, api_secret)
            client.timestamp_offset = offset
            
            # Verificar conectividad
            client.get_account()
            print("✅ Cliente de Binance inicializado correctamente")
            return client
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Fallo al inicializar el cliente de Binance después de {max_retries} intentos: {e}")
                return None
            print(f"Intento {attempt + 1} fallido, reintentando...")
            time.sleep(2 ** attempt)  # Backoff exponencial

def check_binance_api(client):
    try:
        client.get_account()
        return True
    except Exception as e:
        print(f"Fallo en la verificación de la API de Binance: {e}")
        return False

def get_binance_filters(client, symbol):
    try:
        info = client.futures_exchange_info()
        for s in info['symbols']:
            if s['symbol'] == symbol:
                filters = {}
                for f in s['filters']:
                    if f['filterType'] == 'PRICE_FILTER':
                        filters['tickSize'] = float(f['tickSize'])
                    if f['filterType'] == 'LOT_SIZE':
                        filters['stepSize'] = float(f['stepSize'])
                return filters
        return {'tickSize': 0.01, 'stepSize': 0.001}
    except:
        return {'tickSize': 0.01, 'stepSize': 0.001}

def round_by_step(value, step):
    return round(round(value / step) * step, 8)

def get_binance_best_price(client, symbol, side):
    try:
        order_book = client.futures_order_book(symbol=symbol, limit=5)
        best_price = float(order_book['bids'][0][0]) if side == 'BUY' else float(order_book['asks'][0][0])
        return best_price
    except Exception as e:
        print(f"Error al obtener el libro de órdenes de Binance: {e}")
        raise Exception("No se puede obtener el mejor precio de Binance")

def wait_for_binance_order(client, symbol, order_id, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        order = client.futures_get_order(symbol=symbol, orderId=order_id)
        print(f"Verificación de estado de la orden: {order}")
        if order['status'] in ['FILLED', 'CANCELED', 'REJECTED', 'EXPIRED']:
            return order
        time.sleep(1)
    raise Exception(f"La orden {order_id} no se completó en {timeout} segundos")

def get_binance_leverage(client, symbol):
    try:
        leverage_brackets = client.futures_leverage_bracket(symbol=symbol)
        for bracket in leverage_brackets:
            if bracket['symbol'] == symbol:
                return float(bracket['brackets'][0]['initialLeverage'])
        return 1.0
    except:
        return 1.0

def get_current_price(client, symbol):
    try:
        return float(client.futures_symbol_ticker(symbol=symbol)['price'])
    except:
        return 0.0

# Hyperliquid utilities
def validate_hyperliquid_credentials(hyper_address, hyper_private_key):
    """
    Valida el formato y la integridad de las credenciales de Hyperliquid.
    :param hyper_address: Dirección pública de Hyperliquid
    :param hyper_private_key: Clave privada de Hyperliquid
    :return: Tupla (bool, str) con el estado de validación y mensaje
    """
    try:
        # Validar formato de dirección
        if not isinstance(hyper_address, str):
            return False, "La dirección de Hyperliquid debe ser una cadena de texto."
        if not hyper_address.startswith('0x'):
            return False, "La dirección de Hyperliquid debe comenzar con '0x'."
        if len(hyper_address) != 42:
            return False, f"La dirección de Hyperliquid debe tener 42 caracteres, tiene {len(hyper_address)}."
        if not all(c in '0123456789abcdefABCDEF' for c in hyper_address[2:]):
            return False, "La dirección de Hyperliquid contiene caracteres inválidos."

        # Validar formato de clave privada
        if not isinstance(hyper_private_key, str):
            return False, "La clave privada de Hyperliquid debe ser una cadena de texto."
        if not hyper_private_key.startswith('0x'):
            return False, "La clave privada de Hyperliquid debe comenzar con '0x'."
        if len(hyper_private_key) != 66:
            return False, f"La clave privada de Hyperliquid debe tener 66 caracteres, tiene {len(hyper_private_key)}."
        if not all(c in '0123456789abcdefABCDEF' for c in hyper_private_key[2:]):
            return False, "La clave privada de Hyperliquid contiene caracteres inválidos."

        # Validar bytes de la clave privada
        try:
            private_key_bytes = bytes.fromhex(hyper_private_key[2:])
            if len(private_key_bytes) != 32:
                return False, f"La clave privada de Hyperliquid debe tener exactamente 32 bytes, tiene {len(private_key_bytes)}."
        except ValueError:
            return False, "La clave privada de Hyperliquid contiene caracteres hexadecimales inválidos."

        return True, "El formato de las credenciales de Hyperliquid es válido."
    except Exception as e:
        return False, f"Error inesperado al validar las credenciales de Hyperliquid: {str(e)}"

def init_hyperliquid_clients(hyper_private_key):
    try:
        wallet = Account.from_key(hyper_private_key)
        hl_info = hyperliquid_info.Info(base_url=constants.MAINNET_API_URL, skip_ws=True)
        hl_exchange = hyperliquid_exchange.Exchange(
            wallet=wallet,
            base_url=constants.MAINNET_API_URL
        )
        return wallet, hl_info, hl_exchange
    except Exception as e:
        print(f"Error al inicializar clientes de Hyperliquid: {e}")
        return None, None, None

def check_hyperliquid_api(hl_info, hyper_address):
    try:
        meta = hl_info.meta()
        if not meta:
            print("Fallo al obtener metadatos de Hyperliquid.")
            return False
        user_state = hl_info.user_state(hyper_address)
        if not user_state:
            print("Fallo al obtener el estado del usuario de Hyperliquid.")
            return False
        return True
    except Exception as e:
        print(f"Fallo en la verificación de la API de Hyperliquid: {e}")
        return False

def get_hyperliquid_pairs(hl_info):
    try:
        data = hl_info.meta()
        return sorted([coin['name'] + 'USDT' for coin in data['universe']])
    except:
        return ['BTCUSDT']
