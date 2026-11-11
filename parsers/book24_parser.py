import re
import requests
from bs4 import BeautifulSoup

from parsers.data_schema import BOOK_FIELDS


def parse_book24(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    book = {field: None for field in BOOK_FIELDS}

    # Собираем META-теги
    meta_data = {}

    for meta in soup.find_all("meta"):
        name = (
            meta.get("name")
            or meta.get("property")
            or meta.get("itemprop")
        )

        content = meta.get("content")

        if name and content:
            meta_data[name.lower()] = content.strip()

    # Название и автор
    h1 = soup.find("h1")

    if h1:
        heading = h1.get_text(" ", strip=True)

        if ":" in heading:
            author, title = heading.split(":", 1)
            book["author"] = author.strip()
            book["title"] = title.strip()
        else:
            book["title"] = heading

    # ISBN и издательство
    book["isbn"] = meta_data.get("isbn")
    book["publisher"] = meta_data.get("publisher")
    book["price"] = meta_data.get("product:price:amount")

    # Описание и обложка
    book["description"] = (
        meta_data.get("description")
        or meta_data.get("og:description")
    )

    image_url = (
        meta_data.get("image")
        or meta_data.get("og:image")
    )

    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url

    book["image_url"] = image_url

    # Если автора не нашли в H1, пробуем извлечь из заголовка страницы
    if not book["author"]:
        page_title = meta_data.get("og:title", "")
        match = re.search(r"\(([^()]*)\)", page_title)

        if match:
            book["author"] = match.group(1).strip()

    # Ищем год и количество страниц в тексте страницы
    page_text = soup.get_text(" ", strip=True)

    year_match = re.search(
        r"Год издания\s*:\s*(\d{4})",
        page_text,
        re.IGNORECASE
    )

    pages_match = re.search(
        r"Количество страниц\s*:\s*(\d+)",
        page_text,
        re.IGNORECASE
    )

    if year_match:
        book["year"] = int(year_match.group(1))

    if pages_match:
        book["pages"] = int(pages_match.group(1))

    book["source_url"] = url

    # Оставляем только поля из общей схемы
    book = {
        field: book.get(field)
        for field in BOOK_FIELDS
    }

    return book