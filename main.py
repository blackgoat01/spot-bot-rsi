import os
import requests
from pybit.unified_trading import HTTP
from time import sleep

# API-Zugriff
session = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

# Telegram
TELEGRAM_TOKEN = "7969759010:AAHFUKBcEkP8p-CbYQvM-o_gEs74XamR8sjA"
CHAT_ID = "7465646426"
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Fehler beim Senden an Telegram:", e)

def get_rsi(symbol):
    try:
        kline = session.get_kline(
            category="linear",
            symbol=symbol,
            interval="15",
            limit=100
        )["result"]["list"]
        closes = [float(c[4]) for c in kline]
        deltas = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0.01
        avg_loss = sum(losses) / 14 if losses else 0.01
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except Exception as e:
        print("Fehler beim RSI:", e)
        return None

def run():
    symbols = ["ADAUSDT", "DOGEUSDT", "XRPUSDT", "TRXUSDT"]
    while True:
        for symbol in symbols:
            rsi = get_rsi(symbol)
            if rsi and rsi < 40:
                send_telegram_message(f"[GridSignal] RSI für {symbol} = {rsi} — mögliches Kaufsignal!")
        sleep(600)

if __name__ == "__main__":
    send_telegram_message("[GridSignal] Spot-Bot gestartet und überwacht RSI-Werte.")
    run()
