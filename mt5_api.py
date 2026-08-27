"""
MetaTrader 5 API wrapper
Handles connection, data fetching, and order placement
"""

import MetaTrader5 as mt5
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MT5API:
    def __init__(self):
        self.connected = False
        
    def connect(self, login, password, server, path):
        """Connect to MetaTrader 5"""
        try:
            # Initialize MT5
            mt5.initialize(
                path=path,
                login=login,
                password=password,
                server=server
            )
            
            # Check if connected
            if mt5.terminal_info():
                self.connected = True
                account = mt5.account_info()
                logger.info(f"✅ Connected to MT5. Account: {account.login}")
                return True
            else:
                logger.error("❌ Failed to connect to MT5")
                return False
                
        except Exception as e:
            logger.error(f"❌ MT5 connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        mt5.shutdown()
        self.connected = False
        logger.info("Disconnected from MT5")
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        """Fetch OHLC data from MT5"""
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
            
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                '1m': mt5.TIMEFRAME_M1,
                '5m': mt5.TIMEFRAME_M5,
                '15m': mt5.TIMEFRAME_M15,
                '30m': mt5.TIMEFRAME_M30,
                '1h': mt5.TIMEFRAME_H1,
                '4h': mt5.TIMEFRAME_H4,
                '1d': mt5.TIMEFRAME_D1,
                '1w': mt5.TIMEFRAME_W1
            }
            
            tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
            
            if rates is None or len(rates) == 0:
                logger.error(f"No data for {symbol}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename columns
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def get_current_price(self, symbol):
        """Get current bid/ask price"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                return tick.bid, tick.ask
            return None, None
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return None, None
    
    def place_order(self, symbol, action, volume, sl, tp):
        """Place a market order"""
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
            
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
                
            # Round volume to allowed step
            lot_step = symbol_info.volume_step
            volume = round(volume / lot_step) * lot_step
            
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
                "price": symbol_info.ask if action == 'buy' else symbol_info.bid,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": "Trading Bible Bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Order placed: {result}")
                return result
            else:
                logger.error(f"❌ Order failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None