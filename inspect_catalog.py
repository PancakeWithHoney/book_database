
import requests
from bs4 import BeautifulSoup

url = "https://book24.ru/catalog/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=20)

print("Статус ответа:", response.status_code)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    print("\nСсылки на страницы каталога:")

    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = link["href"]

        if text.isdigit() or "next" in href.lower():
            print("Текст:", text, "| Ссылка:", href)

    print("\nЗаголовок страницы:")
    print(soup.title.get_text(strip=True) if soup.title else "Не найден")

    print("\nПервые ссылки, содержащие /product/:")
    links = soup.find_all("a", href=True)

    count = 0

    for link in links:
        href = link["href"]

        if "/product/" in href:
            if href.startswith("/"):
                href = "https://book24.ru" + href

            print(href)
            count += 1

            if count == 10:
                break

    print("\nВсего найдено в примере:", count)
