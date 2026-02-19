import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller


data_path = "data/processed/processed_prices.csv"


def adf_test(series, name):     # Augmented Dickey-Fuller test

    result = adfuller(series, autolag='AIC')

    print(f"\nADF Test for {name}")
    print("-" * 40)
    print(f"ADF Statistic : {result[0]:.4f}")
    print(f"p-value       : {result[1]:.4f}")
    #print(f"Lags Used     : {result[2]}")
    print(f"Observations  : {result[3]}")

    #for key, value in result[4].items():
        #print(f"Critical Value {key}: {value:.4f}")

    if result[1] < 0.05:
        print("Result: Stationary")
    else:
        print("Result: Non-stationary")


def run_stationarity_tests():

    df = pd.read_csv(data_path, index_col=0, parse_dates=True)

    print("\n===== PRICE STATIONARITY TEST =====")

    for col in df.columns:
        adf_test(df[col], col)

    print("\n===== RETURN STATIONARITY TEST =====")

    log_prices = np.log(df)
    returns = log_prices.diff().dropna()

    for col in returns.columns:
        adf_test(returns[col], col)


if __name__ == "__main__":
    run_stationarity_tests()