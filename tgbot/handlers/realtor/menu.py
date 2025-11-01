from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import advertisement_moderation_kb
from tgbot.keyboards.user.inline import (
    advertisement_actions_kb,
    operation_type_kb,
    realtor_advertisements_kb,
    realtor_start_kb,
)
from tgbot.misc.user_states import AdvertisementCreationState
from tgbot.templates.advertisement_creation import (
    choose_operation_type_text,
    realtor_advertisement_completed_text,
)
from tgbot.utils.helpers import get_media_group

config = load_config()

router = Router()
router.message.filter(RoleFilter(role="realtor"))
router.callback_query.filter(RoleFilter(role="realtor"))


@router.message(CommandStart())
async def start(message: Message, repo: RequestsRepo, state: FSMContext):
    username = message.from_user.username
    chat_id = message.from_user.id

    await state.clear()

    await repo.users.update_user_chat_id(
        tg_username=username,
        tg_chat_id=chat_id,
    )

    await message.answer(
        f"Привет, {username.title()}",
        reply_markup=realtor_start_kb(realtor_chat_id=chat_id),
    )


@router.callback_query(F.data.startswith("create_advertisement"))
async def create_advertisement(
    call: CallbackQuery,
    repo: RequestsRepo,
    state: FSMContext,
):
    await call.answer()
    await state.set_state(AdvertisementCreationState.operation_type)
    await call.message.edit_text(
        text=choose_operation_type_text(),
        reply_markup=operation_type_kb(),
    )


@router.callback_query(F.data.startswith("show_realtors_advertisement"))
async def show_realtor_advertisements(
    call: CallbackQuery,
    repo: "RequestsRepo",
    state: FSMContext,
):
    await call.answer()

    try:
        realtor_chat_id = int(call.data.split(":")[-1])
        user = await repo.users.get_user_by_chat_id(tg_chat_id=realtor_chat_id)

        advertisements = await repo.advertisements.get_user_advertisements(
            user_id=user.id
        )
        await state.update_data(advertisements=advertisements)
        await call.message.edit_text(
            text="Ваши объявления",
            reply_markup=realtor_advertisements_kb(advertisements=advertisements),
        )
    except Exception as e:
        await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id, text=str(e))


@router.callback_query(F.data.startswith("realtor_advertisement"))
async def get_realtor_advertisement_detail(
    call: CallbackQuery,
    repo: "RequestsRepo",
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    advertisement_message = realtor_advertisement_completed_text(
        advertisement=advertisement,
    )
    try:
        photos = [obj.tg_image_hash for obj in advertisement.images]
        media_group = get_media_group(photos, advertisement_message)
        await call.message.edit_text(text=advertisement_message)
        if media_group:
            await call.message.answer_media_group(media=media_group)
        await call.message.answer(
            text="Выберите действие над этим объявлением",
            reply_markup=advertisement_actions_kb(advertisement_id=advertisement_id),
        )
    except Exception as e:
        error_message = (
            f"{str(e)}\n{e.__class__.__name__}\nID: {advertisement.unique_id}"
        )

        await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id, text=error_message)


@router.callback_query(F.data.startswith("advertisement_delete"))
async def delete_advertisement(
    call: CallbackQuery,
    repo: RequestsRepo,
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )

    message = realtor_advertisement_completed_text(advertisement=advertisement)
    photos = [obj.tg_image_hash for obj in advertisement.images]
    media_group = get_media_group(photos, message)

    director = await repo.users.get_user_by_chat_id(
        tg_chat_id=advertisement.user.added_by
    )
    await call.message.answer("Удаление объявления отправлено на проверку")
    await call.bot.send_message(
        chat_id=director.tg_chat_id,
        text=f"Агент: {advertisement.user.first_name} {advertisement.user.lastname} хочет удалить объявление",
    )
    await call.bot.send_media_group(chat_id=director.tg_chat_id, media=media_group)
    await call.bot.send_message(
        chat_id=director.tg_chat_id,
        text="Выберите действие",
        reply_markup=advertisement_moderation_kb(
            advertisement_id=advertisement_id, for_delete=True
        ),
    )
