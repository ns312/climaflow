FILE_PATH = "/Users/MacBookPro/Documents/exported_utf8.csv"

def main():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Total lines in CSV: {len(lines)}")
    print("\n=== All Lines ===")
    for idx, line in enumerate(lines):
        # Печатаем первые 40 символов каждой строки
        print(f"Line {idx}: {line[:120].strip()}")

if __name__ == "__main__":
    main()
