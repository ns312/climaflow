import os
import sys
import json
import time
import sqlite3
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

# Инициализация базы данных для лидов
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
            status TEXT DEFAULT 'new', -- new, contact_sent, responded, conversion
            last_contacted TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =====================================================================
# Метод 1: Парсинг через Google Places API (Официальный и точный)
# Требует включенного Places API в панели Google Cloud и API-ключа
# =====================================================================
def clean_phone(phone_str):
    if not phone_str:
        return None
    # Оставляем только цифры
    cleaned = "".join(c for c in phone_str if c.isdigit())
    # Если номер начинается с 0, заменяем на 996 (для Кыргызстана)
    if cleaned.startswith("0"):
        cleaned = "996" + cleaned[1:]
    # Если номер начинается с 7, добавляем + для понимания, но храним как цифры
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
            
            # Делаем запрос деталей для получения телефона и сайта
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
            time.sleep(0.5) # Пауза, чтобы не превысить лимиты запросов в секунду
            
        # Проверяем наличие следующей страницы результатов
        token = data.get("next_page_token")
        if token:
            params = {
                "pagetoken": token,
                "key": api_key
            }
            time.sleep(2) # Google требует небольшую задержку перед использованием page_token
        else:
            next_page_token = False
            
    print(f"Поиск завершен. Успешно собрано {leads_count} контактов с телефонами.")

# =====================================================================
# Метод 2: Парсинг через OpenStreetMap (100% Бесплатно, без API ключей)
# Ищет заведения в Бишкеке
# =====================================================================
def fetch_places_osm(category_type):
    # Категории OSM: cafe, restaurant, dentist, clinic, hairdressing, office
    print(f"Запуск поиска OpenStreetMap по категории: '{category_type}' в Бишкеке...")
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Координаты bounding box для Бишкека (min lat, min lon, max lat, max lon)
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
            print(f"Ошибка запроса к Overpass API: {response.status_code} - {response.text[:200]}")
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
            
            # Собираем адрес
            street = tags.get("addr:street") or ""
            house = tags.get("addr:housenumber") or ""
            address = f"{street} {house}".strip() or "Бишкек"
            
            website = tags.get("website") or tags.get("contact:website")
            
            if phone:
                save_lead(name, address, phone, website, category_type)
                leads_count += 1
                
        print(f"Поиск OSM завершен. Найдено {leads_count} контактов с телефонами.")
    except Exception as e:
        print(f"Ошибка OSM парсинга: {e}")

# =====================================================================
# Вспомогательные функции сохранения и экспорта
# =====================================================================
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
        # Номер телефона уже есть в базе, игнорируем дубликат
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
        print("Использование:")
        print("  Парсинг OSM (бесплатно): python places_scraper.py osm <категория> (категории: cafe, restaurant, dentist, clinic)")
        print("  Парсинг Google:           python places_scraper.py google '<запрос>'")
        print("  Экспорт в CSV:            python places_scraper.py export")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    
    if mode == "osm":
        category = sys.argv[2] if len(sys.argv) > 2 else "restaurant"
        fetch_places_osm(category)
    elif mode == "google":
        if len(sys.argv) < 3:
            print("Укажите поисковый запрос. Пример: python places_scraper.py google 'рестораны Бишкек'")
            sys.exit(1)
        query = sys.argv[2]
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            print("Ошибка: Переменная GOOGLE_PLACES_API_KEY не найдена в файле .env!")
            sys.exit(1)
        fetch_places_google(query, api_key)
    elif mode == "export":
        export_to_csv()
    else:
        print("Неизвестный режим. Используйте 'osm', 'google' или 'export'.")
