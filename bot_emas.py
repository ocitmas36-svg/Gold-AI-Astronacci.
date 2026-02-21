import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(asset_name, p, area, rsi, signal, est_time):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # PROMPT KHUSUS AGAR DETAIL PER ASET
    if "BITCOIN" in asset_name:
        konteks = (
            f"Analisa Bitcoin (BTC) untuk Rosit. Harga: ${p:.2f}, Area: {area:.1f}, RSI: {rsi:.1f}. Sinyal: {signal}. "
            f"Bitcoin adalah aset high volatility. Jelaskan apakah ini karena dorongan Whales, "
            f"apakah RSI {rsi:.1f} sudah terlalu jenuh atau masih kuat naik (bullish momentum). "
            f"Berikan alasan kenapa target bisa tercapai dalam {est_time}."
        )
    else:
        konteks = (
            f"Analisa Emas (PAXG) untuk Rosit. Harga: ${p:.2f}, Area: {area:.1f}, RSI: {rsi:.1f}. Sinyal: {signal}. "
            f"Emas adalah aset safe haven. Jelaskan hubungannya dengan area {area:.1f} yang menunjukkan harga murah atau mahal. "
            f"Berikan alasan teknis kenapa Rosit harus sabar menunggu atau segera masuk di estimasi {est_time}."
        )

    prompt = (
        f"{konteks} Gunakan gaya bicara yang tegas, profesional, tapi akrab. "
        f"Jangan pakai kata-kata umum. Jelaskan detail teknisnya dan panggil Rosit."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, sistem sedang sibuk. Tapi secara teknis {asset_name} berada di posisi {signal}. Fokus pada SL dan TP!"

def get_market_data(symbol):
    url_hist = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=20"
    hist_data = requests.get(url_hist).json()['Data']['Data']
    prices = [d['close'] for d in hist_data]
    
    moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    avg_speed = sum(moves) / len(moves) if moves else 0.01

    gains = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i] > prices[i-1]]
    losses = [prices[i-1] - prices[i] for i in range(1, len(prices)) if prices[i] < prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / (avg_loss if avg_loss > 0 else 0.001))))

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
            
            if asset['type'] == "gold":
                if rsi < 35 and area < 25:
                    signal, emoji = "🟢 BELI SEKARANG (BUY)", "🔱"
                    tp, sl = p * 1.006, p * 0.996
                elif rsi > 65 and area > 75:
                    signal, emoji = "🔴 JUAL SEKARANG (SELL)", "🔱"
                    tp, sl = p * 0.994, p * 1.004
                else:
                    signal, emoji = "🟡 TUNGGU (NEUTRAL)", "🔱"
                    tp, sl = p * 1.003, p * 0.997
            else:
                if rsi < 25:
                    signal, emoji = "🚀 BELI SEKARANG (EXTREME BUY)", "🟠"
                    tp, sl = p * 1.04, p * 0.97
                elif rsi > 55 and area > 55:
                    signal, emoji = "⚡ BELI SEKARANG (MOMENTUM RIDE)", "🟠"
                    tp, sl = p * 1.025, p * 0.985
                elif rsi > 80:
                    signal, emoji = "🩸 JUAL SEKARANG (DANGER SELL)", "🟠"
                    tp, sl = p * 0.96, p * 1.03
                else:
                    signal, emoji = "🟡 TUNGGU (NEUTRAL)", "🟠"
                    tp, sl = p * 1.01, p * 0.99

            dist_to_tp = abs(tp - p)
            est_minutes = round(dist_to_tp / (avg_speed if avg_speed > 0 else 0.001))
            est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

            ai_msg = get_ai_analysis(asset['name'], p, area, rsi, signal, est_text)

            msg = (
                f"{emoji} **{asset['name']}** {emoji}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📢 **AKSI**: `{signal}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🕒 **WAKTU** : {waktu} WIB\n"
                f"💵 **PRICE** : `${p:.2f}`\n"
                f"📊 **RSI** : {rsi:.1f} | **AREA** : {area:.1f}\n"
                f"⏳ **ESTIMASI**: ± {est_text}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 **TARGET TP**: `${tp:.2f}`\n"
                f"🛡️ **STOP LOSS**: `${sl:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🧠 **ANALISA DETAIL AI:**\n_{ai_msg.strip()}_\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
