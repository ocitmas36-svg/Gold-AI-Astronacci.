import requests
from datetime import datetime
import pytz
import os

# --- CONFIGURATION (Pastikan diisi di Environment Variables) ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(asset_name, p, area, rsi, signal, est_time, support, resistance):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # PROMPT DENGAN ILMU SNR (LANTAI & ATAP)
    konteks = (
        f"Analisa untuk Rosit. Aset: {asset_name}. Harga: ${p:.2f}. RSI: {rsi:.1f}. Area: {area:.1f}. "
        f"Lantai (Support): ${support:.2f}, Atap (Resistance): ${resistance:.2f}. Sinyal: {signal}. "
        f"Jelaskan secara detail kenapa angka ini penting. Sebutkan apakah harga sudah 'mentok plafon' "
        f"atau 'injak lantai'. Berikan semangat agar Rosit tetap bahagia dan sopan meski market bergejolak."
    )

    prompt = (
        f"{konteks} Gunakan gaya bahasa asisten trading profesional yang akrab. "
        f"Panggil Rosit. Berikan alasan teknis yang masuk akal tapi mudah dipahami karyawan angkringan."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return f"Rosit, sinyal {signal} terdeteksi. Pantau Lantai di ${support:.2f} dan Atap di ${resistance:.2f}. Tetap tenang!"

def get_market_data(symbol):
    # Ambil data historis 24 jam untuk SNR
    url_hist = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={symbol}&tsym=USD&limit=24"
    hist_data = requests.get(url_hist).json()['Data']['Data']
    prices = [d['close'] for d in hist_data]
    
    # Support & Resistance (Lantai & Atap)
    support = min(prices)
    resistance = max(prices)
    
    # RSI Calculation (14 minutes)
    url_rsi = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=14"
    m_data = requests.get(url_rsi).json()['Data']['Data']
    m_prices = [d['close'] for d in m_data]
    
    gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
    losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
    avg_gain = sum(gains)/14 if gains else 0
    avg_loss = sum(losses)/14 if losses else 0.001
    rsi = 100 - (100 / (1 + (avg_gain / (avg_loss if avg_loss > 0 else 0.001))))

    # Price & Area
    url_price = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD"
    raw_data = requests.get(url_price).json()['RAW'][symbol]['USD']
    p = raw_data['PRICE']
    area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
    
    # Volatility for Estimation
    moves = [abs(m_prices[i] - m_prices[i-1]) for i in range(1, len(m_prices))]
    avg_speed = sum(moves) / len(moves) if moves else 0.01

    return p, rsi, area, avg_speed, support, resistance

def main():
    assets = [
        {"name": "BITCOIN (BTC)", "symbol": "BTC", "emoji": "🟠"},
        {"name": "GOLD (PAXG)", "symbol": "PAXG", "emoji": "🔱"}
    ]
    
    tz = pytz.timezone('Asia/Jakarta')
    waktu = datetime.now(tz).strftime('%H:%M:%S')

    for asset in assets:
        try:
            p, rsi, area, avg_speed, support, resistance = get_market_data(asset['symbol'])
            
            # LOGIKA SINYAL SNIPER (RSI + AREA)
            if rsi < 30 and area < 20:
                signal = "🟢 BELI (INJAK LANTAI)"
                tp, sl = p * 1.02, p * 0.985
            elif rsi > 70 and area > 80:
                signal = "🔴 JUAL (MENTOK PLAFON)"
                tp, sl = p * 0.98, p * 1.015
            else:
                signal = "🟡 TUNGGU (TENGAH TANGGA)"
                tp, sl = p * 1.01, p * 0.99

            dist_to_tp = abs(tp - p)
            est_minutes = round(dist_to_tp / (avg_speed if avg_speed > 0 else 0.001))
            est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

            ai_msg = get_ai_analysis(asset['name'], p, area, rsi, signal, est_text, support, resistance)

            msg = (
                f"{asset['emoji']} **{asset['name']}** {asset['emoji']}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📢 **AKSI**: `{signal}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💵 **PRICE** : `${p:.2f}`\n"
                f"📊 **RSI** : {rsi:.1f} | **AREA** : {area:.1f}%\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🧱 **LANTAI (S)**: `${support:.2f}`\n"
                f"🏠 **ATAP (R)** : `${resistance:.2f}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 **TARGET TP**: `${tp:.2f}`\n"
                f"🛡️ **STOP LOSS**: `${sl:.2f}`\n"
                f"⏳ **ESTIMASI**: ± {est_text}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🧠 **ANALISA AI:**\n_{ai_msg.strip()}_\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
            
        except Exception as e:
            print(f"Error {asset['name']}: {e}")

if __name__ == "__main__":
    main()
