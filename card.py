import requests
from urllib.parse import urlparse
from getting_id_product import getting_id_product
from bucket import get_basket

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

def try_load_menu_json():
    baskets = [f"static-basket-{i:02d}" for i in range(1, 17)]
    vols = [f"vol{i}" for i in range(3)]
    versions = [f"v{i}" for i in range(3, 6)]
    base_path = "/data/main-menu-ru-ru-{}.json"

    for basket in baskets:
        for vol in vols:
            for version in versions:
                url = f"https://{basket}.wbbasket.ru/{vol}{base_path.format(version)}"
                print('try_load_menu_json',url)
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=5)
                    resp.raise_for_status()
                    return resp.json()
                except requests.RequestException:
                    pass  # Игнорируем ошибки и пытаемся следующий URL
    raise RuntimeError("Не удалось загрузить JSON меню.")

def recursive_find_category(items, target_url):
    for item in items:
        if item.get("url") == target_url:
            return item
        if "childs" in item:
            found = recursive_find_category(item["childs"], target_url)
            if found:
                return found
    return None

def extract_path_from_url(full_url):
    return urlparse(full_url).path

def get_category_info_from_url(wb_url):
    menu = try_load_menu_json()
    target_path = extract_path_from_url(wb_url)
    print(target_path)
    category = recursive_find_category(menu, target_path)

    if not category:
        raise ValueError("Категория не найдена в JSON меню.")
    print(f"Найдена категория: ID = {category['id']}, shard = {category.get('shard', 'нет shard')}")

    # Пытаемся извлечь subject из query
    query = category.get("query", "")
    subject_id = None
    if query:
        parts = query.split("=")
        if len(parts) == 2 and parts[0] == "subject":
            subject_id = int(parts[1])

    return category, subject_id



def build_api_catalog_url(shard, category_id, subject_id=None, page=1, sort="popular", spp=30):
    base_url = f"https://catalog.wb.ru/catalog/{shard}/v4/catalog"
    if subject_id:
        param_part = f"subject={subject_id}"
    else:
        param_part = f"cat={category_id}"
    params = (
        f"?ab_testid=no_reranking&appType=1"
        f"&{param_part}&curr=rub&dest=-1257786"
        f"&hide_dtype=13&lang=ru&page={page}"
        f"&sort={sort}&spp={spp}"
    )
    return base_url + params


if __name__ == "__main__":
    url = "https://www.wildberries.ru/catalog/elektronika/noutbuki-periferiya/monitory#c281627157"
    category, subject_id = get_category_info_from_url(url)
    api_url = build_api_catalog_url(category["shard"], category["id"], subject_id)
    print("Сформированный API URL:", api_url)
    getting_id_product(api_url)
