import pandas as pd
import numpy as np
import os

prices_path = "data/processed/processed_prices.csv"
pair_path = "data/processed/half_life.csv"
signals_folder = "data/processed/backtesting/signals/"
zscore_folder = "data/processed/backtesting/zscore/"

entry_Z = 2
exit_Z = 0.15
stop_z = 3
safe_z = 2.5
max_holding_days = 90

os.makedirs(signals_folder, exist_ok=True)
os.makedirs(zscore_folder, exist_ok=True)


def compute_zscore(series, window=60):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    zscore =  (series - mean) / std
    return zscore                             # returns a Series containing rolling z-scores


def generate_signals():

    prices = pd.read_csv(prices_path, index_col=0, parse_dates=True)
    pairs = pd.read_csv(pair_path)

    for index, row in pairs.iterrows():

        y = np.log(prices[row["Asset_Y"]])
        x = np.log(prices[row["Asset_X"]])

        spread = y - (row["Hedge_Ratio"] * x)

        zscore = compute_zscore(spread)

        zdf = pd.DataFrame({
            "Asset_Y": row["Asset_Y"],
            "Asset_X": row["Asset_X"],
            "Hedge_Ratio": row["Hedge_Ratio"],
            "Z_Score": zscore})
        
        filename = f"{row['Asset_Y']}_{row['Asset_X']}_zscore.csv"
        zdf.dropna().tail(50).to_csv(os.path.join(zscore_folder, filename))    
        # saving the last 50 rows of z-scores for reference during trade

        signal = []
        position = 0        # 0 = flat, 1 = long, -1 = short
        entry_date = None

        for date, z in zip(zscore.index, zscore):

            if np.isnan(z):
                signal.append(np.nan)
                continue

            if position == 0:
                if z > entry_Z and z < safe_z:
                    signal.append("SHORT")        
                    position = -1
                    entry_date = date      
                elif z < -entry_Z and z > -safe_z:
                    signal.append("LONG")         
                    position = 1
                    entry_date = date
                else:
                    signal.append(np.nan)

            else:
                days_in_trade = (date - entry_date).days

                if position == 1 and z < -stop_z:     
                    signal.append("EXIT")             # EXIT IF Z-SCORE FURTHER GOES TO -3
                    position = 0
                elif position == -1 and z > stop_z:
                    signal.append("EXIT")             # EXIT IF Z-SCORE FURTHER GOES TO +3
                    position = 0
                elif days_in_trade >= max_holding_days:
                    signal.append("EXIT")             # EXIT IF holding period exceeds 90 days
                    position = 0
                elif abs(z) < exit_Z:
                    signal.append("EXIT")
                    position = 0
                else:
                    signal.append(np.nan)

        df = pd.DataFrame({
            "Asset_Y": row["Asset_Y"],
            "Asset_X": row["Asset_X"],
            "Hedge_Ratio": row["Hedge_Ratio"],
            "Z_Score": zscore,           # even though Asset_X and Asset_y are single values while zscore and signal are entire Series,
            "Signal": signal             # Pandas repeats the scalar value to match the length of the Series (Broadcasting)
        })

        df = df.dropna(subset=["Signal"])

        filename = f"{row['Asset_Y']}_{row['Asset_X']}.csv"
        df.to_csv(os.path.join(signals_folder, filename))

        print(f"Signals generated for {filename}")
        print(df.tail(5))
        print("-"*40)


if __name__ == "__main__":
    generate_signals()
