import requests
from datetime import datetime
import os

# --- KONFIGURASI (Pastikan diisi di Environment Variables / Secrets) ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl):
    """Fungsi edukasi trading dari Gemini AI"""
    if not GEMINI_API_KEY:
        return "Rosit, pantau market ya. Koneksi AI lagi istirahat."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu Guru Trading Pro untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"Data: RSI {rsi:.1f}, Area {area:.1f}%. Sinyal: {signal}. "
        f"Garis: Lantai ${support:,.2f}, Atap ${resistance:,.2f}. "
        f"Rencana: TP ${tp:,.2f} & SL ${sl:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa entry di sini (RSI & Area). "
        f"Kenapa SL & TP ditaruh di situ? Gunakan bahasa abang-adik yang akrab, "
        f"sopan, dan beri semangat buat Rosit yang lagi ngerintis modal dari angkringan."
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=12)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Sinyal masuk, Rosit! Fokus ke angka TP/SL dulu ya!"

def get_market_data():
    """Mengambil data langsung dari API Binance (Agar sinkron dengan MetaTrader)"""
    try:
        # Mengambil data kline/candlestick 5 menit (5m)
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=100"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        # Harga Close ada di indeks ke-4
        prices = [float(d[4]) for d in data]
        
        p = prices[-1]
        support = min(prices)
        resistance = max(prices)
        
        # Hitung RSI sederhana (14 periode)
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        avg_gain = sum(gains)/14 if gains else 0
        avg_loss = sum(losses)/14 if losses else 0.001
        rsi = 100 - (100 / (1 + (avg_gain / avg_loss)))
        
        # Posisi harga (Area %)
        area = ((p - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        # Kecepatan market (Volatilitas)
        moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
        avg_speed = sum(moves) / len(moves) if moves else 0.01
        
        return p, rsi, area, avg_speed, support, resistance
    except Exception as e:
        print(f"Error sinkronisasi Binance: {e}")
        return None

def main():
    asset_name = "BITCOIN (BTCUSDm)"
    print(f"[{datetime.now()}] Sinkronisasi harga dengan platform...")
    
    data = get_market_data()
    if not data: return

    p, rsi, area, avg_speed, support, resistance = data
    
    # --- LOGIKA SCALPER SENSITIF (Sesuai Dana Tipis) ---
    if rsi < 40 and area < 40:
        signal = "🟢 GAS BUY (Momen Murah)"
        tp, sl = p * 1.008, p * 0.99
    elif rsi > 60 and area > 60:
        signal = "🔴 GAS SELL (Momen Mahal)"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal = "🟡 NGOPI DULU (Tengah Tangga)"
        tp, sl = p, p

    # Estimasi Waktu
    dist_to_tp = abs(tp - p)
    est_minutes = round(dist_to_tp / avg_speed) if avg_speed > 0 else 0
    est_text = f"{round(est_minutes/60, 1)} Jam" if est_minutes > 60 else f"{est_minutes} Menit"

    # Analisa Guru AI
    ai_msg = get_ai_analysis(p, area, rsi, signal, support, resistance, tp, sl)

    # Format Pesan Telegram
    msg = (
        f"🟠 **{asset_name} REPORT** 🟠\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA PLATFORM**: `${p:,.2f}`\n"
        f"📊 **RSI**: {rsi:.1f} | **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🧱 **LANTAI (S)**: `${support:,.2f}`\n"
        f"🏠 **ATAP (R)**: `${resistance:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"⏳ **ESTIMASI**: ± {est_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 **KULIAH GURU AI:**\n{ai_msg}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    # Kirim ke Telegram
    try:
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        print("✅ Berhasil! Harga sudah sinkron dengan platform.")
    except Exception as e:
        print(f"❌ Gagal: {e}")

if __name__ == "__main__":
    main()