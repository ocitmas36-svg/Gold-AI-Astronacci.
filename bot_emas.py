import requests
import sys

TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    print("--- MEMULAI PROSES KIRIM ---")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "TES OMNISCIENT: Jalur GitHub sudah Terbuka!"}
    
    r = requests.post(url, json=payload)
    print(f"Status: {r.status_code}")
    print(f"Respon: {r.text}")

if __name__ == "__main__":
    main()
    
