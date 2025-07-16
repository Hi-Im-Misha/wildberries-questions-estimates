import requests
from product import product

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

def fetch_product_ids(api_url):
    try:
        response = requests.get(api_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        return [product["id"] for product in products if "id" in product]
    except requests.RequestException as e:
        print(f"❌ Ошибка при получении товаров: {e}")
        return []

def build_product_links(product_ids):
    links = []
    for pid in product_ids:
        link = product([pid])
        if link:
            links.append(link)
    return links

def getting_id_product(api_url):
    ids = fetch_product_ids(api_url)
    links = build_product_links(ids)

    print(f"🔗 Найдено {len(links)} ссылок:")
    for link in links:
        print(link)

