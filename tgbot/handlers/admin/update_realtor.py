import os
from pathlib import Path
import shutil
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import realtor_fields_kb, directors_kb, realtors_actions_kb
from tgbot.misc.realtor_states import RealtorUpdatingState
from tgbot.templates.realtor_texts import get_realtor_info
from tgbot.utils.helpers import download_file

config = load_config(".env")

router = Router()
router.message.filter(RoleFilter(role="group_director"))
router.callback_query.filter(RoleFilter(role="group_director"))


upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)


@router.callback_query(F.data.startswith("edit_realtor"))
async def edit_realtor_data(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()

    director = await repo.users.get_user_by_chat_id(tg_chat_id=call.from_user.id)

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    await call.message.edit_caption(
        caption=get_realtor_info(realtor),
        reply_markup=realtor_fields_kb(
            realtor_id, is_superadmin=director.is_superadmin
        ),
    )


@router.callback_query(F.data.startswith("update_realtor_director"))
async def update_realtor_director(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])

    current_director = await repo.users.get_user_by_chat_id(
        tg_chat_id=call.from_user.id
    )

    directors = await repo.users.get_users_by_role(role="GROUP_DIRECTOR")

    await call.message.edit_caption(
        caption="Выберите руководителя",
        reply_markup=directors_kb(
            directors=directors, current_director=current_director
        ),
    )
    await state.update_data(realtor_id=realtor_id, current_director=current_director)


@router.callback_query(F.data.startswith("select_director"))
async def select_director_for_agent(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    data = await state.get_data()
    call_data = call.data.split(":")
    director_chat_id = call_data[-1]

    updated = await repo.users.update_user(
        user_id=data["realtor_id"],
        added_by=int(director_chat_id),
    )
    await call.message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtors_actions_kb(),
    )


@router.callback_query(F.data.startswith("update_name"))
async def update_name(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_caption(
        caption=f"Имя агента: <b>{realtor.first_name}</b>\nВведите новое имя агента:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.first_name)


@router.message(RealtorUpdatingState.first_name)
async def update_name(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, first_name=message.text)
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_lastname"))
async def update_lastname(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_caption(
        caption=f"Фамилия агента: <b>{realtor.first_name}</b>\nВведите новую фамилию агента:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.lastname)


@router.message(RealtorUpdatingState.lastname)
async def update_lastname(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, lastname=message.text)
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_phone_number"))
async def update_phone_number(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_caption(
        caption=f"Номер телефона агента: <b>{realtor.first_name}</b>\nВведите новый номер телефона агента:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.phone_number)


@router.message(RealtorUpdatingState.phone_number)
async def update_phone_number(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(
        user_id=realtor_id, phone_number=message.text
    )
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_tg_username"))
async def update_tg_username(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    cur_message = await call.message.edit_caption(
        caption=f"Юзернейм агента: <b>{realtor.first_name}</b>\nВведите новый юзернейм агента:",
        reply_markup=None,
    )

    await state.update_data(realtor_id=realtor_id, realtor_message=cur_message)
    await state.set_state(RealtorUpdatingState.tg_username)


@router.message(RealtorUpdatingState.tg_username)
async def update_tg_username(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.pop("realtor_id")
    cur_message = data.pop("realtor_message")

    updated = await repo.users.update_user(user_id=realtor_id, tg_username=message.text)
    await cur_message.edit_caption(
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )

    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith("update_realtor_photo"))
async def update_profile_image(
        call: CallbackQuery,
        state: FSMContext,
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    cur_message = await call.message.edit_caption(
        caption="Отправьте новую фотографию профиля", reply_markup=None
    )
    await state.set_state(RealtorUpdatingState.photo)
    await state.update_data(realtor_id=realtor_id, cur_message=cur_message)


@router.message(RealtorUpdatingState.photo, F.content_type == ContentType.PHOTO)
async def update_profile_image(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    realtor_id = data.get("realtor_id")
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)
    cur_message = data.get("cur_message")

    try:
        if realtor.profile_image:
            os.remove(realtor.profile_image)
    except Exception as e:
        await message.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=str(e))

    photo_id = message.photo[-1].file_id

    file, filename = await download_file(bot=message.bot, file_id=photo_id)

    user_image_folder = upload_dir / "users"
    user_image_folder.mkdir(parents=True, exist_ok=True)

    file_location = user_image_folder / filename

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file, f)

    updated = await repo.users.update_user(
        user_id=realtor_id,
        profile_image=str(file_location),
        profile_image_hash=photo_id,
    )

    await cur_message.delete()
    await state.clear()
    await message.delete()

    await message.answer_photo(
        photo=photo_id,
        caption=get_realtor_info(updated),
        reply_markup=realtor_fields_kb(realtor_id),
    )
