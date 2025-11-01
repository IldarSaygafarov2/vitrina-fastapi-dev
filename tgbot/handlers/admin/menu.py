import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from backend.core.interfaces.advertisement import AdvertisementForReportDTO
from celery_tasks.tasks import (
    fill_report,
    send_delayed_message,
    remind_agent_to_update_advertisement,
    # send_message_by_queue
)
from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.role import RoleFilter
from tgbot.keyboards.admin.inline import (
    admin_start_kb,
    confirm_realtor_delete_kb,
    delete_advertisement_kb,
    manage_realtor_kb,
    realtors_actions_kb,
    realtors_kb,
)
from tgbot.keyboards.user.inline import realtor_advertisements_kb
from tgbot.misc.user_states import (
    AdvertisementDeletionState,
    AdvertisementModerationState,
)
# from tgbot.scheduler.main import scheduler
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.messages import (
    rent_channel_advertisement_message,
    buy_channel_advertisement_message,
)
from tgbot.templates.realtor_texts import get_realtor_info
from tgbot.utils.helpers import get_media_group, send_message_to_rent_topic, correct_advertisement_dict, \
    serialize_media_group

router = Router()
router.message.filter(RoleFilter(role="group_director"))
router.callback_query.filter(RoleFilter(role="group_director"))

# path to folder for uploading images
upload_dir = Path("media")
upload_dir.mkdir(parents=True, exist_ok=True)

config = load_config()


@router.message(CommandStart())
async def start(message: Message, repo: "RequestsRepo"):
    username = message.from_user.username
    chat_id = message.from_user.id
    await repo.users.update_user_chat_id(
        tg_username=username,
        tg_chat_id=chat_id,
    )
    await message.answer(
        f"""Привет, руководитель группы

Выберите действие снизу    
    """,
        reply_markup=admin_start_kb(),
    )


@router.callback_query(F.data == "rg_realtors")
async def get_realtors(
        call: CallbackQuery,
):
    await call.answer()

    await call.message.edit_text(
        text="Выберите действие ниже",
        reply_markup=realtors_actions_kb(),
    )


@router.callback_query(F.data == "rg_realtors_all")
async def get_all_realtors(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()

    director = await repo.users.get_user_by_chat_id(tg_chat_id=call.from_user.id)
    if not director.is_superadmin:
        realtors = await repo.users.get_director_agents(
            director_chat_id=call.from_user.id
        )
    else:
        realtors = await repo.users.get_users_by_role(role="REALTOR")

    await call.message.edit_text(
        text="Список риелторов",
        reply_markup=realtors_kb(realtors=realtors),
    )


@router.callback_query(F.data.startswith("get_realtor"))
async def get_realtor(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])

    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    advertisements = await repo.advertisements.get_user_advertisements(
        user_id=realtor.id
    )

    await state.update_data(advertisements=advertisements)

    realtor_info = get_realtor_info(realtor)

    profile_image = (
        realtor.profile_image_hash
        if realtor.profile_image_hash
        else "https://cdn.vectorstock.com/i/500p/08/19/gray-photo-placeholder-icon-design-ui-vector-35850819.jpg"
    )
    await call.message.delete()
    await call.message.answer_photo(
        photo=profile_image,
        caption=realtor_info,
        reply_markup=manage_realtor_kb(realtor_id=realtor_id),
    )


