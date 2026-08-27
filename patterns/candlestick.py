"""
Candlestick Pattern Detection
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_all_patterns(self, df):
    """Detect all candlestick patterns"""
    self.patterns = []
    
    # Limit for speed
    if len(df) > 150:
        df = df.tail(150)
    
    if len(df) < 3:
        return self.patterns
    
    # ... rest of the code remains the same

class CandlePatternDetector:
    def __init__(self):
        self.pin_bar_ratio = 2.0
        self.doji_body_threshold = 0.0003
        self.patterns = []
        
    def detect_all_patterns(self, df):
        """Detect all candlestick patterns"""
        self.patterns = []
        
        if len(df) < 3:
            return self.patterns
        
        try:
            c2 = df.iloc[-2]
            c3 = df.iloc[-1]
            
            body3 = abs(c3['Close'] - c3['Open'])
            lower_wick3 = c3['Low'] - min(c3['Open'], c3['Close'])
            upper_wick3 = max(c3['Open'], c3['Close']) - c3['High']
            
            # Bullish Pin Bar
            if lower_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                self.patterns.append({
                    'type': 'BULLISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['Close'],
                    'candle_index': -1
                })
            
            # Bearish Pin Bar
            if upper_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                self.patterns.append({
                    'type': 'BEARISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['Close'],
                    'candle_index': -1
                })
            
            # Bullish Engulfing
            body2 = abs(c2['Close'] - c2['Open'])
            if c3['Close'] > c2['Open'] and c3['Open'] < c2['Close'] and body3 > body2 and body2 > 0:
                self.patterns.append({
                    'type': 'BULLISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['Close'],
                    'candle_index': -1
                })
            
            # Bearish Engulfing
            if c3['Close'] < c2['Open'] and c3['Open'] > c2['Close'] and body3 > body2 and body2 > 0:
                self.patterns.append({
                    'type': 'BEARISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['Close'],
                    'candle_index': -1
                })
            
            # Inside Bar
            if c3['High'] < c2['High'] and c3['Low'] > c2['Low']:
                self.patterns.append({
                    'type': 'INSIDE_BAR',
                    'strength': 'MEDIUM',
                    'direction': 'NEUTRAL',
                    'price': c3['Close'],
                    'candle_index': -1
                })
            
            # Doji
            if body3 < self.doji_body_threshold * c3['Close']:
                if lower_wick3 > body3 * 2 and upper_wick3 < body3 * 0.5:
                    self.patterns.append({
                        'type': 'DRAGONFLY_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BULLISH',
                        'price': c3['Close'],
                        'candle_index': -1
                    })
                elif upper_wick3 > body3 * 2 and lower_wick3 < body3 * 0.5:
                    self.patterns.append({
                        'type': 'GRAVESTONE_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BEARISH',
                        'price': c3['Close'],
                        'candle_index': -1
                    })
                else:
                    self.patterns.append({
                        'type': 'DOJI',
                        'strength': 'MEDIUM',
                        'direction': 'NEUTRAL',
                        'price': c3['Close'],
                        'candle_index': -1
                    })
            
            return self.patterns
        except:
            return self.patterns