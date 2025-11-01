import json
import re


def read_json(json_path: str) -> list[dict]:
    with open(json_path, mode="r", encoding="utf-8") as file:
        return json.load(file)


def fix_json_list(json_list_str: str) -> list[dict]:
    """
    Принимает строку со списком JSON-объектов (возможно с ошибками экранирования)
    и возвращает список словарей.
    """
    # Чиним лишние экранирования кавычек (\\" -> \")
    fixed_str = re.sub(r'\\\\\"', r'\"', json_list_str)

    # Пробуем распарсить как список JSON-объектов
    data = json.loads(fixed_str)

    # Если на вход пришёл один объект, а не список — оборачиваем в список
    if isinstance(data, dict):
        data = [data]

    return data


def clean_json(json_path: str, *fields):
    result = []

    content = read_json(json_path)
    categories = read_json("external/categories.json")
    districts = read_json("external/districts.json")
    users = read_json("external/users.json")
    gallery = read_json("external/api_advertisementgallery.json")

    categories = {i["id"]: i["name"] for i in categories}
    districts = {i["id"]: i["name"] for i in districts}
    users = {i["id"]: i["tg_username"] for i in users}
    # gallery = {i["advertisement_id"]: i["photo"] for i in gallery}
    imgs = {}
    for item in content:
        copied_item = item.copy()
        copied_item["images"] = []

        for key, value in item.items():
            if key in fields:
                copied_item.pop(key)
            if key == "category_id":
                copied_item[key] = categories[value]
            if key == "district_id":
                copied_item[key] = districts[value]
            if key == "user_id":
                copied_item[key] = users.get(value)

            if key == "id":
                imgs[item["name"]] = []
                for img in gallery:
                    if value == img["advertisement_id"]:
                        imgs[item["name"]].append(img)

        result.append(copied_item)

    with open("external/test.json", mode="w", encoding="utf-8") as t:
        json.dump(imgs, t, indent=4, ensure_ascii=False)

    return result
