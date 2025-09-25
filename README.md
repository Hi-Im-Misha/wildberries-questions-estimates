# Парсер Wildberries

Скрипт для получения информации об отзывы, вопросы, категории и сохранение данных в Excel.  

---

## Возможности

- Генерация API URL товара по ссылке на Wildberries
- Получение ID товара и данных с `card.json` и `detail API`
- Сбор отзывов и вопросов о товаре
- Сохранение данных в Excel (`openpyxl`)
- Парсинг категорий и построение API URL каталога
- Рекурсивный поиск категории в JSON меню Wildberries
- Поддержка работы с несколькими "корзинами" (basket) Wildberries

---

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/Hi-Im-Misha/wildberries-questions-estimates.git
2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
3. Использование
    - В скрипте main.py замените переменные wildberries_url
4. Запустите скрипт:
    ```bash
    python main.py
