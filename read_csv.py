import sys

FILE_PATH = "/Users/MacBookPro/Documents/Muslim Elektro+Текущее представление+2026-07-10.csv"

def main():
    try:
        # Пытаемся открыть в utf-16-le
        with open(FILE_PATH, "r", encoding="utf-16") as f:
            content = f.read()
            
        print("=== FILE CONTENT (First 1000 chars) ===")
        print(content[:1500])
        
        # Запишем в UTF-8 для удобства чтения другими инструментами
        utf8_path = "/Users/MacBookPro/Documents/exported_utf8.csv"
        with open(utf8_path, "w", encoding="utf-8") as f_out:
            f_out.write(content)
        print(f"\nФайл успешно сконвертирован в UTF-8 и сохранен как: {utf8_path}")
        
    except Exception as e:
        print(f"Ошибка чтения: {e}")

if __name__ == "__main__":
    main()
