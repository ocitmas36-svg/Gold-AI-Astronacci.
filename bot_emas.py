import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_insight(asset, signal, p, tp, sl, rsi_h1, rsi_m5):
    # Jika API KEY kosong, langsung skip ke pesan standar
    if not GEMINI_API_KEY:
        return "Siap eksekusi, Rosit! Jaga emosi, jaga sate, dan jaga profit."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa singkat untuk Rosit. Aset: {asset}. Sinyal: {signal}. Harga: ${p:.2f}. "
        f"Target TP: {tp:.2f}, SL: {sl:.2f}. Berikan satu alasan logis kenapa angka ini dipilih "
        f"dengan gaya asisten angkringan yang cerdas."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        # Timeout dipercepat biar nggak kelamaan nunggu
        response = requests.post(url, json=payload, timeout=5)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        # Kalo AI Error/Timeout, pesan ini yang muncul biar bot gak mati
        return f"Market lagi kencang, Rosit! Fokus ke TP ${tp:.2f} dan SL ${sl:.2f}. Gas!"

def get_market_data(symbol, timeframe_min):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=50&aggregate={timeframe_min}"
    data = requests.get(url).json()['Data']['Data']
    prices = [d['close'] for d in data]
    p_now = prices[-1]
    
    # RSI Sederhana
    m_prices = prices[-15:]
    gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
    losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
    
    return p_now, rsi, min(prices), max(prices)

def main():
    assets = [{"name": "BITCOIN", "symbol": "BTC", "emoji": "🟠"}, {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}]
    
    for asset in assets:
        try:
            p_h1, rsi_h1, sup_h1, res_h1 = get_market_data(asset['symbol'], 60)
            p_m5, rsi_m5, sup_m5, res_m5 = get_market_data(asset['symbol'], 5)
            
            # Logika Sinyal
            if rsi_h1 > 45 and rsi_m5 < 35:
                signal, tp, sl = "🚀 GAS BUY!", res_m5, sup_m5 - (p_m5 * 0.001)
            elif rsi_h1 < 55 and rsi_m5 > 65:
                signal, tp, sl = "📉 GAS SELL!", sup_m5, res_m5 + (p_m5 * 0.001)
            else:
                signal, tp, sl = "☕ NGOPI DULU", p_m5, p_m5

            # Panggil fungsi AI (sudah ada proteksi error di dalamnya)
            ai_msg = get_ai_insight(asset['name'], signal, p_m5, tp, sl, rsi_h1, rsi_m5)

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
                f"🎯 **TP**: `${tp:.2f}` | 🛡️ **SL**: `${sl:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🧠 **AI ANALISA:**\n_{ai_msg.strip()}_\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
