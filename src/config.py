import yaml
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# config/config.yaml 읽기
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 키움 OpenAPI 로그인 정보(env에서)
KIWOOM_ID = os.getenv("KIWOOM_ID")
KIWOOM_PW = os.getenv("KIWOOM_PW")