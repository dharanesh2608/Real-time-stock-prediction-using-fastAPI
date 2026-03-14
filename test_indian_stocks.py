import yfinance as yf

def test_indian_stocks():
    """Test Indian stock symbols with different suffixes"""
    
    # Indian stock symbols with different suffixes
    indian_stocks = [
        "RELIANCE",      # Reliance Industries
        "TCS",           # Tata Consultancy Services  
        "INFY",          # Infosys
        "HDFCBANK",      # HDFC Bank
        "RELIANCE.NS",   # Reliance on NSE
        "TCS.NS",        # TCS on NSE
        "INFY.NS",       # Infosys on NSE
        "HDFCBANK.NS",   # HDFC Bank on NSE
        "RELIANCE.BO",   # Reliance on BSE
        "TCS.BO",        # TCS on BSE
    ]
    
    print("Testing Indian Stock Symbols")
    print("=" * 40)
    
    for symbol in indian_stocks:
        try:
            print(f"\nTesting: {symbol}")
            stock = yf.Ticker(symbol)
            df = stock.history(period="5d")
            
            if df.empty:
                print(f"❌ {symbol}: No data found")
            else:
                print(f"✅ {symbol}: SUCCESS")
                print(f"   - Latest price: ${df['Close'].iloc[-1]:.2f}")
                print(f"   - Data points: {len(df)}")
                print(f"   - Currency: {stock.info.get('currency', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ {symbol}: ERROR - {str(e)}")

if __name__ == "__main__":
    test_indian_stocks()
