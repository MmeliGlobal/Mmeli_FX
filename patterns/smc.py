"""
Smart Money Concepts - Order Blocks, FVG, Liquidity Zones
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMCDetector:
    def __init__(self):
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
    def detect_all(self, df):
        """Detect all SMC concepts"""
        self.order_blocks = []
        self.fvgs = []
        self.liquidity_zones = []
        
        if len(df) < 10:
            return {
                'order_blocks': [],
                'fvgs': [],
                'liquidity_zones': []
            }
        
        try:
            # Detect FVG
            for i in range(2, len(df) - 1):
                c1 = df.iloc[i-2]
                c2 = df.iloc[i-1]
                c3 = df.iloc[i]
                
                # Bullish FVG
                if c3['Low'] > c1['High']:
                    self.fvgs.append({
                        'type': 'BULLISH_FVG',
                        'high': c3['High'],
                        'low': c1['Low'],
                        'index': i
                    })
                
                # Bearish FVG
                if c3['High'] < c1['Low']:
                    self.fvgs.append({
                        'type': 'BEARISH_FVG',
                        'high': c1['High'],
                        'low': c3['Low'],
                        'index': i
                    })
            
            # Liquidity Zones (previous day high/low)
            if len(df) > 24:
                yesterday = df.iloc[-25:-1]
                self.liquidity_zones.append({
                    'type': 'PREVIOUS_DAY_HIGH',
                    'price': yesterday['High'].max()
                })
                self.liquidity_zones.append({
                    'type': 'PREVIOUS_DAY_LOW',
                    'price': yesterday['Low'].min()
                })
            
        except:
            pass
        
        return {
            'order_blocks': self.order_blocks,
            'fvgs': self.fvgs,
            'liquidity_zones': self.liquidity_zones
        }