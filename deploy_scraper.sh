#!/bin/bash
# =====================================================================
# Скрипт развертывания Парсера и Telegram-Управления на сервере Google
# =====================================================================

cd ~/climaflow

echo "=== Шаг 1. Загружаем places_scraper.py ==="
cat << 'EOF' > places_scraper.py
import os
import sys
import json
import time
import sqlite3
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

DB_FILE = "leads.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            phone TEXT UNIQUE,
            website TEXT,
            category TEXT,
            status TEXT DEFAULT 'new',
            last_contacted TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def clean_phone(phone_str):
    if not phone_str:
        return None
    cleaned = "".join(c for c in phone_str if c.isdigit())
    if cleaned.startswith("0"):
        cleaned = "996" + cleaned[1:]
    return cleaned

def fetch_places_google(query, api_key):
    print(f"Запуск поиска Google Places по запросу: '{query}'...")
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "query": query,
        "key": api_key,
        "language": "ru"
    }
    
    leads_count = 0
    next_page_token = True
    
    while next_page_token:
        response = requests.get(search_url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Ошибка поиска Google: {response.text}")
            break
            
        data = response.json()
        results = data.get("results", [])
        
        for place in results:
            place_id = place.get("place_id")
            name = place.get("name")
            address = place.get("formatted_address")
            
            detail_params = {
                "place_id": place_id,
                "fields": "name,formatted_phone_number,international_phone_number,website",
                "key": api_key,
                "language": "ru"
            }
            
            detail_resp = requests.get(details_url, params=detail_params, timeout=15)
            if detail_resp.status_code == 200:
                details = detail_resp.json().get("result", {})
                raw_phone = details.get("international_phone_number") or details.get("formatted_phone_number")
                phone = clean_phone(raw_phone)
                website = details.get("website")
                
                if phone:
                    save_lead(name, address, phone, website, query)
                    leads_count += 1
            time.sleep(0.5)
            
        token = data.get("next_page_token")
        if token:
            params = {
                "pagetoken": token,
                "key": api_key
            }
            time.sleep(2)
        else:
            next_page_token = False
            
    print(f"Поиск завершен. Успешно собрано {leads_count} контактов с телефонами.")

def fetch_places_osm(category_type):
    print(f"Запуск поиска OpenStreetMap по категории: '{category_type}' в Бишкеке...")
    overpass_url = "https://overpass-api.de/api/interpreter"
    bbox = "42.81,74.50,42.93,74.68"
    
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="{category_type}"]({bbox});
      way["amenity"="{category_type}"]({bbox});
      node["shop"="{category_type}"]({bbox});
      way["shop"="{category_type}"]({bbox});
    );
    out body;
    >;
    out skel qt;
    """
    
    headers = {
        "User-Agent": "ClimaFlowScraper/1.0 (sultan.marketing.dubai@gmail.com)",
        "Referer": "https://google.com/"
    }
    
    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Ошибка запроса к Overpass API: {response.status_code}")
            return
            
        data = response.json()
        elements = data.get("elements", [])
        leads_count = 0
        
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:ru") or tags.get("description")
            if not name:
                continue
                
            raw_phone = tags.get("phone") or tags.get("contact:phone")
            phone = clean_phone(raw_phone)
            
            street = tags.get("addr:street") or ""
            house = tags.get("addr:housenumber") or ""
            address = f"{street} {house}".strip() or "Бишкек"
            website = tags.get("website") or tags.get("contact:website")
            
            if phone:
                save_lead(name, address, phone, website, category_type)
                leads_count += 1
                
        print(f"Поиск OSM завершен. Найдено {leads_count} контактов.")
    except Exception as e:
        print(f"Ошибка OSM парсинга: {e}")

def save_lead(name, address, phone, website, category):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO leads (name, address, phone, website, category)
            VALUES (?, ?, ?, ?, ?)
        """, (name, address, phone, website, category))
        conn.commit()
        print(f"➕ Добавлен лид: {name} ({phone})")
    except sqlite3.IntegrityError:
        pass
    conn.close()

