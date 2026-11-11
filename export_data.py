
import json
import csv
import time

from pathlib import Path

from parsers.labirint_parser import parse_book
from parsers.chitai_gorod_parser import parse_chitai_gorod_book
from parsers.book24_parser import parse_book24


# Соответствие сайтов и их парсеров
PARSERS = {
    "labirint": parse_book,
    "chitai_gorod": parse_chitai_gorod_book,
    "book24": parse_book24
}


# Файл со ссылками
URLS_FILE = Path("book_urls.json")

# Папка для сохранения результатов
OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Загружаем ссылки
with open(URLS_FILE, "r", encoding="utf-8") as file:
    urls_by_site = json.load(file)


# Обрабатываем каждый сайт отдельно
for site, urls in urls_by_site.items():

    parser = PARSERS[site]
    books = []

    print(f"\nОбработка сайта: {site}")

    for index, url in enumerate(urls, start=1):
        try:
            print(f"Обрабатываем книгу {index}/{len(urls)}")

            book = parser(url)

            if book:
                books.append(book)

        except Exception as error:
            print(f"Ошибка при обработке {url}: {error}")

        time.sleep(1)

    # Сохраняем JSON
    json_path = OUTPUT_DIR / f"{site}.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(
            books,
            file,
            ensure_ascii=False,
            indent=4
        )

    # Сохраняем CSV
    csv_path = OUTPUT_DIR / f"{site}.csv"

    if books:
        with open(
            csv_path,
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=books[0].keys()
            )

            writer.writeheader()
            writer.writerows(books)

    print(f"Сохранено книг: {len(books)}")
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")

print("\nОбработка завершена!")
