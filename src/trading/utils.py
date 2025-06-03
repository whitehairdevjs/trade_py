# src/trading/utils.py
import os

def ensure_directories():
    """
    프로젝트 시작 시 필요한 폴더(data/raw, data/processed, models 등)를 미리 생성해 두는 함수
    """
    dirs = ["data/raw", "data/processed", "models", "reports/figures"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)