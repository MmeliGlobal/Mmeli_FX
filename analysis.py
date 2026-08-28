"""
Trading Analysis Engine - No pandas/numpy/scipy required
Works with lists of dictionaries from broker_api.py
"""

import logging
from config import DEFAULT_RULES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyzer:
    def __init__(self):
        self.rules = DEFAULT_RULES.copy()
        self.pin_bar_ratio = self.rules.get('pin_bar_ratio', 2.0)
        self.engulfing_min_ratio = self.rules.get('engulfing_min_ratio', 1.2)
        self.doji_body_threshold = self.rules.get('doji_body_threshold', 0.0003)
        self.confluence_tolerance = self.rules.get('confluence_tolerance', 0.005)
        self.swing_strength = self.rules.get('swing_strength', 5)
        self.min_risk_reward = self.rules.get('min_risk_reward', 2.0)
        self.trend_filter = self.rules.get('trend_filter', True)
        
    def analyze_symbol(self, df_htf, df_ttf, current_price):
        """
        Complete analysis - works with lists of dicts (no pandas!)
        Each candle is a dict with: time, epoch, open, high, low, close
        """
        try:
            trend = self.identify_trend(df_htf)
            support, resistance = self.find_support_resistance(df_htf)
            fib = self.calculate_fibonacci(df_htf)
            sma20 = self.calculate_sma(df_htf, 20)
            patterns = self.find_candlestick_patterns(df_ttf)
            signals = self.generate_signals(current_price, patterns, support, resistance, fib, sma20, trend)
            
            chart_data = self.prepare_chart_data(df_ttf, support, resistance, fib, patterns)
            
            return {
                'trend': trend,
                'support_levels': support[-3:] if support else [],
                'resistance_levels': resistance[-3:] if resistance else [],
                'fibonacci': fib,
                'sma': {'sma20': sma20} if sma20 else {},
                'patterns': patterns,
                'signals': signals,
                'chart_data': chart_data,
                'current_price': current_price
            }
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return None
    
    def identify_trend(self, candles):
        """Identify trend from list of candles (no pandas!)"""
        try:
            if not candles or len(candles) < 20:
                return 'RANGING'
            
            # Get last 10 candles
            recent = candles[-10:]
            
            # Check for higher highs and higher lows
            higher_highs = all(recent[i]['high'] < recent[i+1]['high'] for i in range(len(recent)-1))
            higher_lows = all(recent[i]['low'] < recent[i+1]['low'] for i in range(len(recent)-1))
            
            if higher_highs and higher_lows:
                return 'BULLISH'
            
            # Check for lower highs and lower lows
            lower_highs = all(recent[i]['high'] > recent[i+1]['high'] for i in range(len(recent)-1))
            lower_lows = all(recent[i]['low'] > recent[i+1]['low'] for i in range(len(recent)-1))
            
            if lower_highs and lower_lows:
                return 'BEARISH'
            
            # Check if ranging
            recent_candles = candles[-20:]
            high = max(c['high'] for c in recent_candles)
            low = min(c['low'] for c in recent_candles)
            avg = (high + low) / 2
            range_pct = (high - low) / avg
            
            if range_pct < 0.02:
                return 'RANGING'
            
            return 'CHOPPY'
        except:
            return 'RANGING'
    
    def find_support_resistance(self, candles):
        """Find support and resistance levels (no pandas!)"""
        try:
            if not candles or len(candles) < 20:
                return [], []
            
            strength = self.swing_strength
            resistance = []
            support = []
            
            for i in range(strength, len(candles) - strength):
                # Check if this is a swing high
                is_high = True
                for j in range(1, strength + 1):
                    if candles[i]['high'] <= candles[i-j]['high'] or candles[i]['high'] <= candles[i+j]['high']:
                        is_high = False
                        break
                if is_high:
                    resistance.append(candles[i]['high'])
                
                # Check if this is a swing low
                is_low = True
                for j in range(1, strength + 1):
                    if candles[i]['low'] >= candles[i-j]['low'] or candles[i]['low'] >= candles[i+j]['low']:
                        is_low = False
                        break
                if is_low:
                    support.append(candles[i]['low'])
            
            # Get unique levels (cluster similar values)
            resistance = self._cluster_levels(resistance, tolerance=0.002)
            support = self._cluster_levels(support, tolerance=0.002)
            
            # Sort and return top 3
            resistance = sorted(resistance, reverse=True)[:3] if resistance else []
            support = sorted(support)[:3] if support else []
            
            return support, resistance
        except:
            return [], []
    
    def _cluster_levels(self, levels, tolerance=0.002):
        """Cluster similar price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        
        for level in levels:
            if not clustered or abs(level - clustered[-1]) / level > tolerance:
                clustered.append(level)
        
        return clustered
    
    def calculate_fibonacci(self, candles):
        """Calculate Fibonacci levels"""
        try:
            if not candles:
                return {}
            
            recent_low = min(c['low'] for c in candles)
            recent_high = max(c['high'] for c in candles)
            diff = recent_high - recent_low
            
            return {
                '23.6': recent_low + diff * 0.236,
                '38.2': recent_low + diff * 0.382,
                '50': recent_low + diff * 0.5,
                '61.8': recent_low + diff * 0.618,
                '78.6': recent_low + diff * 0.786,
                '100': recent_high
            }
        except:
            return {}
    
    def calculate_sma(self, candles, period=20):
        """Calculate Simple Moving Average from list of candles"""
        try:
            if not candles or len(candles) < period:
                return None
            
            closes = [c['close'] for c in candles[-period:]]
            return sum(closes) / len(closes)
        except:
            return None
    
    def find_candlestick_patterns(self, candles):
        """Identify candlestick patterns from list of candles (no pandas!)"""
        patterns = []
        
        if not candles or len(candles) < 3:
            return patterns
        
        try:
            # Get last 2 candles
            c2 = candles[-2]
            c3 = candles[-1]
            
            # Calculate body and wicks for c3
            body3 = abs(c3['close'] - c3['open'])
            lower_wick3 = c3['low'] - min(c3['open'], c3['close'])
            upper_wick3 = max(c3['open'], c3['close']) - c3['high']
            
            # Bullish Pin Bar
            if lower_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                patterns.append({
                    'type': 'BULLISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bearish Pin Bar
            if upper_wick3 > body3 * self.pin_bar_ratio and body3 > 0:
                patterns.append({
                    'type': 'BEARISH_PIN_BAR',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bullish Engulfing
            body2 = abs(c2['close'] - c2['open'])
            if (c3['close'] > c2['open'] and c3['open'] < c2['close'] and 
                c3['close'] > c2['close'] and body3 > body2 and body2 > 0):
                patterns.append({
                    'type': 'BULLISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BULLISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Bearish Engulfing
            if (c3['close'] < c2['open'] and c3['open'] > c2['close'] and 
                c3['close'] < c2['close'] and body3 > body2 and body2 > 0):
                patterns.append({
                    'type': 'BEARISH_ENGULFING',
                    'strength': 'HIGH',
                    'direction': 'BEARISH',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Inside Bar
            if (c3['high'] < c2['high'] and c3['low'] > c2['low']):
                patterns.append({
                    'type': 'INSIDE_BAR',
                    'strength': 'MEDIUM',
                    'direction': 'NEUTRAL',
                    'price': c3['close'],
                    'candle_index': -1
                })
            
            # Doji
            if body3 < self.doji_body_threshold * c3['close']:
                if lower_wick3 > body3 * 2 and upper_wick3 < body3 * 0.5:
                    patterns.append({
                        'type': 'DRAGONFLY_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BULLISH',
                        'price': c3['close'],
                        'candle_index': -1
                    })
                elif upper_wick3 > body3 * 2 and lower_wick3 < body3 * 0.5:
                    patterns.append({
                        'type': 'GRAVESTONE_DOJI',
                        'strength': 'HIGH',
                        'direction': 'BEARISH',
                        'price': c3['close'],
                        'candle_index': -1
                    })
                else:
                    patterns.append({
                        'type': 'DOJI',
                        'strength': 'MEDIUM',
                        'direction': 'NEUTRAL',
                        'price': c3['close'],
                        'candle_index': -1
                    })
            
            return patterns
        except Exception as e:
            logger.error(f"Pattern error: {e}")
            return patterns
    
    def generate_signals(self, current_price, patterns, support, resistance, fib, sma, trend):
        """Generate signals from patterns"""
        signals = []
        
        if not patterns:
            return signals
        
        for p in patterns:
            direction = p.get('direction', 'NEUTRAL')
            if direction == 'NEUTRAL':
                continue
            
            # Check confluence
            near_support = any(abs(current_price - s) / current_price < self.confluence_tolerance for s in support)
            near_resistance = any(abs(current_price - r) / current_price < self.confluence_tolerance for r in resistance)
            near_fib = any(abs(current_price - fib[key]) / current_price < self.confluence_tolerance 
                          for key in ['50', '61.8'] if fib.get(key))
            
            is_bullish = direction == 'BULLISH'
            is_bearish = direction == 'BEARISH'
            
            # Check trend filter
            if self.trend_filter:
                if is_bullish and trend == 'BEARISH':
                    continue
                if is_bearish and trend == 'BULLISH':
                    continue
            
            if is_bullish and (near_support or near_fib):
                sl = support[0] if support else current_price * 0.99
                tp = resistance[0] if resistance else current_price * 1.01
                risk = current_price - sl
                reward = tp - current_price
                if risk > 0 and reward > 0 and reward / risk >= self.min_risk_reward:
                    signals.append({
                        'action': 'BUY',
                        'entry': current_price,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'risk_reward': round(reward / risk, 2),
                        'pattern': p.get('type', 'UNKNOWN'),
                        'strength': p.get('strength', 'MEDIUM'),
                        'rule': self._get_rule_for_pattern(p.get('type', ''))
                    })
            
            if is_bearish and (near_resistance or near_fib):
                sl = resistance[0] if resistance else current_price * 1.01
                tp = support[0] if support else current_price * 0.99
                risk = sl - current_price
                reward = current_price - tp
                if risk > 0 and reward > 0 and reward / risk >= self.min_risk_reward:
                    signals.append({
                        'action': 'SELL',
                        'entry': current_price,
                        'stop_loss': sl,
                        'take_profit': tp,
                        'risk_reward': round(reward / risk, 2),
                        'pattern': p.get('type', 'UNKNOWN'),
                        'strength': p.get('strength', 'MEDIUM'),
                        'rule': self._get_rule_for_pattern(p.get('type', ''))
                    })
        
        return signals
    
    def _get_rule_for_pattern(self, pattern_type):
        """Map pattern type to rule name"""
        rule_map = {
            'BULLISH_PIN_BAR': 'Pin Bar Reversal',
            'BEARISH_PIN_BAR': 'Pin Bar Reversal',
            'BULLISH_ENGULFING': 'Engulfing Trend Continuation',
            'BEARISH_ENGULFING': 'Engulfing Trend Continuation',
            'DOJI': 'Doji Reversal',
            'DRAGONFLY_DOJI': 'Doji Reversal',
            'GRAVESTONE_DOJI': 'Doji Reversal',
            'INSIDE_BAR': 'Inside Bar Breakout',
        }
        return rule_map.get(pattern_type, 'Price Action Strategy')
    
    def prepare_chart_data(self, candles, support, resistance, fib, patterns):
        """Prepare data for chart rendering (no pandas!)"""
        try:
            # Get last 80 candles
            chart_candles = []
            for c in candles[-80:]:
                chart_candles.append({
                    'time': c['time'],
                    'open': float(c['open']),
                    'high': float(c['high']),
                    'low': float(c['low']),
                    'close': float(c['close'])
                })
            
            return {
                'candles': chart_candles,
                'levels': {
                    'support': [float(s) for s in support],
                    'resistance': [float(r) for r in resistance],
                    'fibonacci': {k: float(v) for k, v in fib.items()}
                }
            }
        except Exception as e:
            logger.error(f"Chart data error: {e}")
            return {'candles': [], 'levels': {}}