def export_to_csv(filename="leads_export.csv"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, phone, website, category, status FROM leads")
    rows = cursor.fetchall()
    conn.close()
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Название", "Адрес", "Телефон (WhatsApp)", "Сайт", "Категория", "Статус"])
        writer.writerows(rows)
    print(f"✅ База данных успешно экспортирована в файл: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "google":
        query = sys.argv[2]
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            print("Ошибка: API-ключ Google не найден!")
            sys.exit(1)
        fetch_places_google(query, api_key)
    elif mode == "osm":
        category = sys.argv[2] if len(sys.argv) > 2 else "restaurant"
        fetch_places_osm(category)
    elif mode == "export":
        export_to_csv()
EOF

echo "=== Шаг 2. Загружаем telegram_controller.py ==="
cat << 'EOF' > telegram_controller.py
import os
import sys
import subprocess
import sqlite3
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    print("Ошибка: TELEGRAM_BOT_TOKEN не задан")
    sys.exit(1)

ALLOWED_CHAT_ID = int(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID else None

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка в TG: {e}")

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
    send_message(f"⏳ Начинаю парсинг Google Maps по запросу: *{query}*...\nЭто может занять пару минут.")
    try:
        process = subprocess.run(
            ["python3", "places_scraper.py", "google", query],
            capture_output=True,
            text=True,
            timeout=180
        )
        if process.returncode == 0:
            subprocess.run(["python3", "places_scraper.py", "export"], capture_output=True)
            csv_path = "leads_export.csv"
            if os.path.exists(csv_path):
                send_document(csv_path, f"✅ Сбор завершен по запросу: {query}")
            else:
                send_message("❌ Файл экспорта не найден.")
        else:
            send_message(f"❌ Ошибка парсинга Google:\n`{process.stderr[:400]}`")
    except Exception as e:
        send_message(f"❌ Ошибка: {e}")

def run_parser_osm(category):
    send_message(f"⏳ Начинаю БЕСПЛАТНЫЙ парсинг OpenStreetMap по категории: *{category}* в Бишкеке...")
    try:
        process = subprocess.run(
            ["python3", "places_scraper.py", "osm", category],
            capture_output=True,
            text=True,
            timeout=180
        )
        if process.returncode == 0:
            subprocess.run(["python3", "places_scraper.py", "export"], capture_output=True)
            csv_path = "leads_export.csv"
            if os.path.exists(csv_path):
                send_document(csv_path, f"✅ Сбор OSM завершен по категории: {category}")
            else:
                send_message("❌ Файл экспорта не найден.")
        else:
            send_message(f"❌ Ошибка парсинга OSM:\n`{process.stderr[:400]}`")
    except Exception as e:
        send_message(f"❌ Ошибка: {e}")

def get_db_status():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, name TEXT, address TEXT, phone TEXT UNIQUE, website TEXT, category TEXT, status TEXT, last_contacted TEXT)")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]
    cursor.execute("SELECT category, COUNT(*) FROM leads GROUP BY category")
    categories = cursor.fetchall()
    conn.close()
    
    cat_text = ""
    for cat, count in categories:
        cat_text += f"• {cat}: {count}\n"
        
    return (
        f"📊 **База контактов ClimaFlow:**\n"
        f"Всего в базе: *{total_leads}* номеров\n\n"
        f"**Категории:**\n{cat_text if cat_text else 'Пусто'}"
    )

def handle_update(update):
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")
    
    if ALLOWED_CHAT_ID and chat_id != ALLOWED_CHAT_ID:
        return
        
    if not text:
        return
        
    if text.startswith("/start"):
        welcome = (
            "🤖 **Пульт управления парсером ClimaFlow**\n\n"
            "Команды:\n"
            "➡️ `/parse_free <категория>` — Собрать бесплатно контакты через OpenStreetMap (cafe, restaurant, office, clinic, dentist, hairdressing)\n"
            "➡️ `/parse <запрос>` — Собрать через Google Maps (требует API-ключ Google в .env)\n"
            "➡️ `/export` — Скачать всю накопленную базу в CSV-файле\n"
            "➡️ `/status` — Показать количество контактов в базе\n"
            "➡️ `/ping` — Проверить работу сервера"
        )
        send_message(welcome)
        
    elif text.startswith("/parse_free"):
        category = text.replace("/parse_free", "").strip()
        if not category:
            send_message("❌ Напишите категорию. Пример: `/parse_free office` или `/parse_free cafe` (доступные: cafe, restaurant, office, clinic, dentist, hairdressing)")
        else:
            run_parser_osm(category)
            
    elif text.startswith("/parse"):
        query = text.replace("/parse", "").strip()
        if not query:
            send_message("❌ Напишите запрос. Пример: `/parse рестораны Бишкек`")
        else:
            run_parser(query)
            
    elif text.startswith("/export"):
        subprocess.run(["python3", "places_scraper.py", "export"], capture_output=True)
        csv_path = "leads_export.csv"
        if os.path.exists(csv_path):
            send_document(csv_path, "📊 База лидов ClimaFlow")
        else:
            send_message("❌ База пуста.")
            
    elif text.startswith("/status"):
        send_message(get_db_status())
            
    elif text.startswith("/ping"):
        send_message("🟢 Сервер управления онлайн. Скрипты готовы!")

def main():
    print("Telegram-контроллер запущен...")
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
                time.sleep(5)
        except requests.exceptions.Timeout:
            continue
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    main()
EOF

echo "=== Шаг 3. Запускаем Telegram-Управление в фоне ==="
pkill -f telegram_controller.py
nohup ./venv/bin/python -u telegram_controller.py > telegram.log 2>&1 &

echo "=== РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО УСПЕШНО ==="
