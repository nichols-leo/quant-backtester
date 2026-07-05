import pandas as pd

def ma_crossover_signal(df, short_window = 20, long_window = 50):
    signals = pd.DataFrame(index = df.index)

    signals['ma_short'] = df['Close'].rolling(short_window).mean()
    signals['ma_long'] = df['Close'].rolling(long_window).mean()
    signals['signal'] = (signals['ma_short'] > signals['ma_long']).astype(int)

    return signals

def momentum_signal(df, lookback = 126):
    signals = pd.DataFrame(index = df.index)

    signals['momentum'] = df['Close'].pct_change(lookback)
    signals['signal'] = (signals['momentum'] > 0).astype(int)

    return signals