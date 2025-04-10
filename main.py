import requests

def get_basket(product_id):
    _short_id = product_id // 100000
    baskets = [
        (0, 143, "basket-01"), (144, 287, "basket-02"), (288, 431, "basket-03"),
        (432, 719, "basket-04"), (720, 1007, "basket-05"), (1008, 1061, "basket-06"),
        (1062, 1115, "basket-07"), (1116, 1169, "basket-08"), (1170, 1313, "basket-09"),
        (1314, 1601, "basket-10"), (1602, 1655, "basket-11"), (1656, 1919, "basket-12"),
        (1920, 2045, "basket-13"), (2046, 2189, "basket-14"), (2190, 2405, "basket-15"),
        (2406, 2601, "basket-16")
    ]
    
    for min_id, max_id, basket in baskets:
        if min_id <= _short_id <= max_id:
            return basket
    return "basket-17"

def generate_api_url(wildberries_url):
    try:
        product_id = int(wildberries_url.split('/')[-2])
    except (ValueError, IndexError):
        raise ValueError("Неверный формат ссылки. Убедитесь, что URL содержит артикул.")

    basket = get_basket(product_id)
    vol_number = product_id // 100000
    part_number = product_id // 1000

    return f'https://{basket}.wbbasket.ru/vol{vol_number}/part{part_number}/{product_id}/info/ru/card.json'

def fetch_product_data(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных о товаре: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        return data.get('imt_id')
    else:
        print(f"Ошибка запроса: {response.status_code}")
        return None


def parse_feedbacks(feedbacks_url, filename="feedbacks.txt"):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(feedbacks_url, headers=headers)
    try:
        response.raise_for_status()
        feedbacks_data = response.json() 
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса отзывов: {e}")
        return

    if not feedbacks_data or "feedbacks" not in feedbacks_data:
        print("Нет отзывов.")
        return

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Всего Отзывов: {len(feedbacks_url)}\n\n")
        for feedback in feedbacks_data["feedbacks"]:
            user_id = feedback.get("globalUserId", "Нет данных")
            country = feedback.get("wbUserDetails", {}).get("country", "Нет данных")
            name = feedback.get("wbUserDetails", {}).get("name", "Нет данных")
            product_valuation = feedback.get("productValuation", "Нет данных")
            pros = feedback.get("pros", "Нет данных")
            cons = feedback.get("cons", "Нет данных")
            created_date = feedback.get("createdDate", "Нет данных")
            answer = feedback.get("answer")
            answer_text = answer["text"].strip() if answer else "Нет данных"

            file.write(f"ID пользователя: {user_id}\n")
            file.write(f"Страна: {country}\n")
            file.write(f"Имя: {name}\n")
            file.write(f"Оценка товара: {product_valuation}\n")
            file.write(f"Плюсы: {pros}\n")
            file.write(f"Минусы: {cons}\n")
            file.write(f"Комментарий: {answer_text}\n")
            file.write(f"Дата создания: {created_date}\n")
            file.write("-" * 40 + "\n")
    
    print(f"Отзывы сохранены в файл {filename}")



def fetch_all_questions(imt_id):
    url_template = f"https://questions.wildberries.ru/api/v1/questions?imtId={imt_id}&take=30&skip={{skip}}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
    }

    all_questions = []
    count = None
    skip = 0
    take = 30

    while count is None or skip < count:
        url = url_template.format(skip=skip)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения вопросов: {e}")
            break
        
        if count is None:
            count = data.get("count", 0)

        questions = data.get("questions", [])
        all_questions.extend(questions)

        skip += take

    return all_questions

def parse_questions(questions_data, filename="questions.txt"):
    if not questions_data:
        print("Нет данных о вопросах.")
        return

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Всего вопросов: {len(questions_data)}\n\n")

        for question in questions_data:
            question_text = question.get("text", "Нет данных")
            created_date = question.get("createdDate", "Нет данных")
            answer = question.get("answer")
            answer_text = answer["text"].strip() if answer else "Нет ответа"

            file.write(f"Вопрос: {question_text}\n")
            file.write(f"Дата создания: {created_date}\n")
            file.write(f"Ответ: {answer_text}\n")
            file.write("-" * 40 + "\n")

    print(f"Данные успешно сохранены в файл {filename}")

if __name__ == "__main__":
    # заменить на URl товара
    wildberries_url = 'https://www.wildberries.ru/catalog/258486821/detail.aspx'
    
    try:
        api_url = generate_api_url(wildberries_url)
        imt_id = fetch_product_data(api_url)

        if imt_id:
            feedbacks_url = f'https://feedbacks2.wb.ru/feedbacks/v2/{imt_id}'
            parse_feedbacks(feedbacks_url)

            questions_data = fetch_all_questions(imt_id)
            parse_questions(questions_data)

    except ValueError as ve:
        print(ve)