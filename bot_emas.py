import requests
import os

TELE_TOKEN = os.getenv("TELE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def test():
    msg = "Halo Rosit! Kalau pesan ini muncul, berarti koneksi Telegram AMAN. Masalahnya ada di API market atau Gemini."
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    res = requests.post(url, json={"chat_id": CHAT_ID, "text": msg})
    print(res.json())

test()
