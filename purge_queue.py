import os
import requests
from dotenv import load_dotenv

load_dotenv()
GREEN_API_ID_INSTANCE = os.getenv("GREEN_API_ID_INSTANCE")
GREEN_API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN_INSTANCE")

def purge_queue():
    print("Purging Green API webhook queue...")
    count = 0
    while True:
        url_recv = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/receiveNotification/{GREEN_API_TOKEN_INSTANCE}"
        try:
            res = requests.get(url_recv, timeout=5)
            if res.status_code == 200 and res.json():
                data = res.json()
                receipt_id = data.get("receiptId")
                if receipt_id:
                    url_del = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/deleteNotification/{GREEN_API_TOKEN_INSTANCE}/{receipt_id}"
                    requests.delete(url_del, timeout=5)
                    count += 1
                    print(f"Deleted notification {receipt_id}")
            else:
                break
        except Exception as e:
            print(f"Error purging: {e}")
            break
    print(f"Purge complete. Deleted {count} notifications.")

if __name__ == "__main__":
    purge_queue()
