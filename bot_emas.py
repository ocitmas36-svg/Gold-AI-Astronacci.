import requests

# DATA VALID ROSIT - JANGAN SAMPAI ADA SPASI SALAH
TOKEN = "8448141154:AAFSrEfURZe_za0I8jI5h5o4_Z7mWvOSk4Q"
CHAT_ID = "7425438429"

def main():
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID, 
            "text": "🔥 OMNISCIENT AKTIF!\n\nRosit, kalau pesan ini masuk, berarti GitHub kamu sudah SEHAT. Kabari saya kalau sudah bunyi!",
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=data)
        print(f"Status Telegram: {r.status_code}")
        print(f"Respon: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    
