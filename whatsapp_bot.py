import os
import re
import json
import sqlite3
import time
import datetime
import math
import requests
from dotenv import load_dotenv

# Google API imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("[Google API Warning] google-auth or google-api-python-client not installed in this environment.")

# Загружаем переменные окружения из .env
load_dotenv()

# =====================================================================
# НАСТРОЙКИ (считываются из .env файла)
# =====================================================================
GREEN_API_ID_INSTANCE = os.getenv("GREEN_API_ID_INSTANCE")
GREEN_API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN_INSTANCE")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_FILE = "bot_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            chat_id TEXT PRIMARY KEY,
            history TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS masters (
            id TEXT PRIMARY KEY,
            name TEXT,
            calendar_id TEXT,
            tg_chat_id TEXT,
            start_address TEXT,
            rating REAL DEFAULT 5.0,
            average_check REAL DEFAULT 0.0,
            completed_orders_count INTEGER DEFAULT 0,
            commission_percent REAL DEFAULT 50.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_phone TEXT,
            master_id TEXT,
            address TEXT,
            details TEXT,
            date_time_slot TEXT,
            base_price REAL,
            final_price REAL,
            status TEXT DEFAULT 'created',
            photo_arrival TEXT,
            photo_completion TEXT,
            client_rating INTEGER,
            complaint TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Синхронизация мастеров из masters.json
    try:
        import json
        if os.path.exists("masters.json"):
            with open("masters.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for m in data.get("masters", []):
                    cursor.execute("""
                        INSERT INTO masters (id, name, calendar_id, tg_chat_id, start_address, commission_percent)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            name = excluded.name,
                            calendar_id = excluded.calendar_id,
                            tg_chat_id = excluded.tg_chat_id,
                            start_address = excluded.start_address,
                            commission_percent = excluded.commission_percent
                    """, (m["id"], m["name"], m["calendar_id"], m.get("tg_chat_id", ""), m["start_address"], m["commission_percent"]))
            conn.commit()
    except Exception as e:
        print(f"[Init DB Error] Failed to sync masters: {e}")
        
    conn.close()

init_db()

# Загрузка промпта и базы знаний из файла
def load_system_instruction():
    try:
        with open("bot_instructions.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Ты ИИ-продажник компании ClimaFlow в Бишкеке. Продавай чистку и установку кондиционеров."

SYSTEM_PROMPT = load_system_instruction()

# Инструкция для извлечения данных лида
LEAD_EXTRACTION_RULE = """
ОЧЕНЬ ВАЖНО: Когда клиент предоставит 3 обязательных пункта для заказа:
1. Точный адрес объекта в Бишкеке
2. Тип услуги (чистка/заправка/ремонт/диагностика)
3. Желаемую дату и время выезда мастеров (сегодня или завтра)

ВНИМАНИЕ: Спрашивать имя и НОМЕР ТЕЛЕФОНА клиента НЕ нужно! Не трать время на эти вопросы. Номер телефона берется автоматически.

В самый конец своего ответа обязательно добавь технический маркер в таком формате (в одну строчку):
[LEAD_DATA: Клиент | WhatsApp | Адрес | Детали заказа | Дата и время | Цена]

Пример:
[LEAD_DATA: Клиент | WhatsApp | Микрорайон Джал, дом 15, кв 4 | Чистка | Сегодня в 16:00 | 2800 сом]

Этот блок будет скрыт от клиента нашим скриптом, но отправится мне в Telegram. Если каких-то данных не хватает, продолжай задавать вопросы и НЕ выводи этот маркер, пока не соберешь ВСЕ 3 пункта.
"""

FULL_SYSTEM_PROMPT = f"{SYSTEM_PROMPT}\n\n{LEAD_EXTRACTION_RULE}"

# =====================================================================
# Вспомогательные функции для работы с БД
# =====================================================================
def get_chat_history(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT history FROM chat_history WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return []

def save_chat_history(chat_id, history):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    history = history[-20:] # Храним последние 20 сообщений
    cursor.execute("""
        INSERT INTO chat_history (chat_id, history)
        VALUES (?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET history = excluded.history
    """, (chat_id, json.dumps(history)))
    conn.commit()
    conn.close()

# =====================================================================
# Google Calendar и Геокодирование (Интеграция)
# =====================================================================
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"[Calendar Warning] {SERVICE_ACCOUNT_FILE} not found. Running in mock calendar mode.")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"[Calendar Error] Failed to init Calendar Service: {e}")
        return None

def parse_datetime_with_ai(time_str):
    """
    Преобразует русский текст даты/времени в ISO-формат с помощью Gemini
    """
    tz_utc6 = datetime.timezone(datetime.timedelta(hours=6))
    now = datetime.datetime.now(tz_utc6)
    days = {
        0: "понедельник", 1: "вторник", 2: "среда", 3: "четверг",
        4: "пятница", 5: "суббота", 6: "воскресенье"
    }
    weekday = days[now.weekday()]
    context = f"Текущее системное время: {now.strftime('%d.%m.%Y %H:%M')} ({weekday})."
    
    prompt = (
        f"{context}\n"
        f"Преобразуй текст времени: '{time_str}' в точную дату и время начала и окончания работ (продолжительность 2 часа).\n"
        f"Верни ответ строго в формате JSON: \n"
        f"{{\n"
        f"  \"start\": \"YYYY-MM-DDTHH:MM:00+06:00\",\n"
        f"  \"end\": \"YYYY-MM-DDTHH:MM:00+06:00\"\n"
        f"}}\n"
        f"Не пиши никакого другого текста, только чистый JSON."
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            data = json.loads(text)
            return data["start"], data["end"]
    except Exception as e:
        print(f"[Parse AI Error] Failed to parse datetime: {e}")
        
    start = (now + datetime.timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(hours=2)
    return start.strftime("%Y-%m-%dT%H:%M:00+06:00"), end.strftime("%Y-%m-%dT%H:%M:00+06:00")

def check_masters_availability(start_time_iso, end_time_iso):
    """
    Проверяет занятость мастеров через Google Календарь
    """
    service = get_calendar_service()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, calendar_id, start_address, rating, average_check, tg_chat_id FROM masters")
    masters = [
        {
            "id": row[0],
            "name": row[1],
            "calendar_id": row[2],
            "start_address": row[3],
            "rating": row[4],
            "average_check": row[5],
            "tg_chat_id": row[6],
            "is_free": True
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    
    if not service:
        print("[Calendar Mock] Использование базы SQLite для проверки занятости.")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        for m in masters:
            cursor.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE master_id = ? AND date_time_slot = ? AND status NOT IN ('completed', 'cancelled')
            """, (m["id"], start_time_iso))
            if cursor.fetchone()[0] > 0:
                m["is_free"] = False
        conn.close()
        return masters
        
    try:
        items = [{"id": m["calendar_id"]} for m in masters]
        body = {
            "timeMin": start_time_iso,
            "timeMax": end_time_iso,
            "items": items
        }
        freebusy_query = service.freebusy().query(body=body).execute()
        calendars = freebusy_query.get("calendars", {})
        
        for m in masters:
            cal_info = calendars.get(m["calendar_id"], {})
            busy_slots = cal_info.get("busy", [])
            if busy_slots:
                m["is_free"] = False
                print(f"[Calendar] Мастер {m['name']} занят: {busy_slots}")
            else:
                m["is_free"] = True
                print(f"[Calendar] Мастер {m['name']} свободен!")
    except Exception as e:
        print(f"[Calendar API Error] FreeBusy query failed: {e}")
    
    return masters

def geocode_address(address):
    """
    Геокодирует адрес в координаты (широта, долгота) с помощью Nominatim OSM
    """
    query = address
    if "Бишкек" not in query:
        query = "Бишкек, " + query
        
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ClimaFlowBot/1.0 (sydykov.dev@gmail.com)"
    }
    try:
        # Небольшая пауза перед запросом для соблюдения правил OSM
        time.sleep(1)
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon
    except Exception as e:
        print(f"[Geocode Error] Geocoding failed for '{address}': {e}")
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Рассчитывает расстояние в км по формуле гаверсинуса
    """
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_master_last_location(master_id, date_str):
    """
    Определяет предыдущую локацию мастера на указанную дату
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Сначала ищем последний заказ в SQLite на сегодня
    cursor.execute("""
        SELECT address FROM orders 
        WHERE master_id = ? AND date_time_slot LIKE ? AND status IN ('completed', 'arrived', 'en_route')
        ORDER BY date_time_slot DESC LIMIT 1
    """, (master_id, f"{date_str}%"))
    row = cursor.fetchone()
    if row:
        addr = row[0]
        conn.close()
        return addr
        
    # 2. Если заказов в БД на сегодня нет, считываем настройки мастера
    cursor.execute("SELECT start_address, calendar_id FROM masters WHERE id = ?", (master_id,))
    master_info = cursor.fetchone()
    conn.close()
    
    if not master_info:
        return "Бишкек, центр"
        
    start_addr, cal_id = master_info
    
    # 3. Проверяем календарь Google на сегодня
    service = get_calendar_service()
    if service:
        try:
            time_min = f"{date_str}T00:00:00+06:00"
            time_max = f"{date_str}T23:59:59+06:00"
            
            events_result = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            last_location = None
            for event in reversed(events):
                loc = event.get('location')
                if loc:
                    last_location = loc
                    break
            if last_location:
                return last_location
        except Exception as e:
            print(f"[Calendar Error] Failed to get last event location: {e}")
            
    return start_addr

def select_best_master(address, start_time_iso, end_time_iso):
    """
    Выбирает наиболее подходящего свободного мастера на основе рейтинга, чека и расстояния
    """
    masters = check_masters_availability(start_time_iso, end_time_iso)
    free_masters = [m for m in masters if m["is_free"]]
    
    if not free_masters:
        return None
        
    target_coords = geocode_address(address)
    date_str = start_time_iso.split("T")[0]
    
    best_master = None
    best_score = -999999.0
    
    for m in free_masters:
        last_loc = get_master_last_location(m["id"], date_str)
        dist = 5.0
        if target_coords:
            loc_coords = geocode_address(last_loc)
            if loc_coords:
                dist = calculate_distance(target_coords[0], target_coords[1], loc_coords[0], loc_coords[1])
                
        # Формула приоритета: Score = (Рейтинг * 100 + Средний чек) / (Дистанция + 1)
        performance_score = (m["rating"] * 100.0) + m["average_check"]
        score = performance_score / (dist + 1.0)
        
        m["distance"] = dist
        m["score"] = score
        print(f"[Dispatch] Мастер {m['name']}: dist={dist:.2f}км, rating={m['rating']}, check={m['average_check']}, score={score:.2f}")
        
        if score > best_score:
            best_score = score
            best_master = m
            
    return best_master

def create_calendar_event(calendar_id, summary, address, description, start_time, end_time):
    """
    Создает событие в Google Календаре
    """
    service = get_calendar_service()
    if not service:
        print("[Calendar Mock] Событие создано в режиме эмуляции.")
        return True
    try:
        event = {
            'summary': summary,
            'location': address,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Bishkek',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Bishkek',
            },
        }
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"[Calendar] Событие успешно добавлено: {event.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"[Calendar API Error] Failed to create event: {e}")
        return False

# =====================================================================

# =====================================================================
# Взаимодействие с внешними API
# =====================================================================
def send_whatsapp_message(chat_id, text):
    url = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN_INSTANCE}"
    payload = {
        "chatId": chat_id,
        "message": text
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[GreenAPI Error] Failed to send message: {e}")
        return None

def delete_notification(receipt_id):
    url = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/deleteNotification/{GREEN_API_TOKEN_INSTANCE}/{receipt_id}"
    try:
        requests.delete(url, timeout=10)
    except Exception as e:
        print(f"[GreenAPI Error] Failed to delete notification: {e}")

MASTER_STATES = {}

def download_telegram_file(file_id, save_path):
    """
    Скачивает фото из Telegram на диск
    """
    get_file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    try:
        res = requests.get(get_file_url, params={"file_id": file_id}, timeout=10)
        if res.status_code == 200:
            file_path = res.json()["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
            img_data = requests.get(download_url, timeout=20).content
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(img_data)
            return True
    except Exception as e:
        print(f"[Telegram Download Error] {e}")
    return False

def send_telegram_msg(chat_id, text, reply_markup=None):
    """
    Отправляет текстовое сообщение в Telegram
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram Send Error] {e}")

def handle_telegram_update(update):
    """
    Обрабатывает события обратных вызовов кнопок и сообщения от мастеров в Telegram
    """
    if "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        query_id = query["id"]
        data = query["data"]
        
        # Подтверждаем получение клика кнопки
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": query_id})
        
        parts = data.split("_")
        action = parts[0]
        order_id = int(parts[-1])
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT status, master_id, address FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            send_telegram_msg(chat_id, "⚠️ Заказ не найден в базе данных.")
            conn.close()
            return
            
        status, master_id, address = order
        
        # Проверяем, что этот чат принадлежит назначенному мастеру
        cursor.execute("SELECT id, name FROM masters WHERE tg_chat_id = ?", (str(chat_id),))
        master_row = cursor.fetchone()
        if not master_row or master_row[0] != master_id:
            send_telegram_msg(chat_id, "⚠️ Этот заказ назначен другому мастеру.")
            conn.close()
            return
            
        m_name = master_row[1]
        
        if action == "start": # "start_travel_123"
            cursor.execute("UPDATE orders SET status = 'en_route' WHERE id = ?", (order_id,))
            conn.commit()
            markup = {
                "inline_keyboard": [
                    [{"text": "📍 Я на месте", "callback_data": f"arrived_{order_id}"}],
                    [{"text": "❌ Отмена", "callback_data": f"cancel_order_{order_id}"}]
                ]
            }
            send_telegram_msg(chat_id, f"🚀 Выехали на адрес: *{address}*.\nКогда прибудете, нажмите «Я на месте».", reply_markup=markup)
            
            # Уведомляем в менеджерский чат
            send_telegram_msg(TELEGRAM_CHAT_ID, f"🚀 Мастер *{m_name}* выехал на заказ №{order_id} (Адрес: {address})")
            
        elif action == "arrived": # "arrived_123"
            MASTER_STATES[chat_id] = {"state": "waiting_for_arrival_photo", "order_id": order_id}
            send_telegram_msg(chat_id, "📍 Пожалуйста, отправьте ОДНО ФОТО подтверждения, что вы прибыли (например, кондиционер или здание).")
            
        elif action == "complete": # "complete_123"
            MASTER_STATES[chat_id] = {"state": "waiting_for_completion_photo", "order_id": order_id}
            send_telegram_msg(chat_id, "✅ Отлично. Теперь пришлите ОДНО ФОТО завершенных работ.")
            
        elif action == "cancel": # "cancel_order_123"
            cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
            conn.commit()
            send_telegram_msg(chat_id, "❌ Заказ №{} отменен.".format(order_id))
            send_telegram_msg(TELEGRAM_CHAT_ID, f"⚠️ Мастер *{m_name}* отменил заказ №{order_id} (Адрес: {address})!")
            
        conn.close()
        
    elif "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "").strip()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if text.startswith("/start"):
            cursor.execute("SELECT name FROM masters WHERE tg_chat_id = ?", (str(chat_id),))
            row = cursor.fetchone()
            if row:
                send_telegram_msg(chat_id, f"Саламатсызбы, {row[0]}! Вы успешно подключены к боту ClimaFlow. Сюда будут приходить ваши заказы. Отправьте /stats для просмотра отчетов.")
            else:
                send_telegram_msg(chat_id, f"Саламатсызбы! Чтобы привязать ваш аккаунт, отправьте этот ID администратору:\n`{chat_id}`")
            conn.close()
            return
            
        if text == "/stats":
            cursor.execute("SELECT id, name, rating, average_check, completed_orders_count, commission_percent FROM masters WHERE tg_chat_id = ?", (str(chat_id),))
            master = cursor.fetchone()
            if not master:
                send_telegram_msg(chat_id, "⚠️ Вы не зарегистрированы как мастер в нашей базе.")
                conn.close()
                return
                
            m_id, m_name, rating, avg_check, count, comm = master
            cursor.execute("SELECT SUM(final_price) FROM orders WHERE master_id = ? AND status = 'completed'", (m_id,))
            total_sum = cursor.fetchone()[0] or 0.0
            my_share = total_sum * (comm / 100.0)
            
            stats_msg = (
                f"📊 **Ваша статистика (Климат Севера):**\n"
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                f"👤 **Мастер:** {m_name}\n"
                f"⭐ **Рейтинг:** {rating:.1f} / 5.0\n"
                f"✅ **Выполнено заказов:** {count} шт.\n"
                f"💵 **Средний чек:** {avg_check:.0f} сом\n"
                f"💰 **Общая касса:** {total_sum:.0f} сом\n"
                f"📈 **Ваш доход ({comm:.0f}%):** {my_share:.0f} сом\n"
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
            )
            send_telegram_msg(chat_id, stats_msg)
            conn.close()
            return
            
        if chat_id in MASTER_STATES:
            state_data = MASTER_STATES[chat_id]
            state = state_data["state"]
            order_id = state_data["order_id"]
            
            if state == "waiting_for_arrival_photo":
                if "photo" in msg:
                    photo_id = msg["photo"][-1]["file_id"]
                    save_path = f"media/orders/order_{order_id}_arrival.jpg"
                    if download_telegram_file(photo_id, save_path):
                        cursor.execute("UPDATE orders SET status = 'arrived', photo_arrival = ? WHERE id = ?", (save_path, order_id))
                        conn.commit()
                        del MASTER_STATES[chat_id]
                        
                        markup = {
                            "inline_keyboard": [
                                [{"text": "✅ Работы завершены", "callback_data": f"complete_{order_id}"}]
                            ]
                        }
                        send_telegram_msg(chat_id, "✅ Фото прибытия принято. Можете приступать к работе. По завершении нажмите кнопку ниже.", reply_markup=markup)
                        
                        # Сообщаем менеджеру
                        cursor.execute("SELECT name FROM masters WHERE tg_chat_id = ?", (str(chat_id),))
                        m_name = cursor.fetchone()[0]
                        send_telegram_msg(TELEGRAM_CHAT_ID, f"📍 Мастер *{m_name}* прибыл на место выполнения заказа №{order_id}.")
                    else:
                        send_telegram_msg(chat_id, "⚠️ Не удалось сохранить фото. Пожалуйста, отправьте его еще раз.")
                else:
                    send_telegram_msg(chat_id, "⚠️ Пожалуйста, отправьте фотографию (как изображение).")
                    
            elif state == "waiting_for_completion_photo":
                if "photo" in msg:
                    photo_id = msg["photo"][-1]["file_id"]
                    save_path = f"media/orders/order_{order_id}_completion.jpg"
                    if download_telegram_file(photo_id, save_path):
                        cursor.execute("UPDATE orders SET photo_completion = ? WHERE id = ?", (save_path, order_id))
                        conn.commit()
                        MASTER_STATES[chat_id] = {"state": "waiting_for_sum", "order_id": order_id}
                        send_telegram_msg(chat_id, "✅ Фото завершения принято. Теперь введите итоговую сумму заказа (только цифры, например: 2800):")
                    else:
                        send_telegram_msg(chat_id, "⚠️ Не удалось сохранить фото. Пожалуйста, отправьте его еще раз.")
                else:
                    send_telegram_msg(chat_id, "⚠️ Пожалуйста, отправьте фотографию (как изображение).")
                    
            elif state == "waiting_for_sum":
                val = text.strip()
                if val.isdigit():
                    sum_val = float(val)
                    cursor.execute("SELECT master_id, address, details FROM orders WHERE id = ?", (order_id,))
                    m_id, addr, details = cursor.fetchone()
                    
                    cursor.execute("""
                        UPDATE orders SET status = 'completed', final_price = ? WHERE id = ?
                    """, (sum_val, order_id))
                    
                    cursor.execute("SELECT COUNT(*), AVG(final_price) FROM orders WHERE master_id = ? AND status = 'completed'", (m_id,))
                    o_count, o_avg = cursor.fetchone()
                    
                    cursor.execute("""
                        UPDATE masters SET completed_orders_count = ?, average_check = ? WHERE id = ?
                    """, (o_count, o_avg, m_id))
                    
                    conn.commit()
                    del MASTER_STATES[chat_id]
                    
                    send_telegram_msg(chat_id, f"🎉 Заказ №{order_id} успешно закрыт на сумму {sum_val:.0f} сом. Отличная работа!")
                    
                    cursor.execute("SELECT name FROM masters WHERE id = ?", (m_id,))
                    m_name = cursor.fetchone()[0]
                    send_telegram_msg(TELEGRAM_CHAT_ID, 
                                      f"✅ **ЗАКАЗ ВЫПОЛНЕН!**\n"
                                      f"👤 **Мастер:** {m_name}\n"
                                      f"📍 **Адрес:** {addr}\n"
                                      f"🛠️ **Услуга:** {details}\n"
                                      f"💵 **Сумма:** {sum_val:.0f} сом\n"
                                      f"📈 Статистика мастера обновлена.")
                else:
                    send_telegram_msg(chat_id, "⚠️ Пожалуйста, введите сумму только цифрами (например: 2800).")
                    
        conn.close()

def start_telegram_polling():
    """
    Фоновый цикл опроса обновлений Telegram (Long Polling)
    """
    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    print("[Telegram Polling] Запуск опроса...")
    while True:
        try:
            params = {"offset": offset, "timeout": 20}
            response = requests.get(url, params=params, timeout=25)
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    handle_telegram_update(update)
        except Exception as e:
            print(f"[Telegram Polling Error] {e}")
            time.sleep(5)

def check_upcoming_orders():
    """
    Проверяет заказы, начинающиеся через 30 минут, и присылает напоминания
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    tz_utc6 = datetime.timezone(datetime.timedelta(hours=6))
    now = datetime.datetime.now(tz_utc6)
    t_start = (now + datetime.timedelta(minutes=25)).strftime("%Y-%m-%dT%H:%M:00+06:00")
    t_end = (now + datetime.timedelta(minutes=35)).strftime("%Y-%m-%dT%H:%M:00+06:00")
    
    cursor.execute("""
        SELECT orders.id, orders.address, orders.details, orders.date_time_slot, masters.name, masters.tg_chat_id 
        FROM orders 
        JOIN masters ON orders.master_id = masters.id
        WHERE orders.status = 'created' AND orders.date_time_slot BETWEEN ? AND ?
    """, (t_start, t_end))
    
    for row in cursor.fetchall():
        o_id, address, details, slot, m_name, m_tg = row
        cursor.execute("UPDATE orders SET status = 'reminder_sent' WHERE id = ?", (o_id,))
        conn.commit()
        
        print(f"[Reminder] Отправка 30-мин напоминания по заказу №{o_id} мастеру {m_name}")
        
        if m_tg:
            m_message = (
                f"⏰ **НАПОМИНАНИЕ О ЗАКАЗЕ!**\n"
                f"Через 30 минут у вас заказ по адресу:\n"
                f"📍 *{address}*\n"
                f"🛠️ *Детали:* {details}\n"
                f"📅 *Слот:* {slot}\n\n"
                f"Пожалуйста, подтвердите выезд на заказ."
            )
            markup = {
                "inline_keyboard": [
                    [{"text": "🚀 Я выехал", "callback_data": f"start_travel_{o_id}"}],
                    [{"text": "❌ Отмена", "callback_data": f"cancel_order_{o_id}"}]
                ]
            }
            send_telegram_msg(m_tg, m_message, reply_markup=markup)
            
    conn.close()

def send_telegram_notification(lead_info, phone_number):
    """
    Обрабатывает квалифицированного лида, подбирает мастера и создает событие
    """
    parts = [p.strip() for p in lead_info.split("|")]
    name = parts[0] if len(parts) > 0 else "Не указано"
    jid_phone = phone_number.replace("@c.us", "").strip()
    extracted_phone = parts[1].replace("+", "").replace("-", "").replace(" ", "").strip() if len(parts) > 1 else ""
    
    is_numeric = extracted_phone.isdigit()
    if not is_numeric or not extracted_phone or "502985896" in extracted_phone or extracted_phone == jid_phone:
        phone = jid_phone
    else:
        phone = f"{jid_phone} (доп: {extracted_phone})"
        
    address = parts[2] if len(parts) > 2 else "Не указано"
    details = parts[3] if len(parts) > 3 else "Не указано"
    datetime_slot = parts[4] if len(parts) > 4 else "Не указано"
    price_str = parts[5] if len(parts) > 5 else "0"
    
    base_price = 0.0
    price_digits = "".join(c for c in price_str if c.isdigit())
    if price_digits:
        base_price = float(price_digits)
        
    print(f"[Dispatch] Парсинг времени: '{datetime_slot}' с помощью ИИ...")
    start_iso, end_iso = parse_datetime_with_ai(datetime_slot)
    print(f"[Dispatch] Распознанный слот: {start_iso} - {end_iso}")
    
    master = select_best_master(address, start_iso, end_iso)
    
    if master:
        m_id = master["id"]
        m_name = master["name"]
        m_cal = master["calendar_id"]
        m_tg = master["tg_chat_id"]
        
        # Создаем событие в календаре
        summary = f"Заказ ClimaFlow: {details}"
        desc = f"Клиент: {name}\nТелефон: +{phone.replace('+', '').strip()}\nДетали: {details}\nЦена: {price_str}"
        create_calendar_event(m_cal, summary, address, desc, start_iso, end_iso)
        
        # Записываем в локальную БД
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (client_phone, master_id, address, details, date_time_slot, base_price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'created')
        """, (phone, m_id, address, details, start_iso, base_price))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Отправляем оповещение в общую группу менеджеров
        tg_message = (
            "🔔 **НОВЫЙ ЗАКАЗ НАЗНАЧЕН!**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"👤 **Имя:** {name}\n"
            f"📞 **Телефон:** +{phone.replace('+', '').strip()}\n"
            f"📍 **Адрес:** {address}\n"
            f"🛠️ **Заказ:** {details}\n"
            f"💰 **Цена:** {price_str}\n"
            f"📅 **Время выезда:** {datetime_slot}\n"
            f"👷‍♂️ **Назначен мастер:** {m_name}\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"💬 Чат в WhatsApp: https://wa.me/{phone.replace('+', '').strip()}"
        )
        send_telegram_msg(TELEGRAM_CHAT_ID, tg_message)
        
        # Отправляем личное оповещение назначенному мастеру
        if m_tg:
            m_message = (
                "🔔 **ВАМ НАЗНАЧЕН НОВЫЙ ЗАКАЗ!**\n"
                "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                f"📍 **Адрес:** {address}\n"
                f"🛠️ **Заказ:** {details}\n"
                f"💰 **Цена:** {price_str}\n"
                f"📅 **Время:** {datetime_slot}\n"
                "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                "Пожалуйста, подтвердите выезд на заказ:"
            )
            markup = {
                "inline_keyboard": [
                    [{"text": "🚀 Я выехал", "callback_data": f"start_travel_{order_id}"}],
                    [{"text": "❌ Отмена", "callback_data": f"cancel_order_{order_id}"}]
                ]
            }
            send_telegram_msg(m_tg, m_message, reply_markup=markup)
        return m_name
    else:
        # Свободных мастеров нет
        tg_message = (
            "⚠️ **НЕТ СВОБОДНЫХ МАСТЕРОВ НА ЭТО ВРЕМЯ!**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"👤 **Имя:** {name}\n"
            f"📞 **Телефон:** +{phone.replace('+', '').strip()}\n"
            f"📍 **Адрес:** {address}\n"
            f"🛠️ **Заказ:** {details}\n"
            f"💰 **Цена:** {price_str}\n"
            f"📅 **Слот:** {datetime_slot}\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "Заказ нужно распределить вручную."
        )
        send_telegram_msg(TELEGRAM_CHAT_ID, tg_message)
        return None

# =====================================================================
# Логика Gemini AI
# =====================================================================
def get_masters_schedule_summary(now):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, calendar_id FROM masters")
    masters = [{"id": r[0], "name": r[1], "calendar_id": r[2]} for r in cursor.fetchall()]
    conn.close()
    
    if not masters:
        return "Нет доступных мастеров."
        
    today_str = now.strftime("%Y-%m-%d")
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    slots = [
        {"label": "сегодня с 08:00 до 10:00", "start": f"{today_str}T08:00:00+06:00", "end": f"{today_str}T10:00:00+06:00", "day": "today"},
        {"label": "сегодня с 10:00 до 12:00", "start": f"{today_str}T10:00:00+06:00", "end": f"{today_str}T12:00:00+06:00", "day": "today"},
        {"label": "сегодня с 12:00 до 14:00", "start": f"{today_str}T12:00:00+06:00", "end": f"{today_str}T14:00:00+06:00", "day": "today"},
        {"label": "сегодня с 14:00 до 16:00", "start": f"{today_str}T14:00:00+06:00", "end": f"{today_str}T16:00:00+06:00", "day": "today"},
        {"label": "сегодня с 16:00 до 18:00", "start": f"{today_str}T16:00:00+06:00", "end": f"{today_str}T18:00:00+06:00", "day": "today"},
        
        {"label": "завтра с 08:00 до 10:00", "start": f"{tomorrow_str}T08:00:00+06:00", "end": f"{tomorrow_str}T10:00:00+06:00", "day": "tomorrow"},
        {"label": "завтра с 10:00 до 12:00", "start": f"{tomorrow_str}T10:00:00+06:00", "end": f"{tomorrow_str}T12:00:00+06:00", "day": "tomorrow"},
        {"label": "завтра с 12:00 до 14:00", "start": f"{tomorrow_str}T12:00:00+06:00", "end": f"{tomorrow_str}T14:00:00+06:00", "day": "tomorrow"},
        {"label": "завтра с 14:00 до 16:00", "start": f"{tomorrow_str}T14:00:00+06:00", "end": f"{tomorrow_str}T16:00:00+06:00", "day": "tomorrow"},
        {"label": "завтра с 16:00 до 18:00", "start": f"{tomorrow_str}T16:00:00+06:00", "end": f"{tomorrow_str}T18:00:00+06:00", "day": "tomorrow"},
    ]
    
    service = get_calendar_service()
    busy_data = {}
    if service:
        try:
            body = {
                "timeMin": f"{today_str}T08:00:00+06:00",
                "timeMax": f"{tomorrow_str}T18:00:00+06:00",
                "items": [{"id": m["calendar_id"]} for m in masters]
            }
            res = service.freebusy().query(body=body).execute()
            busy_data = res.get("calendars", {})
        except Exception as e:
            print(f"[Calendar Summary Error] FreeBusy failed: {e}")
            service = None
            
    summary_lines = []
    
    def overlaps(s1, e1, s2, e2):
        return max(s1, s2) < min(e1, e2)
        
    for slot in slots:
        slot_start = datetime.datetime.fromisoformat(slot["start"])
        slot_end = datetime.datetime.fromisoformat(slot["end"])
        
        if slot["day"] == "today" and slot_start < now + datetime.timedelta(hours=1):
            continue
            
        free_masters = []
        for m in masters:
            is_free = True
            if service:
                cal_info = busy_data.get(m["calendar_id"], {})
                busy_slots = cal_info.get("busy", [])
                for b in busy_slots:
                    b_start = datetime.datetime.fromisoformat(b["start"])
                    b_end = datetime.datetime.fromisoformat(b["end"])
                    if overlaps(slot_start, slot_end, b_start, b_end):
                        is_free = False
                        break
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM orders 
                    WHERE master_id = ? AND date_time_slot = ? AND status NOT IN ('completed', 'cancelled')
                """, (m["id"], slot["start"]))
                if cursor.fetchone()[0] > 0:
                    is_free = False
                conn.close()
                
            if is_free:
                free_masters.append(m["name"])
                
        if free_masters:
            summary_lines.append(f"- {slot['label']}: СВОБОДНО (доступные мастера: {', '.join(free_masters)})")
        else:
            summary_lines.append(f"- {slot['label']}: ВСЕ ЗАНЯТЫ")
            
    return "\n".join(summary_lines)

def get_ai_response(chat_id, user_message):
    history = get_chat_history(chat_id)
    
    # Проверяем, была ли уже оформлена заявка в этой сессии (есть маркер LEAD_DATA в истории от бота)
    has_lead = any("[LEAD_DATA:" in msg["text"] for msg in history if msg["sender"] == "bot")
    
    contents = []
    for msg in history:
        contents.append({
            "role": "user" if msg["sender"] == "user" else "model",
            "parts": [{"text": msg["text"]}]
        })
        
    # Формируем сообщение пользователя. Если лид уже был оформлен, добавляем скрытый системный маркер-подсказку
    current_text = user_message
    if has_lead:
        current_text = (
            f"{user_message}\n\n"
            f"[СИСТЕМНОЕ УВЕДОМЛЕНИЕ ДЛЯ МОДЕЛИ: Заявка от этого клиента уже была успешно создана и передана мастерам ранее. "
            f"Не квалифицируй клиента заново! Не задавай вопросов про адрес, время или тип услуги. "
            f"Ответь вежливо как менеджер поддержки: подтверди, что ты сейчас связываешься/уточняешь у мастера, где он находится, "
            f"и мастер (или ты) перезвонит/напишет ему в ближайшее время (обычно в течение 1-2 минут). "
            f"Ответь коротко, в вежливом и человечном тоне.]"
        )
        
    contents.append({"role": "user", "parts": [{"text": current_text}]})
    
    import datetime
    tz_utc6 = datetime.timezone(datetime.timedelta(hours=6))
    now = datetime.datetime.now(tz_utc6)
    days = {
        0: "понедельник", 1: "вторник", 2: "среда", 3: "четверг",
        4: "пятница", 5: "суббота", 6: "воскресенье"
    }
    weekday = days[now.weekday()]
    
    # Считываем реальную занятость мастеров из календаря
    schedule_summary = get_masters_schedule_summary(now)
    print(f"[DEBUG Schedule Summary]\n{schedule_summary}")
    
    time_info = (
        f"\n\nТекущее время сервера (Бишкек): {now.strftime('%H:%M')}, дата: {now.strftime('%d.%m.%Y')} ({weekday}).\n"
        f"Текущая занятость и свободные слоты мастеров на сегодня и завтра:\n"
        f"{schedule_summary}\n\n"
        f"КРИТИЧЕСКОЕ ПРАВИЛО ВРЕМЕНИ:\n"
        f"1. Если ты предлагаешь запись на СЕГОДНЯ, всегда предлагай время с запасом минимум в 1-2 часа от текущего времени (например, если сейчас 08:30, ты можешь предлагать время начиная с 10:00, 11:00 или 12:00). Но ни в коем случае не предлагай время, которое наступит менее чем через час.\n"
        f"2. Если текущее время на сервере уже позже 18:00, НЕ предлагай выезд на сегодня — предлагай строго на завтра.\n"
        f"3. Если на какой-то слот все мастера заняты (написано 'ВСЕ ЗАНЯТЫ'), ты НЕ имеешь права предлагать этот слот или соглашаться на него! Выбирай только те слоты, где есть свободные мастера. Если на сегодня все слоты заняты ('ВСЕ ЗАНЯТЫ'), предлагай запись строго на завтра!"
    )
    
    dynamic_system_prompt = FULL_SYSTEM_PROMPT + time_info
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": dynamic_system_prompt}]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            
            history.append({"sender": "user", "text": user_message})
            history.append({"sender": "bot", "text": ai_text})
            save_chat_history(chat_id, history)
            
            return ai_text
        else:
            print(f"[Gemini Error] Status {response.status_code}: {response.text}")
            return "Извините, небольшие технические неполадки. Напишите нам чуть позже или наберите напрямую."
    except Exception as e:
        print(f"[Gemini Error] Generation failed: {e}")
        return "Извините, небольшие технические неполадки. Напишите нам чуть позже или наберите напрямую."

# =====================================================================
# Основной цикл длинных опросов (Polling)
# =====================================================================
def start_bot():
    print("==================================================")
    print("Бот ClimaFlow успешно запущен в режиме опросов!")
    print("Скрипт проверяет новые сообщения каждые 2 секунды...")
    print("Для остановки нажмите Ctrl + C")
    print("==================================================")
    
    # Запуск Telegram Polling в фоновом потоке
    import threading
    t_tg = threading.Thread(target=start_telegram_polling, daemon=True)
    t_tg.start()
    
    def run_reminder_loop():
        print("[Reminder Loop] Запуск цикла напоминаний...")
        while True:
            try:
                check_upcoming_orders()
            except Exception as e:
                print(f"[Reminder Loop Error] {e}")
            time.sleep(60)
            
    t_rem = threading.Thread(target=run_reminder_loop, daemon=True)
    t_rem.start()
    
    url = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/receiveNotification/{GREEN_API_TOKEN_INSTANCE}"
    
    while True:
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if data:
                    receipt_id = data.get("receiptId")
                    body = data.get("body", {})
                    type_webhook = body.get("typeWebhook")
                    
                    # Обрабатываем только входящие текстовые сообщения
                    if type_webhook == "incomingMessageReceived":
                        message_data = body.get("messageData", {})
                        type_msg = message_data.get("typeMessage")
                        
                        if type_msg == "textMessage":
                            chat_id = body["senderData"]["chatId"]
                            sender = body["senderData"].get("sender")
                            
                            # Проверяем, что сообщение не от самого себя
                            user_text = message_data["textMessageData"]["textMessage"]
                            print(f"\n[Получено сообщение] От: {chat_id}. Текст: {user_text}")
                            
                            # Генерируем ответ
                            ai_response = get_ai_response(chat_id, user_text)
                            
                            # Проверка маркера лида
                            lead_match = re.search(r"\[LEAD_DATA:\s*(.*?)\]", ai_response)
                            if lead_match:
                                lead_info = lead_match.group(1)
                                master_name = send_telegram_notification(lead_info, chat_id)
                                ai_response = re.sub(r"\[LEAD_DATA:\s*(.*?)\]", "", ai_response).strip()
                                
                                is_kyrgyz = any(word in ai_response.lower() for word in ["саламатсызбы", "рахмат", "жакшы", "болот"])
                                if master_name:
                                    if is_kyrgyz:
                                        ai_response += f"\n\nЗаявка кабыл алынды! Сизге дайындалган мастер: {master_name}. Ал сиз менен 1-2 мүнөттүн ичинде байланышат."
                                    else:
                                        ai_response += f"\n\nЗаявка успешно принята! Вашим мастером назначен: {master_name}. Он свяжется с вами в течение 1-2 минут для подтверждения."
                                else:
                                    if is_kyrgyz:
                                        ai_response += f"\n\nЗаявка кабыл алынды! Менеджер сиз менен жакынкы убакта байланышат."
                                    else:
                                        ai_response += f"\n\nЗаявка принята в обработку! Менеджер свяжется с вами в ближайшее время для подтверждения деталей."
                            
                            # Отправка ответа в WhatsApp
                            send_whatsapp_message(chat_id, ai_response)
                            print(f"[Отправлен ответ]: {ai_response}")
                    
                    # Обязательно удаляем уведомление, чтобы оно не присылалось повторно
                    delete_notification(receipt_id)
            
        except requests.exceptions.Timeout:
            # Таймаут - это нормально, просто проверяем заново
            continue
        except KeyboardInterrupt:
            print("\nБот остановлен пользователем.")
            break
        except Exception as e:
            import traceback
            print(f"[Error in loop]: {e}")
            traceback.print_exc()
            time.sleep(5)
            
        time.sleep(2)

if __name__ == "__main__":
    start_bot()
