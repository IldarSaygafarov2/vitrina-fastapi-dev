from infrastructure.database.models import Advertisement


def choose_operation_type_text() -> str:
    return "Выберите тип операции для этого объявления"


def choose_category_text(operation_type: str) -> str:
    return f"""Выбранный тип операции: <b>{operation_type}</b>

Выберите категорию недвижимости: """


def choose_photos_quantity_text(category_name: str):
    return f"""Выбранная категория: <b>{category_name}</b>

Напишите сколько фотографий будет в данном объявлении:
"""


def choose_photos_text(photos_quantity: str):
    return f"""Количество фотографий для объявления: <b>{photos_quantity}</b>

Отправьте столько фотографий, сколько указали
"""


def get_title_text(lang: str = "ru"):
    if lang == "uz":
        return "Напишите название объявления на узбекском "
    return "Напишите название объявления"


def get_description_text(lang: str = "ru"):
    if lang == "uz":
        return "Напишите описание для объявления на узбекском языке"
    return "Напишите описание для объвления"


def get_district_text():
    return "Выберите район, в котором расположена недвижимость: "


def get_address_text(district_name: str, lang: str = "ru"):

    return f"""Выбранный район: <b>{district_name}</b>

Напишите точный адрес недвижимости:
"""


def get_address_text_uz():
    return "Напишите точный адрес на узбекском"


def get_propety_type_text():
    return "Выберите текст недвижимости:"


def creation_year_text(property_type: str):
    return f"""Выбранный тип недвижимости: <b>{property_type}</b>

Укажите год постройки недвижимости
"""


def price_text(property_type: str):
    return f"""Выбранный тип недвижимости: <b>{property_type}</b>

Укажите цену для данного объвления
"""




def realtor_advertisement_completed_text(
    advertisement: "Advertisement",
    lang: str = "ru",
    hide_owner_phone: bool = False,
):
    rooms_from_to = f"<b>Кол-во комнат</b>  <i>{advertisement.rooms_quantity}</i>"
    creation_year = (
        f"\n<b>Год постройки: </b><i>{advertisement.creation_year}</i>"
        if advertisement.creation_year
        else ""
    )

    house_quadrature = (
        f"\n<b>Площадь участка: от </b>{advertisement.house_quadrature_from} до {advertisement.house_quadrature_to}"
        if advertisement.house_quadrature_from and advertisement.house_quadrature_to
        else ""
    )

    # name = advertisement.name
    description_uz = (
        f"\n<b>Описание на узбекском: </b><i>{advertisement.description_uz}</i>"
        if lang == "uz"
        else ""
    )

    owner_phone_number = (
        f"\n<b>Номер собственника: </b><i>{advertisement.owner_phone_number}</i>"
        if not hide_owner_phone
        else ""
    )

    name_uz = (
        f"\n<b>Заголовок на узбекском:</b><i>{advertisement.name_uz}</i>"
        if lang == "uz"
        else ""
    )

    adress_uz = (
        f"\n<b>Адрес на узбекском:</b><i>{advertisement.address_uz}</i>"
        if lang == "uz"
        else ""
    )

    return f"""
<b>№</b> <i>{advertisement.unique_id}</i>
<b>Заголовок:</b><i>{advertisement.name}</i>{name_uz}
<b>Тип объявления: </b><i>{advertisement.operation_type.value}</i>
<b>Описание: </b><i>{advertisement.description}</i>{description_uz}
<b>Район: </b><i>{advertisement.district.name}</i>
<b>Адрес: </b><i>{advertisement.address}</i>{adress_uz}{owner_phone_number}
<b>Категория недвижимости: </b><i>{advertisement.category.name}</i>
<b>Тип недвижимости: </b><i>{advertisement.property_type.value}</i>{creation_year}
<b>Цена: </b><i>{advertisement.price}</i>{house_quadrature}
{rooms_from_to}
<b>Квадратура: </b><i>{advertisement.quadrature}</i>
<b>Этаж: </b><i>{advertisement.floor_from}</i> из <i>{advertisement.floor_to}</i>
<b>Ремонт: </b><i>{advertisement.repair_type.value}</i>
"""
