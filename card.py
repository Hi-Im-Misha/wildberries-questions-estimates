import requests
from urllib.parse import urlparse
from getting_id_product import start
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
                try:
                    response = requests.get(url, headers=HEADERS, timeout=5)
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException:
                    continue
    raise RuntimeError("Не удалось загрузить JSON.")

def find_category(menu, target_url):
    def recursive_search(items):
        for item in items:
            if item.get("url") == target_url:
                return item
            if "childs" in item:
                found = recursive_search(item["childs"])
                if found:
                    return found
        return None
    return recursive_search(menu)

def extract_path_from_url(full_url):
    parsed = urlparse(full_url)
    return parsed.path

def get_category_info_from_url(wb_url):
    menu = try_load_menu_json()
    target_path = extract_path_from_url(wb_url)
    category = find_category(menu, target_path)

    if not category:
        raise ValueError("Категория не найдена в JSON.")
    
    print(f"ID: {category['id']}")
    return category

def build_api_catalog_url(shard, cat_id, page=1, sort="popular", spp=30):
    base_url = f"https://catalog.wb.ru/catalog/{shard}/v4/catalog"
    params = (
        f"?ab_testid=no_reranking&appType=1"
        f"&cat={cat_id}&curr=rub&dest=-1257786"
        f"&hide_dtype=13&lang=ru&page={page}"
        f"&sort={sort}&spp={spp}"
    )
    return base_url + params

if __name__ == "__main__":
    url = "https://www.wildberries.ru/catalog/zhenshchinam/odezhda/bryuki-i-shorty"
    category = get_category_info_from_url(url)
    api_url = build_api_catalog_url(category["shard"], category["id"])
    print(api_url)
    start(api_url)
