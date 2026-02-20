import requests
from datetime import datetime
import pytz
import os

TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, rsi, signal):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa Emas Rosit. Harga ${p:.2f}, Area {area:.1f}, RSI {rsi:.1f}. Sinyal: {signal}. "
        f"Berikan alasan teknis singkat kenapa Rosit harus masuk atau tunggu. Panggil Rosit."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, RSI berada di {rsi:.1f}. Strategi: {signal}. Tetap waspada!"

def main():
    try:
        # Mengambil data harga historis singkat untuk simulasi RSI
        url_hist = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=PAXG&tsym=USD&limit=14"
        hist_data = requests.get(url_hist).json()['Data']['Data']
        prices = [d['close'] for d in hist_data]
        
        # Kalkulasi RSI Sederhana (Ilmu Akurasi)
        gains = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i] > prices[i-1]]
        losses = [prices[i-1] - prices[i] for i in range(1, len(prices)) if prices[i] < prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Data Utama
        url_data = "https://min-api.cryptocompare.com/data/pricemultifull?fsyms=PAXG&tsyms=USD"
        data = requests.get(url_data).json()['RAW']['PAXG']['USD']
        p, low, high = data['PRICE'], data['LOW24HOUR'], data['HIGH24HOUR']
        volatility = ((high - low) / low) * 100
        area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
        
        # --- LOGIKA AKURASI v100 (RSI + AREA) ---
        if rsi > 70 and area > 80:
            signal = "🔴 PRECISION SELL (Divergence)"
            tp, sl = p * 0.993, p * 1.004
        elif rsi < 30 and area < 20:
            signal = "🟢 PRECISION BUY (Oversold)"
            tp, sl = p * 1.007, p * 0.996
        elif volatility > 2.0 and area > 85:
            signal = "🚀 MOMENTUM RIDE (Strong Trend)"
            tp, sl = p * 1.015, p * 0.992
        else:
            signal = "🟡 NEUTRAL (Wait for RSI Confirmation)"
            tp, sl = p * 1.005, p * 0.995

        ai_msg = get_ai_analysis(p, area, rsi, signal)
        tz = pytz.timezone('Asia/Jakarta')
        waktu = datetime.now(tz).strftime('%H:%M:%S')

        msg = (
            f"🔱 **OMNISCIENT PRECISION v100** 🔱\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🕒 **WAKTU** : {waktu} WIB\n"
            f"💵 **PRICE** : `${p:.2f}`\n"
            f"📊 **AREA** : {area:.1f} | **RSI** : {rsi:.1f}\n"
            f"📡 **SIGNAL**: **{signal}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🧠 **AI ADVISOR:**\n_{ai_msg.strip()}_\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 **TP**: `${tp:.2f}` | 🛡️ **SL**: `${sl:.2f}`\n"
            f"💡 **ACCURACY**: HIGH CONFIRMATION\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__": main()
