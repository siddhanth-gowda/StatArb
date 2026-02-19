import pandas as pd
import numpy as np
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm


data_path = "data/processed/processed_prices.csv"
ADF_threshold = 0.05


def adf_test(series):
    return adfuller(series, autolag="AIC")[1]   # adfuller()[1] gives the p-value


def estimate_hedge_ratio(y, x):
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    return model.params.iloc[1], model.resid    # model.params[1] gives hedge ratio beta
                                                # model.resid gives the residual value of the pair

def find_cointegrated_pairs(df):
    results = []

    pairs = list(combinations(df.columns, 2))

    print(f"Testing {len(pairs)} pairs for cointegration...\n")

    for asset_y, asset_x in pairs:

        y = np.log(df[asset_y])
        x = np.log(df[asset_x])

        beta, residuals = estimate_hedge_ratio(y, x)
        p_value = adf_test(residuals)

        results.append({
            "Asset_Y": asset_y,
            "Asset_X": asset_x,
            "Hedge_Ratio": beta,
            "ADF_p_value": p_value})

    results_df = pd.DataFrame(results)
    return results_df


if __name__ == "__main__":

    df = pd.read_csv(data_path, index_col=0, parse_dates=True)

    results = find_cointegrated_pairs(df)

    cointegrated = results[results["ADF_p_value"] < ADF_threshold]      # Selects only rows where "ADF_p_value" is less than ADF_threshold
    cointegrated = cointegrated[cointegrated["Hedge_Ratio"]>0].sort_values("ADF_p_value").reset_index(drop=True)    # Sorting the dataframe in increasing order of p-value

    print("\n=====",len(cointegrated[cointegrated.columns[0]]),"COINTEGRATED PAIRS =====\n")
    print(cointegrated)

    cointegrated.to_csv("data/processed/cointegrated_pairs.csv", index=False)
