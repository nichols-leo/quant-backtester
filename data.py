import yfinance as yf
import pandas as pd
import os

def fetch_data(tickers, start = "2015-01-01", cache_dir = "data"):
    os.makedirs(cache_dir, exist_ok = True)
    data = {}

    for ticker in tickers:
        path = f"{cache_dir}/{ticker}.csv"

        if os.path.exists(path):
            df = pd.read_csv(path, index_col = 0, parse_dates = True)
        else:
            df = yf.download(ticker, start = start)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.to_csv(path)

        data[ticker] = df

    return data