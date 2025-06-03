import backtrader as bt
import pickle
import pandas as pd
import os


class MLStrategy(bt.Strategy):
    params = (
        ("model_path", ""),
        ("features", []),
        ("split_idx", 0),
        ("position_size", 100),
    )

    def __init__(self):
        # 모델과 스케일러 로드
        with open(self.params.model_path, "rb") as f:
            loaded = pickle.load(f)
        self.model = loaded["model"]
        self.scaler = loaded["scaler"]

        # processed CSV 전체 로드
        csv_path = self.params.model_path.replace("models\\", "data\\processed\\").replace(".pkl", "_processed.csv")
        self.df = pd.read_csv(csv_path, index_col=0, parse_dates=True).reset_index()
        self.current_idx = self.params.split_idx

    def next(self):
        if self.current_idx >= len(self.df):
            return

        # 현재 pandas 인덱스 기준 행 추출
        data_row = self.df.loc[self.current_idx, self.params.features].values.reshape(1, -1)
        scaled_row = self.scaler.transform(data_row)
        pred = self.model.predict(scaled_row)[0]

        if not self.position and pred == 1:
            self.buy(size=self.params.position_size)
        elif self.position and pred == 0:
            self.sell(size=self.params.position_size)

        self.current_idx += 1


def run_backtest(model_filename: str, cash=10000000, commission=0.001):
    """
    model_filename: models 폴더 내 pickle 파일 이름 (예: random_forest_model.pkl)
    """
    cerebro = bt.Cerebro()
    model_path = os.path.join("models", model_filename)
    processed_csv = model_path.replace("models\\", "data\\processed\\").replace(".pkl", "_processed.csv")
    df = pd.read_csv(processed_csv, index_col=0, parse_dates=True)

    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)

    split_idx = int(len(df) * 0.8)
    features = ['MA20', 'MA60', 'RSI14', 'MACD_signal', 'Volume']

    cerebro.addstrategy(MLStrategy, model_path=model_path, features=features, split_idx=split_idx)
    print(f"[INFO] Starting Portfolio Value: {cerebro.broker.getvalue():,.0f} KRW")
    cerebro.run()
    print(f"[INFO] Final Portfolio Value:   {cerebro.broker.getvalue():,.0f} KRW")
    cerebro.plot()


if __name__ == "__main__":
    run_backtest("random_forest_model.pkl")