import requests
from excel import save_to_excel
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}


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
    return {
        "imt_name": data.get("imt_name"),
        "subj_name": data.get("subj_name"),
        "subj_root_name": data.get("subj_root_name"),
        "vendor_code": data.get("vendor_code"),
        "kinds": kinds,
        "description": data.get("description"),
        "photo_count": data.get("photos", {}).get("count")
    }


def fetch_product_info(product_id: int) -> dict | None:
    # Шаг 1: попытка по стандартному бакету
    basket = get_basket(product_id)
    url = build_card_url(product_id, basket)
    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        if response.status_code == 200:
            print(f"✅ Найден по {basket}")
            return extract_fields(response.json())
    except requests.RequestException:
        pass

    # Шаг 2: перебор всех бакетов
    vol = product_id // 100000
    part = product_id // 1000
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
    ids_str = ",".join(str(pid) for pid in product_ids)
    url = (
        "https://card.wb.ru/cards/v4/detail?"
        f"appType=1&curr=rub&dest=-1257786&spp=30&hide_dtype=13"
        f"&ab_testid=no_reranking&lang=ru&nm={ids_str}"
    )

    try:
        response = requests.get(url, headers=HEADERS, timeout=3)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"❌ Ошибка при обращении к detail API: {e}")
        return []

    products = data.get("data", {}).get("products", [])
    result = []

    for item in products:
        result.append({
            "name": item.get("name"),
            "origName": item.get("origName"),
            "basic": item.get("basic"),
            "product": item.get("product"),
        })

    return result



# === Пример запуска ===
def product(product_ids: list[int]):
    card_data = []
    
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

    save_to_excel(card_data, detail_data)
