from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.models import (
    Advertisement,
    Category,
    District,
    AdvertisementImage,
)

from tgbot.misc.constants import (
    ADVERTISEMENT_UPDATE_FIELDS,
    OPERATION_TYPE_MAPPING,
    PROPERTY_TYPE_MAPPING,
    REPAIR_TYPE_MAPPING,
)


def realtor_start_kb(realtor_chat_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Создать объявление", callback_data=f"create_advertisement")
    kb.button(
        text="Мои объявления",
        callback_data=f"show_realtors_advertisement:{realtor_chat_id}",
    )
    return kb.as_markup()


def operation_type_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Покупка", callback_data="operation_type:buy")
    kb.button(text="Аренда", callback_data="operation_type:rent")

    return kb.as_markup()


def categories_kb(categories: list["Category"], for_update: bool = False):
    kb = InlineKeyboardBuilder()

    for category in categories:
        callback = (
            f"update_chosen_category:{category.id}"
            if for_update
            else f"chosen_category:{category.id}"
        )
        kb.button(text=category.name, callback_data=callback)

    kb.adjust(2)
    return kb.as_markup()


def districts_kb(districts: list["District"], for_update: bool = False):
    kb = InlineKeyboardBuilder()
    for district in districts:

        callback = (
            f"update_chosen_district:{district.id}"
            if for_update
            else f"chosen_district:{district.id}"
        )

        kb.button(text=district.name, callback_data=callback)

    kb.adjust(1)
    return kb.as_markup()


def property_type_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Новостройка", callback_data=f"property_type:new")
    kb.button(text="Вторичный фонд", callback_data=f"property_type:old")
    return kb.as_markup()



def repair_type_kb(repair_types: dict):
    kb = InlineKeyboardBuilder()
    for key, value in repair_types.items():
        kb.button(text=value, callback_data=f"repair_type:{key}")
    kb.adjust(2)
    return kb.as_markup()


def realtor_advertisements_kb(
    advertisements: list["Advertisement"],
    for_admin: bool = False,
    start: int = 0,
    finish: int = 15,
    page: int = 1,
):
    kb = InlineKeyboardBuilder()

    total_pages = len(advertisements) // 15 + 1

    for idx, advertisement in enumerate(advertisements[start:finish], start=start):
        callback = (
            f"realtor_advertisement:{advertisement.id}"
            if not for_admin
            else f"rg_realtor_advertisement:{advertisement.id}"
        )
        kb.button(
            text=f"{idx}. {advertisement.unique_id}. {advertisement.name}.",
            callback_data=callback,
        )

    kb.adjust(1)

    kb.row(
        InlineKeyboardButton(
            text="<", callback_data=f"prev_page:{start}:{finish}:{page}"
        ),
        InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="do_nothing"),
        InlineKeyboardButton(
            text=">", callback_data=f"next_page:{start}:{finish}:{page}:{total_pages}"
        ),
    )
    kb.row(InlineKeyboardButton(text='Поиск по ID', callback_data='search_by_id'))
    kb.row(InlineKeyboardButton(text="На главную", callback_data="return_home"))

    return kb.as_markup()


def return_home_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="На главную", callback_data="return_home")
    return kb.as_markup()


def advertisement_actions_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить", callback_data=f"advertisement_update:{advertisement_id}")
    kb.button(text="Удалить", callback_data=f"advertisement_delete:{advertisement_id}")
    kb.button(text="На главную", callback_data="return_home")
    kb.adjust(2)
    return kb.as_markup()


def advertisement_update_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()
    for key, value in ADVERTISEMENT_UPDATE_FIELDS.items():
        kb.button(text=value, callback_data=f"{key}:{advertisement_id}")

    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="На главную", callback_data="return_home"))
    return kb.as_markup()



def return_back_kb(callback: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=callback)
    return kb.as_markup()


def advertisement_choices_kb(
    choice_type: str, callback_for_return: str | None = None, **kwargs
):
    kb = InlineKeyboardBuilder()

    prefix = "update_"

    if choice_type == "repair_type":
        for key, value in REPAIR_TYPE_MAPPING.items():
            kb.button(text=value, callback_data=f"{prefix}{choice_type}:{key}")
    elif choice_type == "property_type":
        for key, value in PROPERTY_TYPE_MAPPING.items():
            kb.button(text=value, callback_data=f"{prefix}{choice_type}:{key}")
    elif choice_type == "operation_type":
        for key, value in OPERATION_TYPE_MAPPING.items():
            kb.button(text=value, callback_data=f"{prefix}{choice_type}:{key}")

    kb.adjust(2)
    if callback_for_return is not None:
        kb.row(InlineKeyboardButton(text="Назад", callback_data=callback_for_return))

    return kb.as_markup()


def advertisement_images_kb(images: list[AdvertisementImage]):
    kb = InlineKeyboardBuilder()

    for idx, image in enumerate(images, start=1):
        kb.button(text=f"{idx}", callback_data=f"adv_img:{image.id}")

    kb.adjust(2)
    return kb.as_markup()


def is_advertisement_actual_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()

    kb.add(InlineKeyboardButton(text='Да', callback_data=f'actual:{advertisement_id}'))
    kb.add(InlineKeyboardButton(text='Нет', callback_data=f'not_actual:{advertisement_id}'))
    return kb.as_markup()


def is_price_actual_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Да', callback_data=f'price_changed:{advertisement_id}'))
    kb.add(InlineKeyboardButton(text='Нет', callback_data=f'price_not_changed:{advertisement_id}'))
    return kb.as_markup()