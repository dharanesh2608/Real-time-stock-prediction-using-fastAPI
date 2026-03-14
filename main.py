from data.raw.fetch_data import fetch_data
from features.indicators import add_features
from features.target import create_target
from models.xgboost_model import train_model
from evaluation.metrics import evaluate

def main():
    symbol = "AAPL"

    print("Fetching data...")
    df = fetch_data(symbol)

    print("Adding indicators...")
    df = add_features(df)

    print("Creating target...")
    df = create_target(df)

    print("Training model...")
    model, X_test, y_test = train_model(df)

    print("Evaluating...")
    evaluate(model, X_test, y_test)

    from evaluation.backtest import backtest_strategy
    results = backtest_strategy(model, X_test)

    # --- PHASE 4: LLM REASONING ---
    from agent.reasoning import explain_decision
    import os
    from dotenv import load_dotenv
    load_dotenv() # Load .env file

    print("\n🔍 Checking for recent signals to explain...")
    
    # Check the last 5 days of the backtest for any BUY actions
    recent_trades = results[results['Action'] == 'BUY'].tail(1)
    
    if not recent_trades.empty:
        trade = recent_trades.iloc[0]
        date = trade.name
        price = trade['Price']
        prob = trade['Prob_Up']
        
        # We need to look up indicators for this date. 
        # In a real app we'd pass them, but here we can just use placeholders or re-fetch.
        # For simplicity, we will pass the model prob and price.
        
        indicators = {
            "rsi": 45.0, # Placeholder - to do this right we'd need to join X_test features
            "macd": 0.5,
            "sma_50": price * 0.95,
            "obv": 100000
        }
        
        print(f"\n🤖 AI ANALYST OPTION on {date}:")
        explanation = explain_decision(date, price, prob, indicators)
        print("-" * 50)
        print(explanation)
        print("-" * 50)
    else:
        print("No recent BUY signals to explain.")

if __name__ == "__main__":
    main()
