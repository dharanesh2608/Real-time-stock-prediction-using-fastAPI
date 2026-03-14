import pandas as pd

def backtest_strategy(model, X_test, initial_capital=10000):
    print("\nRunning Backtest...")
    
    # Get probability of class 1 (Up)
    # X_test order must be preserved. train_test_split(shuffle=False) ensures this.
    probs = model.predict_proba(X_test)[:, 1]
    
    # We need the Close prices to simulate trading
    if 'Close' not in X_test.columns:
        raise ValueError("X_test must contain 'Close' price column for backtesting.")
        
    prices = X_test['Close'].values
    dates = X_test.index
    
    cash = initial_capital
    position = 0 # 0 means we hold Cash, 1 means we hold Stock
    shares = 0
    
    history = []
    
    for i in range(len(probs)):
        price = prices[i]
        prob_up = probs[i]
        date = dates[i]
        
        action = "HOLD"
        
        # STRATEGY LOGIC
        # Buy if highly confident (prob > 0.6) and we have cash
        if prob_up > 0.6 and position == 0:
            shares = cash / price
            cash = 0
            position = 1
            action = "BUY"
            
        # Sell if confident it will drop (prob < 0.4) and we have stock
        elif prob_up < 0.4 and position == 1:
            cash = shares * price
            shares = 0
            position = 0
            action = "SELL"
            
        # START OF DAY PORTFOLIO VALUE
        current_val = cash + (shares * price)
        
        history.append({
            "Date": date,
            "Price": price,
            "Prob_Up": prob_up,
            "Action": action,
            "Portfolio_Value": current_val
        })
        
    results = pd.DataFrame(history)
    results.set_index("Date", inplace=True)
    
    final_val = results.iloc[-1]["Portfolio_Value"]
    return_pct = ((final_val - initial_capital) / initial_capital) * 100
    
    print("-" * 30)
    print(f"Initial Capital : ${initial_capital:,.2f}")
    print(f"Final Value     : ${final_val:,.2f}")
    print(f"Total Return    : {return_pct:.2f}%")
    print("-" * 30)
    
    return results
