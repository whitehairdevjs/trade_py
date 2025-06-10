# python scripts\insert_price_data.py --start 20250101 --end 20250610

import os
import sys
import argparse
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values
from pykrx import stock


def fetch_tickers(conn_params):
    """ krx_tickers 테이블에서 모든 ticker 목록을 가져옴 """
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ticker FROM krx_tickers;")
            return [row[0] for row in cur.fetchall()]


def fetch_ohlcv(ticker, start, end):
    """
       pykrx로 일별 OHLCV+Adj Close 조회
       start/end는 'YYYYMMDD' 문자열
       반환: list of tuples (ticker, date, open, high, low, close, adj_close, volume)
       """
    df = stock.get_market_ohlcv_by_date(start, end, ticker)
    df = df.rename(columns={
        "시가": "open_price",
        "고가": "high_price",
        "저가": "low_price",
        "종가": "close_price",
        "거래량": "volume"
    })
    df["adj_close"] = df["close_price"]

    # 인덱스 이름 확인 (None 이면 'index'가 기본)
    idx_name = df.index.name if df.index.name else "index"
    # reset_index 한 뒤 실제 컬럼명으로 price_date 리네임
    df_reset = df.reset_index()
    df_reset = df_reset.rename(columns={idx_name: "price_date"})

    records = []
    for _, row in df_reset.iterrows():
        # 'price_date' 컬럼이 이제 확실히 존재합니다
        records.append((
            ticker,
            row["price_date"].strftime("%Y-%m-%d"),
            float(row["open_price"]),
            float(row["high_price"]),
            float(row["low_price"]),
            float(row["close_price"]),
            float(row["adj_close"]),
            int(row["volume"])
        ))
    return records


def insert_prices(records, conn_params):
    """
    krx_daily_price 테이블에 bulk insert
    """
    sql = """
    INSERT INTO krx_daily_price
      (ticker, price_date, open_price, high_price, low_price, close_price, adj_close, volume)
    VALUES %s
    ON CONFLICT (ticker, price_date) DO UPDATE
      SET open_price = EXCLUDED.open_price,
          high_price = EXCLUDED.high_price,
          low_price  = EXCLUDED.low_price,
          close_price = EXCLUDED.close_price,
          adj_close  = EXCLUDED.adj_close,
          volume     = EXCLUDED.volume;
    """
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            execute_values(cur, sql, records, page_size=500)
        conn.commit()


def main():
    parser = argparse.ArgumentParser(
        description="KRX 티커별 일별 시세를 DB에 저장"
    )
    parser.add_argument("--start", required=True,
        help="조회 시작일 (YYYYMMDD)")
    parser.add_argument("--end", required=True,
        help="조회 종료일 (YYYYMMDD)")
    args = parser.parse_args()

    # DB 연결정보 (환경 변수)
    conn_params = {
        "host":     os.getenv("PGHOST", "localhost"),
        "port":     os.getenv("PGPORT", "5432"),
        "dbname":   os.getenv("PGDATABASE", "postgres"),
        "user":     os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PDB_KEY", ""),
        "options":  "-c client_encoding=UTF8 -c lc_messages=C"
    }

    # 1) krx_tickers에서 티커 목록 읽기
    print("[INFO] krx_tickers 테이블에서 ticker 목록 조회...")
    tickers = fetch_tickers(conn_params)
    print(f"[INFO] 총 {len(tickers)}개 티커 조회됨.")

    # 2) 각 티커별 OHLCV 조회 & DB 삽입
    for tic in tickers:
        print(f"[INFO] {tic} 시세 조회 ({args.start}~{args.end})...")
        try:
            recs = fetch_ohlcv(tic, args.start, args.end)
            if recs:
                insert_prices(recs, conn_params)
                print(f"[INFO]  → {len(recs)}건 삽입/업데이트 완료.")
            else:
                print("  → 데이터 없음, 건너뜀.")
        except Exception as e:
            print(f"[ERROR] {tic} 처리 중 오류: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
