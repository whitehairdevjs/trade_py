from pykiwoom.kiwoom import Kiwoom
from PyQt5.QtWidgets import QApplication
import sys
import os
from src.config import KIWOOM_ID, KIWOOM_PW

class RealTimeApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = Kiwoom()
        # 로그인 시 ID/PW를 자동 입력하려면 아래 방식도 가능하나,
        # 일반적으로 CommConnect() 호출 시 HTS 로그인 창이 뜹니다.
        # self.kiwoom.CommConnect(block=True, user=KIWOOM_ID, pwd=KIWOOM_PW)

        self.kiwoom.CommConnect()  # 공인인증서 로그인 창
        # 실시간 데이터 수신 콜백 등록
        self.kiwoom.OnReceiveRealData.connect(self.on_receive_realdata)
        # SCR1 윈도우로 삼성전자(005930) 현재가(10)·체결량(15) 실시간 등록
        self.kiwoom.SetRealReg("SCR1", "005930", "10;15", "0")

    def on_receive_realdata(self, screen_no, real_type, real_data):
        price = self.kiwoom.GetCommRealData("005930", 10)   # 10: 현재가
        volume = self.kiwoom.GetCommRealData("005930", 15)  # 15: 체결량
        print(f"[REALTIME] 현재가: {price} KRW, 체결량: {volume}")

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    # 반드시 PowerShell에서 venv 활성화한 상태에서 실행
    app = RealTimeApp()
    app.run()