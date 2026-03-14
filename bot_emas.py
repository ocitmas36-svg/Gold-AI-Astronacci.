import requests
from datetime import datetime
import pytz
import os
import time

# ==========================================
# 1. KONFIGURASI (Ambil dari Environment)
# ==========================================
TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf4cF9UwXaPEuSHFVcL36LvDSrBk41H4c_8n9810uMllAG49g/formResponse"

LAST_SIGNAL = None 

# ==========================================
# 2. MESIN ANALISA (The "Brain")
# ==========================================
def get_smart_analysis(symbol="BTC"):
    try:
        # Ambil data lebih banyak (100 candle) untuk hitung MA & Volatilitas
        url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={symbol}&tsym=USD&limit=100"
        res = requests.get(url, timeout=10).json()
        data = res['Data']['Data']
        prices = [d['close'] for d in data]
        
        current_p = prices[-1]
        
        # --- A. Hitung RSI (Momentum) ---
        diffs = [prices[i] - prices[i-1] for i in range(len(prices)-14, len(prices))]
        gains = sum([d for d in diffs if d > 0]) / 14
        losses = abs(sum([d for d in diffs if d < 0])) / 14
        rsi = 100 - (100 / (1 + (gains / (losses if losses > 0 else 0.001))))
        
        # --- B. Hitung MA-50 (Trend Jangka Panjang) ---
        ma50 = sum(prices[-50:]) / 50
        
        # --- C. Hitung MA-20 (Trend Jangka Pendek) ---
        ma20 = sum(prices[-20:]) / 20
        
        # --- D. Cek Volatilitas (Bollinger-ish) ---
        avg_move = sum([abs(prices[i] - prices[i-1]) for i in range(len(prices)-10, len(prices))]) / 10
        is_volatile = current_p * 0.0005 # Minimal gerak 0.05% untuk dianggap valid

        # --- LOGIKA PENGAMBILAN KEPUTUSAN (THE BRAIN) ---
        signal = "🟡 NGOPI DULU"
        
        # SYARAT BUY: RSI Murah (<35) + Harga di atas MA-50 (Trend Naik) + Harga nembus MA-20 ke atas
        if rsi < 35 and current_p > ma50 and current_p > ma20:
            signal = "🟢 GAS BUY"
            
        # SYARAT SELL: RSI Mahal (>65) + Harga di bawah MA-50 (Trend Turun) + Harga nembus MA-20 ke bawah
        elif rsi > 65 and current_p < ma50 and current_p < ma20:
            signal = "🔴 GAS SELL"
            
        # FILTER TAMBAHAN: Jika gerak terlalu sempit, paksa NGOPI (Anti-Sideways)
        if avg_move < is_volatile:
            signal = "🟡 NGOPI DULU (Market Tidur)"

        return {"price": current_p, "rsi": rsi, "ma50": ma50, "signal": signal}
    except Exception as e:
        print(f"Error Brain: {e}")
        return None

# ==========================================
# 3. ENGINE EKSEKUSI
# ==========================================
def jalankan_bot():
    global LAST_SIGNAL
    tz = pytz.timezone('Asia/Jakarta')
    waktu_skrg = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    brain = get_smart_analysis("BTC")
    if not brain: return
    
    p, rsi, signal = brain['price'], brain['rsi'], brain['signal']
    
    # 1. Update Database (Google Sheets) - Tetap kirim agar grafik web update
    payload = {
        "entry.497131546": waktu_skrg, "entry.1075855313": p,
        "entry.2000248052": round(rsi, 2), "entry.1827234230": round(brain['ma50'], 2),
        "entry.237807986": signal
    }
    requests.post(FORM_URL, data=payload)

    # 2. Notifikasi Telegram (HANYA JIKA SINYAL BERUBAH & BUKAN NGOPI)
    if signal != LAST_SIGNAL:
        if "GAS" in signal:
            msg = (
                f"🦅 **ROSIT GOLD AI - SMART SIGNAL**\n"
                f"━━━━━━━━━━━━━━\n"
                f"📢 **AKSI**: `{signal}`\n"
                f"💵 **HARGA**: `${p:,.2f}`\n"
                f"📊 **RSI**: {rsi:.1f}\n"
                f"📈 **TREND**: {'UP' if p > brain['ma50'] else 'DOWN'}\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ *Segera cek dashboard web kamu!*"
            )
            requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        
        LAST_SIGNAL = signal
        print(f"[{waktu_skrg}] Sinyal Baru: {signal}")
    else:
        print(f"[{waktu_skrg}] Menunggu momentum... (Status: {signal})")

# ==========================================
# 4. MAIN LOOP
# ==========================================
if __name__ == "__main__":
    print("🚀 Mesin 'Otak Baru' Rosit Gold AI Aktif!")
    while True:
        jalankan_bot()
        time.sleep(300) # Cek setiap 5 menit (lebih responsif tapi aman)
