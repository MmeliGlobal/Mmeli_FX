"""
Trading Analysis Engine - Updated for Mmeli_FX Platform
"""

import pandas as pd
import numpy as np
import logging
from patterns import CandlePatternDetector, ChartPatternDetector, SMCDetector
from config import PATTERN_RULES, SIGNAL_SETTINGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyzer:
    def __init__(self):
        # Load settings
        self.min_risk_reward = SIGNAL_SETTINGS.get('min_risk_reward', 2.0)
        self.confluence_tolerance = SIGNAL_SETTINGS.get('confluence_tolerance', 0.005)
        self.trend_filter = SIGNAL_SETTINGS.get('trend_filter', True)
        self.swing_strength = 5
        
        # Initialize pattern detectors
        self.candle_detector = CandlePatternDetector()
        self.chart_detector = ChartPatternDetector()
        self.smc_detector = SMCDetector()
        
    def analyze_symbol(self, df_htf, df_ttf, current_price):
        """Complete analysis - returns all patterns and signals"""
        try:
            # 1. Trend Analysis
            trend = self.identify_trend(df_htf)
            
            # 2. Support & Resistance
            support, resistance = self.find_support_resistance(df_htf)
            
            # 3. Fibonacci
            fib = self.calculate_fibonacci(df_htf)
            
            # 4. Moving Averages
            sma20 = df_htf['Close'].rolling(window=20).mean().iloc[-1] if len(df_htf) > 20 else None
            
            # 5. Detect All Patterns
            candle_patterns = self.candle_detector.detect_all_patterns(df_ttf)
            chart_patterns = self.chart_detector.detect_all_patterns(df_ttf)
            smc_data = self.smc_detector.detect_all(df_ttf)
            
            # Combine all patterns
            all_patterns = candle_patterns + chart_patterns
            all_patterns.extend(smc_data.get('order_blocks', []))
            all_patterns.extend(smc_data.get('fvgs', []))
            all_patterns.extend(smc_data.get('liquidity_zones', []))
            
            # 6. Generate Signals
            signals = self.generate_signals(
                current_price, candle_patterns, 
                support, resistance, fib, sma20, trend
            )
            
            # 7. Chart Data
            chart_data = self.prepare_chart_data(df_ttf, support, resistance, fib, all_patterns, smc_data)
            
            return {
                'trend': trend,
                'support_levels': support[-3:],
                'resistance_levels': resistance[-3:],
                'fibonacci': fib,
                'sma': {'sma20': sma20} if sma20 else {},
                'patterns': all_patterns,
                'candle_patterns': candle_patterns,
                'chart_patterns': chart_patterns,
                'smc': smc_data,
                'signals': signals,
                'chart_data': chart_data,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return None
    
    def identify_trend(self, df):
        """Identify trend using swing points"""
        try:
            highs = df['High'].values
            lows = df['Low'].values
            strength = self.swing_strength
            
            swing_highs = []
            swing_lows = []
            
            for i in range(strength, len(highs) - strength):
                if all(highs[i] >= highs[i-j] for j in range(1, strength+1)) and \
                   all(highs[i] >= highs[i+j] for j in range(1, strength+1)):
                    swing_highs.append(i)
                
                if all(lows[i] <= lows[i-j] for j in range(1, strength+1)) and \
                   all(lows[i] <= lows[i+j] for j in range(1, strength+1)):
                    swing_lows.append(i)
            
            if len(swing_highs) < 3 or len(swing_lows) < 3:
                return 'RANGING'
            
            recent_highs = [highs[i] for i in swing_highs[-3:]]
            recent_lows = [lows[i] for i in swing_lows[-3:]]
            
            if (recent_highs[-1] > recent_highs[-2] > recent_highs[-3] and 
                recent_lows[-1] > recent_lows[-2] > recent_lows[-3]):
                return 'BULLISH'
            
            if (recent_highs[-1] < recent_highs[-2] < recent_highs[-3] and 
                recent_lows[-1] < recent_lows[-2] < recent_lows[-3]):
                return 'BEARISH'
            
            recent_close = df['Close'].iloc[-20:].values
            range_pct = (recent_close.max() - recent_close.min()) / recent_close.mean()
            
            if range_pct < 0.02:
                return 'RANGING'
            return 'CHOPPY'
            
        except:
            return 'RANGING'
    
    def find_support_resistance(self, df):
        """Find support and resistance levels"""
        try:
            highs = df['High'].values
            lows = df['Low'].values
            strength = self.swing_strength
            
            resistance = []
            support = []
            
            for i in range(strength, len(highs) - strength):
                if all(highs[i] >= highs[i-j] for j in range(1, strength+1)) and \
                   all(highs[i] >= highs[i+j] for j in range(1, strength+1)):
                    resistance.append(highs[i])
                
                if all(lows[i] <= lows[i-j] for j in range(1, strength+1)) and \
                   all(lows[i] <= lows[i+j] for j in range(1, strength+1)):
                    support.append(lows[i])
            
            resistance = sorted(set(resistance), reverse=True)[:3] if resistance else []
            support = sorted(set(support))[:3] if support else []
            
            return support, resistance
        except:
            return [], []
    
    def calculate_fibonacci(self, df):
        """Calculate Fibonacci levels"""
        try:
            recent_low = df['Low'].min()
            recent_high = df['High'].max()
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
            'MORNING_STAR': 'Morning Star Reversal',
            'EVENING_STAR': 'Evening Star Reversal',
            'BULLISH_ENGULFING': 'Engulfing Trend Continuation',
            'BEARISH_ENGULFING': 'Engulfing Trend Continuation',
            'HAMMER': 'Hammer Reversal',
            'SHOOTING_STAR': 'Shooting Star Reversal',
            'DOJI': 'Doji Reversal',
            'DRAGONFLY_DOJI': 'Doji Reversal',
            'GRAVESTONE_DOJI': 'Doji Reversal',
            'DOUBLE_BOTTOM': 'Double Bottom Reversal',
            'DOUBLE_TOP': 'Double Top Reversal',
            'HEAD_SHOULDERS': 'Head & Shoulders Reversal',
            'INVERTED_HEAD_SHOULDERS': 'Inverted H&S Reversal',
            'BULLISH_OB': 'Order Block SMC',
            'BEARISH_OB': 'Order Block SMC',
            'BULLISH_FVG': 'FVG Fill',
            'BEARISH_FVG': 'FVG Fill',
        }
        return rule_map.get(pattern_type, 'Price Action Strategy')
    
    def prepare_chart_data(self, df, support, resistance, fib, patterns, smc_data):
        """Prepare data for chart rendering"""
        try:
            candles = []
            for idx, row in df.tail(80).iterrows():
                candles.append({
                    'time': row['time'].isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close'])
                })
            
            # Prepare all levels
            levels = {
                'support': [float(s) for s in support],
                'resistance': [float(r) for r in resistance],
                'fibonacci': {k: float(v) for k, v in fib.items()},
                'order_blocks': [
                    {
                        'high': float(ob['high']),
                        'low': float(ob['low']),
                        'type': ob.get('type', 'BULLISH_OB')
                    } for ob in smc_data.get('order_blocks', [])
                ],
                'fvgs': [
                    {
                        'high': float(fvg['high']),
                        'low': float(fvg['low']),
                        'type': fvg.get('type', 'FVG')
                    } for fvg in smc_data.get('fvgs', [])
                ],
                'liquidity': [
                    {
                        'price': float(lz['price']),
                        'type': lz.get('type', 'LIQUIDITY')
                    } for lz in smc_data.get('liquidity_zones', [])
                ]
            }
            
            return {
                'candles': candles,
                'levels': levels,
                'patterns': [{'type': p.get('type'), 'direction': p.get('direction'), 'price': p.get('price')} for p in patterns]
            }
        except Exception as e:
            logger.error(f"Chart data error: {e}")
            return {'candles': [], 'levels': {}, 'patterns': []}