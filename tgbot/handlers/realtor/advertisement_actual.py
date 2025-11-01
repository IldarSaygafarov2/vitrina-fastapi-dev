from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.app.config import config
from celery_tasks.tasks import remind_agent_to_update_advertisement
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.admin.inline import advertisement_moderation_kb
from tgbot.keyboards.user.inline import is_price_actual_kb, advertisement_actions_kb
from tgbot.misc.user_states import AdvertisementRelevanceState
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.utils.helpers import get_reminder_time_by_operation_type, filter_digits, get_media_group

router = Router()


# TODO: если объявление является актуальным нужно узнать новую цену на объявление и поменять время напоминания проверки актуальности объявления
@router.callback_query(F.data.startswith("actual"))
async def react_to_advertisement_actual(call: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    """Если объявление явялется актуальным"""
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
async def react_to_advertisement_price_not_actual(call: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    await call.answer()

    chat_id = call.message.chat.id
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    operation_type = advertisement.operation_type.value

    reminder_time = get_reminder_time_by_operation_type(operation_type)
    formatted_reminder_time = reminder_time.strftime('%Y-%m-%d %H:%M%:%S')
    await repo.advertisements.update_advertisement(reminder_time=reminder_time, advertisement_id=advertisement_id)

    # ставим новую задачу для напоминания в очередь
    remind_agent_to_update_advertisement.apply_async(
        args=[advertisement.unique_id, chat_id, advertisement.id],
        eta=reminder_time,
    )
    await call.message.answer("Спасибо за ответ!")
    await call.message.answer(
        f"Уведомление для проверки актуальности данного объявления будет отправлено в <b>{formatted_reminder_time}</b>"
    )


#
#
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

    reminder_time = get_reminder_time_by_operation_type(operation_type)
    formatted_reminder_time = reminder_time.strftime('%Y-%m-%d %H:%M%:%S')

    new_price = filter_digits(message.text)

    # обновляем цену объявления
    updated_advertisement = await repo.advertisements.update_advertisement(advertisement_id=advertisement_id,
                                                                           updated_price=int(new_price),
                                                                           reminder_time=reminder_time)

    print(f'new reminder time: {formatted_reminder_time} for {operation_type=}')

    # подготавливаем медиа группу для отправки
    advertisement_photos = await repo.advertisement_images.get_advertisement_images(advertisement_id=advertisement_id)
    advertisement_photos = [i.tg_image_hash for i in advertisement_photos]

    # подготавливаем готовое сообщение объявления
    advertisement_message = realtor_advertisement_completed_text(updated_advertisement, lang="uz")
    media_group = get_media_group(advertisement_photos, advertisement_message)

    reminder_time = get_reminder_time_by_operation_type(operation_type)

    if operation_type == 'Аренда':
        # отправляем сообщение в канал по аренде
        await message.bot.send_media_group(config.tg_bot.rent_channel_name, media=media_group)
        await message.answer("Обновили цену и отправили в канал")
        await message.answer(
            f"Следующее уведомление для проверки актуальности будет отправлено в <b>{formatted_reminder_time}</b>"
        )
        # TODO: изменить время актуальности данного объявления и добавить в очередь
        remind_agent_to_update_advertisement.apply_async(
            args=[updated_advertisement.unique_id, message.chat.id, updated_advertisement.id],
            eta=reminder_time
        )
    elif operation_type == 'Покупка':
        await message.answer("Объявление отправлено руководителю на проверку")
        agent_fullname = f"{user.first_name} {user.lastname}"
        # TODO:  отправить объявление на подтверждение руководителю группы
        await message.bot.send_media_group(director_chat_id, media_group)
        await message.bot.send_message(
            director_chat_id,
            f"""
Риелтор: <i>{agent_fullname}</i> обновил объявление
Новая цена объявления: <b>{new_price}</b>
Объявление прошло модерацию?
""",
            reply_markup=advertisement_moderation_kb(advertisement_id=advertisement_id))


# TODO: если объявление не актуальное нужно отправить агенту клавиатуру для удаления данного объявление,
# проверка отправляется руководителью данного агента для подтверждения удаления
@router.callback_query(F.data.startswith("not_actual"))
async def react_to_advertisement_not_actual(call: CallbackQuery, repo: RequestsRepo, state: FSMContext):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    await call.message.answer(f"Выберите действие над данным объявлением",
                              reply_markup=advertisement_actions_kb(advertisement_id))
