import openpyxl


def save_to_excel(card_data: list[dict], detail_data: list[dict], filename: str = "wb_products.xlsx"):
    wb = openpyxl.Workbook()

    # card.json sheet
    ws1 = wb.active
    ws1.title = "card.json"
    headers1 = ["imt_name", "subj_name", "subj_root_name", "vendor_code", "kinds", "description", "photo_count"]
    ws1.append(headers1)
    for item in card_data:
        ws1.append([item.get(key, "") for key in headers1])

    # detail API sheet
    ws2 = wb.create_sheet("detail")
    headers2 = ["name", "origName", "brand", "subjectName", "root", "id"]
    ws2.append(headers2)
    for item in detail_data:
        basic = item.get("basic", {})
        product = item.get("product", {})
        ws2.append([
            item.get("name"),
            item.get("origName"),
            basic.get("brand"),
            basic.get("subjectName"),
            product.get("root"),
            product.get("id"),
        ])

    wb.save(filename)
    print(f"✅ Excel файл сохранен: {filename}")
