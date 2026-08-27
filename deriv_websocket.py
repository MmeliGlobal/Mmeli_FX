"""
Deriv WebSocket API - With Correct Headers
"""

import json
import websocket
import pandas as pd
import logging
import time
import threading
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DerivWebSocket:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.authorized = False
        self.token = None
        self.app_id = None
        self.account_id = None
        self.responses = []
        self.is_running = False
        
    def connect(self, token, app_id):
        """Connect to Deriv WebSocket with proper headers"""
        try:
            self.token = token
            self.app_id = app_id
            
            # Build WebSocket URL
            ws_url = f"wss://ws.binaryws.com/websockets/v3"
            
            logger.info(f"🔌 Connecting to {ws_url}")
            logger.info(f"📡 App ID: {app_id}")
            
            # Create WebSocket with headers
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                header={
                    "Deriv-App-ID": str(app_id),  # ✅ Send App ID in header!
                    "Authorization": f"Bearer {token}",  # ✅ Send token as Bearer!
                    "Content-Type": "application/json"
                }
            )
            
            # Run WebSocket in thread
            self.is_running = True
            thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            thread.start()
            
            # Wait for authorization
            timeout = 15
            while timeout > 0:
                if self.authorized:
                    logger.info(f"✅ Connected and authorized: {self.account_id}")
                    return True
                time.sleep(0.5)
                timeout -= 0.5
            
            logger.error("❌ Authorization timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            return False
    
    def on_open(self, ws):
        logger.info("✅ WebSocket opened")
        # Send ping to test connection
        self.send({"ping": 1})
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            
            # Check for ping response
            if data.get('msg_type') == 'ping':
                logger.info("📩 Received ping response")
            
            # Check authorization
            if 'authorize' in data:
                if 'error' in data:
                    logger.error(f"❌ Auth error: {data['error'].get('message', 'Unknown')}")
                else:
                    self.authorized = True
                    self.account_id = data['authorize'].get('loginid', 'Unknown')
                    logger.info(f"✅ Authorized: {self.account_id}")
            
            self.responses.append(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
        except Exception as e:
            logger.error(f"❌ Message error: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self.authorized = False
        self.is_running = False
        logger.info(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
    
    def send(self, data):
        """Send message"""
        try:
            if self.ws:
                self.ws.send(json.dumps(data))
                return True
            else:
                logger.warning("⚠️ Cannot send: WebSocket not connected")
                return False
        except Exception as e:
            logger.error(f"❌ Send error: {e}")
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
        forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
        
        if symbol in forex_pairs:
            return f"frx{symbol}"
        elif symbol == 'XAUUSD':
            return 'frxXAUUSD'
        elif symbol == 'XAGUSD':
            return 'frxXAGUSD'
        else:
            return symbol
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical candles from Deriv"""
        if not self.authorized:
            logger.error("❌ Not authorized")
            return None
        
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            tf_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
            }
            minutes = tf_map.get(timeframe, 60)
            
            end_time = int(time.time())
            start_time = end_time - (bars * minutes * 60)
            
            logger.info(f"📡 Fetching {bars} candles for {deriv_symbol} from Deriv...")
            
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
                    logger.warning(f"⚠️ No candles for {deriv_symbol}")
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
                
                logger.info(f"✅ Fetched {len(df)} candles from Deriv")
                return df
            else:
                error = response.get('error', {}).get('message', 'Unknown') if response else 'No response'
                logger.warning(f"⚠️ No data: {error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price"""
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            self.responses = []
            
            self.send({
                "ticks": deriv_symbol,
                "subscribe": False
            })
            
            response = self.wait_for_response('tick', timeout=5)
            
            if response and 'tick' in response:
                price = response['tick']['ask']
                return price - 0.0001, price
            return None, None
        except Exception as e:
            logger.error(f"❌ Price error: {e}")
            return None, None
    
    def disconnect(self):
        """Disconnect"""
        self.is_running = False
        if self.ws:
            self.ws.close()
            self.connected = False
            self.authorized = False

# Test function
def test_deriv():
    from config import DERIV_TOKEN, DERIV_APP_ID
    
    print("="*50)
    print("🔌 Testing Deriv WebSocket...")
    print("="*50)
    
    if not DERIV_TOKEN or DERIV_TOKEN == 'YOUR_DERIV_TOKEN_HERE':
        print("❌ No token found!")
        print("💡 Get token from: https://app.deriv.com/account/api-token")
        return
    
    print(f"\n📡 App ID: {DERIV_APP_ID}")
    print(f"📡 Token: {DERIV_TOKEN[:20]}...")
    
    api = DerivWebSocket()
    
    if api.connect(DERIV_TOKEN, DERIV_APP_ID):
        print(f"✅ Connected! Account: {api.account_id}")
        
        print("\n📊 Fetching EURUSD 1h data...")
        df = api.get_historical_data('EURUSD', '1h', 20)
        
        if df is not None and len(df) > 0:
            print(f"✅ Fetched {len(df)} candles")
            print(df[['time', 'Open', 'Close']].tail())
        else:
            print("❌ No data returned")
        
        print("\n💰 Getting current price...")
        bid, ask = api.get_current_price('EURUSD')
        if bid and ask:
            print(f"✅ EURUSD: Bid={bid:.5f}, Ask={ask:.5f}")
        else:
            print("❌ Could not get price")
        
        api.disconnect()
    else:
        print("❌ Connection failed!")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    test_deriv()