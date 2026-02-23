import requests
from datetime import datetime
import os

# --- KONFIGURASI ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl):
    if not GEMINI_API_KEY:
        return "Rosit, fokus pantau harga dulu ya. AI lagi istirahat."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu Guru Trading Pro untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"Data: RSI {rsi:.1f}, Area {area:.1f}%. Sinyal: {signal}. "
        f"Garis: Lantai ${support:,.2f}, Atap ${resistance:,.2f}. "
        f"Rencana: TP ${tp:,.2f} & SL ${sl:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa entry di sini. "
        f"Gunakan gaya bahasa abang-adik yang akrab dan beri semangat buat Rosit yang lagi ngerintis angkringan."
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=12)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu ya!"

def get_market_data():
    try:
        # Ganti ke Binance API agar harganya SAMA dengan MetaTrader
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
        res = requests.get(url, timeout=10)
        data = res.json()
        prices = [float(d[4]) for d in data] # Harga Close
        
        p = prices[-1]
        support = min(prices)
        resistance = max(prices)
        
        # Hitung RSI 14
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        rsi = 100 - (100 / (1 + (sum(gains) / (sum(losses) if sum(losses) > 0 else 0.1))))
        
        area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        # Kecepatan gerak
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return p, rsi, area, avg_speed, support, resistance
    except Exception as e:
        print(f"Error ambil data: {e}")
        return None

def main():
    asset_name = "BITCOIN (BTCUSDm)"
    print(f"Memulai analisa {asset_name}...")
    
    data = get_market_data()
    if not data: return

    p, rsi, area, avg_speed, support, resistance = data
    
    # LOGIKA ENTRY
    if rsi < 40 and area < 40:
        signal, emoji = "GAS BUY (Momen Murah)", "🟢"
        tp, sl = p + 400, p - 300
    elif rsi > 60 and area > 60:
        signal, emoji = "GAS SELL (Momen Mahal)", "🔴"
        tp, sl = p - 400, p + 300
    else:
        signal, emoji = "NGOPI DULU (Tunggu Momen)", "🟡"
        tp, sl = p, p

    ai_msg = get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl)

    msg = (
        f"🟠 **{asset_name} REPORT** 🟠\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{emoji} {signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **RSI**: {rsi:.1f} | **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧱 **LANTAI (S)**: `${support:,.2f}`\n"
        f"🏠 **ATAP (R)**: `${resistance:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 **KULIAH GURU AI:**\n{ai_msg}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("✅ Laporan terkirim!")
    except:
        print("❌ Gagal kirim!")

if __name__ == "__main__":
    main()