"""
Chart Pattern Detection
Double Top/Bottom, Head & Shoulders, Channels, Flags, Triangles, Wedges
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import logging
from config import PATTERN_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartPatternDetector:
    def __init__(self):
        self.rules = PATTERN_RULES
        self.patterns = []
        
    def detect_all_patterns(self, df):
        """Detect all chart patterns"""
        self.patterns = []
        
        if len(df) < 30:
            return self.patterns
        
        try:
            # Find swing points
            highs = df['High'].values
            lows = df['Low'].values
            
            swing_highs = argrelextrema(highs, np.greater, order=5)[0]
            swing_lows = argrelextrema(lows, np.less, order=5)[0]
            
            if len(swing_highs) < 5 or len(swing_lows) < 5:
                return self.patterns
            
            # --- Double Bottom ---
            if self._detect_double_bottom(df, swing_lows):
                self.patterns.append({
                    'type': 'DOUBLE_BOTTOM',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': df['Close'].iloc[-1]
                })
            
            # --- Double Top ---
            if self._detect_double_top(df, swing_highs):
                self.patterns.append({
                    'type': 'DOUBLE_TOP',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': df['Close'].iloc[-1]
                })
            
            # --- Head & Shoulders ---
            if self._detect_head_shoulders(df, swing_highs):
                self.patterns.append({
                    'type': 'HEAD_SHOULDERS',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': df['Close'].iloc[-1]
                })
            
            # --- Inverted Head & Shoulders ---
            if self._detect_inverted_head_shoulders(df, swing_lows):
                self.patterns.append({
                    'type': 'INVERTED_HEAD_SHOULDERS',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': df['Close'].iloc[-1]
                })
            
            # --- Channels ---
            channel = self._detect_channel(df, swing_highs, swing_lows)
            if channel:
                self.patterns.append(channel)
            
            # --- Flags ---
            flag = self._detect_flag(df)
            if flag:
                self.patterns.append(flag)
            
            # --- Triangles ---
            triangle = self._detect_triangle(df, swing_highs, swing_lows)
            if triangle:
                self.patterns.append(triangle)
            
            # --- Wedges ---
            wedge = self._detect_wedge(df, swing_highs, swing_lows)
            if wedge:
                self.patterns.append(wedge)
            
        except Exception as e:
            logger.error(f"Chart pattern error: {e}")
        
        return self.patterns
    
    # --- Double Bottom ---
    def _detect_double_bottom(self, df, swing_lows):
        if len(swing_lows) < 4:
            return False
        
        # Get last 4 swing lows
        last_lows = swing_lows[-4:]
        if len(last_lows) < 4:
            return False
        
        # Check if pattern resembles "W"
        low1 = df['Low'].iloc[last_lows[0]]
        low2 = df['Low'].iloc[last_lows[1]]
        low3 = df['Low'].iloc[last_lows[2]]
        low4 = df['Low'].iloc[last_lows[3]]
        
        # Check if two lows are at similar level
        if abs(low1 - low3) > 0.002 * low1:
            return False
        
        # Check if middle peak is higher
        if low2 <= max(low1, low3):
            return False
        
        # Check if price is breaking above the middle peak
        current_price = df['Close'].iloc[-1]
        if current_price <= low2:
            return False
        
        return True
    
    # --- Double Top ---
    def _detect_double_top(self, df, swing_highs):
        if len(swing_highs) < 4:
            return False
        
        last_highs = swing_highs[-4:]
        if len(last_highs) < 4:
            return False
        
        high1 = df['High'].iloc[last_highs[0]]
        high2 = df['High'].iloc[last_highs[1]]
        high3 = df['High'].iloc[last_highs[2]]
        high4 = df['High'].iloc[last_highs[3]]
        
        if abs(high1 - high3) > 0.002 * high1:
            return False
        
        if high2 <= min(high1, high3):
            return False
        
        current_price = df['Close'].iloc[-1]
        if current_price >= high2:
            return False
        
        return True
    
    # --- Head & Shoulders ---
    def _detect_head_shoulders(self, df, swing_highs):
        if len(swing_highs) < 6:
            return False
        
        last_highs = swing_highs[-6:]
        if len(last_highs) < 6:
            return False
        
        # Get the last 3 peaks
        peak1 = df['High'].iloc[last_highs[-3]]
        peak2 = df['High'].iloc[last_highs[-2]]
        peak3 = df['High'].iloc[last_highs[-1]]
        
        # Check if middle peak is highest (head)
        if peak2 <= max(peak1, peak3) * 1.1:
            return False
        
        # Check if shoulders are roughly equal
        if abs(peak1 - peak3) > 0.005 * peak1:
            return False
        
        return True
    
    # --- Inverted Head & Shoulders ---
    def _detect_inverted_head_shoulders(self, df, swing_lows):
        if len(swing_lows) < 6:
            return False
        
        last_lows = swing_lows[-6:]
        if len(last_lows) < 6:
            return False
        
        trough1 = df['Low'].iloc[last_lows[-3]]
        trough2 = df['Low'].iloc[last_lows[-2]]
        trough3 = df['Low'].iloc[last_lows[-1]]
        
        if trough2 >= min(trough1, trough3) * 0.9:
            return False
        
        if abs(trough1 - trough3) > 0.005 * trough1:
            return False
        
        return True
    
    # --- Channels ---
    def _detect_channel(self, df, swing_highs, swing_lows):
        if len(swing_highs) < 4 or len(swing_lows) < 4:
            return None
        
        # Check for parallel lines
        high_slope = (df['High'].iloc[swing_highs[-1]] - df['High'].iloc[swing_highs[-3]]) / 2
        low_slope = (df['Low'].iloc[swing_lows[-1]] - df['Low'].iloc[swing_lows[-3]]) / 2
        
        if abs(high_slope - low_slope) < 0.0005:
            if high_slope > 0:
                return {
                    'type': 'BULLISH_CHANNEL',
                    'strength': 'MEDIUM',
                    'direction': 'BULLISH',
                    'price': df['Close'].iloc[-1]
                }
            else:
                return {
                    'type': 'BEARISH_CHANNEL',
                    'strength': 'MEDIUM',
                    'direction': 'BEARISH',
                    'price': df['Close'].iloc[-1]
                }
        return None
    
    # --- Flags ---
    def _detect_flag(self, df):
        # Simple flag detection - look for sharp move followed by consolidation
        recent_high = df['High'].iloc[-20:].max()
        recent_low = df['Low'].iloc[-20:].min()
        recent_range = recent_high - recent_low
        
        last_10_range = df['High'].iloc[-10:].max() - df['Low'].iloc[-10:].min()
        
        if last_10_range < recent_range * 0.3:
            # Check direction of the pole
            first_5_avg = df['Close'].iloc[-20:-15].mean()
            last_5_avg = df['Close'].iloc[-5:].mean()
            
            if last_5_avg > first_5_avg * 1.02:
                return {
                    'type': 'BULL_FLAG',
                    'strength': 'MEDIUM',
                    'direction': 'BULLISH',
                    'price': df['Close'].iloc[-1]
                }
            elif last_5_avg < first_5_avg * 0.98:
                return {
                    'type': 'BEAR_FLAG',
                    'strength': 'MEDIUM',
                    'direction': 'BEARISH',
                    'price': df['Close'].iloc[-1]
                }
        
        return None
    
    # --- Triangles ---
    def _detect_triangle(self, df, swing_highs, swing_lows):
        if len(swing_highs) < 4 or len(swing_lows) < 4:
            return None
        
        # Check for converging highs and lows
        high_diff = df['High'].iloc[swing_highs[-1]] - df['High'].iloc[swing_highs[-3]]
        low_diff = df['Low'].iloc[swing_lows[-1]] - df['Low'].iloc[swing_lows[-3]]
        
        if high_diff < 0 and low_diff > 0:
            return {
                'type': 'BULLISH_TRIANGLE',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': df['Close'].iloc[-1]
            }
        elif high_diff > 0 and low_diff < 0:
            return {
                'type': 'BEARISH_TRIANGLE',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': df['Close'].iloc[-1]
            }
        elif high_diff < 0 and low_diff < 0:
            return {
                'type': 'BULLISH_WEDGE',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': df['Close'].iloc[-1]
            }
        elif high_diff > 0 and low_diff > 0:
            return {
                'type': 'BEARISH_WEDGE',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': df['Close'].iloc[-1]
            }
        
        return None
    
    # --- Wedges ---
    def _detect_wedge(self, df, swing_highs, swing_lows):
        if len(swing_highs) < 4 or len(swing_lows) < 4:
            return None
        
        high_slope = (df['High'].iloc[swing_highs[-1]] - df['High'].iloc[swing_highs[-3]]) / 2
        low_slope = (df['Low'].iloc[swing_lows[-1]] - df['Low'].iloc[swing_lows[-3]]) / 2
        
        if high_slope < 0 and low_slope < 0 and high_slope > low_slope:
            return {
                'type': 'BULLISH_WEDGE',
                'strength': 'MEDIUM',
                'direction': 'BULLISH',
                'price': df['Close'].iloc[-1]
            }
        elif high_slope > 0 and low_slope > 0 and high_slope < low_slope:
            return {
                'type': 'BEARISH_WEDGE',
                'strength': 'MEDIUM',
                'direction': 'BEARISH',
                'price': df['Close'].iloc[-1]
            }
        
        return None