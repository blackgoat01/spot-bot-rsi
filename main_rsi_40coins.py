import os
import requests
from pybit import HTTP
from time import sleep

# Telegram Nachricht senden
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Fehler beim Senden an Telegram:", e)

# Startmeldung
send_telegram_message("✅ Der GridSignal Bot wurde auf Render erfolgreich gestartet.")
send_telegram_message("📡 RSI-Überwachung für 40 Coins wurde gestartet.")

# Bybit Session
session = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

# RSI Berechnung
def get_rsi(symbol):
    try:
        kline = session.get_kline(
            category="linear",
            symbol=symbol,
            interval="15",
            limit=100
        )["result"]["list"]
        closes = [float(c[4]) for c in kline]
        deltas = [closes[i + 1] - closes[i] for i in range(len(closes) - 1)]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0.01
        avg_loss = sum(losses) / 14 if losses else 0.01
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except Exception as e:
        print(f"Fehler bei RSI für {symbol}: {e}")
        return None

# Überwachung starten
def run():
    symbols = [
        "ADAUSDT", "XRPUSDT", "DOGEUSDT", "TRXUSDT", "SOLUSDT", "AVAXUSDT", "SHIBUSDT", "DOTUSDT", "MATICUSDT",
        "LINKUSDT", "LTCUSDT", "BNBUSDT", "FILUSDT", "APTUSDT", "INJUSDT", "ARBUSDT", "PEPEUSDT", "PYTHUSDT",
        "FLOKIUSDT", "WIFUSDT", "TONUSDT", "RNDRUSDT", "TIAUSDT", "NEARUSDT", "OPUSDT", "JUPUSDT", "SUIUSDT",
        "SEIUSDT", "NOTUSDT", "DEGENUSDT", "ETHUSDT", "BTCUSDT", "STRKUSDT", "TURBOUSDT", "JASMYUSDT", "1000SATSUSDT",
        "BONKUSDT", "ARKMUSDT", "DYDXUSDT", "UNFIUSDT"
    ]

    while True:
        for symbol in symbols:
            rsi = get_rsi(symbol)
            if rsi:
                if rsi < 40:
                    send_telegram_message(f"🟢 [GridSignal] RSI für {symbol} = {rsi} — mögliches **Kaufsignal**!")
                elif rsi > 70:
                    send_telegram_message(f"🔴 [GridSignal] RSI für {symbol} = {rsi} — mögliches **Verkaufssignal**!")
        sleep(600)  # 10 Minuten Pause

if __name__ == "__main__":
    run()
