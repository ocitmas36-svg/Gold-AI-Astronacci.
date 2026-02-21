import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION (AMBIL DARI GITHUB SECRETS) ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(asset_name, p, area, rsi, signal, est_time):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa {asset_name} untuk Rosit. Harga: ${p:.2f}, Area: {area:.1f}, RSI: {rsi:.1f}. Sinyal: {signal}. "
        f"Estimasi waktu ke target: {est_time}. "
        f"Berikan saran ke Rosit: Jika sudah lewat {est_time} tapi masih profit dan belum kena TP, apakah sebaiknya diclose manual? "
        f"Panggil Rosit dengan akrab dan beri semangat jualan angkringannya."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, estimasi waktu target ±{est_time}. Jika sudah biru/profit tapi waktu habis, pertimbangkan close manual!"

def get_market_data(symbol):
    # Mengambil histori 20 menit terakhir
    url_hist = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=20"
    hist_data = requests.get(url_hist).json()['Data']['Data']
    prices = [d['close'] for d in hist_data]
    
    # Hitung Kecepatan Gerak (Volatility per Minute)
    moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    avg_speed = sum(moves) / len(moves) if moves else 0.01

    # Kalkulasi RSI
    gains = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i] > prices[i-1]]
    losses = [prices[i-1] - prices[i] for i in range(1, len(prices)) if prices[i] < prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / (avg_loss if avg_loss > 0 else 0.001))))

    # Data Harga Terkini
    url_price = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD"
    raw_data = requests.get(url_price).json()['RAW'][symbol]['USD']
    p = raw_data['PRICE']
    low = raw_data['LOW24HOUR']
    high = raw_data['HIGH24HOUR']
    area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
    
    return p, rsi, area, avg_speed

def main():
    assets = [
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "type": "gold"},
        {"name": "BITCOIN (BTC)", "symbol": "BTC", "type": "crypto"}
    ]
    
    tz = pytz.timezone('Asia/Jakarta')
    waktu = datetime.now(tz).strftime('%H:%M:%S')

    for asset in assets:
        try:
            p, rsi, area, avg_speed = get_market_data(asset['symbol'])
            
            # --- LOGIKA TARGET & ESTIMASI ---
            if asset['type'] == "gold":
                if rsi < 35 and area < 25:
                    signal, emoji = "🟢 PRECISION BUY", "🔱"
                    tp, sl = p * 1.006, p * 0.996
                elif rsi > 65 and area > 75:
                    signal, emoji = "🔴 PRECISION SELL", "🔱"
                    tp, sl = p * 0.994, p * 1.004
                else:
                    signal, emoji = "🟡 NEUTRAL", "🔱"
                    tp, sl = p * 1.003, p * 0.997
            else:
                if rsi < 25:
                    signal, emoji = "🚀 EXTREME BUY", "🟠"
                    tp, sl = p * 1.04, p * 0.97
                elif rsi > 55 and area > 55:
                    signal, emoji = "⚡ MOMENTUM RIDE", "🟠"
                    tp, sl = p * 1.025, p * 0.985
                elif rsi > 80:
                    signal, emoji = "🩸 DANGER SELL", "🟠"
                    tp, sl = p * 0.96, p * 1.03
                else:
                    signal, emoji = "🟡 CONSOLIDATION", "🟠"
                    tp, sl = p * 1.01, p * 0.99

            # Hitung Estimasi Waktu (Jarak TP / Kecepatan gerak per menit)
            dist_to_tp = abs(tp - p)
            est_minutes = round(dist_to_tp / (avg_speed if avg_speed > 0 else 0.001))
            
            if est_minutes > 60:
                est_text = f"{round(est_minutes/60, 1)} Jam"
            else:
                est_text = f"{est_minutes} Menit"

            ai_msg = get_ai_analysis(asset['name'], p, area, rsi, signal, est_text)

            msg = (
                f"{emoji} **{asset['name']} v100** {emoji}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 **WAKTU** : {waktu} WIB\n"
                f"💵 **PRICE** : `${p:.2f}`\n"
                f"📊 **AREA** : {area:.1f} | **RSI** : {rsi:.1f}\n"
                f"📡 **SIGNAL**: **{signal}**\n"
                f"⏳ **ESTIMASI**: ± {est_text}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🧠 **AI ADVISOR:**\n_{ai_msg.strip()}_\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 **TP**: `${tp:.2f}` | 🛡️ **SL**: `${sl:.2f}`\n"
                f"💡 **STRATEGY**: TIME-BASED EXIT READY\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
