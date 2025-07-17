# product.py

import os
import json
import requests
from excel import save_to_excel

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

all_card_data = []
all_detail_data = []


def get_basket(product_id: int) -> str:
    _short_id = product_id // 100000
    baskets = [
        (0, 143, "basket-01"), (144, 287, "basket-02"), (288, 431, "basket-03"),
        (432, 719, "basket-04"), (720, 1007, "basket-05"), (1008, 1061, "basket-06"),
        (1062, 1115, "basket-07"), (1116, 1169, "basket-08"), (1170, 1313, "basket-09"),
        (1314, 1601, "basket-10"), (1602, 1655, "basket-11"), (1656, 1919, "basket-12"),
        (1920, 2045, "basket-13"), (2046, 2189, "basket-14"), (2190, 2405, "basket-15"),
        (2406, 2601, "basket-16"), (2602, 3000, "basket-17"), (3001, 3500, "basket-18"),
        (3501, 4000, "basket-19"), (4001, 4500, "basket-20"), (4501, 5000, "basket-21"),
        (5001, 6000, "basket-22"), (6001, 7000, "basket-23"), (7001, 8000, "basket-24"),
        (8001, 9999, "basket-25")
    ]
    for min_id, max_id, basket in baskets:
        if min_id <= _short_id <= max_id:
            return basket
    return "basket-unknown"


def build_card_url(product_id: int, basket: str) -> str:
    vol = product_id // 100000
    part = product_id // 1000
    return f"https://{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/info/ru/card.json"


def extract_fields(data: dict) -> dict:
    kinds = data.get("kinds")
    if isinstance(kinds, list):
        kinds = ", ".join(kinds)

    photo_count = None
    photos = data.get("photos")
    if isinstance(photos, dict):
        photo_count = photos.get("count")
    elif isinstance(data.get("images"), list):
        photo_count = len(data["images"])

    return {
        "imt_name": data.get("imt_name"),
        "subj_name": data.get("subj_name"),
        "subj_root_name": data.get("subj_root_name"),
        "vendor_code": data.get("vendor_code"),
        "kinds": kinds,
        "description": data.get("description"),
        "photo_count": photo_count
    }


def download_photos(photo_urls: list[str], folder: str):
    os.makedirs(folder, exist_ok=True)
    for url in photo_urls:
        filename = os.path.join(folder, url.split("/")[-1])
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print(f"❌ Ошибка при загрузке {url}: {e}")


def generate_photo_urls(product_id: int, count: int) -> list[str]:
    vol = product_id // 100000
    part = product_id // 1000
    return [
        f"https://basket-0{vol + 1}.wb.ru/vol{vol}/part{part}/{product_id}/images/big/{i}.jpg"
        for i in range(1, count + 1)
    ]


def fetch_product_info(product_id: int) -> dict | None:
    basket = get_basket(product_id)
    url = build_card_url(product_id, basket)
    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        if response.status_code == 200:
            print(f"✅ Найден по {basket}")
            return extract_fields(response.json())
    except requests.RequestException:
        pass

    for i in range(1, 33):
        basket = f"basket-{i:02d}"
        url = build_card_url(product_id, basket)
        try:
            response = requests.get(url, headers=HEADERS, timeout=3)
            if response.status_code == 200:
                print(f"✅ Найден перебором: {basket}")
                return extract_fields(response.json())
        except requests.RequestException:
            continue

    print("❌ Не удалось найти рабочую ссылку для товара.")
    return None


def fetch_detail_card_info(product_ids: list[int]) -> list[dict]:
    url = (
        "https://card.wb.ru/cards/v4/detail?"
        f"appType=1&curr=rub&dest=-1257786&spp=30&hide_dtype=13"
        f"&ab_testid=no_reranking&lang=ru&nm={','.join(map(str, product_ids))}"
    )
    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        response.raise_for_status()
        products = response.json().get("data", {}).get("products", [])
        return [
            {
                "name": p.get("name"),
                "origName": p.get("origName"),
                "basic": p.get("basic"),
                "product": p.get("product")
            }
            for p in products
        ]
    except requests.RequestException as e:
        print(f"❌ Ошибка при обращении к detail API: {e}")
        return []


def save_to_json(card_data: list[dict], detail_data: list[dict], filename: str = "wb_products.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f)
        card_data = existing.get("card_data", []) + card_data
        detail_data = existing.get("detail_data", []) + detail_data

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"card_data": card_data, "detail_data": detail_data}, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON файл обновлен: {filename}")


def product(product_ids: list[int], save: bool = False):
    global all_card_data, all_detail_data

    # Загружаем уже сохранённые данные, если они есть
    if save and os.path.exists("wb_products.json"):
        with open("wb_products.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
        all_card_data = existing.get("card_data", [])
        all_detail_data = existing.get("detail_data", [])

    card_data = []
    print(f"Запущено для {len(product_ids)} товаров")

    for pid in product_ids:
        data = fetch_product_info(pid)
        if data:
            print(f"\n🔎 Информация о товаре {pid}:")
            for key, value in data.items():
                print(f"{key}: {value}")
            card_data.append(data)
        else:
            print(f"\n🚫 Данные не найдены для товара {pid}")

    detail_data = fetch_detail_card_info(product_ids)
    print(f"✅ Найдено {len(card_data)} карточек, {len(detail_data)} детальных описаний")

    all_card_data.extend(card_data)
    all_detail_data.extend(detail_data)

    if save:
        save_to_excel(all_card_data, all_detail_data)
        save_to_json(all_card_data, all_detail_data)

