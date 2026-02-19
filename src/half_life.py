import pandas as pd
import numpy as np
import statsmodels.api as sm


data_path = "data/processed/processed_prices.csv"
coint_path = "data/processed/cointegrated_pairs.csv"

half_life_threshold = 60

def estimate_half_life(spread):
 
    spread_lag = spread.shift(1).dropna()    # previous day's mispricing
    spread_ret = spread.diff().dropna()     # today's correction

    spread_lag = spread_lag.loc[spread_ret.index]

    X = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret, X).fit()    # run OLS to find theta

    theta = model.params.iloc[1]

    if theta >= 0:   
        return np.nan

    half_life = -np.log(2) / theta
    return half_life


def run_half_life_analysis():

    prices = pd.read_csv(data_path, index_col=0, parse_dates=True)
    pairs = pd.read_csv(coint_path)

    results = []

    for index, row in pairs.iterrows():

        y = np.log(prices[row["Asset_Y"]])     # accesses the prices of the stock taken as Asset_Y
        x = np.log(prices[row["Asset_X"]])

        spread = y - (row["Hedge_Ratio"] * x)

        hl = estimate_half_life(spread)

        results.append({                         # creates a list of dictionaries
            "Asset_Y": row["Asset_Y"],
            "Asset_X": row["Asset_X"],
            "Hedge_Ratio": row["Hedge_Ratio"],
            "Half_Life": hl,
            "ADF_p_value": row["ADF_p_value"]
        })

    results_df = pd.DataFrame(results)

    results_df = results_df[results_df["Half_Life"] < half_life_threshold].sort_values("Half_Life")  # keeping only those pairs that revert with 50 days

    print("\n===== HALF LIFE RESULTS =====\n")
    print(results_df)

    results_df.to_csv("data/processed/half_life.csv", index=False)


if __name__ == "__main__":
    run_half_life_analysis()