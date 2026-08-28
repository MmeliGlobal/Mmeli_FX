"""
Candlestick Pattern Detection - No pandas required!
Works with lists of dictionaries
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandlePatternDetector:
    def __init__(self):
        self.pin_bar_ratio = 2.0
        self.doji_body_threshold = 0.0003
        self.patterns = []
        
    def detect_all_patterns(self, candles):
        """Detect all candlestick patterns - No pandas!"""
        self.patterns = []
        
        if not candles or len(candles) < 3:
            return self.patterns
        
        try:
            c2 = candles[-2]
            c3 = candles[-1]
            
            body3 = abs(c3['close'] - c3['open'])
            lower_wick3 = c3['low'] - min(c3['open'], c3['close'])
            upper_wick3 = max(c3['open'], c3['close']) - c3['high']
            
            # Bullish Pin Bar
            if lower_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                self.patterns.append({
                    'type': 'BULLISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bearish Pin Bar
            if upper_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                self.patterns.append({
                    'type': 'BEARISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bullish Engulfing
            body2 = abs(c2['close'] - c2['open'])
            if c3['close'] > c2['open'] and c3['open'] < c2['close'] and body3 > body2 and body2 > 0:
                self.patterns.append({
                    'type': 'BULLISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bearish Engulfing
            if c3['close'] < c2['open'] and c3['open'] > c2['close'] and body3 > body2 and body2 > 0:
                self.patterns.append({
                    'type': 'BEARISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Inside Bar
            if c3['high'] < c2['high'] and c3['low'] > c2['low']:
                self.patterns.append({
                    'type': 'INSIDE_BAR',
                    'strength': 'MEDIUM',
                    'direction': 'NEUTRAL',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Doji
            if body3 < self.doji_body_threshold * c3['close']:
                if lower_wick3 > body3 * 2 and upper_wick3 < body3 * 0.5:
                    self.patterns.append({
                        'type': 'DRAGONFLY_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BULLISH',
                        'price': c3['close'],
                        'candle_index': -1
                    })
                elif upper_wick3 > body3 * 2 and lower_wick3 < body3 * 0.5:
                    self.patterns.append({
                        'type': 'GRAVESTONE_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BEARISH',
                        'price': c3['close'],
                        'candle_index': -1
                    })
                else:
                    self.patterns.append({
                        'type': 'DOJI',
                        'strength': 'MEDIUM',
                        'direction': 'NEUTRAL',
                        'price': c3['close'],
                        'candle_index': -1
                    })
            
            return self.patterns
        except:
            return self.patterns