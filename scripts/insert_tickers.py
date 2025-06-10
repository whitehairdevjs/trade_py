# scripts/insert_tickers.py

import os
import sys
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pykrx import stock


def fetch_all_tickers(date: str) -> pd.DataFrame:
    """
    지정한 날짜(date, 'YYYYMMDD') 기준으로 KOSPI/KOSDAQ 티커와 마켓 정보를 DataFrame 으로 반환
    """
    all_data = []
    markets = {
        "KOSPI": "KOSPI",
        "KOSDAQ": "KOSDAQ"
    }

    for market_name, market_code in markets.items():
        try:
            tickers = stock.get_market_ticker_list(market=market_code, date=date)
        except Exception as e:
            print(f"[WARN] get_market_ticker_list('{market_code}', '{date}') 예외: {e}", file=sys.stderr)
            continue

        for tic in tickers:
            try:
                name = stock.get_market_ticker_name(tic)
                if not name:
                    name = ""
            except Exception:
                name = ""
            all_data.append({
                "ticker": tic,
                "name"  : name,
                "market": market_name
            })

    df = pd.DataFrame(all_data, columns=["ticker", "name", "market"])
    return df


def insert_into_db(df: pd.DataFrame, conn_params: dict):
    """
    DataFrame의 ticker/market을 PostgreSQL의 krx_tickers 테이블에 삽입.
    conn_params: dict with keys: host, port, dbname, user, password
    """
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()

        # 1) 테이블 생성 (없으면)
        create_sql = """
        CREATE TABLE IF NOT EXISTS krx_tickers (
            ticker VARCHAR(10) PRIMARY KEY,
            name   VARCHAR(100) NOT null,
            market VARCHAR(10) NOT NULL
        );
        """
        cur.execute(create_sql)
        conn.commit()

        # 2) 기존 데이터 삭제 혹은 ON CONFLICT 처리
        #    여기선 모든 데이터를 지우고 재삽입하는 예시
        cur.execute("DELETE FROM krx_tickers;")
        conn.commit()

        # 3) DataFrame을 튜플 리스트로 변환 후 bulk insert
        records = df.to_records(index=False)
        values = [(r["ticker"], r["name"], r["market"]) for r in records]

        insert_sql = """
        INSERT INTO krx_tickers (ticker, name, market)
        VALUES %s
        ON CONFLICT (ticker) DO NOTHING;
        """
        execute_values(cur, insert_sql, values)
        conn.commit()

        print(f"[INFO] 총 {len(values)}개 레코드를 krx_tickers 테이블에 삽입했습니다.")

    except Exception as e:
        print(f"[ERROR] DB 삽입 중 예외 발생: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()


def main():
    # 1) 기준일자를 오늘로 지정 (원한다면 고정 날짜로 바꿔도 됨)
    today = datetime.today().strftime("%Y%m%d")

    print(f"[INFO] {today} 기준으로 KOSPI/KOSDAQ 티커 목록을 가져옵니다.")
    df_tickers = fetch_all_tickers(date=today)
    print(f"[INFO] 총 {len(df_tickers)}개 티커 데이터를 가져왔습니다.")

    # 2) DB 연결 정보 (환경 변수에서 불러오기)
    conn_params = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "dbname": os.getenv("PGDATABASE", "postgres"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PDB_KEY", ""),
    }

    # 3) 삽입 함수 호출
    insert_into_db(df_tickers, conn_params)


if __name__ == "__main__":
    main()