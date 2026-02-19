import pandas as pd
import numpy as np
import os

prices_path = "data/processed/processed_prices.csv"
pairs_list = "data/trades/final_pairs.csv"

year=2026
yearly_folder = f"data/trades/{year}/"

os.makedirs(yearly_folder, exist_ok=True)

entry_Z = 2
exit_Z = 0.15
stop_z = 3
safe_z = 2.5
max_holding_days = 90

def compute_zscore(series, window=60):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    zscore =  (series - mean) / std
    return zscore

def generate_signals():

    prices = pd.read_csv(prices_path, index_col=0, parse_dates=True)
    pairs = pd.read_csv(pairs_list)

    for index, row in pairs.iterrows():

        y = np.log(prices[row["Asset_Y"]])
        x = np.log(prices[row["Asset_X"]])

        spread = y - (row["Hedge_Ratio"] * x)

        zscore = compute_zscore(spread)

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
            "Z_Score": zscore,    
            "Signal": signal})

        df = df.dropna(subset=["Signal"])
        df = df[df.index.year==year]

        filename = f"{row['Asset_Y']}_{row['Asset_X']}.csv"
        df.to_csv(os.path.join(yearly_folder, filename))

        if len(df):
            print(f"Final Signals generated for {filename}")
            print(df.tail())
            print("-"*40)    


if __name__ == "__main__":
    generate_signals()
