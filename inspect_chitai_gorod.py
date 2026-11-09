import requests
from bs4 import BeautifulSoup
import json

url = "https://www.chitai-gorod.ru/product/nablyudatelnica-2894005"

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    print("Статус ответа:", response.status_code)
    print("Размер HTML:", len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")

    print("\n--- META-теги ---")

    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property") or meta.get("itemprop")

        if name and any(word in name.lower() for word in [
            "title", "author", "isbn", "description",
            "publisher", "image", "price"
        ]):
            print(name, ":", meta.get("content"))

    print("\n--- Структурированные данные о книге ---")

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.get_text(strip=True))

            for item in data.get("@graph", []):
                if item.get("@type") == "Book":
                    print("Название:", item.get("name"))
                    print("Автор:", item.get("author"))
                    print("ISBN:", item.get("isbn"))
                    print("Издательство:", item.get("publisher"))
                    print("Год:", item.get("datePublished"))
                    print("Страницы:", item.get("numberOfPages"))
                    print("Описание:", item.get("description"))

        except json.JSONDecodeError as error:
            print("Ошибка чтения JSON-LD:", error)

    print("\n--- Элементы с itemprop ---")

    for element in soup.find_all(attrs={"itemprop": True}):
        print(
            element.get("itemprop"),
            ":",
            element.get("content") or element.get_text(" ", strip=True)[:200]
        )

    print("Заголовок страницы:")
    print(soup.title.get_text(strip=True) if soup.title else "Не найден")

    print("\nЗаголовки H1:")
    for h1 in soup.find_all("h1"):
        print(h1.get_text(" ", strip=True))

    with open("chitai_gorod_page.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    print("\nHTML сохранён в chitai_gorod_page.html")

except requests.RequestException as error:
    print("Ошибка:", error)