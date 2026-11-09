import requests
import json
from bs4 import BeautifulSoup

url = "https://book24.ru/product/voskhozhdenie-feniksov-1-6671647/"

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

    print("\n--- Поиск характеристик книги ---")

    page_text = soup.get_text(" ", strip=True)

    keywords = [
        "Год издания",
        "Год выпуска",
        "Количество страниц",
        "Страниц",
        "Объем",
        "Переплет",
    ]

    for keyword in keywords:
        position = page_text.lower().find(keyword.lower())

        if position != -1:
            start = max(0, position - 100)
            end = min(len(page_text), position + 250)

            print(f"\nНайдено '{keyword}':")
            print(page_text[start:end])


    print("\n--- META-теги ---")

    for meta in soup.find_all("meta"):
        name = (
                meta.get("name")
                or meta.get("property")
                or meta.get("itemprop")
        )

        if name and any(word in name.lower() for word in [
            "title", "author", "isbn", "description",
            "publisher", "image", "price"
        ]):
            print(name, ":", meta.get("content"))

    print("\n--- JSON-LD ---")

    for script in soup.find_all(
            "script",
            type="application/ld+json"
    ):
        try:
            data = json.loads(script.get_text(strip=True))

            items = data.get("@graph", [])

            if not items:
                items = data if isinstance(data, list) else [data]

            for item in items:
                print("\nТип:", item.get("@type"))
                print("Название:", item.get("name"))
                print("Автор:", item.get("author"))
                print("ISBN:", item.get("isbn"))
                print("Издательство:", item.get("publisher"))
                print("Год:", item.get("datePublished"))
                print("Страницы:", item.get("numberOfPages"))

        except json.JSONDecodeError:
            print("Не удалось прочитать JSON-LD")

    print("\nЗаголовок страницы:")
    print(
        soup.title.get_text(strip=True)
        if soup.title else "Не найден"
    )

    print("\nЗаголовки H1:")
    for h1 in soup.find_all("h1"):
        print(h1.get_text(" ", strip=True))

    with open(
        "book24_page.html",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(response.text)

    print("\nHTML сохранён в book24_page.html")

except requests.RequestException as error:
    print("Ошибка:", error)