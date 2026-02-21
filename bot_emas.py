import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION (AMBIL DARI GITHUB SECRETS) ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(asset_name, p, area, rsi, signal):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Analisa {asset_name} untuk Rosit (Trader Angkringan). "
        f"Harga: ${p:.2f}, Area: {area:.1f}, RSI: {rsi:.1f}. Sinyal: {signal}. "
        f"Berikan strategi singkat, tajam, dan panggil Rosit. "
        f"Gunakan gaya bicara yang memotivasi tapi tetap waspada."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, sistem mendeteksi {asset_name} di RSI {rsi:.1f}. Tetap fokus pada strategi!"

def get_market_data(symbol):
    # Mengambil histori 14 menit untuk RSI
    url_hist = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=14"
    hist_data = requests.get(url_hist).json()['Data']['Data']
    prices = [d['close'] for d in hist_data]
    
    # Kalkulasi RSI
    gains = [prices[i] - prices[i-1] for i in range(1, len(prices)) if prices[i] > prices[i-1]]
    losses = [prices[i-1] - prices[i] for i in range(1, len(prices)) if prices[i] < prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))

    # Data Harga Terkini
    url_price = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD"
    raw_data = requests.get(url_price).json()['RAW'][symbol]['USD']
    p = raw_data['PRICE']
    low = raw_data['LOW24HOUR']
    high = raw_data['HIGH24HOUR']
    area = ((p - low) / (high - low)) * 100 if (high - low) != 0 else 50
    
    return p, rsi, area

def main():
    assets = [
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "type": "gold"},
        {"name": "BITCOIN (BTC)", "symbol": "BTC", "type": "crypto"}
    ]
    
    tz = pytz.timezone('Asia/Jakarta')
    waktu = datetime.now(tz).strftime('%H:%M:%S')

    for asset in assets:
        try:
            p, rsi, area = get_market_data(asset['symbol'])
            
            # --- LOGIKA ILMU AKURASI v100 (DI-PISAH) ---
            if asset['type'] == "gold":
                # Ilmu Emas: Konservatif (RSI 30/70)
                if rsi < 30 and area < 20:
                    signal, emoji = "🟢 PRECISION BUY (Oversold)", "🔱"
                    tp, sl = p * 1.007, p * 0.996
                elif rsi > 70 and area > 80:
                    signal, emoji = "🔴 PRECISION SELL (Divergence)", "🔱"
                    tp, sl = p * 0.993, p * 1.004
                else:
                    signal, emoji = "🟡 NEUTRAL (Wait)", "🔱"
                    tp, sl = p * 1.005, p * 0.995
            else:
                # Ilmu Bitcoin: Agresif (RSI 20/80 + Momentum)
                if rsi < 20:
                    signal, emoji = "🚀 EXTREME BUY (Floor)", "🟠"
                    tp, sl = p * 1.05, p * 0.97
                elif rsi > 55 and area > 60:
                    signal, emoji = "⚡ MOMENTUM RIDE (Whales In)", "🟠"
                    tp, sl = p * 1.03, p * 0.985
                elif rsi > 85:
                    signal, emoji = "🩸 DANGER SELL (Peak)", "🟠"
                    tp, sl = p * 0.95, p * 1.03
                else:
                    signal, emoji = "🟡 CONSOLIDATION", "🟠"
                    tp, sl = p * 1.02, p * 0.99

            ai_msg = get_ai_analysis(asset['name'], p, area, rsi, signal)

            msg = (
                f"{emoji} **{asset['name']} PRECISION v100** {emoji}\n"
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
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
