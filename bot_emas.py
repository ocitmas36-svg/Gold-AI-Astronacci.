import requests
from datetime import datetime
import os

# --- KUNCI RAHASIA ---
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_ai_analysis(p, rsi, area, signal, support, resistance, tp, sl):
    """Kuliah Trading dari Gemini AI"""
    if not GEMINI_API_KEY: return "AI sedang istirahat, Sit!"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"Jelaskan ke Rosit kenapa BTC di harga ${p:,.2f} ini statusnya {signal}. "
        f"Data: RSI {rsi:.1f}, Area {area:.1f}%. Support: ${support:,.2f}, Resistance: ${resistance:,.2f}. "
        f"Kenapa TP di ${tp:,.2f} dan SL di ${sl:,.2f}? Beri penjelasan edukatif tapi santai "
        f"kayak abang ke adeknya yang lagi jualan sate sambil belajar trading."
    )
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "Fokus ke angka TP/SL dulu ya Sit, market lagi lincah!"

def get_market_data():
    """Ambil data harga dengan cara yang stabil"""
    try:
        # Ambil harga detik ini (Ticker)
        p_res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10).json()
        p_now = float(p_res['price'])
        
        # Ambil data kline 5 menit (M5)
        k_res = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=5m&limit=50", timeout=10).json()
        prices = [float(x[4]) for x in k_res] 
        
        support = min(prices)
        resistance = max(prices)
        
        # Hitung RSI sederhana
        m_prices = prices[-15:]
        gains = [m_prices[i] - m_prices[i-1] for i in range(1, len(m_prices)) if m_prices[i] > m_prices[i-1]]
        losses = [m_prices[i-1] - m_prices[i] for i in range(1, len(m_prices)) if m_prices[i] < m_prices[i-1]]
        rsi = 100 - (100 / (1 + (sum(gains) / (sum(losses) if sum(losses) > 0 else 0.1))))
        
        area = ((p_now - support) / (resistance - support)) * 100 if (resistance - support) != 0 else 50
        
        return p_now, rsi, area, support, resistance
    except Exception as e:
        print(f"❌ Error Data: {e}")
        return None

def main():
    data = get_market_data()
    if not data: return

    p, rsi, area, support, resistance = data
    
    # LOGIKA ENTRY
    if rsi < 40 and area < 35:
        signal, emoji = "GAS BUY (Momen Murah)", "🟢"
        tp, sl = p * 1.008, p * 0.99
    elif rsi > 60 and area > 65:
        signal, emoji = "GAS SELL (Momen Mahal)", "🔴"
        tp, sl = p * 0.992, p * 1.01
    else:
        signal, emoji = "NGOPI DULU (Tunggu Momen)", "🟡"
        tp, sl = p, p

    ai_msg = get_ai_analysis(p, rsi, area, signal, support, resistance, tp, sl)

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
    
    # KIRIM KE TELEGRAM
    url_tele = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    requests.post(url_tele, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    print("✅ Berhasil kirim laporan lengkap!")

if __name__ == "__main__":
    main()