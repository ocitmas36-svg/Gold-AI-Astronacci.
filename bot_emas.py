import requests
from datetime import datetime
import os

# --- AMBIL KUNCI DARI GITHUB SECRETS ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, rsi, area, signal, support, resistance, tp, sl):
    """Fungsi edukasi dari Gemini AI"""
    if not GEMINI_API_KEY: 
        return "Rosit, AI lagi istirahat bentar. Fokus ke angka TP/SL dulu ya!"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = (
        f"Kamu Guru Trading Pro untuk Rosit. Aset: BITCOIN (BTC). Harga: ${p:,.2f}. "
        f"Data: RSI {rsi:.1f}, Area {area:.1f}%. Sinyal: {signal}. "
        f"Rencana: TP ${tp:,.2f} & SL ${sl:,.2f}. "
        f"TUGAS: Jelaskan singkat kenapa kondisi ini disebut {signal}. "
        f"Beri semangat buat Rosit yang lagi jualan sate sambil belajar trading!"
    )
    
    try:
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Pasar lagi lincah, Sit! Tetap disiplin sama Stop Loss ya!"

def get_market_data():
    """Ambil data harga dari Binance API"""
    try:
        # Ambil harga detik ini
        p_now = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()['price'])
        
        # Ambil data 5 menit terakhir (M5)
        data_kline = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=50").json()
        prices = [float(x[4]) for x in data_kline]
        
        support = min(prices)
        resistance = max(prices)
        
        # RSI Sederhana
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        rsi = 100 - (100 / (1 + (sum(gains) / (sum(losses) if sum(losses) > 0 else 0.1))))
        
        # Area (Posisi harga terhadap lantai/atap)
        area = ((p_now - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        return p_now, rsi, area, support, resistance
    except Exception as e:
        print(f"Gagal tarik data: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Memulai Bot Bitcoin...")
    
    data = get_market_data()
    if not data:
        print("Data market kosong!")
        return

    p, rsi, area, support, resistance = data
    
    # --- LOGIKA SINYAL ---
    if rsi < 40 and area < 30:
        signal, emoji = "GAS BUY (Momen Murah)", "🟢"
        tp, sl = p * 1.008, p * 0.99
    elif rsi > 60 and area > 70:
        signal, emoji = "GAS SELL (Momen Mahal)", "🔴"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal, emoji = "NGOPI DULU (Sabar)", "🟡"
        tp, sl = p, p

    # Ambil Analisa AI
    ai_msg = get_ai_analysis(p, rsi, area, signal, support, resistance, tp, sl)

    # Susun Pesan
    msg = (
        f"🟠 **BITCOIN (BTCUSDm) REPORT** 🟠\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 **AKSI**: `{emoji} {signal}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 **HARGA**: `${p:,.2f}`\n"
        f"📊 **RSI**: {rsi:.1f} | **AREA**: {area:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **TARGET TP**: `${tp:,.2f}`\n"
        f"🛡️ **STOP LOSS**: `${sl:,.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📚 **KULIAH GURU AI:**\n{ai_msg}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    
    # PROSES KIRIM KE TELEGRAM (Wajib kirim!)
    try:
        url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
        payload_tele = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        response = requests.post(url_tele, json=payload_tele, timeout=10)
        
        if response.status_code == 200:
            print("✅ Berhasil kirim pesan ke Telegram!")
        else:
            print(f"❌ Gagal kirim! Respon Telegram: {response.text}")
            
    except Exception as e:
        print(f"❌ Error saat kirim: {e}")

if __name__ == "__main__":
    main()