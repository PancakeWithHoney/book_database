
import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://book24.ru"
CATALOG_URL = "https://book24.ru/catalog/"


def collect_book_urls(limit=20):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        CATALOG_URL,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    urls = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/product/" in href:
            full_url = urljoin(BASE_URL, href)

            if full_url not in urls:
                urls.append(full_url)

        if len(urls) >= limit:
            break

    return urls


def save_book_urls(site_name, urls):
    file_path = Path("book_urls.json")

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            all_urls = json.load(file)
    else:
        all_urls = {}

    all_urls[site_name] = list(dict.fromkeys(urls))

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            all_urls,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Сохранено ссылок для {site_name}: {len(all_urls[site_name])}")


if __name__ == "__main__":
    print("Собираем ссылки Book24...")

    try:
        urls = collect_book_urls(limit=20)

        for url in urls:
            print(url)

        save_book_urls("book24", urls)

    except requests.RequestException as error:
        print("Ошибка запроса:", error)
