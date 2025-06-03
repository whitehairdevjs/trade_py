# excute command: python scripts\export_tickers.py

import os
from datetime import datetime

import pandas as pd
from pykrx import stock

def fetch_all_tickers(date: str) -> pd.DataFrame:
    """
    지정한 날짜(date, 'YYYYMMDD') 기준으로 KOSPI와 KOSDAQ 시장의
    모든 티커(ticker), 종목명(name), 시장(market) 정보를 DataFrame으로 반환.
    """
    all_data = []

    # 조회할 시장 목록 (필요 시 'KONEX' 등 다른 시장도 추가 가능)
    markets = {
        "KOSPI": "KOSPI",   # KOSPI(유가증권시장)
        "KOSDAQ": "KOSDAQ"  # KOSDAQ(코스닥시장)
    }

    for market_name, market_code in markets.items():
        # 1) 해당 시장의 티커 리스트 조회
        try:
            tickers = stock.get_market_ticker_list(market=market_code, date=date)
        except Exception as e:
            print(f"[WARN] get_market_ticker_list('{market_code}', '{date}') 호출 중 예외 발생: {e}")
            continue

        # 2) 각 티커별 종목명(name)을 조회
        for tic in tickers:
            try:
                name = stock.get_market_ticker_name(tic)
                if not name:
                    name = ""
            except Exception:
                name = ""
            all_data.append({
                "Ticker": tic,
                "Name": name,
                "Market": market_name
            })

    # 3) DataFrame 생성
    df = pd.DataFrame(all_data, columns=["Ticker", "Name", "Market"])
    return df

def save_to_excel(df: pd.DataFrame, output_path: str):
    """
    DataFrame을 지정된 경로(output_path)로 Excel(.xlsx) 파일로 저장.
    """
    # 저장할 디렉터리가 없으면 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Excel 파일로 저장 (index 없이)
    df.to_excel(output_path, index=False)
    print(f"[INFO] Saved ticker list to '{output_path}'")

def main():
    # 1) 날짜를 오늘 기준 'YYYYMMDD'로 설정 (원하는 날짜가 있으면 직접 문자열로 바꿔도 됩니다)
    today = datetime.today().strftime("%Y%m%d")

    # 2) 모든 티커 정보 가져오기
    print(f"[INFO] Fetching all tickers for date: {today}")
    df_tickers = fetch_all_tickers(date=today)

    # 3) 결과를 Excel 파일로 저장
    output_file = f"data/tickers_{today}.xlsx"
    save_to_excel(df_tickers, output_file)

if __name__ == "__main__":
    main()
