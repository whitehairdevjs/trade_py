import argparse
import pandas as pd
import numpy as np
from src.trading.model.ml_models import RandomForestModel, XGBoostModel, LightGBMModel

def load_processed_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, index_col=0, parse_dates=True)

def create_target(df: pd.DataFrame):
    # 내일 종가 상승 여부 이진 분류 (1: 상승, 0: 하락/보합)
    df['Target'] = np.where(df['Adj Close'].shift(-1) > df['Adj Close'], 1, 0)
    df.dropna(subset=['Target'], inplace=True)
    return df

def main():
    parser = argparse.ArgumentParser(description="모델 학습 스크립트 (Python 3.11.9 기준)")
    parser.add_argument("--input", type=str, required=True, help="processed CSV 파일 경로")
    parser.add_argument("--model", type=str, choices=["rf","xgb","lgb"], default="rf", help="학습할 모델 종류")
    args = parser.parse_args()

    print(f"[INFO] Loading processed data from {args.input}...")
    df = load_processed_csv(args.input)
    df = create_target(df)

    features = ['MA20','MA60','RSI14','MACD_signal','Volume']
    X = df[features].values
    y = df['Target'].values

    # 시계열 특성: 80%를 학습, 20%를 테스트 (shuffle=False)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    if args.model == "rf":
        model = RandomForestModel(n_estimators=100)
        X_train_scaled, X_test_scaled = model.scale(X_train, X_test)
        model.train(X_train_scaled, y_train)
        model.evaluate(X_test_scaled, y_test)
        model.save("models/random_forest_model.pkl")

    elif args.model == "xgb":
        model = XGBoostModel(params={"objective": "binary:logistic", "eval_metric": "error"})
        X_train_scaled, X_test_scaled = model.scaler.fit_transform(X_train), model.scaler.transform(X_test)
        model.train(X_train_scaled, y_train, X_val=X_test_scaled, y_val=y_test)
        model.evaluate(X_test_scaled, y_test)
        model.save("models/xgboost_model.pkl")

    else:  # lightgbm
        model = LightGBMModel(params={"objective": "binary", "metric": "binary_error"})
        X_train_scaled, X_test_scaled = model.scaler.fit_transform(X_train), model.scaler.transform(X_test)
        model.train(X_train_scaled, y_train, X_val=X_test_scaled, y_val=y_test)
        model.evaluate(X_test_scaled, y_test)
        model.save("models/lightgbm_model.pkl")

if __name__ == "__main__":
    main()