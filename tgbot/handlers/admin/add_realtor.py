import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, CallbackQuery

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import manage_realtor_kb
from tgbot.misc.realtor_states import RealtorCreationState
from tgbot.utils.helpers import download_file

router = Router()
router.message.filter(RoleFilter(role="group_director"))

upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)


@router.callback_query(F.data == "rg_realtors_add")
async def add_new_realtor(
    call: CallbackQuery,
    state: FSMContext,
):
    await call.answer()

    await call.message.edit_text(text="Напишите имя", reply_markup=None)
    await state.set_state(RealtorCreationState.first_name)


@router.message(RealtorCreationState.first_name)
async def get_first_name_set_lastname(
    message: Message,
    state: FSMContext,
):
    chat_id = message.from_user.id

    await state.update_data(first_name=message.text, chat_id=chat_id)
    await state.set_state(RealtorCreationState.lastname)

    await message.answer(text="Напишите фамилию")


@router.message(RealtorCreationState.lastname)
async def get_lastname_set_phone_number(
    message: Message,
    state: FSMContext,
):
    await state.update_data(lastname=message.text)
    await state.set_state(RealtorCreationState.phone_number)

    await message.answer(text="Напишите номер телефона")


@router.message(RealtorCreationState.phone_number)
async def get_phone_number_set_tg_username(
    message: Message, state: FSMContext, repo: RequestsRepo
):
    phone_number = message.text

    user = await repo.users.get_user_by_phone_number(phone_number=phone_number)
    if user is not None:
        await state.set_state(RealtorCreationState.phone_number)
        await message.answer("Пользователь с таким номером телефона уже существует")
        return await message.answer("Проверьте номер телефона и напишите его еще раз")

    await state.update_data(phone_number=phone_number)
    await state.set_state(RealtorCreationState.tg_username)
    return await message.answer(text="Напишите username без @")


@router.message(RealtorCreationState.tg_username)
async def get_tg_username_set_profile_image(
    message: Message, state: FSMContext, repo: RequestsRepo
):
    username = message.text

    user = await repo.users.get_user_by_username(username=username)
    if user is not None:
        await state.set_state(RealtorCreationState.tg_username)
        await message.answer("Пользователь с таким username уже существует")
        return await message.answer("Проверьте правильность и напишите его еще раз")

    await state.set_state(RealtorCreationState.photo)
    await state.update_data(tg_username=username)
    return await message.answer("Отправьте фото агента")


@router.message(RealtorCreationState.photo, F.content_type == ContentType.PHOTO)
async def get_profile_image_create_user(
    message: Message,
    repo: "RequestsRepo",
    state: FSMContext,
):
    data = await state.get_data()

    photo_id = message.photo[-1].file_id

    file, filename = await download_file(bot=message.bot, file_id=photo_id)

    user_image_folder = upload_dir / "users"
    user_image_folder.mkdir(parents=True, exist_ok=True)

    file_location = user_image_folder / filename

    with open(file_location, "wb") as f:
        shutil.copyfileobj(file, f)

    user = await repo.users.create_user(
        first_name=data["first_name"],
        lastname=data["lastname"],
        phone_number=data["phone_number"],
        tg_username=data["tg_username"],
        profile_image=str(file_location),
        profile_image_hash=photo_id,
        role="REALTOR",
        added_by=data["chat_id"],
    )

    user_message = f"""
Риелтор успешно добавлен:

Имя: <b>{user.first_name}</b>
Фамилия: <b>{user.lastname}</b>
Номер телефона: <b>{user.phone_number}</b>
Юзернейм: <b>{user.tg_username}</b>
    """

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=photo_id,
        caption=user_message,
        reply_markup=manage_realtor_kb(realtor_id=user.id),
    )
