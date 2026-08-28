"""
Broker API - Yahoo Finance
Works everywhere! No WebSocket needed.
"""

import pandas as pd
import logging
import yfinance as yf
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokerAPI:
    def __init__(self):
        self.connected = False
        self.source = 'yahoo'
        self.cache = {}
        self.cache_duration = 60
        
    def connect(self, app_id=None, token=None):
        """Connect to Yahoo Finance"""
        try:
            test = yf.Ticker('EURUSD=X').history(period='1d')
            if test is not None and len(test) > 0:
                self.connected = True
                logger.info("✅ Connected to Yahoo Finance")
                return True
            else:
                logger.error("❌ Yahoo Finance test failed")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_symbol_mapping(self, symbol):
        """Map symbol for Yahoo Finance"""
        mapping = {
            'XAUUSD': 'GC=F',
            'XAGUSD': 'SI=F',
            'BTCUSD': 'BTC-USD',
            'ETHUSD': 'ETH-USD',
            'SOLUSD': 'SOL-USD',
            'US30': 'YM=F',
            'NAS100': 'NQ=F',
            'SPX500': 'ES=F',
            'UK100': 'FTSE=F',
            'GER30': 'DAX=F'
        }
        return mapping.get(symbol, f"{symbol}=X")
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical data from Yahoo Finance with caching"""
        if not self.connected:
            logger.error("Not connected")
            return None
        
        # Check cache
        cache_key = f"{symbol}_{timeframe}_{bars}"
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_duration:
                logger.info(f"📦 Cache hit for {symbol}")
                return data
        
        try:
            yahoo_symbol = self.get_symbol_mapping(symbol)
            
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '60m', '4h': '60m', '1d': '1d', '1w': '1wk'
            }
            
            period_map = {
                '1m': '2d', '5m': '5d', '15m': '7d', '30m': '14d',
                '1h': '30d', '4h': '60d', '1d': '1y', '1w': '2y'
            }
            
            interval = tf_map.get(timeframe, '60m')
            period = period_map.get(timeframe, '30d')
            
            logger.info(f"📡 Fetching {symbol} from Yahoo Finance...")
            
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df is None or len(df) == 0:
                logger.warning(f"⚠️ No data for {symbol}")
                return None
            
            df = df.reset_index()
            
            if 'Datetime' in df.columns:
                df.rename(columns={'Datetime': 'time'}, inplace=True)
            elif 'Date' in df.columns:
                df.rename(columns={'Date': 'time'}, inplace=True)
            
            df.rename(columns={
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close'
            }, inplace=True)
            
            df['Open'] = pd.to_numeric(df['Open'])
            df['High'] = pd.to_numeric(df['High'])
            df['Low'] = pd.to_numeric(df['Low'])
            df['Close'] = pd.to_numeric(df['Close'])
            
            df = df.sort_values('time')
            df = df.tail(bars)
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
            
            # Store in cache
            self.cache[cache_key] = (df, datetime.now())
            
            return df
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price"""
        try:
            yahoo_symbol = self.get_symbol_mapping(symbol)
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data is not None and len(data) > 0:
                last_price = data['Close'].iloc[-1]
                spread = 0.0005 if symbol in ['XAUUSD', 'XAGUSD'] else 0.0001
                return last_price - spread, last_price
            return None, None
        except:
            return None, None
    
    def get_data_source(self):
        return self.source
    
    def switch_source(self, source):
        self.source = source
        return True
    
    def clear_cache(self):
        self.cache = {}
        logger.info("🧹 Cache cleared")
    
    def disconnect(self):
        self.connected = False

# Test function
def test_broker():
    broker = BrokerAPI()
    
    print("="*50)
    print("🔌 Testing Yahoo Finance Connection")
    print("="*50)
    
    if broker.connect():
        print("✅ Connected to Yahoo Finance!")
        
        print("\n📊 Fetching EURUSD 1h data...")
        df = broker.get_historical_data('EURUSD', '1h', 20)
        
        if df is not None and len(df) > 0:
            print(f"✅ Fetched {len(df)} candles")
            print(df[['time', 'Open', 'Close']].tail())
        else:
            print("❌ No data returned")
        
        print("\n💰 Getting current price...")
        bid, ask = broker.get_current_price('EURUSD')
        if bid and ask:
            print(f"✅ EURUSD: Bid={bid:.5f}, Ask={ask:.5f}")
        else:
            print("❌ Could not get price")
    else:
        print("❌ Connection failed!")
        print("💡 Run: pip install yfinance")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    test_broker()