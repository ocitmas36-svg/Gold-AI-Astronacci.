import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_insight(asset, signal, p, tp, sl, rsi_h1, rsi_m5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Prompt supaya AI kasih alasan random tapi masuk akal
    prompt = (
        f"Berikan analisa singkat dan unik untuk Rosit (karyawan angkringan). "
        f"Aset: {asset}. Sinyal: {signal}. Harga: ${p:.2f}. TP: {tp:.2f}, SL: {sl:.2f}. "
        f"RSI H1: {rsi_h1:.1f}, RSI M5: {rsi_m5:.1f}. "
        f"Jelaskan dengan gaya santai kenapa angka SL dan TP itu penting di momen ini. "
        f"Gunakan analogi sate atau angkringan sesekali. Jangan terlalu kaku."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Rosit, fokus ke angka TP & SL ya. Tetap sopan dan jangan lupa senyum ke pelanggan!"

def get_market_data(symbol, timeframe_min):
    limit = 100
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit={limit}&aggregate={timeframe_min}"
    data = requests.get(url).json()['Data']['Data']
    prices = [d['close'] for d in data]
    
    m_prices = prices[-15:]
    gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
    losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / (avg_loss if avg_loss > 0 else 0.001))))
    
    p_now = prices[-1]
    support = min(prices)
    resistance = max(prices)
    
    return p_now, rsi, support, resistance

def main():
    assets = [
        {"name": "BITCOIN", "symbol": "BTC", "emoji": "🟠"},
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}
    ]
    
    for asset in assets:
        try:
            p_h1, rsi_h1, sup_h1, res_h1 = get_market_data(asset['symbol'], 60)
            p_m5, rsi_m5, sup_m5, res_m5 = get_market_data(asset['symbol'], 5)
            
            if rsi_h1 > 45 and rsi_m5 < 35:
                signal = "🚀 GAS BUY!"
                tp, sl = res_m5, sup_m5 - (p_m5 * 0.001)
            elif rsi_h1 < 55 and rsi_m5 > 65:
                signal = "📉 GAS SELL!"
                tp, sl = sup_m5, res_m5 + (p_m5 * 0.001)
            else:
                signal = "☕ NGOPI DULU"
                tp, sl = p_m5, p_m5

            # Panggil Gemini kalau ada sinyal GAS
            ai_msg = ""
            if "GAS" in signal:
                ai_msg = get_ai_insight(asset['name'], signal, p_m5, tp, sl, rsi_h1, rsi_m5)
            else:
                ai_msg = "Belum ada momen pas, Rosit. Mending lap meja dulu atau siapin arang, market lagi galau."

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
                f"🧠 **AI INSIGHT:**\n_{ai_msg.strip()}_\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
