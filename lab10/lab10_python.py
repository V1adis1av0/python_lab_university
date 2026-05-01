from pathlib import Path
import shutil
import hashlib
import time

# Путь к исходной папке
SOURCE_DIR = Path(r"C:\Users\testpc\Desktop\test_dir")

# Словарь категорий и соответствующих расширений
CATEGORIES = {
    "docs": [".doc", ".docx", ".txt", ".xls", ".xlsx"],
    "pdf": [".pdf"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
}

# Сбор статистики выполнения
stats = {
    "total_files": 0,
    "moved": 0,
    "skipped": 0,
    "duplicates_removed": 0,
    "by_category": {
        "docs": 0,
        "pdf": 0,
        "images": 0,
        "others": 0
    }
}

# Вывод логов в консоль
def log(message):
    print(f"[LOG] {message}")

# Определение категории файла по расширению
def get_category(file: Path):
    ext = file.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "others"

# ГЕНЕРАЦИЯ УНИКАЛЬНОГО ИМЕНИ ПРИ КОНФИЛИКТЕ
def get_unique_path(dest: Path):
    counter = 1
    new_dest = dest

    while new_dest.exists():
        new_dest = dest.with_stem(f"{dest.stem} ({counter})")
        counter += 1

    return new_dest

# Вычисление хеша файла (для поиска дубликатов)
def file_hash(path):
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Основная функция обработки файлов
def organize_files():

    # Проверка существования папки
    if not SOURCE_DIR.exists():
        print("Ошибка: папка не существует")
        return

    start_time = time.time()
    seen_hashes = {}

    # Создание подпапок
    for category in list(CATEGORIES.keys()) + ["others"]:
        (SOURCE_DIR / category).mkdir(exist_ok=True)

    # Перебор файлов 
    for file in SOURCE_DIR.iterdir():
        if file.is_file():
            stats["total_files"] += 1

            # Проверка на дубликаты 
            try:
                h = file_hash(file)
                if h in seen_hashes:
                    log(f"Удалён дубликат: {file.name}")
                    file.unlink()
                    stats["duplicates_removed"] += 1
                    continue
                else:
                    seen_hashes[h] = file
            except Exception as e:
                log(f"Ошибка хеша {file.name}: {e}")
                stats["skipped"] += 1
                continue

            # Определение категории
            category = get_category(file)
            stats["by_category"][category] += 1

            dest_path = SOURCE_DIR / category / file.name
            dest_path = get_unique_path(dest_path)

            # Перемещение файла
            try:
                shutil.move(str(file), str(dest_path))
                log(f"{file.name} → {category}/")
                stats["moved"] += 1
            except Exception as e:
                log(f"Ошибка перемещения {file.name}: {e}")
                stats["skipped"] += 1

    end_time = time.time()

    # Обновление статистики 
    print("\n=== СТАТИСТИКА ===")
    print(f"Всего файлов: {stats['total_files']}")
    print(f"Перемещено: {stats['moved']}")
    print(f"Удалено дубликатов: {stats['duplicates_removed']}")
    print(f"Пропущено: {stats['skipped']}\n")

    print("По категориям:")
    for cat, count in stats["by_category"].items():
        print(f"  {cat}: {count}")

    print(f"\nВремя выполнения: {end_time - start_time:.2f} сек")

# Точка входа в программу
if __name__ == "__main__":
    organize_files()
