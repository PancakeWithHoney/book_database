from parsers.chitai_gorod_parser import parse_chitai_gorod_book

url = "https://www.chitai-gorod.ru/product/my-spravilis-paren-memuary-3161461"

book = parse_chitai_gorod_book(url)

if book:
    print("\n--- Данные книги ---")

    for field, value in book.items():
        print(f"{field}: {value}")