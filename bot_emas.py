import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(asset_name, p, area, rsi, signal, est_time, support, resistance):
    if not GEMINI_API_KEY:
        return f"Rosit, sinyal {signal} terdeteksi. Pantau area ${p:,.2f}. Tetap sopan!"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa singkat untuk Rosit (modal terbatas). Aset: {asset_name}. Harga: ${p:,.2f}. "
        f"RSI: {rsi:.1f}. Area: {area:.1f}%. Sinyal: {signal}. "
        f"Berikan saran trading scalping yang aman tapi lincah. Pakai analogi angkringan yang cerdas."
    )
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=8)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Fokus ke angka TP/SL ya Sit, market lagi lincah!"

def get_market_data(symbol):
    try:
        # Ambil data M5 (5 menit) biar lebih sensitif buat scalping
        url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=100"
        data = requests.get(url, timeout=10).json()['Data']['Data']
        prices = [d['close'] for d in data]
        
        p = prices[-1]
        support = min(prices)
        resistance = max(prices)
        
        # RSI 14
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        # Volatilitas untuk estimasi
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return p, rsi, area, avg_speed, support, resistance
    except:
        return None

def main():
    assets = [
        {"name": "BITCOIN (BTC)", "symbol": "BTC", "emoji": "🟠"},
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}
    ]
    
    for asset in assets:
        data = get_market_data(asset['symbol'])
        if not data: continue
        
        p, rsi, area, avg_speed, support, resistance = data
        
        # --- LOGIKA MODAL TIPIS (SCALPER SOPAN) ---
        if rsi < 40 and area < 40:
            signal = "🟢 GAS BUY (Momen Murah)"
            tp, sl = p * 1.008, p * 0.99  # Untung 0.8%, Rugi 1%
        elif rsi > 60 and area > 60:
            signal = "🔴 GAS SELL (Momen Mahal)"
            tp, sl = p * 0.992, p * 1.01  # Untung 0.8%, Rugi 1%
        else:
            signal = "🟡 NGOPI DULU (Tunggu Momen)"
            tp, sl = p, p

        dist_to_tp = abs(tp - p)
        est_minutes = round(dist_to_tp / avg_speed) if avg_speed > 0 else 0
        est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

        ai_msg = get_ai_analysis(asset['name'], p, area, rsi, signal, est_text, support, resistance)

        msg = (
            f"{asset['emoji']} **{asset['name']} (SCALPING)** {asset['emoji']}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📢 **AKSI**: `{signal}`\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💵 **PRICE** : `${p:,.2f}`\n"
            f"📊 **RSI** : {rsi:.1f} | **AREA** : {area:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
            f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
            f"⏳ **ESTIMASI**: ± {est_text}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AI INSIGHT:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
        
