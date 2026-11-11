
import json
import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup


BASE_URL = "https://book24.ru"
CATALOG_URL = "https://book24.ru/catalog/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def collect_book_urls(limit=1000, max_pages=50):
    urls = []
    seen_urls = set()

    for page in range(1, max_pages + 1):

        if page == 1:
            page_url = CATALOG_URL
        else:
            page_url = f"{CATALOG_URL}page-{page}/"

        print(f"\nОбрабатываем страницу {page}: {page_url}")

        response = requests.get(
            page_url,
            headers=HEADERS,
            timeout=20
        )

        if response.status_code in (403, 429):
            print("Сайт ограничил запросы. Останавливаем сбор.")
            break

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        page_count = 0

        for link in soup.find_all("a", href=True):
            href = link["href"]

            if "/product/" not in href:
                continue

            full_url = urljoin(BASE_URL, href)

            if full_url not in seen_urls:
                seen_urls.add(full_url)
                urls.append(full_url)
                page_count += 1

            if len(urls) >= limit:
                break

        print(f"Новых ссылок на странице: {page_count}")
        print(f"Всего уникальных ссылок: {len(urls)}")

        if len(urls) >= limit or page_count == 0:
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

    print(f"\nСохранено ссылок для {site_name}: {len(urls)}")


if __name__ == "__main__":
    print("Начинаем сбор ссылок Book24...")

    try:
        urls = collect_book_urls(limit=1000, max_pages=50)
        save_book_urls("book24", urls)

    except requests.RequestException as error:
        print("Ошибка запроса:", error)
