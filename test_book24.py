from parsers.book24_parser import parse_book24

url = "https://book24.ru/product/voskhozhdenie-feniksov-1-6671647/"

book = parse_book24(url)

if book:
    for field, value in book.items():
        print(f"{field}: {value}")