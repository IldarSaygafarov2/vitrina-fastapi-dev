from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.app.config import config
from celery_tasks.tasks import remind_agent_to_update_advertisement_extended
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin.inline import (
    advertisement_moderation_kb,
    delete_advertisement_kb,
)
from tgbot.keyboards.user.inline import is_price_actual_kb
from tgbot.misc.user_states import AdvertisementRelevanceState
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.messages import advertisement_reminder_message
from tgbot.utils import helpers

router = Router()


@router.callback_query(F.data.startswith("actual"))
async def react_to_advertisement_actual(call: CallbackQuery):
    """Если объявление является актуальным"""
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    await call.message.edit_text(
        text="Изменилась ли цена данного объявления ?",
        reply_markup=is_price_actual_kb(advertisement_id),
    )


@router.callback_query(F.data.startswith("price_changed"))
async def react_to_advertisement_price_changed(call: CallbackQuery, state: FSMContext):
    """Если цена объявления поменялась."""
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    await state.set_state(AdvertisementRelevanceState.new_price)
    await state.update_data(advertisement_id=advertisement_id)
    await call.message.edit_text(
        "Напишите новую цену для объявления", reply_markup=None
    )


@router.message(AdvertisementRelevanceState.new_price)
async def set_actual_price_for_advertisement(
    message: Message, repo: RequestsRepo, state: FSMContext
):
    """Добавляем новую цену объявлению."""
    state_data = await state.get_data()
    chat_id = message.chat.id

    # users data
    user = await repo.users.get_user_by_chat_id(chat_id)
    director_chat_id = user.added_by

    # advertisement data
    advertisement_id = state_data.get("advertisement_id")
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    operation_type = advertisement.operation_type.value

    reminder_time = helpers.get_reminder_time_by_operation_type(operation_type)

    new_price = helpers.filter_digits(message.text)

    updated_advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id,
        price=int(new_price),
        new_price=int(new_price),
        reminder_time=reminder_time,
    )

    # подготавливаем медиа группу для отправки
    media_group = await helpers.collect_media_group_for_advertisement(
        updated_advertisement, repo
    )

    await message.answer("Объявление отправлено руководителю на проверку")
    agent_fullname = f"{user.first_name} {user.lastname}"

    await message.bot.send_media_group(director_chat_id, media_group)
    await message.bot.send_message(
        director_chat_id,
        f"""
Агент: <i>{agent_fullname}</i> обновил объявление
Новая цена объявления: <b>{new_price}</b>
Объявление прошло модерацию?
""",
        reply_markup=advertisement_moderation_kb(advertisement_id=advertisement_id),
    )


@router.callback_query(F.data.startswith("price_not_changed"))
async def react_to_advertisement_price_not_changed(
    call: CallbackQuery,
    repo: RequestsRepo,
):
    """Отправляем сообщения во все группу и топики если цена не поменялась."""
    await call.answer()
    await call.message.delete()

    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    advertisement_message_for_remind = realtor_advertisement_completed_text(
        advertisement
    )

    advertisement_photos = await helpers.get_advertisement_photos(
        advertisement_id, repo
    )

    # получаем новое время обновления
    operation_type = advertisement.operation_type.value
    reminder_time = helpers.get_reminder_time_by_operation_type(operation_type)
    formatted_reminder_time = (reminder_time + timedelta(hours=5)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # медиа группа для проверки актуальности
    advertisement_media_group_for_remind = helpers.get_media_group(
        advertisement_photos, advertisement_message_for_remind
    )

    channel_name, advertisement_message = (
        helpers.get_channel_name_and_message_by_operation_type(advertisement)
    )
    media_group = helpers.get_media_group(advertisement_photos, advertisement_message)

    agent = await repo.users.get_user_by_id(advertisement.user_id)

    # обновляем дату проверки актуальности
    await repo.advertisements.update_advertisement(
        reminder_time=reminder_time, advertisement_id=advertisement_id
    )

    # отправляем сообщение в супер группу по топикам
    await helpers.send_message_to_rent_topic(
        bot=call.bot,
        price=advertisement.price,
        media_group=media_group,
        operation_type=operation_type,
    )

    if operation_type == "Покупка":
        await call.bot.send_media_group(
            chat_id=config.tg_bot.base_channel_name,
            media=media_group,
        )

    # отправляем сообщение в каналы по типу операции
    try:
        await call.bot.send_media_group(
            chat_id=channel_name,
            media=media_group,
        )
    except Exception as e:
        await call.bot.send_message(
            chat_id=config.tg_bot.test_main_chat_id,
            text=f"ошибка при отправке медиа группы\n{str(e)}",
        )

    remind_agent_to_update_advertisement_extended.apply_async(
        args=[
            advertisement.unique_id,
            advertisement.id,
            agent.tg_chat_id,
            helpers.serialize_media_group(advertisement_media_group_for_remind),
        ],
        eta=reminder_time,
    )

    await call.message.answer(
        f"Уведомление для проверки актуальности отправится агенту в \n<b>{formatted_reminder_time}</b>"
    )
    await call.bot.send_message(
        agent.added_by, text=advertisement_reminder_message(formatted_reminder_time)
    )


@router.callback_query(F.data.startswith("not_actual"))
async def react_to_advertisement_not_actual(call: CallbackQuery, repo: RequestsRepo):
    """Отправляем объявление на удаление если оно не является актуальным."""
    await call.message.delete()
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    media_group = await helpers.collect_media_group_for_advertisement(
        advertisement, repo
    )

    # данные агента, который добавил объявление
    agent = await repo.users.get_user_by_id(advertisement.user_id)
    director_chat_id = agent.added_by
    agent_fullname = f"{agent.first_name} {agent.lastname}"

    msg = f"""
Агент: <i>{agent_fullname}</i> указал, что объявление: <b>{advertisement.unique_id}</b>
больше не актуально!

Удалить данное объявление?
"""
    await call.message.answer(
        "Объявление было отправлено на проверку вашему руководителю"
    )
    await call.bot.send_media_group(chat_id=director_chat_id, media=media_group)
    await call.bot.send_message(
        chat_id=director_chat_id,
        text=msg,
        reply_markup=delete_advertisement_kb(advertisement_id),
    )
