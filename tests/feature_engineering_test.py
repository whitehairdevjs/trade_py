# tests/feature_engineering_test.py
import pandas as pd
import numpy as np
import pytest
from src.trading.feature_engineering import basic_preprocessing, calculate_technical_indicators

@pytest.fixture
def dummy_df():
    dates = pd.date_range("2022-01-01", periods=50, freq="D")
    df = pd.DataFrame({
        "Open": np.random.rand(50) * 100,
        "High": np.random.rand(50) * 100,
        "Low": np.random.rand(50) * 100,
        "Close": np.random.rand(50) * 100,
        "Adj Close": np.random.rand(50) * 100 + 1,
        "Volume": np.random.randint(1000, 10000, size=50),
    }, index=dates)
    return df

def test_basic_preprocessing(dummy_df):
    df = basic_preprocessing(dummy_df.copy())
    assert "LogReturn" in df.columns
    assert not df["LogReturn"].isna().any()

def test_calculate_technical_indicators(dummy_df):
    df_clean = basic_preprocessing(dummy_df.copy())
    df_feat = calculate_technical_indicators(df_clean.copy())
    for col in ["MA20", "MA60", "RSI14", "MACD", "MACD_signal", "BB_High", "BB_Low"]:
        assert col in df_feat.columns
    assert not df_feat.isna().any().any()