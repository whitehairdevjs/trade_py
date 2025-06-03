import pytest
import pandas as pd
from src.trading.data_loader import download_stock_data

def test_download_stock_data_valid():
    df = download_stock_data("005930.KS", "2022-01-01", "2022-01-10")
    assert isinstance(df, pd.DataFrame)
    assert "Close" in df.columns

def test_download_stock_data_invalid():
    with pytest.raises(ValueError):
        _ = download_stock_data("INVALID", "2022-01-01", "2022-01-10")