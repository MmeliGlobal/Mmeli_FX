"""
Deriv WebSocket API - Direct connection without external package
Uses websocket-client library (widely available)
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

class DerivWS:
    def __init__(self):
        self.connected = False
        self.ws = None
        self.token = None
        self.account_id = None
        self.response_queue = []
        self.is_running = False
        
    def connect(self, token, app_id=1234):
        """Connect to Deriv WebSocket"""
        try:
            self.token = token
            
            # WebSocket URL
            ws_url = f"wss://ws.binaryws.com/websockets/v3?app_id={app_id}"
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Start WebSocket in a separate thread
            self.is_running = True
            thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            thread.start()
            
            # Wait for connection
            time.sleep(2)
            
            # Send authorization
            self.send({"authorize": token})
            
            # Wait for auth response
            timeout = 10
            while timeout > 0 and not self.connected:
                time.sleep(0.5)
                timeout -= 0.5
            
            return self.connected
            
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            return False
    
    def on_open(self, ws):
        logger.info("✅ WebSocket connected")
    
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            
            # Check for authorization response
            if 'authorize' in data:
                if 'error' in data:
                    logger.error(f"❌ Auth error: {data['error']['message']}")
                else:
                    self.connected = True
                    self.account_id = data['authorize']['loginid']
                    logger.info(f"✅ Authorized: {self.account_id}")
            
            # Store response for later
            self.response_queue.append(data)
            
        except Exception as e:
            logger.error(f"Message error: {e}")
    
    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        self.is_running = False
        logger.info("WebSocket closed")
    
    def send(self, data):
        """Send message to WebSocket"""
        if self.ws:
            self.ws.send(json.dumps(data))
    
    def wait_for_response(self, msg_type, timeout=10):
        """Wait for a specific response type"""
        start = time.time()
        while time.time() - start < timeout:
            for i, data in enumerate(self.response_queue):
                if msg_type in data:
                    self.response_queue.pop(i)
                    return data
            time.sleep(0.1)
        return None
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical OHLC data"""
        if not self.connected:
            logger.error("Not connected")
            return None
            
        try:
            # Map symbol to Deriv format
            deriv_symbol = symbol
            if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD']:
                deriv_symbol = f"frx{symbol}"
            
            # Map timeframe to minutes
            tf_map = {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '4h': 240,
                '1d': 1440,
                '1w': 10080
            }
            
            minutes = tf_map.get(timeframe, 60)
            
            # Calculate start time
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (bars * minutes * 60)
            
            logger.info(f"📡 Fetching {bars} candles for {deriv_symbol}...")
            
            # Send request
            self.send({
                "ticks_history": deriv_symbol,
                "start": start_time,
                "end": end_time,
                "adjust_start_time": 1,
                "style": "candles",
                "granularity": minutes * 60
            })
            
            # Wait for response
            response = self.wait_for_response('candles', timeout=15)
            
            if response and 'candles' in response:
                candles = response['candles']
                
                # Convert to DataFrame
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
            else:
                logger.warning(f"⚠️ No data for {deriv_symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price"""
        try:
            deriv_symbol = symbol
            if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD']:
                deriv_symbol = f"frx{symbol}"
            
            self.send({"ticks": deriv_symbol, "subscribe": False})
            
            response = self.wait_for_response('tick', timeout=5)
            
            if response and 'tick' in response:
                price = response['tick']['ask']
                return price - 0.0001, price
            return None, None
        except:
            return None, None
    
    def disconnect(self):
        """Disconnect from Deriv"""
        self.is_running = False
        if self.ws:
            self.ws.close()