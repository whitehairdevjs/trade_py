import argparse
from src.trading.feature_engineering import load_raw_csv, basic_preprocessing, calculate_technical_indicators, save_processed_csv

def main():
    parser = argparse.ArgumentParser(description="데이터 전처리 및 기술적 지표 계산 스크립트 (Python 3.11.9 기준)")
    parser.add_argument("--input", type=str, required=True, help="raw CSV 파일 경로 (예: data/raw/005930.KS_20250603_153012.csv)")
    args = parser.parse_args()

    print(f"[INFO] Loading raw data from {args.input}...")
    df_raw = load_raw_csv(args.input)
    df_clean = basic_preprocessing(df_raw)
    df_feat = calculate_technical_indicators(df_clean)
    save_processed_csv(df_feat, args.input)

if __name__ == "__main__":
    main()
