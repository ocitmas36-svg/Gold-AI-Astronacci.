import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_market_data(symbol, timeframe_min):
    limit = 100
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit={limit}&aggregate={timeframe_min}"
    data = requests.get(url).json()['Data']['Data']
    prices = [d['close'] for d in data]
    
    # RSI 14
    m_prices = prices[-15:]
    gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
    losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / (avg_loss if avg_loss > 0 else 0.001))))
    
    p_now = prices[-1]
    support = min(prices)
    resistance = max(prices)
    area = ((p_now - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
    
    return p_now, rsi, area, support, resistance

def main():
    assets = [
        {"name": "BITCOIN", "symbol": "BTC", "emoji": "🟠"},
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}
    ]
    
    for asset in assets:
        try:
            # 1. Peta H1
            p_h1, rsi_h1, area_h1, sup_h1, res_h1 = get_market_data(asset['symbol'], 60)
            # 2. Eksekusi M5
            p_m5, rsi_m5, area_m5, sup_m5, res_m5 = get_market_data(asset['symbol'], 5)
            
            # LOGIKA SINYAL (BELI MURAH / JUAL MAHAL)
            if rsi_h1 > 45 and rsi_m5 < 35:
                # KONDISI BELI MURAH (BUY)
                signal = "🚀 GAS BUY! (Beli di Murah)"
                tp = res_m5
                sl = sup_m5 - (p_m5 * 0.001) # SL dikit di bawah lantai
            elif rsi_h1 < 55 and rsi_m5 > 65:
                # KONDISI JUAL MAHAL (SELL)
                signal = "📉 GAS SELL! (Jual di Mahal)"
                tp = sup_m5
                sl = res_m5 + (p_m5 * 0.001) # SL dikit di atas atap
            else:
                signal = "☕ NGOPI DULU"
                tp = p_m5
                sl = p_m5

            msg = (
                f"{asset['emoji']} **{asset['name']}** {asset['emoji']}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🗺️ **PETA H1**: `{'NAIK' if rsi_h1 > 50 else 'TURUN'}`\n"
                f"🎯 **EKSEKUSI M5**: `{signal}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💵 **HARGA**: `${p_m5:.2f}`\n"
                f"🧱 **LANTAI**: `${sup_m5:.2f}`\n"
                f"🏠 **ATAP**: `${res_m5:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 **TARGET TP**: `${tp:.2f}`\n"
                f"🛡️ **STOP LOSS**: `${sl:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Saran: Jika SELL, pasang SL di Atap. Jika BUY, pasang SL di Lantai. Tetap sopan!*"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
