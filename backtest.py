import data
import pandas as pd
from scipy import stats

from strategies import ma_crossover_signal

def backtest(df, signals, cost_per_trade = 0.001):
    signal_shifted = signals['signal'].shift(1)
    returns = df['Close'].pct_change()
    strategy_returns = signal_shifted * returns
    trades = signal_shifted.diff().abs()
    strategy_returns_net = strategy_returns - (trades * cost_per_trade)
    equity_curve = (1 + strategy_returns_net.fillna(0)).cumprod()
    return strategy_returns_net, equity_curve

def annualised_return(equity_curve, periods_per_year = 252):
    n_days = len(equity_curve)
    total_return = equity_curve.iloc[-1]
    return total_return ** (periods_per_year / n_days) - 1

def annualised_volume(returns, periods_per_year = 252):
    return returns.std() * (periods_per_year ** 0.5)

def sharpe_ratio(returns, risk_free = 0.0, periods_per_year = 252):
    excess = returns - risk_free / periods_per_year
    return (excess.mean() / excess.std()) * (periods_per_year ** 0.5)

def drawdown_series(equity_curve):
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown

def max_drawdown(equity_curve):
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown.min()

def sharpe_significance(returns):
    clean_returns = returns.dropna()
    t_stat, p_value = stats.ttest_1samp(clean_returns, 0)
    return t_stat, p_value

def metrics_summary(returns, equity_curve):
    t_stat, p_value = sharpe_significance(returns)
    return {
        'annualised_return': annualised_return(equity_curve),
        'annualised_volume': annualised_volume(returns),
        'sharpe': sharpe_ratio(returns),
        'max_drawdown': max_drawdown(equity_curve),
        't_stat': t_stat,
        'p_value': p_value
        }

def metrics_summary_df(returns, equity_curve, ticker = "Strategy"):
    summary = metrics_summary(returns, equity_curve)
    return pd.DataFrame([summary], index = [ticker])

def build_sharpe_grid(ticker, short_windows, long_windows, data):
    grid = pd.DataFrame(index = short_windows, columns = long_windows, dtype = float)
    for s in short_windows:
        for l in long_windows:
            if s >= l:
                continue
            signals = ma_crossover_signal(data[ticker], short_window = s, long_window = l)
            returns, equity = backtest(data[ticker], signals)
            grid.loc[s, l] = sharpe_ratio(returns)
    return grid