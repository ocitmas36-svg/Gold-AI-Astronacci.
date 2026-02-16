import requests
import sys

# DATA VALID ROSIT
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("Memulai pengiriman pesan ke Telegram...", flush=True)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": "🔥 OMNISCIENT BERHASIL!\n\nRosit, kalau pesan ini muncul, berarti sistem kita sudah 100% sinkron. Gaskeun pantau Emas!"
    }
    
    try:
        r = requests.post(url, json=payload)
        print(f"Status: {r.status_code}", flush=True)
        print(f"Respon: {r.text}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    main()
    
