from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# Simple mock implementation for testing
app = FastAPI(title="Stock Prediction API", description="AI-powered stock trading recommendations", version="1.1")

class StockRequest(BaseModel):
    symbol: str = "AAPL"
    days: Optional[int] = 30

class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    prediction: str
    confidence: float
    recommendation: str
    indicators: Dict[str, float]
    explanation: Optional[str] = None

class DataResponse(BaseModel):
    symbol: str
    data_points: int
    latest_date: str
    columns: list
    sample_data: list
    currency: str = "USD"
    exchange: str = "Unknown"
    company_name: str = ""

def fetch_real_stock_data(symbol: str, days: int = 251):
    """Fetch real stock data using yfinance"""
    try:
        # Validate symbol format
        if not symbol or len(symbol.strip()) < 1:
            raise ValueError(f"Invalid symbol: '{symbol}'. Symbol must be at least 1 character.")
        
        symbol = symbol.upper().strip()
        
        # Convert days to yfinance period format
        if days <= 30:
            period = "1mo"
        elif days <= 60:
            period = "2mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 180:
            period = "6mo"
        elif days <= 251:
            period = "1y"
        else:
            period = "2y"
            
        # Fetch stock data
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            # Try to get more info about why it failed
            try:
                info = stock.info
                if 'regularMarketPrice' in info and info['regularMarketPrice'] is None:
                    raise ValueError(f"Symbol '{symbol}' exists but has no market data (possibly delisted)")
                else:
                    raise ValueError(f"No data found for symbol '{symbol}'. Symbol may be invalid or delisted.")
            except:
                raise ValueError(f"No data found for symbol '{symbol}'. Please check the symbol and try again.")
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns for {symbol}")
        
        return df
        
    except Exception as e:
        if "No data found" in str(e) or "possibly delisted" in str(e):
            raise ValueError(f"Symbol '{symbol}' not found or delisted. Please verify the stock symbol.")
        elif "Could not resolve host" in str(e) or "Failed to perform" in str(e):
            raise ValueError("Network error: Unable to connect to Yahoo Finance. Please check your internet connection.")
        else:
            raise ValueError(f"Error fetching data for '{symbol}': {str(e)}")

def get_stock_info(symbol: str):
    """Get additional stock information including currency and exchange"""
    try:
        stock = yf.Ticker(symbol.upper())
        info = stock.info
        return {
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange', 'Unknown'),
            'longName': info.get('longName', ''),
            'market': info.get('market', 'Unknown')
        }
    except:
        return {'currency': 'USD', 'exchange': 'Unknown', 'longName': '', 'market': 'Unknown'}

