import pandas as pd
import numpy as np
import os
import glob

prices_path = "data/processed/processed_prices.csv"
signals_folder = "data/processed/backtesting/signals/"
results_folder = "data/processed/backtesting/results/"
trades_path = "data/trades/final_pairs.csv"

os.makedirs(results_folder, exist_ok=True)

prices = pd.read_csv(prices_path, index_col=0, parse_dates=True)


def backtest_pair(signal_file):

    df = pd.read_csv(signal_file, index_col=0, parse_dates=True)

    asset_y = df["Asset_Y"].iloc[0]
    asset_x = df["Asset_X"].iloc[0]
    beta = df["Hedge_Ratio"].iloc[0]

    price_y = prices[asset_y]      # loads the entire Close price column of Asset_Y from processed_prices.csv as a Series
    price_x = prices[asset_x]      # loads the entire Close price column of Asset_X from processed_prices.csv as a Series

    trades = []
    i = 0

    while i < len(df) - 1:        # not <= as j=i+1 which will automatically access the last row of df

        row = df.iloc[i]

        if row["Signal"] in ["LONG", "SHORT"]:

            entry_date = df.index[i]            # gets the Date of ENTRY signal
            entry_y = price_y.loc[entry_date]   # obtains Asset_Y price on that ENTRY date
            entry_x = price_x.loc[entry_date]   # obtains Asset_X price on that ENTRY date

            direction = row["Signal"]

            # search for EXIT
            j = i + 1
            while j < len(df) and df["Signal"].iloc[j] != "EXIT":
                j += 1

            if j >= len(df):
                break          # ignore incomplete trade

            exit_date = df.index[j]            # gets the Date of EXIT signal
            exit_y = price_y.loc[exit_date]    # Asset_Y price on that EXIT date
            exit_x = price_x.loc[exit_date]    # Asset_X price on that EXIT date

            if direction == "LONG":
                entry_value = entry_y - (beta * entry_x)     # Long = Y - beta(X)
                exit_value = exit_y - (beta * exit_x)

            else:  # SHORT
                entry_value = -entry_y + (beta * entry_x)    # Short = -Y + beta(X)
                exit_value = -exit_y + (beta * exit_x)

            pnl = exit_value - entry_value
            return_pct = pnl / abs(entry_value)

            holding_days = (exit_date - entry_date).days

            trades.append({
                "Entry_Date": entry_date,
                "Exit_Date": exit_date,
                "Holding_Days": holding_days,
                "Asset_Y": asset_y,
                "Asset_X": asset_x,
                "Hedge_Ratio": beta,
                "Entry_Value": entry_value,
                "Exit_Value": exit_value,
                "PnL": pnl,
                "Return_%": return_pct
            })
 
            i = j + 1
        else:
            i += 1

    return pd.DataFrame(trades)


def run_backtest():

    files = glob.glob(os.path.join(signals_folder, "*.csv"))
    # glob.glob() returns all the files within a directory as list of strings of filenames

    print("\n===== PAIRWISE BACKTEST RESULTS =====\n")

    filtered_pairs = []

    for file in files:

        pair_name = os.path.basename(file).replace(".csv", "")

        result_df = backtest_pair(file)

        if result_df.empty:
            print(f"{pair_name}: No completed trades\n")
            continue

        avg_days = result_df["Holding_Days"].mean()
        total_return = result_df["Return_%"].sum() * 100
        win_rate = (result_df["Return_%"] >= 0).mean() * 100      # Avg. of True = 1 and False = 0
        avg_return = result_df["Return_%"].mean() * 100
        median_return = result_df["Return_%"].median() * 100
        no_of_trades = len(result_df)

        result_df["Year"] = pd.to_datetime(result_df["Entry_Date"]).dt.year    # creates a new column "Year" and assigns it the year value
        yearly_returns = result_df.groupby("Year")["Return_%"].sum()      # year-wise returns


        if ((total_return > 100) and 
            (median_return > 1.5) and
            (win_rate > 55) and
            (avg_days < 50) and
            (no_of_trades > 30)):

            dict = {"Asset_Y": result_df["Asset_Y"].iloc[0],
                    "Asset_X": result_df["Asset_X"].iloc[0],
                    "Hedge_Ratio": result_df["Hedge_Ratio"].iloc[0],
                    "Total_Trades": no_of_trades,
                    "Avg_Holding_Period": avg_days,
                    "Total_Return": total_return,
                    "Avg_Return": avg_return,
                    "Median_Return": median_return,
                    "Win_rate": win_rate
                    }
            lst=[]
            for year, ret in yearly_returns.items():
                dict[str(year)] = ret*100
                lst.append(ret)

            output_path = os.path.join(results_folder, pair_name + "_results.csv")
            result_df.to_csv(output_path, index=False)
            
            filtered_pairs.append(dict)

            print(pair_name)
            print(f"Trades: {len(result_df)}")
            print(f"Average Holding Days: {avg_days:.2f}")
            print(f"Total Return (%): {total_return:.2f}%")
            print(f"Average Return per Trade: {avg_return:.2f}%")
            print(f"Median Return: {median_return:.2f}%")
            print(f"Win Rate: {win_rate:.2f}%")
        
            print("Year-wise Returns:")
            for year, ret in yearly_returns.items():
                print(f"  {year}: {ret*100:.2f}%")

            print("-" * 50)

        else:
            continue

    tdf = (pd.DataFrame(filtered_pairs)).round(2)
    tdf.to_csv(trades_path, index=False)


if __name__ == "__main__":
    run_backtest()
