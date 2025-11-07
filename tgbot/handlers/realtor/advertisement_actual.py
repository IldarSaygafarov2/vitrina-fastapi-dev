from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.app.config import config
from celery_tasks.tasks import remind_agent_to_update_advertisement_extended
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin.inline import advertisement_moderation_kb
from tgbot.keyboards.user.inline import is_price_actual_kb, advertisement_actions_kb
from tgbot.misc.user_states import AdvertisementRelevanceState
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.messages import rent_channel_advertisement_message, advertisement_reminder_message
from tgbot.utils import helpers
from tgbot.utils.helpers import send_message_to_rent_topic

router = Router()


# TODO: если объявление является актуальным нужно узнать новую цену на объявление и поменять время напоминания проверки актуальности объявления
@router.callback_query(F.data.startswith("actual"))
async def react_to_advertisement_actual(call: CallbackQuery):
    """Если объявление является актуальным"""
    await call.answer()

    # айди объявления
    advertisement_id = int(call.data.split(":")[-1])
    await call.message.edit_text(text="Изменилась ли цена данного объявления ?",
                                 reply_markup=is_price_actual_kb(advertisement_id))


# TODO: если цена на объявление актуальная просто обновляем время напоминания и запускаем службу уведомления по новому времени
@router.callback_query(F.data.startswith("price_changed"))
async def react_to_advertisement_price_actual(call: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    await state.set_state(AdvertisementRelevanceState.new_price)
    await state.update_data(advertisement_id=advertisement_id)
    await call.message.answer("Напишите новую цену для объявления", reply_markup=None)


# TODO: если цена поменялась, то спрашиваем у агента новую цену и меняем объявление
# если тип операции объявления покупка то нужно отправить на модерацию руководителю
# если аренда то сразу публиковать в канал повторно меняя дату проверку актуальности
@router.callback_query(F.data.startswith("price_not_changed"))
async def react_to_advertisement_price_not_changed(call: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    await call.answer()

    chat_id = call.message.chat.id
    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    # получаем все фотографии объявления
    advertisement_photos = await helpers.get_advertisement_photos(advertisement_id=advertisement_id, repo=repo)

    advertisement_message = realtor_advertisement_completed_text(advertisement)
    media_group = helpers.get_media_group(advertisement_photos, advertisement_message)

    # получаем новое время обновления
    operation_type = advertisement.operation_type.value
    reminder_time = helpers.get_reminder_time_by_operation_type(operation_type)

    formatted_reminder_time = (reminder_time + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
    await repo.advertisements.update_advertisement(reminder_time=reminder_time, advertisement_id=advertisement_id)

    if operation_type == 'Аренда':
        await call.bot.send_media_group(
            config.tg_bot.rent_channel_name,
            media=media_group
        )
        await send_message_to_rent_topic(
            bot=call.bot,
            price=advertisement.price,
            media_group=media_group,
            operation_type=advertisement.operation_type.value
        )
        # ставим новую задачу для напоминания в очередь
        remind_agent_to_update_advertisement_extended.apply_async(
            args=[
                advertisement.unique_id,
                advertisement.id,
                chat_id,
                helpers.serialize_media_group(media_group)
            ],
            eta=reminder_time,
        )
    else:
        agent = await repo.users.get_user_by_chat_id(chat_id)
        agent_fullname = f"{agent.first_name} {agent.lastname}"

        agent_director_chat_id = agent.added_by
        await call.message.answer('Объявление отправлено на проверку вашему руководителю')
        await call.bot.send_media_group(agent_director_chat_id, media=media_group)
        await call.bot.send_message(
            agent_director_chat_id,
            f"Агент: <b>{agent_fullname}</b> отправил объявление на проверку"
        )

    await call.message.answer("Спасибо за ответ!")
    await call.message.answer(
        text=advertisement_reminder_message(formatted_reminder_time)
    )


@router.message(AdvertisementRelevanceState.new_price)
async def set_actual_price_for_advertisement(message: Message, repo: RequestsRepo, state: FSMContext):
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
    formatted_reminder_time = (reminder_time + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')

    new_price = helpers.filter_digits(message.text)

    # обновляем цену объявления
    if operation_type == 'Аренда':
        updated_advertisement = await repo.advertisements.update_advertisement(
            advertisement_id=advertisement_id,
            price=int(new_price),
            reminder_time=reminder_time
        )
    else:
        updated_advertisement = await repo.advertisements.update_advertisement(
            advertisement_id=advertisement_id,
            updated_price=int(new_price),
            reminder_time=reminder_time
        )

    print(f'new reminder time: {formatted_reminder_time} for {operation_type=}')

    # подготавливаем медиа группу для отправки
    advertisement_photos = await  helpers.get_advertisement_photos(advertisement_id=advertisement_id, repo=repo)

    if operation_type == 'Аренда':
        # подготавливаем медиа для отправки в канал телеграмма
        message_for_rent_channel = rent_channel_advertisement_message(updated_advertisement)
        media_group_for_rent_channel = helpers.get_media_group(advertisement_photos, message_for_rent_channel)

        # подготавливаем медиа для отправки сообщения проверки актуальности
        advertisement_message = realtor_advertisement_completed_text(updated_advertisement, lang='uz')
        advertisement_media_group = helpers.get_media_group(advertisement_photos, advertisement_message)

        # отправляем сообщение в канал по аренде
        await message.bot.send_media_group(config.tg_bot.rent_channel_name, media=media_group_for_rent_channel)
        await message.answer("Обновили цену и отправили в канал")
        await message.answer(
            text=advertisement_reminder_message(formatted_reminder_time)
        )

        remind_agent_to_update_advertisement_extended.apply_async(
            args=[
                updated_advertisement.unique_id,
                updated_advertisement.id,
                message.chat.id,
                helpers.serialize_media_group(media_group=advertisement_media_group)
            ],
            eta=reminder_time
        )
    elif operation_type == 'Покупка':
        media_group = helpers.get_media_group(advertisement_photos,
                                              realtor_advertisement_completed_text(updated_advertisement))
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
            reply_markup=advertisement_moderation_kb(advertisement_id=advertisement_id))


# TODO: если объявление не актуальное нужно отправить агенту клавиатуру для удаления данного объявление,
# проверка отправляется руководителю данного агента для подтверждения удаления
@router.callback_query(F.data.startswith("not_actual"))
async def react_to_advertisement_not_actual(call: CallbackQuery):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    await call.message.answer(f"Выберите действие над данным объявлением",
                              reply_markup=advertisement_actions_kb(advertisement_id))
