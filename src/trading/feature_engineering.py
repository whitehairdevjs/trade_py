import pandas as pd
import numpy as np
import os
from scipy import stats
import ta

def load_raw_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return df

def basic_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    # 결측치 제거
    df = df.dropna()
    # 로그 수익률 계산
    df['LogReturn'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
    df = df.dropna(subset=['LogReturn'])
    # 이상치 제거 (z-score 기준)
    df['zscore'] = stats.zscore(df['LogReturn'])
    df = df[df['zscore'].abs() < 3]
    df.drop(columns=['zscore'], inplace=True)
    return df

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # 단순 이동평균
    df['MA20'] = ta.trend.sma_indicator(close=df['Close'], window=20)
    df['MA60'] = ta.trend.sma_indicator(close=df['Close'], window=60)
    # RSI
    df['RSI14'] = ta.momentum.rsi(close=df['Close'], window=14)
    # MACD
    macd = ta.trend.MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    # 볼린저 밴드
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_High'] = bb.bollinger_hband()
    df['BB_Low']  = bb.bollinger_lband()
    df.dropna(inplace=True)
    return df

def save_processed_csv(df: pd.DataFrame, raw_filename: str):
    """
    data/processed/{raw_filename}_processed.csv 형태로 저장
    """
    os.makedirs("data/processed", exist_ok=True)
    base = os.path.basename(raw_filename).replace(".csv", "")
    out_name = f"data/processed/{base}_processed.csv"
    df.to_csv(out_name, encoding="utf-8-sig")
    print(f"[INFO] Saved processed data to {out_name}")