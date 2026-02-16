import requests
from datetime import datetime
import pytz
import math

# --- CORE ACCESS ---
TOKEN = "7864440626:AAH_Qz67CNo5XW1iXW9o17l1xR0YpD7G5mI"
CHAT_ID = "5378770281"

def get_deep_intelligence():
    try:
        # Data Emas (PAXG)
        gold = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT").json()
        # Data Market Global (BTC) sebagai alat ukur sentimen risiko
        market = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT").json()
        return {
            "p": float(gold['lastPrice']),
            "h": float(gold['highPrice']),
            "l": float(gold['lowPrice']),
            "o": float(gold['openPrice']),
            "v": float(gold['volume']),
            "qv": float(gold['quoteVolume']),
            "c": int(gold['count']),
            "cp": float(gold['priceChangePercent']),
            "m_cp": float(market['priceChangePercent'])
        }
    except: return None

def main():
    d = get_deep_intelligence()
    if not d: return

    # --- 1. DATA PROCESSING ---
    p, h, l, o = d['p'], d['h'], d['l'], d['o']
    d_range = h - l
    vwap = d['qv'] / d['v'] if d['v'] != 0 else p
    
    # --- 2. ADVANCED MATHEMATICS (Z-SCORE & VOLATILITY) ---
    mean = (h + l + o + p) / 4
    std_dev = max((h - l) / 4, 0.01)
    z_score = (p - mean) / std_dev
    rsi = ((p - l) / d_range) * 100 if d_range != 0 else 50

    # --- 3. SMC & VSA LOGIC (SMART MONEY) ---
    vol_density = d['v'] / d['c'] if d['c'] != 0 else 0
    is_liquidity_grab = (p - l) < (d_range * 0.1) or (h - p) < (d_range * 0.1)
    fvg_gap = abs(p - vwap) > (std_dev * 2.5)

    # --- 4. THE 100-POINT SUPREME MATRIX ---
    score = 0
    reasons = []

    # BUY CONFLUENCE
    if z_score < -1.8: score += 25; reasons.append("Z-Score: Anomali Harga Murah")
    if p < vwap: score += 15; reasons.append("VWAP: Di bawah Harga Institusi")
    if rsi < 30: score += 20; reasons.append("RSI: Penjualan Jenuh (Capitulation)")
    if d['m_cp'] < -3.0: score += 15; reasons.append("Global: Safe Haven Demand")
    if vol_density > (d['v'] * 0.0001): score += 15; reasons.append("VSA: Jejak Uang Besar")
    if is_liquidity_grab and p < vwap: score += 10; reasons.append("SMC: Liquidity Hunt")

    # SELL CONFLUENCE
    sell_score = 0
    if z_score > 1.8: sell_score += 30
    if rsi > 75: sell_score += 25
    if h - p < (d_range * 0.05): sell_score += 20

    # --- 5. DECISION & RISK MGMT ---
    action = None
    final_score = 0
    if score >= 70: action, final_score = "BUY", score
    elif sell_score >= 70: action, final_score = "SELL", sell_score
    else: return

    # Virtual SL & Adaptive TP
    atr = d_range / 10
    tp1, tp2 = 6.5 + (atr * 0.5), 15.0 + (atr * 1.5)
    v_sl = 4.5 + (atr * 0.3)

    # Timezone WIB
    wib = pytz.timezone('Asia/Jakarta')
    time_now = datetime.now(wib).strftime('%H:%M:%S')

    # --- MESSAGE ---
    emoji = "🔮" if action == "BUY" else "⚔️"
    msg = (
        f"{emoji} **OMNISCIENT ARCHITECT v17.0**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 **WAKTU:** {time_now} WIB\n"
        f"💵 **HARGA:** ${p:.2f} | **SKOR:** {final_score}/100\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 **INTEL DATA:**\n"
        f"• " + "\n• ".join(reasons) + "\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 **SINYAL: {action}**\n"
        f"✅ **ENTRY:** {p:.2f}\n"
        f"🎯 **TP 1:** {p+tp1 if action=='BUY' else p-tp1:.2f}\n"
        f"🎯 **TP 2:** {p+tp2 if action=='BUY' else p-tp2:.2f}\n"
        f"🛡️ **V-SL (Virtual):** {p-v_sl if action=='BUY' else p+v_sl:.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 *Saran: Jika TP1 kena, amankan modal ke titik entry!*"
    )
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    main()