def calculate_technical_indicators(df):
    """Calculate real technical indicators"""
    try:
        # Check if we have enough data
        if len(df) < 50:
            raise ValueError("Insufficient data for technical indicators. Need at least 50 data points.")
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (Moving Average Convergence Divergence)
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Simple Moving Averages
        df['sma_20'] = df['Close'].rolling(window=20).mean()
        df['sma_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Average
        df['ema_20'] = df['Close'].ewm(span=20).mean()
        
        # ATR (Average True Range)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = np.maximum(high_low, np.maximum(high_close, low_close))
        df['atr'] = tr.rolling(window=14).mean()
        
        # OBV (On Balance Volume)
        obv = np.where(df['Close'] > df['Close'].shift(), df['Volume'], 
                      np.where(df['Close'] < df['Close'].shift(), -df['Volume'], 0)).cumsum()
        df['obv'] = obv
        
        # Drop rows with NaN values from indicators
        df.dropna(inplace=True)
        
        # Check if we still have data after dropping NaNs
        if df.empty:
            raise ValueError("No valid data remaining after calculating technical indicators.")
        
        return df
        
    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        raise ValueError(f"Error calculating technical indicators: {str(e)}")

def generate_trading_signal(latest_data):
    """Generate trading signal based on technical indicators"""
    try:
        rsi = latest_data['rsi']
        macd = latest_data['macd']
        macd_signal = latest_data['macd_signal']
        sma_20 = latest_data['sma_20']
        sma_50 = latest_data['sma_50']
        current_price = latest_data['Close']
        
        # Initialize signals
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals
        if rsi < 30:  # Oversold
            buy_signals += 2
        elif rsi > 70:  # Overbought
            sell_signals += 2
        elif rsi < 50:  # Bearish momentum
            sell_signals += 1
        else:  # Bullish momentum
            buy_signals += 1
            
        # MACD signals
        if macd > macd_signal and macd > 0:  # Bullish crossover
            buy_signals += 2
        elif macd < macd_signal and macd < 0:  # Bearish crossover
            sell_signals += 2
            
        # Moving average signals
        if current_price > sma_20 > sma_50:  # Strong uptrend
            buy_signals += 2
        elif current_price < sma_20 < sma_50:  # Strong downtrend
            sell_signals += 2
        elif sma_20 > sma_50:  # General uptrend
            buy_signals += 1
        else:  # General downtrend
            sell_signals += 1
            
        # Determine final signal and confidence
        total_signals = buy_signals + sell_signals
        if total_signals == 0:
            return "SIDEWAYS", "HOLD", 0.5
            
        confidence = max(buy_signals, sell_signals) / total_signals
        
        if buy_signals > sell_signals:
            return "UP", "BUY", confidence
        elif sell_signals > buy_signals:
            return "DOWN", "SELL", confidence
        else:
            return "SIDEWAYS", "HOLD", 0.5
            
    except Exception as e:
        raise ValueError(f"Error generating trading signal: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Stock Prediction API", "version": "1.0", "status": "Real data mode"}

@app.post("/fetch-data", response_model=DataResponse)
async def fetch_stock_data(request: StockRequest):
    """Fetch real stock data for a given symbol"""
    try:
        df = fetch_real_stock_data(request.symbol, request.days or 30)
        stock_info = get_stock_info(request.symbol)
        
        return DataResponse(
            symbol=request.symbol.upper(),
            data_points=len(df),
            latest_date=df.index[-1].strftime("%Y-%m-%d"),
            columns=list(df.columns),
            sample_data=df.tail(5).to_dict('records'),
            currency=stock_info['currency'],
            exchange=stock_info['exchange'],
            company_name=stock_info['longName']
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock(request: StockRequest):
    """Predict stock movement and provide recommendation using real data"""
    try:
        # Ensure we have enough data for technical indicators (minimum 50 days needed)
        days_needed = 251  # Always use 1 year (251 trading days) for reliable technical indicators
        
        # Fetch real stock data
        df = fetch_real_stock_data(request.symbol, days_needed)
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Get latest data
        latest_data = df.iloc[-1]
        current_price = latest_data['Close']
        
        # Generate trading signal
        prediction, recommendation, confidence = generate_trading_signal(latest_data)
        
        # Get indicators
        indicators = {
            'rsi': latest_data.get('rsi', 0),
            'macd': latest_data.get('macd', 0),
            'sma_50': latest_data.get('sma_50', 0),
            'obv': latest_data.get('obv', 0),
            'sma_20': latest_data.get('sma_20', 0),
            'ema_20': latest_data.get('ema_20', 0),
            'atr': latest_data.get('atr', 0)
        }
        
        # Generate AI explanation
        explanation = f"""
    AI ANALYST REPORT for {latest_data.name.strftime("%Y-%m-%d")}
    Stock: {request.symbol.upper()} | Price: ${current_price:.2f} | Confidence: {confidence:.1%}
    
    Technical Analysis:
    - RSI: {indicators.get('rsi', 0):.1f} (Momentum indicator - {'Oversold' if indicators.get('rsi', 0) < 30 else 'Overbought' if indicators.get('rsi', 0) > 70 else 'Neutral'})
    - MACD: {indicators.get('macd', 0):.3f} (Trend indicator)
    - SMA 20: ${indicators.get('sma_20', 0):.2f} (Short-term trend)
    - SMA 50: ${indicators.get('sma_50', 0):.2f} (Long-term trend)
    - ATR: {indicators.get('atr', 0):.2f} (Volatility indicator)
    - Volume: {indicators.get('obv', 0):.0f} (Volume trend)
    
    Recommendation: {recommendation} - Based on technical analysis, 
    our model suggests {recommendation} with {confidence:.1%} confidence.
    Current price is ${current_price:.2f} with prediction of {prediction} movement.
    """
        
        return PredictionResponse(
            symbol=request.symbol.upper(),
            current_price=float(current_price),
            prediction=prediction,
            confidence=float(confidence),
            recommendation=recommendation,
            indicators={k: float(v) for k, v in indicators.items()},
            explanation=explanation.strip()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.post("/backtest")
async def run_backtest(request: StockRequest):
    """Run mock backtesting for the stock"""
    try:
        # Mock backtest results
        np.random.seed(42)
        days = 252  # 1 year of trading days
        
        # Generate mock portfolio performance
        portfolio_values = []
        value = 10000
        
        for i in range(days):
            daily_return = np.random.normal(0.0005, 0.02)  # Small positive drift with volatility
            value = value * (1 + daily_return)
            portfolio_values.append(value)
        
        final_value = portfolio_values[-1]
        total_return = ((final_value - 10000) / 10000) * 100
        
        backtest_summary = {
            "initial_capital": 10000,
            "final_value": float(final_value),
            "total_return_pct": float(total_return),
            "total_trades": np.random.randint(10, 50),
            "buy_signals": np.random.randint(5, 25),
            "sell_signals": np.random.randint(5, 25),
            "recent_signals": [
                {
                    "Action": np.random.choice(["BUY", "SELL", "HOLD"]),
                    "Price": float(150 + np.random.normal(0, 10)),
                    "Prob_Up": float(np.random.uniform(0.3, 0.8))
                }
                for _ in range(5)
            ]
        }
        
        return backtest_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "real_data", "data_source": "yfinance"}

@app.post("/validate-symbol")
async def validate_symbol(request: StockRequest):
    """Validate if a stock symbol exists and has data"""
    try:
        symbol = request.symbol.upper().strip()
        if not symbol or len(symbol) < 1:
            raise HTTPException(status_code=400, detail="Symbol cannot be empty")
        
        stock = yf.Ticker(symbol)
        
        # Try to get basic info
        try:
            info = stock.info
            company_name = info.get('longName', 'Unknown')
            currency = info.get('currency', 'USD')
            exchange = info.get('exchange', 'Unknown')
            
            # Try to get recent price data
            df = stock.history(period="5d")
            
            if df.empty:
                return {
                    "symbol": symbol,
                    "valid": False,
                    "error": "No recent price data found",
                    "company_name": company_name
                }
            
            latest_price = df['Close'].iloc[-1]
            
            return {
                "symbol": symbol,
                "valid": True,
                "company_name": company_name,
                "currency": currency,
                "exchange": exchange,
                "latest_price": float(latest_price),
                "latest_date": df.index[-1].strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "valid": False,
                "error": f"Unable to fetch data: {str(e)}"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

def main():
    """Main function for uvicorn"""
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
