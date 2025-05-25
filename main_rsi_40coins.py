import os
import requests
from pybit import HTTP
from time import sleep

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = { "chat_id": chat_id, "text": message }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Fehler beim Senden an Telegram:", e)

send_telegram_message("✅ Der GridSignal Bot wurde auf Render erfolgreich gestartet.")

session = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

symbols = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "DOGEUSDT", "TRXUSDT", "DOTUSDT", "AVAXUSDT",
    "MATICUSDT", "SHIBUSDT", "ATOMUSDT", "LINKUSDT", "APTUSDT", "NEARUSDT", "ARBUSDT", "FILUSDT", "SUIUSDT", "OPUSDT",
    "STXUSDT", "INJUSDT", "RUNEUSDT", "LDOUSDT", "IMXUSDT", "PEPEUSDT", "FLOKIUSDT", "NOTUSDT", "PYTHUSDT", "RNDRUSDT",
    "JASMYUSDT", "BONKUSDT", "WLDUSDT", "SEIUSDT", "GALAUSDT", "CHZUSDT", "ENJUSDT", "DYDXUSDT", "APEUSDT", "TIAUSDT"
]

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
        print(f"Fehler beim RSI für {symbol}:", e)
        return None

def run():
    send_telegram_message("📡 RSI-Überwachung für 40 Coins wurde gestartet.")
    while True:
        for symbol in symbols:
            rsi = get_rsi(symbol)
            if rsi and rsi < 40:
                send_telegram_message(f"[GridSignal] RSI für {symbol} = {rsi} — mögliches Kaufsignal!")
        sleep(600)

if __name__ == "__main__":
    run()