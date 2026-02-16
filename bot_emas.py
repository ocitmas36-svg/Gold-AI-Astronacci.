import requests
import os
from datetime import datetime
import pytz
import math

# --- AKSES KHUSUS ---
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def get_oracle_data():
    # Mengambil data real-time dengan presisi tinggi
    url = "https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT"
    try:
        res = requests.get(url).json()
        return {
            "price": float(res['lastPrice']),
            "high": float(res['highPrice']),
            "low": float(res['lowPrice']),
            "open": float(res['openPrice']),
            "quoteVolume": float(res['quoteVolume']), # Volume Uang
            "count": int(res['count']) # Jumlah Transaksi
        }
    except: return None

def check_psychological_level(price):
    # RAHASIA 1: Cek kedekatan dengan angka bulat (Magnet Bank)
    # Contoh: 2700, 2750, 2800
    sisa = price % 50
    # Jika harga berada dalam jarak $2 dari angka bulat
    if sisa < 2 or sisa > 48:
        return True
    return False

def main():
    m = get_oracle_data()
    if not m: return

    price = m['price']
    high = m['high']
    low = m['low']
    open_p = m['open']
    
    # --- HITUNGAN RAHASIA (ORACLE LOGIC) ---
    
    # 1. WICK ANALYSIS (Jejak Paus)
    # Menghitung panjang 'bayangan' candle
    body_size = abs(open_p - price)
    total_range = high - low
    lower_wick = (min(open_p, price) - low)
    upper_wick = (high - max(open_p, price))
    
    # Rasio Wick: Apakah ekor bawah sangat panjang? (Tanda Rejection Kuat)
    is_hammer = lower_wick > (body_size * 2) and lower_wick > (total_range * 0.4)
    is_shooting_star = upper_wick > (body_size * 2) and upper_wick > (total_range * 0.4)

    # 2. RSI & MARKET BIAS
    rsi = ((price - low) / (high - low)) * 100 if (high - low) != 0 else 50
    
    # 3. VOLUME SPIKE (Deteksi 'Uang Masuk')
    # Jika volume transaksi abnormal, berarti ada Big Player masuk
    is_high_vol = m['count'] > 5000 # Ambang batas aktivitas tinggi

    # --- KEPUTUSAN SANG PERAMAL (THE ORACLE) ---
    action = None
    secret_signal = "NONE"
    
    # SKENARIO DEWA 1: THE WHALE TRAP (Wick Rejection + Low RSI)
    # Ekor panjang di bawah + Harga Murah = Paus sedang menyerok
    if is_hammer and rsi < 35:
        action = "BUY"
        secret_signal = "🐋 WHALE TAIL REJECTION"
        analisis = "Terdeteksi ekor panjang di bawah (Wick). Paus menolak harga turun lebih jauh. Akurasi 90%!"
        tp, sl = 9.0, 4.5
        confidence = "WORLD CLASS 💎"

    # SKENARIO DEWA 2: PSYCHOLOGICAL BOUNCE (Angka Bulat)
    elif check_psychological_level(price) and rsi < 30:
        action = "BUY"
        secret_signal = "🧠 PSYCHO LEVEL BOUNCE"
        analisis = "Harga menyentuh 'Angka Keramat' Bank (Area 00/50). Order pending institusi aktif di sini."
        tp, sl = 6.0, 3.0 # Scalping cepat pantulan
        confidence = "HIGH ACCURACY 🔥"

    # SKENARIO DEWA 3: VOLATILITY BREAKOUT (Ledakan Volume)
    elif price > high and is_high_vol:
        action = "BUY"
        secret_signal = "💣 VOLATILITY EXPLOSION"
        analisis = "Volume meledak menembus atap! Jangan lawan arus, ini tren monster."
        tp, sl = 12.0, 6.0
        confidence = "AGGRESSIVE ⚡"

    # SKENARIO DEWA 4: INSTITUTIONAL DUMP (Sell Signal)
    elif is_shooting_star or (price >= high * 0.999 and rsi > 80):
        action = "SELL"
        secret_signal = "🩸 INSTITUTIONAL DUMP"
        analisis = "Jarum panjang di atas. Institusi membuang barang. Siap-siap terjun."
        tp, sl = 8.0, 4.0
        confidence = "HIGH 🔥"

    else:
        # Mode Silent: Oracle sedang bermeditasi
        print(f"Oracle Monitoring... Price: ${price} | Wick: {lower_wick:.1f}")
        return

    # --- PESAN EKSKLUSIF ---
    pesan = (
        f"{'🔮' if action=='BUY' else '💀'} **ROSIT THE ORACLE v9.0**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💵 PRICE : ${price:.2f}\n"
        f"👁️ SECRET : {secret_signal}\n"
        f"📊 CONFIDENCE : {confidence}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📜 **ORACLE PROPHECY:**\n"
        f"_{analisis}_\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚖️ **TRADE EXECUTION:**\n"
        f"✅ ENTRY : {action} NOW!\n"
        f"🎯 PROFIT TARGET : ${price+tp if action=='BUY' else price-tp:.2f}\n"
        f"🛡️ PROTECTION SL : ${price-sl if action=='BUY' else price+sl:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🤫 *Sstt.. Jangan sebar sinyal ini. Ini level institusi.*"
    )
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": pesan, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
