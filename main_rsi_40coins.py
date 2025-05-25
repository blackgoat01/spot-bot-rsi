import os
import requests
from pybit import HTTP
from time import sleep

# Telegram Setup
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": message})
    except Exception as e:
        print("Telegram Fehler:", e)

# Startmeldung
send_telegram_message("✅ Der GridSignal Bot wurde auf Render erfolgreich gestartet.")
send_telegram_message("📡 RSI-Überwachung für 40 Coins wurde gestartet mit 5 % Trailing-Stop.")

# Bybit API Setup
session = HTTP(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Globale Liste aktiver Positionen mit Trailing
open_positions = {}

# RSI Berechnung
def get_rsi(symbol):
    try:
        candles = session.get_kline(
            category="linear", symbol=symbol, interval="15", limit=100
        )["result"]["list"]
        closes = [float(c[4]) for c in candles]
        deltas = [closes[i+1] - closes[i] for i in range(len(closes)-1)]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0.01
        avg_loss = sum(losses) / 14 if losses else 0.01
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2), closes[-1]
    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")
        return None, None

# Überwachte Coins
symbols = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TRXUSDT",
    "MATICUSDT", "DOTUSDT", "LTCUSDT", "SHIBUSDT", "NEARUSDT", "BCHUSDT", "LINKUSDT", "OPUSDT",
    "HBARUSDT", "RNDRUSDT", "UNIUSDT", "ICPUSDT", "TONUSDT", "SUIUSDT", "SEIUSDT", "ARBUSDT",
    "PEPEUSDT", "TIAUSDT", "INJUSDT", "FTMUSDT", "GALAUSDT", "BLURUSDT", "PYTHUSDT", "1000SATSUSDT",
    "FETUSDT", "JASMYUSDT", "ORDIUSDT", "WUSDT", "DYDXUSDT", "LDOUSDT", "ENSUSDT", "COTIUSDT"
]

# Hauptfunktion mit RSI & Trailing
def run():
    trailing_percent = 5  # Trailing Stop Abstand
    while True:
        for symbol in symbols:
            rsi, price = get_rsi(symbol)
            if rsi is None or price is None:
                continue

            # Einstiegssignal
            if rsi < 40 and symbol not in open_positions:
                open_positions[symbol] = {
                    "entry": price,
                    "highest": price
                }
                send_telegram_message(f"📈 RSI Signal: {symbol} RSI={rsi} — Einstieg bei {price:.4f}")

            # Trailing Stop Überwachung
            if symbol in open_positions:
                position = open_positions[symbol]
                if price > position["highest"]:
                    position["highest"] = price
                trailing_stop = position["highest"] * (1 - trailing_percent / 100)
                if price <= trailing_stop:
                    send_telegram_message(
                        f"✅ Gewinn gesichert bei {symbol}! Verkauf bei {price:.4f} (Trailing Stop aktiviert)"
                    )
                    del open_positions[symbol]
        sleep(600)  # 10 Minuten warten

# Start
if __name__ == "__main__":
    send_telegram_message("🛰 RSI-Überwachung läuft jetzt live.")
    run()
