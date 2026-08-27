"""
Broker API - Uses Deriv Public WebSocket with Aggressive Caching
"""

import pandas as pd
import logging
import time
from datetime import datetime, timedelta
import json
import websocket
import threading
from collections import OrderedDict
from config import CACHE_DURATION, MAX_CACHE_SIZE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokerAPI:
    def __init__(self):
        self.connected = False
        self.source = 'deriv_public'
        self.ws = None
        self.responses = []
        self.is_running = False
        # Cache for speed
        self.cache = OrderedDict()
        self.cache_duration = 60  # Cache for 60 seconds (increased from 30)
        self.price_cache = {}  # Separate cache for prices
        self.price_cache_time = {}
        
    def connect(self, app_id=None, token=None):
        """Connect to Deriv Public WebSocket - NO CREDENTIALS NEEDED!"""
        try:
            ws_url = "wss://api.derivws.com/trading/v1/options/ws/public"
            
            logger.info(f"🔌 Connecting to Public WebSocket...")
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            self.is_running = True
            thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            thread.start()
            
            timeout = 10
            while timeout > 0:
                if self.connected:
                    logger.info("✅ Connected to Deriv Public WebSocket")
                    return True
                time.sleep(0.5)
                timeout -= 0.5
            
            logger.error("❌ Connection timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            return False
    
    def on_open(self, ws):
        logger.info("✅ WebSocket opened")
        self.connected = True
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.responses.append(data)
            if len(self.responses) > 500:
                self.responses = self.responses[-250:]
        except Exception as e:
            logger.error(f"Message error: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self.is_running = False
        logger.info(f"🔌 WebSocket closed")
    
    def send(self, data):
        """Send message"""
        try:
            if self.ws:
                self.ws.send(json.dumps(data))
                return True
            return False
        except:
            return False
    
    def wait_for_response(self, msg_type, timeout=10):
        """Wait for specific response"""
        start = time.time()
        while time.time() - start < timeout:
            for i, data in enumerate(self.responses):
                if msg_type in data:
                    self.responses.pop(i)
                    return data
            time.sleep(0.1)
        return None
    
    def get_symbol_mapping(self, symbol):
        """Convert symbol to Deriv format"""
        forex_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF',
            'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
            'GBPJPY', 'GBPAUD', 'GBPCAD', 'GBPNZD', 'GBPCHF',
            'AUDJPY', 'AUDCAD', 'AUDNZD', 'AUDCHF',
            'NZDJPY', 'NZDCAD', 'NZDCHF',
            'CADJPY', 'CHFJPY',
            'USDTRY', 'USDZAR', 'USDMXN', 'USDSGD', 'USDHKD',
            'EURTRY', 'EURZAR', 'EURMXN',
            'GBPTRY', 'GBPZAR',
            'AUDTRY', 'NZDTRY'
        ]
        
        if symbol in forex_pairs:
            return f"frx{symbol}"
        elif symbol == 'XAUUSD':
            return 'frxXAUUSD'
        elif symbol == 'XAGUSD':
            return 'frxXAGUSD'
        else:
            return symbol
    
    def _get_cache_key(self, symbol, timeframe, bars):
        return f"{symbol}_{timeframe}_{bars}"
    
    def _get_from_cache(self, key):
        """Get data from cache if valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if (datetime.now() - timestamp).seconds < self.cache_duration:
                return data
            else:
                del self.cache[key]
        return None
    
    def _set_cache(self, key, data):
        """Store data in cache"""
        if len(self.cache) >= 100:
            self.cache.popitem(last=False)
        self.cache[key] = (data, datetime.now())
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical candles with caching"""
        if not self.connected:
            logger.error("Not connected")
            return None
        
        # Check cache first
        cache_key = self._get_cache_key(symbol, timeframe, bars)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            tf_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
            }
            minutes = tf_map.get(timeframe, 60)
            
            end_time = int(time.time())
            start_time = end_time - (bars * minutes * 60)
            
            # Only log if not a frequent fallback call
            if bars > 10:
                logger.info(f"📡 Fetching {bars} candles for {symbol}...")
            
            self.responses = []
            
            request = {
                "ticks_history": deriv_symbol,
                "start": start_time,
                "end": end_time,
                "adjust_start_time": 1,
                "style": "candles",
                "granularity": minutes * 60
            }
            self.send(request)
            
            response = self.wait_for_response('candles', timeout=15)
            
            if response and 'candles' in response:
                candles = response['candles']
                
                if not candles:
                    logger.warning(f"⚠️ No candles for {symbol}")
                    return None
                
                df = pd.DataFrame(candles)
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                
                df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close'
                }, inplace=True)
                
                df['Open'] = pd.to_numeric(df['Open'])
                df['High'] = pd.to_numeric(df['High'])
                df['Low'] = pd.to_numeric(df['Low'])
                df['Close'] = pd.to_numeric(df['Close'])
                
                df = df.sort_values('time')
                
                if bars > 10:
                    logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
                
                # Store in cache
                self._set_cache(cache_key, df)
                
                return df
            else:
                if bars > 10:
                    logger.warning(f"⚠️ No data for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price with aggressive caching"""
        # Check price cache first (valid for 30 seconds)
        if symbol in self.price_cache:
            price_data, timestamp = self.price_cache[symbol]
            if (datetime.now() - timestamp).seconds < 30:
                return price_data
        
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            # Clear responses for this request
            self.responses = []
            
            self.send({
                "ticks": deriv_symbol,
                "subscribe": False
            })
            
            start = time.time()
            while time.time() - start < 3:
                for i, data in enumerate(self.responses):
                    if 'tick' in data:
                        self.responses.pop(i)
                        if 'ask' in data['tick']:
                            price = data['tick']['ask']
                            result = (price - 0.0001, price)
                            self.price_cache[symbol] = (result, datetime.now())
                            return result
                        elif 'quote' in data['tick']:
                            price = data['tick']['quote']
                            result = (price - 0.0001, price)
                            self.price_cache[symbol] = (result, datetime.now())
                            return result
                time.sleep(0.1)
            
            # Fallback: use last close from historical data (cached)
            logger.warning(f"⚠️ Could not get current price for {symbol}, using fallback...")
            df = self.get_historical_data(symbol, '1m', 5)
            if df is not None and len(df) > 0:
                last_price = df['Close'].iloc[-1]
                result = (last_price - 0.0001, last_price)
                self.price_cache[symbol] = (result, datetime.now())
                return result
            
            return None, None
        except Exception as e:
            logger.error(f"❌ Price error: {e}")
            return None, None
    
    def get_data_source(self):
        return self.source
    
    def switch_source(self, source):
        self.source = source
        return True
    
    def place_order(self, symbol, action, volume, sl, tp):
        logger.info(f"⚠️ Order function disabled: {action} {symbol}")
        return {'order': None, 'status': 'disabled'}
    
    def clear_cache(self):
        """Clear all caches"""
        self.cache.clear()
        self.price_cache.clear()
        logger.info("🧹 Cache cleared")
    
    def disconnect(self):
        """Disconnect"""
        self.is_running = False
        if self.ws:
            self.ws.close()
            self.connected = False

# Test function
def test_broker():
    broker = BrokerAPI()
    
    print("="*50)
    print("🔌 Testing Broker API (Public WebSocket)")
    print("📡 No credentials needed!")
    print("="*50)
    
    if broker.connect():
        print("✅ Connected!")
        
        test_symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        for symbol in test_symbols:
            print(f"\n📊 Testing {symbol}...")
            # First call - should fetch
            df1 = broker.get_historical_data(symbol, '1h', 20)
            # Second call - should use cache
            df2 = broker.get_historical_data(symbol, '1h', 20)
            
            if df1 is not None and len(df1) > 0:
                print(f"   ✅ Fetched {len(df1)} candles (cached: {df2 is not None})")
            else:
                print(f"   ❌ No data")
        
        broker.disconnect()
    else:
        print("❌ Connection failed!")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    test_broker()