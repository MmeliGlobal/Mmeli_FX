"""
Smart Money Concepts - NO PANDAS REQUIRED!
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMCDetector:
    def __init__(self):
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
    def detect_all(self, candles):
        """Detect all SMC concepts - No pandas!"""
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
        if not candles or len(candles) < 10:
            return {
                'order_blocks': [],
                'fvgs': [],
                'liquidity_zones': []
            }
        
        try:
            # Detect FVG (Fair Value Gaps)
            for i in range(2, len(candles) - 1):
                c1 = candles[i-2]
                c2 = candles[i-1]
                c3 = candles[i]
                
                # Bullish FVG - Gap up
                if c3['low'] > c1['high']:
                    self.fvgs.append({
                        'type': 'BULLISH_FVG',
                        'high': c3['high'],
                        'low': c1['low'],
                        'index': i
                    })
                
                # Bearish FVG - Gap down
                if c3['high'] < c1['low']:
                    self.fvgs.append({
                        'type': 'BEARISH_FVG',
                        'high': c1['high'],
                        'low': c3['low'],
                        'index': i
                    })
            
            # Liquidity Zones (previous day high/low - approx 24 candles)
            if len(candles) > 24:
                yesterday = candles[-25:-1]
                if yesterday:
                    self.liquidity_zones.append({
                        'type': 'PREVIOUS_DAY_HIGH',
                        'price': max(c['high'] for c in yesterday)
                    })
                    self.liquidity_zones.append({
                        'type': 'PREVIOUS_DAY_LOW',
                        'price': min(c['low'] for c in yesterday)
                    })
            
        except Exception as e:
            logger.error(f"SMC error: {e}")
        
        return {
            'order_blocks': self.order_blocks,
            'fvgs': self.fvgs,
            'liquidity_zones': self.liquidity_zones
        }