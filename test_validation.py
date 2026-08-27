"""
Mmeli_FX - Complete System Validation
Tests: Data, Patterns, Analysis, Rules, Signals
"""

import json
import requests
import time
from datetime import datetime

print("="*60)
print("🔍 Mmeli_FX System Validation")
print("="*60)
print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

BASE_URL = "http://127.0.0.1:5000"

# ============================================
# TEST 1: Check if bot is running
# ============================================
print("\n📡 TEST 1: System Status")
try:
    response = requests.get(f"{BASE_URL}/api/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Bot is running")
        print(f"   📊 Data Source: {data.get('data_source', 'N/A')}")
        print(f"   📈 Cache Size: {data.get('cache_size', 0)}")
    else:
        print(f"   ❌ Bot not responding: {response.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect: {e}")
    print("   💡 Make sure python app.py is running!")
    exit()

# ============================================
# TEST 2: Test Data Fetching
# ============================================
print("\n📊 TEST 2: Data Fetching")
test_symbols = ['EURUSD', 'GBPUSD', 'XAUUSD']

for symbol in test_symbols:
    try:
        response = requests.get(f"{BASE_URL}/api/analysis/{symbol}?tf=15m", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                result = data.get('data', {})
                candles = result.get('chart_data', {}).get('candles', [])
                print(f"   ✅ {symbol}: {len(candles)} candles fetched")
            else:
                print(f"   ⚠️ {symbol}: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ {symbol}: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ {symbol}: Error - {e}")

# ============================================
# TEST 3: Pattern Detection
# ============================================
print("\n📈 TEST 3: Pattern Detection")
try:
    response = requests.get(f"{BASE_URL}/api/patterns/EURUSD?tf=15m", timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            patterns = data.get('data', {}).get('candle_patterns', [])
            print(f"   ✅ Patterns detected: {len(patterns)}")
            for p in patterns[:3]:
                print(f"      🔹 {p.get('type', 'Unknown')} ({p.get('strength', 'MEDIUM')})")
        else:
            print(f"   ⚠️ Pattern detection: {data.get('message', 'Unknown')}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# TEST 4: Rules Loading
# ============================================
print("\n⚙️ TEST 4: Strategy Rules")
try:
    response = requests.get(f"{BASE_URL}/api/rules", timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            rules = data.get('rules', [])
            enabled = [r for r in rules if r.get('enabled', True)]
            print(f"   ✅ Rules loaded: {len(rules)} total, {len(enabled)} enabled")
            
            # Show categories
            categories = {}
            for r in rules:
                cat = r.get('category', 'Uncategorized')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"   📂 Categories:")
            for cat, count in categories.items():
                print(f"      🔹 {cat}: {count} rules")
        else:
            print(f"   ⚠️ Rules: {data.get('message', 'Unknown')}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# TEST 5: Signal Generation
# ============================================
print("\n🔔 TEST 5: Signal Generation")
try:
    response = requests.get(f"{BASE_URL}/api/signals", timeout=15)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            signals = data.get('signals', [])
            print(f"   ✅ Signals generated: {len(signals)}")
            
            if signals:
                # Group by type
                buy_signals = [s for s in signals if s.get('action') == 'BUY']
                sell_signals = [s for s in signals if s.get('action') == 'SELL']
                print(f"      📈 BUY: {len(buy_signals)}")
                print(f"      📉 SELL: {len(sell_signals)}")
                
                # Show top 5 signals
                print(f"\n   📊 Top Signals:")
                for i, s in enumerate(signals[:5]):
                    rr = s.get('risk_reward', 0)
                    print(f"      {i+1}. {s.get('symbol')} {s.get('action')} - {s.get('pattern')} (RR 1:{rr})")
                    print(f"         📋 Rule: {s.get('rule', 'N/A')}")
            else:
                print(f"   💡 No signals at this time. This is normal - wait for market conditions.")
        else:
            print(f"   ⚠️ Signals: {data.get('message', 'Unknown')}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*60)
print("📋 SUMMARY")
print("="*60)
print("✅ If all tests passed, your system is working perfectly!")
print("💡 If some tests failed, check:")
print("   1. python app.py is running")
print("   2. Internet connection is working")
print("   3. Command Prompt for error messages")
print("="*60)