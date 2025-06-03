import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

class BaseModel:
    def __init__(self, scaler: StandardScaler = None):
        self.scaler = scaler or StandardScaler()
        self.model = None

    def scale(self, X_train: np.ndarray, X_test: np.ndarray):
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled  = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def save(self, model_path: str):
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler}, f)
        print(f"[INFO] Saved model to {model_path}")

    @staticmethod
    def load(model_path: str):
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        return data["model"], data["scaler"]

class RandomForestModel(BaseModel):
    def __init__(self, n_estimators=100, random_state=42):
        super().__init__()
        self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        print("[INFO] Training RandomForest...")
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[RESULT] RandomForest Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred))

class XGBoostModel(BaseModel):
    def __init__(self, params=None, num_boost_round=100):
        super().__init__()
        self.params = params or {"objective": "binary:logistic", "eval_metric": "error", "verbosity": 0}
        self.num_boost_round = num_boost_round
        self.model = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_val=None, y_val=None):
        print("[INFO] Training XGBoost...")
        dtrain = xgb.DMatrix(X_train, label=y_train)
        evals = [(dtrain, "train")]
        if X_val is not None:
            dval = xgb.DMatrix(X_val, label=y_val)
            evals.append((dval, "validation"))
        self.model = xgb.train(self.params, dtrain, num_boost_round=self.num_boost_round, evals=evals, early_stopping_rounds=10)

    def predict(self, X: np.ndarray):
        dtest = xgb.DMatrix(X)
        preds = self.model.predict(dtest)
        return (preds > 0.5).astype(int)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        y_pred = self.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[RESULT] XGBoost Accuracy: {acc:.4f}")

class LightGBMModel(BaseModel):
    def __init__(self, params=None, num_boost_round=100):
        super().__init__()
        self.params = params or {"objective": "binary", "metric": "binary_error", "verbosity": -1}
        self.num_boost_round = num_boost_round
        self.model = None

    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_val=None, y_val=None):
        print("[INFO] Training LightGBM...")
        lgb_train = lgb.Dataset(X_train, label=y_train)
        valid_sets = []
        if X_val is not None:
            lgb_val = lgb.Dataset(X_val, label=y_val, reference=lgb_train)
            valid_sets.append(lgb_val)
        self.model = lgb.train(self.params, lgb_train, num_boost_round=self.num_boost_round, valid_sets=valid_sets, early_stopping_rounds=10)

    def predict(self, X: np.ndarray):
        preds = self.model.predict(X)
        return (preds > 0.5).astype(int)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        y_pred = self.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[RESULT] LightGBM Accuracy: {acc:.4f}")