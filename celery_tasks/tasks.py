import time
from datetime import datetime, timedelta

from backend.app.config import config
from celery_tasks.app import celery_app_dev
from tgbot.keyboards.user.inline import is_advertisement_actual_kb
from tgbot.misc.constants import MONTHS_DICT
from tgbot.utils.google_sheet import (
    client_init_json,
    get_table_by_url,
    fill_row_with_data,
)
from tgbot.utils.helpers import deserialize_media_group
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.utils.helpers import send_message_to_rent_topic


@celery_app_dev.task
def fill_report(month: int, data: dict, operation_type: str):
    client = client_init_json()

    spread = None
    if operation_type == "Аренда":
        spread = get_table_by_url(client, config.report_sheet.rent_report_sheet_link)
    elif operation_type == "Покупка":
        spread = get_table_by_url(client, config.report_sheet.buy_report_sheet_link)

    fill_row_with_data(spread, worksheet_name=MONTHS_DICT[month], data=data)
    time.sleep(2)


@celery_app_dev.task
def send_delayed_message(chat_id, media_group):
    from aiogram import Bot
    import asyncio

    async def send_media_group():
        bot = Bot(token=config.tg_bot.token)
        _media = deserialize_media_group(media_group)
        await bot.send_media_group(chat_id=chat_id, media=_media)
        await bot.session.close()

    asyncio.run(send_media_group())


@celery_app_dev.task
def remind_agent_to_update_advertisement(unique_id, agent_chat_id: int, advertisement_id: int):
    import asyncio
    from aiogram import Bot

    async def send_reminder():
        bot = Bot(token=config.tg_bot.token)
        msg = f"""
Объявление: №{unique_id} актуально?
"""
        await bot.send_message(
            agent_chat_id, msg, parse_mode='HTML', reply_markup=is_advertisement_actual_kb(advertisement_id)
        )
        await bot.session.close()

    asyncio.run(send_reminder())


@celery_app_dev.task
def remind_agent_to_update_advertisement_extended(
        advertisement_unique_id,
        advertisement_id,
        agent_chat_id,
        media_group
):
    import asyncio
    from aiogram import Bot

    async def send_reminder():
        bot = Bot(token=config.tg_bot.token)
        await bot.send_message(agent_chat_id, "Проверка актуальности")
        await bot.send_media_group(chat_id=agent_chat_id, media=media_group)
        await bot.send_message(
            chat_id=agent_chat_id,
            text=f"Объявление: №{advertisement_unique_id} актуально?",
            reply_markup=is_advertisement_actual_kb(advertisement_id)
        )

        await bot.session.close()

    asyncio.run(send_reminder())

@celery_app_dev.task
def send_message_by_queue(
        advertisement_id,
        price,
        media_group,
        operation_type,
        channel_name,
        user_chat_id,
        director_chat_id
):
    import asyncio
    from aiogram import Bot

    # bot object
    bot = Bot(token=config.tg_bot.token)

    # database connection
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async def send_test():
        async with session_pool() as session:
            repo = RequestsRepo(session)

        # обновляем объявление в очереди
        await repo.advertisement_queue.update_advertisement_queue(advertisement_id=advertisement_id)

        await send_message_to_rent_topic(
            bot=bot,
            price=price,
            media_group=media_group,
            operation_type=operation_type
        )

        try:
            await bot.send_media_group(
                chat_id=channel_name,
                media=media_group,
            )
        except Exception as e:
            await bot.send_message(chat_id=config.tg_bot.test_main_chat_id,
                                               text=f'ошибка при отправке медиа группы\n{str(e)}')

        await bot.session.close()  # closing bot session

    asyncio.run(send_test())
