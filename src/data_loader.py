import pandas as pd
import yfinance as yf
from datetime import datetime

tickers_path = "data/raw/nifty50.csv"
tickers = [i+".NS" for i in pd.read_csv(tickers_path)["Symbol"]]

start_date = "2015-01-01"
end_date = datetime.today().strftime("%Y-%m-%d")

raw_data_path = "data/raw/raw_prices.csv"
processed_data_path = "data/processed/processed_prices.csv"

def load_price_data(tickers,start_date,end_date):     #function to download adjusted close, align dates, drop rows with any missing value
    
    data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    auto_adjust=True, 
    progress=False)["Close"]

    if isinstance(data, pd.Series):
        data = data.to_frame()   
    data.to_csv(raw_data_path)    # df.to_csv() overwrites if file of same name already exists

    data_clean = data.dropna()    # drop rows with missing values in any of the columns
    data_clean.to_csv(processed_data_path)

    return data_clean


if __name__ == "__main__":

    df = load_price_data(tickers,start_date,end_date)

    print(df.head())
    print(df.tail())
    print(df.describe())
    print(df.index.min(),"to",df.index.max())
    print(list(df.columns))