import pandas as pd
import numpy as np
import glob
import os

results_folder = "data/processed/backtesting/results/"

files = glob.glob(os.path.join(results_folder, "*_results.csv"))

all_trades = []

for file in files:
    df = pd.read_csv(file, parse_dates=["Entry_Date","Exit_Date"])
    df["Pair"] = os.path.basename(file).replace("_results.csv","")
    all_trades.append(df)

portfolio_trades = pd.concat(all_trades, ignore_index=True)

# Expand trades into daily returns
daily_returns = []

for _, row in portfolio_trades.iterrows():

    days = pd.date_range(row["Entry_Date"], row["Exit_Date"])

    daily_return = row["Return_%"] / len(days)

    for d in days:
        daily_returns.append({"Date": d, "Return": daily_return})

daily_df = pd.DataFrame(daily_returns)

portfolio_daily = daily_df.groupby("Date")["Return"].mean()

portfolio_cum = portfolio_daily.cumsum()

portfolio_combined = pd.concat([portfolio_daily, portfolio_cum], axis=1)

# Metrics
sharpe = np.sqrt(252) * portfolio_daily.mean() / portfolio_daily.std()    # Sharpe ratio >1=good, >2=outstanding, >3=exceptional
max_dd = (portfolio_cum - portfolio_cum.cummax()).min()

print("\n===== PORTFOLIO RESULTS =====")
print(f"Sharpe Ratio: {sharpe:.2f}")
print(f"Max Drawdown: {max_dd*100:.2f}%")
print(f"Total Return: {portfolio_cum.iloc[-1]*100:.2f}%")

portfolio_combined.to_csv("data/processed/backtesting/portfolio_cumulative_returns.csv")