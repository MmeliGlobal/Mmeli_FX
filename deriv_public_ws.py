"""
Deriv Public WebSocket - No App ID, No Token Needed!
For live market prices and analysis
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

class DerivPublicWebSocket:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.responses = []
        self.is_running = False
        
    def connect(self):
        """Connect to Deriv Public WebSocket - NO CREDENTIALS NEEDED!"""
        try:
            # Public WebSocket URL - No App ID, No Token!
            ws_url = "wss://api.derivws.com/trading/v1/options/ws/public"
            
            logger.info(f"🔌 Connecting to Public WebSocket: {ws_url}")
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket in thread
            self.is_running = True
            thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            thread.start()
            
            # Wait for connection
            timeout = 10
            while timeout > 0:
                if self.connected:
                    logger.info("✅ Connected to Public WebSocket")
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
        
        # Subscribe to live ticks for EURUSD (public data)
        self.send({
            "ticks": "frxEURUSD",
            "subscribe": True
        })
        logger.info("📤 Subscribed to EURUSD ticks")
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            
            # Handle different message types
            if 'tick' in data:
                tick = data['tick']
                logger.info(f"💰 {tick.get('symbol', 'UNKNOWN')}: {tick.get('ask', 0):.5f}")
            
            elif 'candles' in data:
                candles = data['candles']
                logger.info(f"📊 Received {len(candles)} candles")
            
            self.responses.append(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error: {e}")
        except Exception as e:
            logger.error(f"❌ Message error: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
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
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical candles from public endpoint"""
        if not self.connected:
            logger.error("❌ Not connected")
            return None
        
        try:
            # Convert symbol to Deriv format
            forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
            if symbol in forex_pairs:
                deriv_symbol = f"frx{symbol}"
            else:
                deriv_symbol = symbol
            
            # Map timeframe to minutes
            tf_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
            }
            minutes = tf_map.get(timeframe, 60)
            
            end_time = int(time.time())
            start_time = end_time - (bars * minutes * 60)
            
            logger.info(f"📡 Fetching {bars} candles for {deriv_symbol}...")
            
            # Clear old responses
            self.responses = []
            
            # Send request
            request = {
                "ticks_history": deriv_symbol,
                "start": start_time,
                "end": end_time,
                "adjust_start_time": 1,
                "style": "candles",
                "granularity": minutes * 60
            }
            self.send(request)
            
            # Wait for response
            start = time.time()
            while time.time() - start < 15:
                for i, data in enumerate(self.responses):
                    if 'candles' in data:
                        self.responses.pop(i)
                        candles = data['candles']
                        
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
                        
                        logger.info(f"✅ Fetched {len(df)} candles")
                        return df
                time.sleep(0.1)
            
            logger.warning("⚠️ No response received")
            return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price from public endpoint"""
        try:
            # Convert symbol to Deriv format
            forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
            if symbol in forex_pairs:
                deriv_symbol = f"frx{symbol}"
            else:
                deriv_symbol = symbol
            
            self.responses = []
            
            self.send({
                "ticks": deriv_symbol,
                "subscribe": False
            })
            
            # Wait for response
            start = time.time()
            while time.time() - start < 5:
                for i, data in enumerate(self.responses):
                    if 'tick' in data:
                        self.responses.pop(i)
                        price = data['tick']['ask']
                        return price - 0.0001, price
                time.sleep(0.1)
            
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

# Test function
def test_public_ws():
    print("="*50)
    print("🔌 Testing Deriv Public WebSocket...")
    print("📡 NO App ID or Token Needed!")
    print("="*50)
    
    api = DerivPublicWebSocket()
    
    if api.connect():
        print("\n✅ Connected to Public WebSocket!")
        
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
        
        time.sleep(2)
        api.disconnect()
    else:
        print("❌ Connection failed!")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    test_public_ws()