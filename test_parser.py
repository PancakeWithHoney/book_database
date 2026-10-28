from parsers.labirint_parser import parse_book

url = "https://www.labirint.ru/books/1031358/"

book = parse_book(url)

if book:
    print("\n--- Данные книги ---")

    for field, value in book.items():
        print(f"{field}: {value}")
else:
    print("Не удалось получить данные книги.")