from broker_api import BrokerAPI
import pandas as pd

api = BrokerAPI()
print("Testing API connection...")

# Connect
api.connect()

# Test fetch EURUSD
print("\nFetching EURUSD 1h data...")
df = api.get_historical_data('EURUSD', '1h', 20)

if df is not None:
    print(f"✅ Success! Fetched {len(df)} candles")
    print(df[['time', 'Open', 'Close']].tail())
else:
    print("❌ Failed to fetch data")