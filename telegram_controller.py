import os
import sys
import subprocess
import sqlite3
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("LEADS_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Проверка токена
if not TELEGRAM_BOT_TOKEN:
    print("Ошибка: TELEGRAM_BOT_TOKEN не задан в .env")
    sys.exit(1)

# Преобразуем ID чата в число для сравнения
ALLOWED_CHAT_ID = int(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else None

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки сообщения в TG: {e}")

def send_document(filepath, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(filepath, "rb") as doc:
            files = {"document": doc}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            requests.post(url, data=data, files=files, timeout=30)
    except Exception as e:
        send_message(f"❌ Ошибка отправки файла: {e}")

def run_parser(query):
    send_message(f"⏳ Начинаю парсинг по запросу: *{query}*...\nЭто займет около 1-2 минут.")
    
    # Запускаем places_scraper.py в режиме google через subprocess
    try:
        process = subprocess.run(
            ["./venv/bin/python", "places_scraper.py", "google", query],
            capture_output=True,
            text=True,
            timeout=180
        )
        if process.returncode == 0:
            # Делаем экспорт собранных контактов в CSV
            subprocess.run(["./venv/bin/python", "places_scraper.py", "export"], capture_output=True)
            
            # Отправляем файл
            csv_path = "leads_export.csv"
            if os.path.exists(csv_path):
                send_document(csv_path, f"✅ Парсинг завершен по запросу: {query}")
            else:
                send_message("❌ Файл экспорта не был создан.")
        else:
            send_message(f"❌ Ошибка при парсинге:\n`{process.stderr[:400]}`")
    except subprocess.TimeoutExpired:
        send_message("❌ Время ожидания парсера истекло (таймаут 3 минуты).")
    except Exception as e:
        send_message(f"❌ Системная ошибка: {e}")

def get_db_status():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]
    
    # Группировка по категориям
    cursor.execute("SELECT category, COUNT(*) FROM leads GROUP BY category")
    categories = cursor.fetchall()
    conn.close()
    
    cat_text = ""
    for cat, count in categories:
        cat_text += f"• {cat}: {count} контактов\n"
        
    status_text = (
        f"📊 **Статус базы лидов:**\n"
        f" Всего собрано: *{total_leads}*\n\n"
        f"**По категориям:**\n{cat_text if cat_text else 'База пуста'}"
    )
    return status_text

def handle_update(update):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")
    
    # Безопасность: отвечаем ТОЛЬКО владельцу бота
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        print(f"Игнорируем сообщение от неизвестного чата: {chat_id}")
        return
        
    if not text:
        return
        
    if text.startswith("/start"):
        welcome = (
            "👋 Привет! Я твой пульт управления ИИ-системой на Google Cloud.\n\n"
            "**Доступные команды:**\n"
            "➡️ `/parse <запрос>` — Запустить сбор контактов из Google Maps (например, `/parse кафе Бишкек`)\n"
            "➡️ `/export` — Выгрузить всю текущую базу контактов в Excel-таблицу (CSV)\n"
            "➡️ `/status` — Посмотреть статистику собранных контактов\n"
            "➡️ `/ping` — Проверить работу сервера"
        )
        send_message(welcome)
        
    elif text.startswith("/parse"):
        query = text.replace("/parse", "").strip()
        if not query:
            send_message("❌ Укажите запрос. Пример: `/parse рестораны Бишкек`")
        else:
            run_parser(query)
            
    elif text.startswith("/export"):
        try:
            subprocess.run(["./venv/bin/python", "places_scraper.py", "export"], capture_output=True)
            csv_path = "leads_export.csv"
            if os.path.exists(csv_path):
                send_document(csv_path, "📊 Текущая база контактов (Excel/CSV)")
            else:
                send_message("❌ База пуста, нечего экспортировать.")
        except Exception as e:
            send_message(f"❌ Ошибка экспорта: {e}")
            
    elif text.startswith("/status"):
        try:
            status = get_db_status()
            send_message(status)
        except Exception as e:
            send_message(f"❌ Ошибка базы данных: {e}")
            
    elif text.startswith("/ping"):
        send_message("🟢 Сервер работает в штатном режиме. ИИ-продавец на связи!")

def main():
    print("Управляющий Telegram-бот запущен...")
    offset = None
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    while True:
        try:
            params = {"timeout": 30, "offset": offset}
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    handle_update(update)
                    offset = update["update_id"] + 1
            else:
                print(f"Ошибка TG API: {response.text}")
                time.sleep(5)
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            print(f"Ошибка в цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
