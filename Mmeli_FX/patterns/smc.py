"""
Smart Money Concepts - Order Blocks, FVG, Liquidity Zones
"""

import pandas as pd
import numpy as np
import logging
from config import ORDER_BLOCK_SETTINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMCDetector:
    def __init__(self):
        self.settings = ORDER_BLOCK_SETTINGS
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
    def detect_all(self, df):
        """Detect all SMC concepts"""
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
        if len(df) < 20:
            return {
                'order_blocks': [],
                'fvgs': [],
                'liquidity_zones': []
            }
        
        try:
            # --- Order Blocks ---
            self._detect_order_blocks(df)
            
            # --- Fair Value Gaps ---
            self._detect_fvg(df)
            
            # --- Liquidity Zones ---
            self._detect_liquidity_zones(df)
            
        except Exception as e:
            logger.error(f"SMC detection error: {e}")
        
        return {
            'order_blocks': self.order_blocks,
            'fvgs': self.fvgs,
            'liquidity_zones': self.liquidity_zones
        }
    
    # --- Order Blocks ---
    def _detect_order_blocks(self, df):
        """Detect bullish and bearish order blocks"""
        for i in range(5, len(df) - 1):
            # Bullish Order Block - Last bearish candle before a strong up move
            if self._is_bearish(df.iloc[i]) and self._is_strong_move(df, i, 'up'):
                self.order_blocks.append({
                    'type': 'BULLISH_OB',
                    'high': df['High'].iloc[i],
                    'low': df['Low'].iloc[i],
                    'open': df['Open'].iloc[i],
                    'close': df['Close'].iloc[i],
                    'index': i,
                    'strength': 'HIGH'
                })
            
            # Bearish Order Block - Last bullish candle before a strong down move
            if self._is_bullish(df.iloc[i]) and self._is_strong_move(df, i, 'down'):
                self.order_blocks.append({
                    'type': 'BEARISH_OB',
                    'high': df['High'].iloc[i],
                    'low': df['Low'].iloc[i],
                    'open': df['Open'].iloc[i],
                    'close': df['Close'].iloc[i],
                    'index': i,
                    'strength': 'HIGH'
                })
    
    def _is_bullish(self, candle):
        return candle['Close'] > candle['Open']
    
    def _is_bearish(self, candle):
        return candle['Close'] < candle['Open']
    
    def _is_strong_move(self, df, idx, direction):
        """Check if there was a strong move after the candle"""
        lookahead = 3
        if idx + lookahead >= len(df):
            return False
        
        start_price = df['Close'].iloc[idx]
        end_price = df['Close'].iloc[idx + lookahead]
        
        if direction == 'up':
            move = (end_price - start_price) / start_price
            return move > 0.005  # 0.5% move
        else:
            move = (start_price - end_price) / start_price
            return move > 0.005
    
    # --- Fair Value Gaps ---
    def _detect_fvg(self, df):
        """Detect Fair Value Gaps (FVG)"""
        for i in range(2, len(df) - 1):
            c1 = df.iloc[i-2]
            c2 = df.iloc[i-1]
            c3 = df.iloc[i]
            
            # Bullish FVG - Gap up
            if c3['Low'] > c1['High']:
                self.fvgs.append({
                    'type': 'BULLISH_FVG',
                    'high': c3['High'],
                    'low': c1['Low'],
                    'index': i,
                    'strength': 'HIGH',
                    'filled': False
                })
            
            # Bearish FVG - Gap down
            if c3['High'] < c1['Low']:
                self.fvgs.append({
                    'type': 'BEARISH_FVG',
                    'high': c1['High'],
                    'low': c3['Low'],
                    'index': i,
                    'strength': 'HIGH',
                    'filled': False
                })
        
        # Check which FVGs have been filled (IFVG)
        self._check_fvg_filled(df)
    
    def _check_fvg_filled(self, df):
        """Check if FVGs have been filled (Inverse FVG)"""
        current_price = df['Close'].iloc[-1]
        
        for fvg in self.fvgs:
            if fvg['low'] <= current_price <= fvg['high']:
                fvg['filled'] = True
                fvg['type'] = f"{fvg['type'].replace('FVG', 'IFVG')}"
    
    # --- Liquidity Zones ---
    def _detect_liquidity_zones(self, df):
        """Detect liquidity zones (previous day high/low, swing highs/lows)"""
        # Previous day high and low
        if len(df) > 24:  # Assuming 1h timeframe, 24 hours
            yesterday = df.iloc[-25:-1]
            self.liquidity_zones.append({
                'type': 'PREVIOUS_DAY_HIGH',
                'price': yesterday['High'].max(),
                'strength': 'MEDIUM'
            })
            self.liquidity_zones.append({
                'type': 'PREVIOUS_DAY_LOW',
                'price': yesterday['Low'].min(),
                'strength': 'MEDIUM'
            })
        
        # Swing highs and lows (liquidity sweeps)
        highs = df['High'].values
        lows = df['Low'].values
        
        for i in range(5, len(df) - 5):
            if all(highs[i] > highs[i-j] for j in range(1, 6)) and \
               all(highs[i] > highs[i+j] for j in range(1, 6)):
                self.liquidity_zones.append({
                    'type': 'SWING_HIGH',
                    'price': highs[i],
                    'index': i,
                    'strength': 'HIGH'
                })
            
            if all(lows[i] < lows[i-j] for j in range(1, 6)) and \
               all(lows[i] < lows[i+j] for j in range(1, 6)):
                self.liquidity_zones.append({
                    'type': 'SWING_LOW',
                    'price': lows[i],
                    'index': i,
                    'strength': 'HIGH'
                })
        
        # Psychological levels (round numbers)
        current_price = df['Close'].iloc[-1]
        base = int(current_price)
        for level in [base + 0.1 * i for i in range(-5, 6)]:
            if abs(current_price - level) / current_price < 0.05:
                self.liquidity_zones.append({
                    'type': 'PSYCHOLOGICAL_LEVEL',
                    'price': round(level, 4),
                    'strength': 'MEDIUM'
                })