@router.callback_query(F.data.startswith("delete_realtor"))
async def delete_realtor(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    await call.message.answer(
        text=f"Вы действительно хотите удалить агента: <b>{realtor.first_name} {realtor.lastname}</b>",
        reply_markup=confirm_realtor_delete_kb(realtor_id=realtor_id),
    )


@router.callback_query(F.data.startswith("confirm_delete"))
async def confirm_realtor_delete(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()
    realtor_id = int(call.data.split(":")[-1])
    await repo.users.delete_user(user_id=realtor_id)

    realtors = await repo.users.get_users_by_role(role="REALTOR")
    await call.message.edit_text(
        text="Агент успешно удален",
        reply_markup=realtors_kb(realtors=realtors),
    )


@router.callback_query(F.data.startswith("realtor_advertisements"))
async def get_realtor_advertisements(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    realtor_id = int(call.data.split(":")[-1])
    realtor = await repo.users.get_user_by_id(user_id=realtor_id)

    advertisements = await repo.advertisements.get_user_advertisements(
        user_id=realtor_id
    )
    await state.update_data(for_admin=True)
    await call.message.delete()
    await call.message.answer(
        text=f"Объявления агента: <b>{realtor.first_name} {realtor.lastname}</b>",
        reply_markup=realtor_advertisements_kb(
            advertisements=advertisements, for_admin=True
        ),
    )


@router.callback_query(F.data.startswith("rg_realtor_advertisement"))
async def get_realtor_advertisement(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    advertisement_message = realtor_advertisement_completed_text(advertisement)
    photos = [obj.tg_image_hash for obj in advertisement.images]

    try:
        media_group = get_media_group(photos, advertisement_message) if all(photos) else []

        if media_group:
            await call.message.answer_media_group(
                media=media_group,
                reply_markup=delete_advertisement_kb(advertisement_id),
            )
            return await call.message.answer(
                text="Выберите действие над объявлением",
                reply_markup=delete_advertisement_kb(advertisement_id),
            )

        return await call.message.edit_text(
            text=advertisement_message,
            reply_markup=delete_advertisement_kb(advertisement_id),
        )
    except Exception as e:
        return await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id, text=str(e))


@router.callback_query(F.data.startswith("moderation_confirm"))
async def process_moderation_confirm(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])

    advertisement = await repo.advertisements.update_advertisement(
        advertisement_id=advertisement_id, is_moderated=True
    )
    operation_type = advertisement.operation_type.value

    photos = [obj.tg_image_hash for obj in advertisement.images]

    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

    if advertisement.operation_type.value == "Аренда":
        chat_id = config.tg_bot.rent_channel_name
        advertisement_message = rent_channel_advertisement_message(advertisement)
    else:
        chat_id = config.tg_bot.buy_channel_name
        advertisement_message = buy_channel_advertisement_message(advertisement)

    media_group = get_media_group(photos, advertisement_message)

    month = datetime.datetime.now().month

    advertisement_data = AdvertisementForReportDTO.model_validate(advertisement, from_attributes=True).model_dump()
    advertisement_data = correct_advertisement_dict(advertisement_data)

    # добавляем запись в таблицу очереди

    if operation_type == 'Покупка':
        await call.bot.send_media_group(
            chat_id=config.tg_bot.base_channel_name,
            media=media_group,
        )

    # TODO: не забыть убрать с комментария при заливке на гитхаб
    fill_report.delay(month=month, operation_type=advertisement.operation_type.value,
                      data=advertisement_data)

    await send_message_to_rent_topic(
        bot=call.bot,
        price=advertisement.price,
        media_group=media_group,
        operation_type=advertisement.operation_type.value
    )

    # получаем все не отправленные объявления из очереди
    # not_sent_advertisements = await repo.advertisement_queue.get_all_not_sent_advertisements()
    # not_sent_advertisements_ids = [item.advertisement_id for item in not_sent_advertisements]
    #
    # if advertisement.id not in not_sent_advertisements_ids:
    #     time_to_send = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    #     await repo.advertisement_queue.add_advertisement_to_queue(advertisement.id, time_to_send)
    # else:
    #     time_to_send = not_sent_advertisements[-1].time_to_send + datetime.timedelta(minutes=5)



    # send_message_by_queue.apply_async(
    #     args=[advertisement.id, advertisement.price, serialize_media_group(media_group), operation_type, chat_id],
    #     eta=time_to_send,
    # )
    #
    # # отправляем сообщения руководителю и агенту
    # await call.message.answer(
    #     f"Объявление добавлено в очередь, будет отправлено в {time_to_send.strftime('%Y-%m-%d %H:%M%:%S')}"
    # )
    # await call.bot.send_message(
    #     user.tg_chat_id,
    #     f"Объявление добавлено в очередь, будет отправлено в {time_to_send.strftime('%Y-%m-%d %H:%M%:%S')}"
    # )


    # remind_agent_to_update_advertisement.apply_async(
    #     args=[advertisement.unique_id, user.tg_chat_id, advertisement.id],
    #     eta=advertisement.reminder_time
    # )


    try:
        # Отправка в базовый канал
        if operation_type == 'Покупка':
            # отложенная отправка в основной канал покупки
            time_to_send = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            time_for_info = datetime.datetime.now() + datetime.timedelta(minutes=5)

            await call.message.answer(f'Объявление в бот будет отправлено в {time_for_info}')
            await call.bot.send_message(user.tg_chat_id, f'Объявление будет отправлено в {time_for_info.strftime("%Y-%m-%d %H:M%:%S")}')
            send_delayed_message.apply_async(
                args=[chat_id, serialize_media_group(media_group)],
                eta=time_to_send,
            )
        elif operation_type == 'Аренда':
            await call.bot.send_media_group(
                chat_id=chat_id,
                media=media_group,
            )

    except Exception as e:
        return await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id,
                                           text=f'ошибка при отправке медиа группы\n{str(e)}')

    await call.message.edit_text("Спасибо! Объявление отправлено в канал")
    await call.bot.send_message(
        chat_id=user.tg_chat_id, text="Объявление прошло модерацию"
    )

    formatted_reminder_time = advertisement.reminder_time.strftime('%Y-%m-%d %H:%M%:%S')
    await call.message.answer(
        f"Уведомление для проверки актуальности отправится агенту в \n<b>{formatted_reminder_time}</b>"
    )
    await call.bot.send_message(
        user.tg_chat_id,
        f'Уведомление для проверки актуальности будет отправлено в \n<b>{formatted_reminder_time}</b>'
    )

    return await call.message.delete()


@router.callback_query(F.data.startswith("for_base_channel"))
async def get_advertisement_for_base_channel(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

    chat_id = config.tg_bot.base_channel_name
    photos = [obj.tg_image_hash for obj in advertisement.images]

    if advertisement.operation_type.value == "Аренда":
        return await call.bot.send_message(user.added_by, "Пропускаем объявление, так как Аренда")

    advertisement_message = buy_channel_advertisement_message(advertisement)

    media_group = get_media_group(photos, advertisement_message)

    try:
        await call.bot.send_media_group(
            chat_id=chat_id,
            media=media_group,
        )
    except Exception as e:
        await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id,
                                    text='Ошибка при отправке в резервный канал')
        return await call.bot.send_message(chat_id=config.tg_bot.main_chat_id, text=f'{chat_id=} {e}')

    await call.message.edit_text("Спасибо! Объявление отправлено в резервный канал")
    await call.bot.send_message(
        chat_id=user.tg_chat_id, text="Объявление отправлено в резервный канал"
    )
    return await call.message.delete()


@router.callback_query(F.data.startswith("moderation_deny"))
async def process_moderation_deny(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    try:
        await call.answer()

        advertisement_id = int(call.data.split(":")[-1])

        advertisement = await repo.advertisements.update_advertisement(
            advertisement_id=advertisement_id, is_moderated=False
        )
        user = await repo.users.get_user_by_id(user_id=advertisement.user_id)

        await state.update_data(user=user, advertisement=advertisement)
        await state.set_state(AdvertisementModerationState.message)

        await call.message.edit_text(
            "Напишите причину, почему данное объявление не прошло модерацию",
            reply_markup=None,
        )
    except Exception as e:
        await call.bot.send_message(chat_id=config.tg_bot.test_main_chat_id, text=str(e))


@router.message(AdvertisementModerationState.message)
async def process_moderation_deny_message(
        message: Message,
        state: FSMContext,
):
    try:
        data = await state.get_data()
        user = data.pop("user")
        advertisement = data.pop("advertisement")

        await message.bot.send_message(
            chat_id=user.tg_chat_id,
            text=f"Объявление <b>{advertisement.name}</b> не прошло модерацию",
        )
        await message.bot.send_message(chat_id=user.tg_chat_id, text=message.text)
        await state.clear()
    except Exception as e:
        await message.bot.send_message(chat_id=config.tg_bot.test_main_chat_id, text=str(e))


@router.callback_query(F.data.startswith("rg_advertisement_delete"))
async def delete_realtor_advertisement(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user_id = advertisement.user_id

    user = await repo.users.get_user_by_id(user_id)

    await call.bot.send_message(
        user.tg_chat_id, f"Объявление {advertisement.name} было удалено"
    )
    await call.message.answer("Объявление успешно удалено")
    await repo.advertisements.delete_advertisement(advertisement_id)


@router.callback_query(F.data.startswith("confirm_advertisement_delete"))
async def confirm_advertisement_delete(
        call: CallbackQuery,
        repo: "RequestsRepo",
):
    await call.answer()
    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)
    user_id = advertisement.user_id

    user = await repo.users.get_user_by_id(user_id)

    await call.bot.send_message(
        user.tg_chat_id,
        f"Объявление {advertisement.name} {advertisement.unique_id} было удалено",
    )
    await call.message.answer("Объявление успешно удалено")
    await repo.advertisements.delete_advertisement(advertisement_id)


@router.callback_query(F.data.startswith("deny_advertisement_delete"))
async def deny_advertisement_delete(
        call: CallbackQuery,
        repo: "RequestsRepo",
        state: FSMContext,
):
    await call.answer()

    advertisement_id = int(call.data.split(":")[-1])
    advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id)

    await call.message.answer("напишите причину отказа")
    await state.set_state(AdvertisementDeletionState.message)
    await state.update_data(advertisement=advertisement)


@router.message(AdvertisementDeletionState.message)
async def process_advertisement_deletion_message(
        message: Message,
        repo: "RequestsRepo",
        state: FSMContext,
):
    data = await state.get_data()
    advertisement = data.pop("advertisement")

    user = await repo.users.get_user_by_id(user_id=advertisement.user_id)
    await message.bot.send_message(
        user.tg_chat_id,
        f"Объявление {advertisement.name} {advertisement.unique_id} не было удалено",
    )
    await message.bot.send_message(user.tg_chat_id, f"Причина: {message.text}")
    await state.clear()
