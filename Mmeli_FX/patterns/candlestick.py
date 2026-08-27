"""
Candlestick Pattern Detection
Complete list of bullish, bearish, and neutral patterns
"""

import pandas as pd
import numpy as np
import logging
from config import PATTERN_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandlePatternDetector:
    def __init__(self):
        self.rules = PATTERN_RULES
        self.patterns = []
        
    def detect_all_patterns(self, df):
        """Detect all candlestick patterns in the DataFrame"""
        self.patterns = []
        
        if len(df) < 5:
            return self.patterns
        
        # Get last 5 candles for pattern detection
        c1 = df.iloc[-5]
        c2 = df.iloc[-4]
        c3 = df.iloc[-3]
        c4 = df.iloc[-2]
        c5 = df.iloc[-1]
        
        # ============ REVERSAL PATTERNS ============
        
        # --- Morning Star ---
        if self._is_morning_star(c1, c2, c3):
            self.patterns.append({
                'type': 'MORNING_STAR',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Evening Star ---
        if self._is_evening_star(c1, c2, c3):
            self.patterns.append({
                'type': 'EVENING_STAR',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Morning Doji Star ---
        if self._is_morning_doji_star(c1, c2, c3):
            self.patterns.append({
                'type': 'MORNING_DOJI_STAR',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Evening Doji Star ---
        if self._is_evening_doji_star(c1, c2, c3):
            self.patterns.append({
                'type': 'EVENING_DOJI_STAR',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Bullish Engulfing ---
        if self._is_bullish_engulfing(c4, c5):
            self.patterns.append({
                'type': 'BULLISH_ENGULFING',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Bearish Engulfing ---
        if self._is_bearish_engulfing(c4, c5):
            self.patterns.append({
                'type': 'BEARISH_ENGULFING',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Hammer ---
        if self._is_hammer(c5):
            self.patterns.append({
                'type': 'HAMMER',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Shooting Star ---
        if self._is_shooting_star(c5):
            self.patterns.append({
                'type': 'SHOOTING_STAR',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Hanging Man ---
        if self._is_hanging_man(c5):
            self.patterns.append({
                'type': 'HANGING_MAN',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Bullish Harami ---
        if self._is_bullish_harami(c4, c5):
            self.patterns.append({
                'type': 'BULLISH_HARAMI',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Bearish Harami ---
        if self._is_bearish_harami(c4, c5):
            self.patterns.append({
                'type': 'BEARISH_HARAMI',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Piercing Line ---
        if self._is_piercing_line(c4, c5):
            self.patterns.append({
                'type': 'PIERCING_LINE',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Dark Cloud Cover ---
        if self._is_dark_cloud_cover(c4, c5):
            self.patterns.append({
                'type': 'DARK_CLOUD_COVER',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Tweezer Bottom ---
        if self._is_tweezer_bottom(c4, c5):
            self.patterns.append({
                'type': 'TWEEZER_BOTTOM',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Tweezer Top ---
        if self._is_tweezer_top(c4, c5):
            self.patterns.append({
                'type': 'TWEEZER_TOP',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Three White Soldiers ---
        if self._is_three_white_soldiers(c1, c2, c3):
            self.patterns.append({
                'type': 'THREE_WHITE_SOLDIERS',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Three Black Crows ---
        if self._is_three_black_crows(c1, c2, c3):
            self.patterns.append({
                'type': 'THREE_BLACK_CROWS',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Doji Patterns ---
        if self._is_doji(c5):
            self.patterns.append({
                'type': 'DOJI',
                'strength': 'MEDIUM',
                'direction': 'NEUTRAL',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Dragonfly Doji ---
        if self._is_dragonfly_doji(c5):
            self.patterns.append({
                'type': 'DRAGONFLY_DOJI',
                'strength': 'HIGH',
                'direction': 'BULLISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Gravestone Doji ---
        if self._is_gravestone_doji(c5):
            self.patterns.append({
                'type': 'GRAVESTONE_DOJI',
                'strength': 'HIGH',
                'direction': 'BEARISH',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Spinning Top ---
        if self._is_spinning_top(c5):
            self.patterns.append({
                'type': 'SPINNING_TOP',
                'strength': 'LOW',
                'direction': 'NEUTRAL',
                'price': c5['Close'],
                'candle_index': -1
            })
        
        # --- Marubozu ---
        if self._is_marubozu(c5):
            direction = 'BULLISH' if c5['Close'] > c5['Open'] else 'BEARISH'
            self.patterns.append({
                'type': 'MARUBOZU',
                'strength': 'MEDIUM',
                'direction': direction,
                'price': c5['Close'],
                'candle_index': -1
            })
        
        return self.patterns
    
    # ============ PATTERN DETECTION METHODS ============
    
    def _is_bullish(self, candle):
        return candle['Close'] > candle['Open']
    
    def _is_bearish(self, candle):
        return candle['Close'] < candle['Open']
    
    def _get_body(self, candle):
        return abs(candle['Close'] - candle['Open'])
    
    def _get_upper_wick(self, candle):
        return max(candle['Open'], candle['Close']) - candle['High']
    
    def _get_lower_wick(self, candle):
        return candle['Low'] - min(candle['Open'], candle['Close'])
    
    def _get_wick_to_body_ratio(self, candle):
        body = self._get_body(candle)
        if body == 0:
            return 10
        return max(self._get_upper_wick(candle), self._get_lower_wick(candle)) / body
    
    # --- Morning Star ---
    def _is_morning_star(self, c1, c2, c3):
        if not self._is_bearish(c1):
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        body3 = self._get_body(c3)
        if body2 > body1 * 0.5:
            return False
        if not self._is_bullish(c3):
            return False
        if c3['Close'] <= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Evening Star ---
    def _is_evening_star(self, c1, c2, c3):
        if not self._is_bullish(c1):
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        body3 = self._get_body(c3)
        if body2 > body1 * 0.5:
            return False
        if not self._is_bearish(c3):
            return False
        if c3['Close'] >= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Morning Doji Star ---
    def _is_morning_doji_star(self, c1, c2, c3):
        if not self._is_bearish(c1):
            return False
        if not self._is_doji(c2):
            return False
        if not self._is_bullish(c3):
            return False
        if c3['Close'] <= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Evening Doji Star ---
    def _is_evening_doji_star(self, c1, c2, c3):
        if not self._is_bullish(c1):
            return False
        if not self._is_doji(c2):
            return False
        if not self._is_bearish(c3):
            return False
        if c3['Close'] >= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Bullish Engulfing ---
    def _is_bullish_engulfing(self, c1, c2):
        if not self._is_bearish(c1):
            return False
        if not self._is_bullish(c2):
            return False
        if c2['Open'] <= c1['Close']:
            return False
        if c2['Close'] <= c1['Open']:
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        if body2 <= body1 * 1.2:
            return False
        return True
    
    # --- Bearish Engulfing ---
    def _is_bearish_engulfing(self, c1, c2):
        if not self._is_bullish(c1):
            return False
        if not self._is_bearish(c2):
            return False
        if c2['Open'] >= c1['Close']:
            return False
        if c2['Close'] >= c1['Open']:
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        if body2 <= body1 * 1.2:
            return False
        return True
    
    # --- Hammer ---
    def _is_hammer(self, candle):
        body = self._get_body(candle)
        lower_wick = self._get_lower_wick(candle)
        upper_wick = self._get_upper_wick(candle)
        if body == 0:
            return False
        if lower_wick <= body * 2:
            return False
        if upper_wick > body * 0.5:
            return False
        if body > (candle['High'] - candle['Low']) * 0.3:
            return False
        return True
    
    # --- Shooting Star ---
    def _is_shooting_star(self, candle):
        body = self._get_body(candle)
        upper_wick = self._get_upper_wick(candle)
        lower_wick = self._get_lower_wick(candle)
        if body == 0:
            return False
        if upper_wick <= body * 2:
            return False
        if lower_wick > body * 0.5:
            return False
        if body > (candle['High'] - candle['Low']) * 0.3:
            return False
        return True
    
    # --- Hanging Man ---
    def _is_hanging_man(self, candle):
        body = self._get_body(candle)
        lower_wick = self._get_lower_wick(candle)
        upper_wick = self._get_upper_wick(candle)
        if body == 0:
            return False
        if lower_wick <= body * 2:
            return False
        if upper_wick > body * 0.3:
            return False
        if body > (candle['High'] - candle['Low']) * 0.3:
            return False
        return True
    
    # --- Bullish Harami ---
    def _is_bullish_harami(self, c1, c2):
        if not self._is_bearish(c1):
            return False
        if not self._is_bullish(c2):
            return False
        if c2['High'] >= c1['High']:
            return False
        if c2['Low'] <= c1['Low']:
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        if body2 > body1 * 0.5:
            return False
        return True
    
    # --- Bearish Harami ---
    def _is_bearish_harami(self, c1, c2):
        if not self._is_bullish(c1):
            return False
        if not self._is_bearish(c2):
            return False
        if c2['High'] >= c1['High']:
            return False
        if c2['Low'] <= c1['Low']:
            return False
        body1 = self._get_body(c1)
        body2 = self._get_body(c2)
        if body2 > body1 * 0.5:
            return False
        return True
    
    # --- Piercing Line ---
    def _is_piercing_line(self, c1, c2):
        if not self._is_bearish(c1):
            return False
        if not self._is_bullish(c2):
            return False
        if c2['Open'] >= c1['Close']:
            return False
        if c2['Close'] <= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Dark Cloud Cover ---
    def _is_dark_cloud_cover(self, c1, c2):
        if not self._is_bullish(c1):
            return False
        if not self._is_bearish(c2):
            return False
        if c2['Open'] <= c1['Close']:
            return False
        if c2['Close'] >= (c1['Open'] + c1['Close']) / 2:
            return False
        return True
    
    # --- Tweezer Bottom ---
    def _is_tweezer_bottom(self, c1, c2):
        if not self._is_bearish(c1):
            return False
        if not self._is_bullish(c2):
            return False
        if abs(c1['Low'] - c2['Low']) > 0.0003:
            return False
        return True
    
    # --- Tweezer Top ---
    def _is_tweezer_top(self, c1, c2):
        if not self._is_bullish(c1):
            return False
        if not self._is_bearish(c2):
            return False
        if abs(c1['High'] - c2['High']) > 0.0003:
            return False
        return True
    
    # --- Three White Soldiers ---
    def _is_three_white_soldiers(self, c1, c2, c3):
        candles = [c1, c2, c3]
        for c in candles:
            if not self._is_bullish(c):
                return False
            if self._get_body(c) < 0.3 * (c['High'] - c['Low']):
                return False
        if c1['Close'] > c2['Close'] or c2['Close'] > c3['Close']:
            return False
        return True
    
    # --- Three Black Crows ---
    def _is_three_black_crows(self, c1, c2, c3):
        candles = [c1, c2, c3]
        for c in candles:
            if not self._is_bearish(c):
                return False
            if self._get_body(c) < 0.3 * (c['High'] - c['Low']):
                return False
        if c1['Close'] < c2['Close'] or c2['Close'] < c3['Close']:
            return False
        return True
    
    # --- Doji ---
    def _is_doji(self, candle):
        body = self._get_body(candle)
        if body == 0:
            return True
        if body > 0.05 * (candle['High'] - candle['Low']):
            return False
        return True
    
    # --- Dragonfly Doji ---
    def _is_dragonfly_doji(self, candle):
        if not self._is_doji(candle):
            return False
        lower_wick = self._get_lower_wick(candle)
        upper_wick = self._get_upper_wick(candle)
        if lower_wick <= upper_wick * 2:
            return False
        return True
    
    # --- Gravestone Doji ---
    def _is_gravestone_doji(self, candle):
        if not self._is_doji(candle):
            return False
        upper_wick = self._get_upper_wick(candle)
        lower_wick = self._get_lower_wick(candle)
        if upper_wick <= lower_wick * 2:
            return False
        return True
    
    # --- Spinning Top ---
    def _is_spinning_top(self, candle):
        body = self._get_body(candle)
        total_range = candle['High'] - candle['Low']
        if total_range == 0:
            return False
        body_ratio = body / total_range
        if body_ratio > 0.3:
            return False
        if body_ratio < 0.05:
            return False
        upper_wick = self._get_upper_wick(candle)
        lower_wick = self._get_lower_wick(candle)
        if upper_wick < 0.3 * total_range:
            return False
        if lower_wick < 0.3 * total_range:
            return False
        return True
    
    # --- Marubozu ---
    def _is_marubozu(self, candle):
        total_range = candle['High'] - candle['Low']
        if total_range == 0:
            return False
        upper_wick = self._get_upper_wick(candle)
        lower_wick = self._get_lower_wick(candle)
        if upper_wick > 0.05 * total_range:
            return False
        if lower_wick > 0.05 * total_range:
            return False
        return True