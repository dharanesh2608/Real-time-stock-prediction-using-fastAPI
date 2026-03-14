import ta

def add_features(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['macd'] = ta.trend.MACD(df['Close']).macd()

    df['sma_20'] = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
    df['sma_50'] = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
    df['ema_20'] = ta.trend.EMAIndicator(df['Close'], window=20).ema_indicator()

    df['atr'] = ta.volatility.AverageTrueRange(
        df['High'], df['Low'], df['Close']
    ).average_true_range()

    df['obv'] = ta.volume.OnBalanceVolumeIndicator(
        df['Close'], df['Volume']
    ).on_balance_volume()

    df.dropna(inplace=True)
    return df
