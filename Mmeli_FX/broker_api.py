"""
Broker API - Yahoo Finance with all symbols support
"""

import yfinance as yf
import pandas as pd
import logging
from config import ALL_SYMBOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokerAPI:
    def __init__(self):
        self.connected = False
        
    def connect(self, app_id=None, token=None):
        try:
            test_data = self.get_historical_data('EURUSD', '1h', 5)
            if test_data is not None and len(test_data) > 0:
                self.connected = True
                logger.info("✅ Connected to Yahoo Finance")
                return True
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_symbol_mapping(self, symbol):
        mapping = {
            'XAUUSD': 'GC=F', 'XAGUSD': 'SI=F',
            'EURUSD': 'EURUSD=X', 'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X', 'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X', 'NZDUSD': 'NZDUSD=X',
            'USDCHF': 'USDCHF=X',
            'US30': 'YM=F', 'NAS100': 'NQ=F',
            'SPX500': 'ES=F', 'UK100': 'FTSE=F',
            'GER30': 'DAX=F',
            'BTCUSD': 'BTC-USD', 'ETHUSD': 'ETH-USD',
            'SOLUSD': 'SOL-USD', 'ADAUSD': 'ADA-USD'
        }
        return mapping.get(symbol, f"{symbol}=X")
    
    def get_historical_data(self, symbol, timeframe, bars=100):
        try:
            yahoo_symbol = self.get_symbol_mapping(symbol)
            
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '60m', '4h': '60m', '1d': '1d'
            }
            
            period_map = {
                '1m': '2d', '5m': '5d', '15m': '7d', '30m': '14d',
                '1h': '30d', '4h': '60d', '1d': '1y'
            }
            
            interval = tf_map.get(timeframe, '60m')
            period = period_map.get(timeframe, '30d')
            
            logger.info(f"📡 Fetching {symbol} ({yahoo_symbol})...")
            
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
                'Open': 'Open', 'High': 'High',
                'Low': 'Low', 'Close': 'Close',
                'Volume': 'Volume'
            }, inplace=True)
            
            df['Open'] = pd.to_numeric(df['Open'])
            df['High'] = pd.to_numeric(df['High'])
            df['Low'] = pd.to_numeric(df['Low'])
            df['Close'] = pd.to_numeric(df['Close'])
            
            df = df.sort_values('time')
            df = df.tail(bars)
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol):
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