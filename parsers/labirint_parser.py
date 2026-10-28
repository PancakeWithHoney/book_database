
import re

import requests
from bs4 import BeautifulSoup


def parse_book(url):
    """Получает страницу книги и извлекает её характеристики."""

    headers = {
        "User-Agent": "BookDatabaseStudentProject/1.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print("Ошибка загрузки страницы:", error)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Название и автор
    h1 = soup.find("h1")

    title = None
    author = None

    if h1:
        full_title = h1.get_text(" ", strip=True)

        if " : " in full_title:
            title, author = full_title.rsplit(" : ", 1)
        else:
            title = full_title

    # 2. ISBN
    isbn_tag = soup.find(
        "meta",
        attrs={"itemprop": "isbn"}
    )

    isbn = isbn_tag.get("content") if isbn_tag else None

    # Извлекаем ID книги из URL
    book_id_match = re.search(r"/books/(\d+)/?", url)
    book_id = book_id_match.group(1) if book_id_match else None

    # Извлекаем ссылку на обложку именно этой книги
    image_url = None

    if book_id:
        for img in soup.find_all("img"):
            src = img.get("src", "")

            if f"/books/{book_id}/cover.jpg/" in src:
                image_url = (
                    "https:" + src
                    if src.startswith("//")
                    else src
                )
                break

    # 3. Издательство
    publisher = None

    publisher_block = soup.find(
        attrs={
            "itemprop": "brand",
            "itemtype": "http://schema.org/Thing"
        }
    )

    if publisher_block:
        publisher_tag = publisher_block.find(
            "meta",
            attrs={"itemprop": "name"}
        )

        if publisher_tag:
            publisher = publisher_tag.get("content")

    # Вспомогательная функция для поиска характеристик
    def get_feature_block(label):
        for element in soup.find_all(
            string=lambda text: text and text.strip() == label
        ):
            return element.parent.parent

        return None

    # 4. Год издания
    year = None
    publisher_feature = get_feature_block("Издательство")

    if publisher_feature:
        for span in publisher_feature.find_all("span"):
            text = span.get_text(strip=True)

            if text.isdigit() and len(text) == 4:
                year = int(text)
                break

    # 5. Количество страниц
    pages = None
    pages_block = get_feature_block("Страниц")

    if pages_block:
        first_span = pages_block.find("span")

        if first_span:
            text = first_span.get_text(strip=True)

            if text.isdigit():
                pages = int(text)

    # 6. Краткое описание из метаданных
    description_tag = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    description = (
        description_tag.get("content")
        if description_tag
        else None
    )

    # Проверяем, что страница действительно содержит книгу
    if not title:
        print("Не удалось определить название книги.")
        return None

    # Собираем результаты в один объект
    book = {
        "title": title,
        "author": author,
        "isbn": isbn,
        "publisher": publisher,
        "year": year,
        "pages": pages,
        "description": description,
        "source_url": url,
        "image_url": image_url,
    }

    return book


if __name__ == "__main__":
    test_url = "https://www.labirint.ru/books/250002/"

    book = parse_book(test_url)

    if book:
        print("\n--- Результат парсинга ---")

        for field, value in book.items():
            print(f"{field}: {value}")
