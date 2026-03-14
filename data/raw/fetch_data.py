import yfinance as yf
import pandas as pd

def fetch_data(symbol):
    df = yf.download(symbol, start="2015-12-01", progress=False)
    
    # Flatten MultiIndex columns if present (common in recent yfinance versions)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.dropna(inplace=True)
    return df
symbol = "AAPL"
    
print("Fetching data...")
df = fetch_data(symbol)
print(df.head())
print(len(df))
print(df.tail())