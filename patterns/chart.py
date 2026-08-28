"""
Chart Pattern Detection - NO PANDAS REQUIRED!
Works with lists of dictionaries
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartPatternDetector:
    def __init__(self):
        self.patterns = []
        
    def detect_all_patterns(self, candles):
        """Detect chart patterns - No pandas!"""
        self.patterns = []
        
        if not candles or len(candles) < 30:
            return self.patterns
        
        try:
            # Get highs and lows
            highs = [c['high'] for c in candles]
            lows = [c['low'] for c in candles]
            
            # Find swing points
            swing_highs = self._find_swing_highs(highs)
            swing_lows = self._find_swing_lows(lows)
            
            if len(swing_highs) < 4 or len(swing_lows) < 4:
                return self.patterns
            
            # Check for Double Bottom
            if len(swing_lows) >= 4:
                last_lows = swing_lows[-4:]
                if len(last_lows) >= 4:
                    low1 = lows[last_lows[0]]
                    low3 = lows[last_lows[2]]
                    if abs(low1 - low3) < 0.002 * low1:
                        self.patterns.append({
                            'type': 'DOUBLE_BOTTOM',
                            'strength': 'HIGH',
                            'direction': 'BULLISH',
                            'price': candles[-1]['close']
                        })
            
            # Check for Double Top
            if len(swing_highs) >= 4:
                last_highs = swing_highs[-4:]
                if len(last_highs) >= 4:
                    high1 = highs[last_highs[0]]
                    high3 = highs[last_highs[2]]
                    if abs(high1 - high3) < 0.002 * high1:
                        self.patterns.append({
                            'type': 'DOUBLE_TOP',
                            'strength': 'HIGH',
                            'direction': 'BEARISH',
                            'price': candles[-1]['close']
                        })
            
            # Check for Bull Flag
            if len(candles) >= 20:
                recent_range = max(highs[-20:]) - min(lows[-20:])
                last_10_range = max(highs[-10:]) - min(lows[-10:])
                if last_10_range < recent_range * 0.3:
                    first_5_avg = sum(highs[-20:-15]) / 5
                    last_5_avg = sum(highs[-5:]) / 5
                    if last_5_avg > first_5_avg * 1.02:
                        self.patterns.append({
                            'type': 'BULL_FLAG',
                            'strength': 'MEDIUM',
                            'direction': 'BULLISH',
                            'price': candles[-1]['close']
                        })
                    elif last_5_avg < first_5_avg * 0.98:
                        self.patterns.append({
                            'type': 'BEAR_FLAG',
                            'strength': 'MEDIUM',
                            'direction': 'BEARISH',
                            'price': candles[-1]['close']
                        })
            
            return self.patterns
        except Exception as e:
            logger.error(f"Chart pattern error: {e}")
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