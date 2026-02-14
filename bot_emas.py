import yfinance as yf
import pandas as pd

def run_analysis():
    # Ambil data Emas (XAU/USD)
    gold = yf.Ticker("GC=F")
    data = gold.history(period="5d", interval="1h")
    
    if data.empty: return "Data tidak ditemukan."

    high = data['High'].max()
    low = data['Low'].min()
    price_now = data['Close'].iloc[-1]
    
    # Hitung Golden Ratio Fibonacci (0.618)
    fib_618 = high - (0.382 * (high - low))
    
    report = f"📊 GOLD REPORT @ya_rositt\n"
    report += f"Harga: ${price_now:.2f}\n"
    
    # Logika Alert Sederhana
    if price_now <= fib_618 * 1.002: # Toleransi 0.2% dari garis
        report += "⚠️ STATUS: AREA GOLDEN RATIO! (Potensi Pantulan)"
    else:
        report += "Status: Sideways / Belum masuk area buy."
        
    print(report)
    # Nanti di sini kita tambah fungsi kirim_notifikasi()

if __name__ == "__main__":
    run_analysis()
