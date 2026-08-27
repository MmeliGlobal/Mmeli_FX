"""
Chart Pattern Detection
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartPatternDetector:
    def __init__(self):
        self.patterns = []
        
    def detect_all_patterns(self, df):
        """Detect chart patterns"""
        self.patterns = []
        
        if len(df) < 20:
            return self.patterns
        
        try:
            highs = df['High'].values
            lows = df['Low'].values
            
            # Find swing points without scipy
            swing_highs = self._find_swing_highs(highs)
            swing_lows = self._find_swing_lows(lows)
            
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return self.patterns
            
            # Check for Double Bottom
            if len(swing_lows) >= 4:
                last_lows = swing_lows[-4:]
                low1 = df['Low'].iloc[last_lows[0]]
                low3 = df['Low'].iloc[last_lows[2]]
                if abs(low1 - low3) < 0.002 * low1:
                    self.patterns.append({
                        'type': 'DOUBLE_BOTTOM',
                        'strength': 'HIGH',
                        'direction': 'BULLISH',
                        'price': df['Close'].iloc[-1]
                    })
            
            # Check for Double Top
            if len(swing_highs) >= 4:
                last_highs = swing_highs[-4:]
                high1 = df['High'].iloc[last_highs[0]]
                high3 = df['High'].iloc[last_highs[2]]
                if abs(high1 - high3) < 0.002 * high1:
                    self.patterns.append({
                        'type': 'DOUBLE_TOP',
                        'strength': 'HIGH',
                        'direction': 'BEARISH',
                        'price': df['Close'].iloc[-1]
                    })
            
            # Check for Bull Flag
            recent_range = df['High'].iloc[-20:].max() - df['Low'].iloc[-20:].min()
            last_10_range = df['High'].iloc[-10:].max() - df['Low'].iloc[-10:].min()
            if last_10_range < recent_range * 0.3:
                first_5_avg = df['Close'].iloc[-20:-15].mean()
                last_5_avg = df['Close'].iloc[-5:].mean()
                if last_5_avg > first_5_avg * 1.02:
                    self.patterns.append({
                        'type': 'BULL_FLAG',
                        'strength': 'MEDIUM',
                        'direction': 'BULLISH',
                        'price': df['Close'].iloc[-1]
                    })
                elif last_5_avg < first_5_avg * 0.98:
                    self.patterns.append({
                        'type': 'BEAR_FLAG',
                        'strength': 'MEDIUM',
                        'direction': 'BEARISH',
                        'price': df['Close'].iloc[-1]
                    })
            
            return self.patterns
        except:
            return self.patterns
    
    def _find_swing_highs(self, highs, window=5):
        """Find swing highs"""
        swing_highs = []
        for i in range(window, len(highs) - window):
            is_high = True
            for j in range(1, window + 1):
                if highs[i] <= highs[i-j] or highs[i] <= highs[i+j]:
                    is_high = False
                    break
            if is_high:
                swing_highs.append(i)
        return swing_highs
    
    def _find_swing_lows(self, lows, window=5):
        """Find swing lows"""
        swing_lows = []
        for i in range(window, len(lows) - window):
            is_low = True
            for j in range(1, window + 1):
                if lows[i] >= lows[i-j] or lows[i] >= lows[i+j]:
                    is_low = False
                    break
            if is_low:
                swing_lows.append(i)
        return swing_lows