import pandas as pd
from scipy import stats

def backtest(df, signals, cost_per_trade = 0.001):
    signal_shifted = signals['signal'].shift(1)
    returns = df['Close'].pct_change()
    strategy_returns = signal_shifted * returns
    trades = signal_shifted.diff().abs()

    strategy_returns_net = strategy_returns - (trades * cost_per_trade)
    equity_curve = (1 + strategy_returns_net.fillna(0)).cumprod()
    
    return strategy_returns_net, equity_curve

def annualized_return(equity_curve, periods_per_year = 252):
    n_days = len(equity_curve)
    total_return = equity_curve.iloc[-1]
    return total_return ** (periods_per_year / n_days) - 1

def annualized_vol(returns, periods_per_year = 252):
    return returns.std() * (periods_per_year ** 0.5)

def sharpe_ratio(returns, risk_free = 0.0, periods_per_year = 252):
    excess = returns - risk_free / periods_per_year
    return (excess.mean() / excess.std()) * (periods_per_year ** 0.5)

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
        'annualized_return': annualized_return(equity_curve),
        'annualized_vol': annualized_vol(returns),
        'sharpe': sharpe_ratio(returns),
        'max_drawdown': max_drawdown(equity_curve),
        't_stat': t_stat,
        'p_value': p_value
    }

def metrics_summary_df(returns, equity_curve, ticker = "Strategy"):
    summary = metrics_summary(returns, equity_curve)
    return pd.DataFrame([summary], index=[ticker])
