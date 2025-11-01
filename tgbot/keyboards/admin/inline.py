from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.models import User


def admin_start_kb():
    kb = InlineKeyboardBuilder()

    kb.button(text="Риелторы", callback_data="rg_realtors")

    kb.adjust(1)
    return kb.as_markup()


def realtors_actions_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Показать все", callback_data="rg_realtors_all")
    kb.button(text="Добавить", callback_data="rg_realtors_add")
    kb.button(text="На главную", callback_data="return_home")
    kb.adjust(2)
    return kb.as_markup()


def realtors_kb(realtors: list["User"]):
    kb = InlineKeyboardBuilder()
    for idx, realtor in enumerate(realtors, start=1):
        fullname = f"{realtor.first_name} {realtor.lastname}"
        kb.button(text=f"{idx}. {fullname}", callback_data=f"get_realtor:{realtor.id}")

    kb.button(text="На главную", callback_data="return_home")

    kb.adjust(1)
    return kb.as_markup()


def manage_realtor_kb(realtor_id: int):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Редактировать", callback_data=f"edit_realtor:{realtor_id}"
        ),
        InlineKeyboardButton(
            text="Удалить", callback_data=f"delete_realtor:{realtor_id}"
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Список объявлений",
            callback_data=f"realtor_advertisements:{realtor_id}",
        )
    )
    kb.row(
        InlineKeyboardButton(text="На главную", callback_data="return_home"),
    )

    return kb.as_markup()


def confirm_realtor_delete_kb(realtor_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data=f"confirm_delete:{realtor_id}")
    kb.button(text="Нет", callback_data="rg_realtors_all")
    return kb.as_markup()


def return_kb(callback: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=callback)
    return kb.as_markup()


def realtor_fields_kb(realtor_id: int, is_superadmin: bool = False):
    kb = InlineKeyboardBuilder()
    kb.button(text="Имя", callback_data=f"update_name:{realtor_id}")
    kb.button(text="Фамилия", callback_data=f"update_lastname:{realtor_id}")
    kb.button(text="Номер телефона", callback_data=f"update_phone_number:{realtor_id}")
    kb.button(text="Юзернейм", callback_data=f"update_tg_username:{realtor_id}")
    kb.button(text="Фото", callback_data=f"update_realtor_photo:{realtor_id}")
    kb.adjust(2)
    if is_superadmin:
        kb.row(
            InlineKeyboardButton(
                text="Привязать к руководителю",
                callback_data=f"update_realtor_director:{realtor_id}",
            )
        )

    kb.row(InlineKeyboardButton(text="На главную", callback_data="return_home"))
    return kb.as_markup()


def directors_kb(directors: list["User"], current_director: "User"):
    kb = InlineKeyboardBuilder()
    for idx, director in enumerate(directors, start=1):
        if not director.tg_chat_id == current_director.tg_chat_id:
            fullname = f"{director.first_name} {director.lastname}"
            kb.button(
                text=f"{idx}. {fullname}",
                callback_data=f"select_director:{director.tg_chat_id}",
            )

    kb.button(text="На главную", callback_data="return_home")

    kb.adjust(1)
    return kb.as_markup()


def advertisement_moderation_kb(advertisement_id: int, for_delete: bool = False):
    kb = InlineKeyboardBuilder()

    call_1 = (
        f"moderation_confirm:{advertisement_id}"
        if not for_delete
        else f"confirm_advertisement_delete:{advertisement_id}"
    )
    call_2 = (
        f"moderation_deny:{advertisement_id}"
        if not for_delete
        else f"deny_advertisement_delete:{advertisement_id}"
    )

    kb.button(text="Да ✔", callback_data=call_1)
    kb.button(text="Нет ❌", callback_data=call_2)
    if not for_delete:
        kb.button(text='Категория С', callback_data=f'for_base_channel:{advertisement_id}')
    return kb.as_markup()


def delete_advertisement_kb(advertisement_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Удалить", callback_data=f"rg_advertisement_delete:{advertisement_id}"
    )
    kb.button(text="На главную", callback_data="return_home")
    kb.adjust(1)
    return kb.as_markup()
