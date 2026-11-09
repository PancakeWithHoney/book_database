import json
import requests
from bs4 import BeautifulSoup

from parsers.data_schema import BOOK_FIELDS


def parse_chitai_gorod_book(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
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

    book = {field: None for field in BOOK_FIELDS}

    # Название
    h1 = soup.find("h1")
    if h1:
        book["title"] = h1.get_text(" ", strip=True)

    # Автор, ISBN и изображение из META
    author_tag = soup.find("meta", property="og:author")
    isbn_tag = soup.find(
        "meta",
        attrs={"property": "og:isbn"}
    )

    if not isbn_tag:
        isbn_tag = soup.find(
            "meta",
            attrs={"name": "og:isbn"}
        )
    image_tag = soup.find("meta", property="og:image")

    if author_tag:
        book["author"] = author_tag.get("content")

    if isbn_tag:
        book["isbn"] = isbn_tag.get("content", "").replace("ISBN ", "").strip()

    if image_tag:
        book["image_url"] = image_tag.get("content")

    # Структурированные данные JSON-LD
    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):
        try:
            data = json.loads(script.get_text(strip=True))

            for item in data.get("@graph", []):
                if item.get("@type") == "Book":

                    description = item.get("description")

                    if description:
                        description_soup = BeautifulSoup(description, "html.parser")
                        book["description"] = description_soup.get_text(" ", strip=True)

                    author = item.get("author")
                    if isinstance(author, dict):
                        book["author"] = author.get("name")
                    elif isinstance(author, str):
                        book["author"] = author

                    book["publisher"] = item.get("publisher")
                    book["year"] = item.get("datePublished")
                    book["pages"] = item.get("numberOfPages")

        except json.JSONDecodeError:
            continue

    book["source_url"] = url

    return book