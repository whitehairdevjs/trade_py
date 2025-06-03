# excute command: python scripts\collect_data.py --ticker 005930 --start 2020-01-01 --end 2025-05-31
import argparse
import os
from datetime import datetime

import pandas as pd
from pykrx import stock

def download_stock_data_pykrx(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    pykrx를 이용해 한국 주가 데이터를 가져옵니다.

    Parameters:
    - ticker: '005930'처럼 KRX 종목 코드(끝에 .KS 붙이지 않음)
    - start:   시작 날짜 (YYYY-MM-DD)
    - end:     종료 날짜 (YYYY-MM-DD)

    Returns:
    - DataFrame(index=날짜, columns=['Open','High','Low','Close','Volume','Adj Close'])
    """
    # 1) 만약 ticker에 ".KS"나 ".KQ" 등이 붙어 있으면 잘라내기
    raw_ticker = ticker
    if "." in ticker:
        ticker = ticker.split(".")[0]
        print(f"[WARN] '.KS' 등 접미사를 제거하여 '{raw_ticker}' → '{ticker}'로 재설정")

    # 2) 종목명 조회 시도. 실패 시 ticker(숫자) 자체를 이름으로 사용
    try:
        name = stock.get_market_ticker_name(ticker)
        if not name:  # 빈 문자열로 반환될 수도 있으므로 확인
            raise ValueError("get_market_ticker_name returned empty string")
    except Exception as e:
        print(f"[WARN] get_market_ticker_name('{ticker}') 호출 중 예외 발생: {e}")
        name = ticker  # 종목명 조회 실패 시 ticker 코드로 대체

    # pykrx는 날짜를 YYYYMMDD 형태로 받아야 함
    start_dt = start.replace("-", "")
    end_dt = end.replace("-", "")

    # 지정 기간 동안의 시가/고가/저가/종가/거래량을 반환
    df = stock.get_market_ohlcv_by_date(start_dt, end_dt, ticker)

    # 컬럼명 한글 → 영어로 변경
    df = df.rename(columns={
        "날짜": "Date",
        "시가": "Open",
        "고가": "High",
        "저가": "Low",
        "종가": "Close",
        "거래량": "Volume"
    })

    # Adj Close(보정 종가) 컬럼이 별도로 없으므로, 'Close'를 복사
    df["Adj Close"] = df["Close"]

    # 'Name' 컬럼을 맨 앞에 추가 (모든 행에 동일한 종목명)
    df.insert(0, "Name", name)

    return df

def save_raw_csv(df: pd.DataFrame, ticker: str):
    """
    data/raw/{ticker}_{YYYYMMDD_HHMMSS}.csv 형태로 파일 저장
    """
    os.makedirs("data/raw", exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/raw/{ticker}_{date_str}.csv"
    df.to_csv(filename, encoding="cp949")
    print(f"[INFO] Saved raw data to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="pykrx 기반 주식 데이터 수집 스크립트 (Python 3.11.9)"
    )
    parser.add_argument(
        "--ticker", type=str, required=True,
        help="KRX 종목 코드 (예: 005930) – 끝에 .KS 붙이지 말 것"
    )
    parser.add_argument(
        "--start", type=str, required=True,
        help="시작 날짜 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end", type=str, required=True,
        help="종료 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    print(f"[INFO] Downloading data for {args.ticker} from {args.start} to {args.end} with pykrx...")
    df = download_stock_data_pykrx(args.ticker, args.start, args.end)
    save_raw_csv(df, args.ticker)

if __name__ == "__main__":
    main()