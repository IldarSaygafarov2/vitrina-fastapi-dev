from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin.inline import admin_start_kb, delete_advertisement_kb
from tgbot.keyboards.user.inline import (
    realtor_advertisements_kb,
    realtor_start_kb,
    advertisement_actions_kb,
    return_home_kb,
)
from tgbot.misc.common import AdvertisementSearchStates
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.utils.helpers import get_media_group

router = Router()


@router.callback_query(F.data.contains("return_home"))
async def return_home(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()
    await state.clear()

    username = call.message.chat.username
    chat_id = call.message.chat.id

    user = await repo.users.get_user_by_chat_id(tg_chat_id=chat_id)

    if user.role.value == "realtor":
        return await call.message.edit_text(
            f"Привет, {username.title()}",
            reply_markup=realtor_start_kb(realtor_chat_id=chat_id),
        )
    if user.role.value == "group_director":
        if call.message.content_type == ContentType.PHOTO:
            await call.message.delete()
            return await call.bot.send_message(
                chat_id,
                text=f"""Привет, руководитель группы

Выберите действие снизу    
    """,
                reply_markup=admin_start_kb(),
            )

        return await call.message.edit_text(
            f"""Привет, руководитель группы

Выберите действие снизу    
    """,
            reply_markup=admin_start_kb(),
        )


@router.callback_query(F.data.startswith("next_page"))
async def next_page(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):

    state_data = await state.get_data()
    for_admin = state_data.get("for_admin", False)

    _, start, finish, page, total_pages = call.data.split(":")

    if int(page) == int(total_pages):
        return await call.answer("Это последняя страница", show_alert=True)

    return await call.message.edit_reply_markup(
        reply_markup=realtor_advertisements_kb(
            advertisements=state_data["advertisements"],
            start=int(start) + 15,
            finish=int(finish) + 15,
            page=int(page) + 1,
            for_admin=for_admin,
        )
    )


@router.callback_query(F.data.startswith("prev_page"))
async def prev_page(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    state_data = await state.get_data()
    for_admin = state_data.get("for_admin", False)

    _, start, finish, page = call.data.split(":")

    if int(page) == 1:
        return await call.answer("Это первая страница", show_alert=True)

    return await call.message.edit_reply_markup(
        reply_markup=realtor_advertisements_kb(
            advertisements=state_data["advertisements"],
            start=int(start) - 15,
            finish=int(finish) - 15,
            page=int(page) - 1,
            for_admin=for_admin,
        )
    )


@router.callback_query(F.data.startswith("search_by_id"))
async def search_by_id(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id

    await call.answer()
    await state.set_state(AdvertisementSearchStates.id)
    await state.update_data(chat_id=chat_id)

    await call.message.edit_text("Напиши ID объявления!", reply_markup=None)


async def _send_searched_advertisement(
    message: Message,
    advertisement,
    is_group_director,
):
    advertisement_message = realtor_advertisement_completed_text(
        advertisement=advertisement,
    )
    photos = [obj.tg_image_hash for obj in advertisement.images]
    media_group = get_media_group(photos, advertisement_message)
    if media_group:
        await message.answer_media_group(media=media_group)  # type: ignore

    if not is_group_director:
        return await message.answer(
            text="Выберите действие над этим объявлением",
            reply_markup=advertisement_actions_kb(advertisement_id=advertisement.id),
        )
    return await message.answer(
        text="Выберите действие над этим объявлением",
        reply_markup=delete_advertisement_kb(advertisement_id=advertisement.id),
    )


@router.message(AdvertisementSearchStates.id)
async def get_searched_advertisement(message: Message, repo: RequestsRepo):
    advertisement = await repo.advertisements.get_advertisement_by_unique_id(
        unique_id=message.text
    )
    user = await repo.users.get_user_by_chat_id(tg_chat_id=message.chat.id)

    is_group_director = user.role.value == "group_director"

    if user.is_superadmin:
        return await _send_searched_advertisement(
            message, advertisement, is_group_director
        )

    if not advertisement:
        text = (
            f"Объявление с ID: {message.text} не найдено, перепроверьте правильность ID"
        )
        return await message.answer(text, reply_markup=return_home_kb())

    elif is_group_director:
        agents = await repo.users.get_director_agents(director_chat_id=user.tg_chat_id)
        if advertisement.user not in agents:
            text = f"Объявление с ID: {message.text} не добавлено вашей командой, перепроверьте правильность ID"
            return await message.answer(text, reply_markup=return_home_kb())
    elif advertisement.user != user:
        text = f"Объявление с ID: {message.text} не найдено либо не является вашим объявлением, перепроверьте правильность ID"
        return await message.answer(text, reply_markup=return_home_kb())

    try:
        return await _send_searched_advertisement(
            message, advertisement, is_group_director
        )
    except Exception as e:
        error_message = (
            f"{str(e)}\n{e.__class__.__name__}\nID: {advertisement.unique_id}"
        )
        print(error_message)
        return None
