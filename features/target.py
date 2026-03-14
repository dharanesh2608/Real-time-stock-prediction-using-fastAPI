def create_target(df):
    df['target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    print(df['target'])
    df.dropna(inplace=True)
    return df
