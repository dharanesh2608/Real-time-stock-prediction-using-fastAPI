from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import existing modules
from data.raw.fetch_data import fetch_data
from features.indicators import add_features
from features.target import create_target
from models.xgboost_model import train_model
from agent.reasoning import explain_decision
from evaluation.backtest import backtest_strategy

app = FastAPI(title="Stock Prediction API", description="AI-powered stock trading recommendations")

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

# Global model cache
model_cache = {}

def get_or_train_model(symbol: str):
    """Get cached model or train new one"""
    if symbol not in model_cache:
        print(f"Training model for {symbol}...")
        df = fetch_data(symbol)
        df = add_features(df)
        df = create_target(df)
        
        model, X_test, y_test = train_model(df)
        model_cache[symbol] = {
            'model': model,
            'X_test': X_test,
            'y_test': y_test,
            'latest_data': df.iloc[-1]
        }
    
    return model_cache[symbol]

@app.get("/")
async def root():
    return {"message": "Stock Prediction API", "version": "1.0"}

@app.post("/fetch-data", response_model=DataResponse)
async def fetch_stock_data(request: StockRequest):
    """Fetch stock data for a given symbol"""
    try:
        df = fetch_data(request.symbol)
        
        return DataResponse(
            symbol=request.symbol,
            data_points=len(df),
            latest_date=df.index[-1].strftime("%Y-%m-%d"),
            columns=list(df.columns),
            sample_data=df.tail(5).to_dict('records')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock(request: StockRequest):
    """Predict stock movement and provide recommendation"""
    try:
        # Get or train model
        cached = get_or_train_model(request.symbol)
        model = cached['model']
        latest_data = cached['latest_data']
        
        # Get latest indicators
        indicators = {
            'rsi': latest_data.get('rsi', 0),
            'macd': latest_data.get('macd', 0),
            'sma_50': latest_data.get('sma_50', 0),
            'obv': latest_data.get('obv', 0),
            'sma_20': latest_data.get('sma_20', 0),
            'ema_20': latest_data.get('ema_20', 0),
            'atr': latest_data.get('atr', 0)
        }
        
        # Prepare features for prediction
        feature_columns = ['Close', 'Volume', 'rsi', 'macd', 'sma_20', 'sma_50', 'ema_20', 'atr', 'obv']
        latest_features = latest_data[feature_columns].values.reshape(1, -1)
        
        # Get prediction
        prediction_proba = model.predict_proba(latest_features)[0]
        prob_up = prediction_proba[1]
        
        # Make recommendation
        if prob_up > 0.6:
            recommendation = "BUY"
            prediction = "UP"
        elif prob_up < 0.4:
            recommendation = "SELL"
            prediction = "DOWN"
        else:
            recommendation = "HOLD"
            prediction = "SIDEWAYS"
        
        current_price = latest_data['Close']
        
        # Get AI explanation
        explanation = None
        try:
            explanation = explain_decision(
                date=latest_data.name.strftime("%Y-%m-%d"),
                price=current_price,
                prob=prob_up,
                indicators=indicators
            )
        except Exception as e:
            print(f"AI explanation failed: {e}")
            explanation = "AI explanation unavailable"
        
        return PredictionResponse(
            symbol=request.symbol,
            current_price=float(current_price),
            prediction=prediction,
            confidence=float(prob_up),
            recommendation=recommendation,
            indicators={k: float(v) for k, v in indicators.items()},
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/backtest")
async def run_backtest(request: StockRequest):
    """Run backtesting for the stock"""
    try:
        cached = get_or_train_model(request.symbol)
        model = cached['model']
        X_test = cached['X_test']
        
        results = backtest_strategy(model, X_test)
        
        # Convert to serializable format
        backtest_summary = {
            "initial_capital": 10000,
            "final_value": float(results.iloc[-1]["Portfolio_Value"]),
            "total_return_pct": float(((results.iloc[-1]["Portfolio_Value"] - 10000) / 10000) * 100),
            "total_trades": len(results[results['Action'] != 'HOLD']),
            "buy_signals": len(results[results['Action'] == 'BUY']),
            "sell_signals": len(results[results['Action'] == 'SELL']),
            "recent_signals": results.tail(10)[['Action', 'Price', 'Prob_Up']].to_dict('records')
        }
        
        return backtest_summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_cached": list(model_cache.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
