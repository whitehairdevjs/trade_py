import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def download_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    yfinance를 이용해 ticker의 데이터를 DataFrame으로 반환.
    start, end는 'YYYY-MM-DD' 형식 문자열.
    """
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data fetched for {ticker} between {start} and {end}")
    return df

def save_raw_csv(df: pd.DataFrame, ticker: str):
    """
    data/raw/{ticker}_{YYYYMMDD_HHMMSS}.csv 형태로 저장.
    """
    os.makedirs("data/raw", exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/raw/{ticker}_{date_str}.csv"
    df.to_csv(filename, encoding="utf-8-sig")
    print(f"[INFO] Saved raw data to {filename}")