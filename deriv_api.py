"""
Deriv API Wrapper - Real Deriv Data
Matches your Deriv web platform charts!
"""

import asyncio
import pandas as pd
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DerivAPIWrapper:
    def __init__(self):
        self.api = None
        self.connected = False
        self.token = None
        self.account_id = None
        
    def connect(self, token, app_id=1234):
        """Connect to Deriv API"""
        try:
            from deriv_api import DerivAPI
            
            self.token = token
            self.api = DerivAPI(app_id=app_id)
            
            # Run async connection
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self._authorize())
            
            if response and 'authorize' in response:
                self.connected = True
                self.account_id = response['authorize'].get('loginid', 'Unknown')
                logger.info(f"✅ Connected to Deriv API. Account: {self.account_id}")
                return True
            else:
                error = response.get('error', {}).get('message', 'Unknown') if response else 'No response'
                logger.error(f"❌ Authorization failed: {error}")
                return False
                
        except ImportError:
            logger.error("❌ python_deriv_api not installed. Run: pip install python_deriv_api")
            return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    async def _authorize(self):
        """Authorize with Deriv"""
        try:
            return await self.api.authorize(self.token)
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return None
    
    async def _get_ticks_history(self, symbol, start, end, granularity):
        """Get historical candles"""
        try:
            return await self.api.ticks_history({
                "ticks_history": symbol,
                "start": start,
                "end": end,
                "style": "candles",
                "granularity": granularity
            })
        except Exception as e:
            logger.error(f"Ticks history error: {e}")
            return None
    
    async def _get_current_tick(self, symbol):
        """Get current price"""
        try:
            return await self.api.ticks({
                "ticks": symbol,
                "subscribe": False
            })
        except Exception as e:
            logger.error(f"Tick error: {e}")
            return None
    
    def get_symbol_mapping(self, symbol):
        """Convert symbol to Deriv format"""
        # Forex pairs need 'frx' prefix
        forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDCHF']
        
        if symbol in forex_pairs:
            return f"frx{symbol}"
        elif symbol == 'XAUUSD':
            return 'frxXAUUSD'  # Gold
        elif symbol == 'XAGUSD':
            return 'frxXAGUSD'  # Silver
        else:
            return symbol
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch historical OHLC data from Deriv"""
        if not self.connected:
            logger.error("Not connected to Deriv")
            return None
        
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            # Map timeframe to minutes
            tf_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
            }
            minutes = tf_map.get(timeframe, 60)
            
            # Calculate time range
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (bars * minutes * 60)
            
            logger.info(f"📡 Fetching {bars} candles for {deriv_symbol} from Deriv...")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(
                self._get_ticks_history(
                    deriv_symbol, 
                    start_time, 
                    end_time, 
                    minutes * 60
                )
            )
            
            if response and 'candles' in response:
                candles = response['candles']
                
                if not candles:
                    logger.warning(f"⚠️ No candles for {deriv_symbol}")
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(candles)
                df['time'] = pd.to_datetime(df['epoch'], unit='s')
                
                df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close'
                }, inplace=True)
                
                # Convert to numeric
                df['Open'] = pd.to_numeric(df['Open'])
                df['High'] = pd.to_numeric(df['High'])
                df['Low'] = pd.to_numeric(df['Low'])
                df['Close'] = pd.to_numeric(df['Close'])
                
                # Sort chronologically
                df = df.sort_values('time')
                
                logger.info(f"✅ Fetched {len(df)} candles from Deriv for {symbol}")
                return df
            else:
                error = response.get('error', {}).get('message', 'Unknown') if response else 'No response'
                logger.warning(f"⚠️ No data: {error}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current price"""
        try:
            deriv_symbol = self.get_symbol_mapping(symbol)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(self._get_current_tick(deriv_symbol))
            
            if response and 'tick' in response:
                price = response['tick']['ask']
                return price - 0.0001, price
            return None, None
        except:
            return None, None
    
    def disconnect(self):
        """Disconnect from Deriv"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.api.clear())
            self.connected = False
            logger.info("Disconnected from Deriv")
        except:
            pass

# Test function
def test_deriv():
    """Test Deriv API connection"""
    from config import DERIV_TOKEN, DERIV_APP_ID
    
    api = DerivAPIWrapper()
    
    print("="*50)
    print("🔌 Testing Deriv API Connection...")
    print("="*50)
    
    if not DERIV_TOKEN or DERIV_TOKEN == 'YOUR_DERIV_TOKEN_HERE':
        print("❌ No token found!")
        print("💡 Get your token from: https://app.deriv.com/account/api-token")
        return
    
    print(f"\n📡 Token: {DERIV_TOKEN[:15]}...")
    
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
    else:
        print("❌ Connection failed!")
        print("💡 Check your DERIV_TOKEN in config.py")
    
    api.disconnect()
    print("\n" + "="*50)

if __name__ == '__main__':
    test_deriv()