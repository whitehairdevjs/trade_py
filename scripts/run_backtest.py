import argparse
from src.trading.backtesting import run_backtest

def main():
    parser = argparse.ArgumentParser(description="백테스트 실행 스크립트 (Python 3.11.9 기준)")
    parser.add_argument("--model", type=str, required=True, help="models 폴더 내 모델 파일 이름 (예: random_forest_model.pkl)")
    args = parser.parse_args()

    run_backtest(args.model)

if __name__ == "__main__":
    main()
