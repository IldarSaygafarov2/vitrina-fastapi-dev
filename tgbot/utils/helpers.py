import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path


from aiogram import Bot
from aiogram.types import InputMediaPhoto

from backend.app.config import config


def read_json(file_path: str):
    with open(file_path, mode='r', encoding='utf-8') as f:
        return json.load(f)


def filter_digits(message: str):
    return "".join(list(filter(lambda i: i.isdigit(), message)))


def get_media_group(photos, message: str | None = None) -> list[InputMediaPhoto]:
    media_group: list[InputMediaPhoto] = [
        (
            InputMediaPhoto(media=img, caption=message)
            if i == 0
            else InputMediaPhoto(media=img)
        )
        for i, img in enumerate(photos)
    ]
    return media_group


def serialize_media_group(media_group: list[InputMediaPhoto]) -> list[dict]:
    serialized = []
    for m in media_group:
        serialized.append({
            "type": "photo",
            "media": m.media,
            "caption": getattr(m, "caption", None),
            "parse_mode": "HTML",
        })
    return serialized


def deserialize_media_group(media_data: list[dict]) -> list[InputMediaPhoto]:
    return [InputMediaPhoto(**item) for item in media_data]


async def send_message_to_rent_topic(
        bot: Bot,
        price: int,
        operation_type: str,
        media_group: list[InputMediaPhoto],
):
    topic_data = config.super_group.make_forum_topics_data(operation_type)
    prices = list(topic_data.items())

    # supergroups ids
    rent_supergroup_id = config.super_group.rent_supergroup_id
    buy_supergroup_id = config.super_group.buy_supergroup_id

    supergroup_id = rent_supergroup_id if operation_type == 'Аренда' else buy_supergroup_id

    for thread_id, _price in prices:
        a, b = _price

        price_range = list(range(a, b))
        if price not in price_range:
            continue
        await bot.send_media_group(
            chat_id=supergroup_id,
            message_thread_id=thread_id,
            media=media_group
        )


def correct_advertisement_dict(data: dict):
    data['created_at'] = data['created_at'].strftime("%d.%m.%Y %H:%M:%S")
    data['category'] = data['category']['name']
    data['district'] = data['district']['name']
    data['user'] = data['user']['fullname'] if data.get('user') else None
    return data


async def download_file(bot: Bot, file_id: str):
    preview_file_obj = await bot.get_file(file_id)
    filename = preview_file_obj.file_path.split("/")[-1]
    file = await bot.download_file(preview_file_obj.file_path)
    return file, filename


async def download_advertisement_photo(bot: Bot, file_id: str, folder: Path):
    file, filename = await download_file(bot, file_id)
    location = folder / filename
    with open(location, "wb") as f:
        shutil.copyfileobj(file, f)  # type: ignore
    return location


def get_reminder_time_by_operation_type(operation_type: str) -> datetime:
    if operation_type == 'Покупка':
        return datetime.utcnow() + timedelta(days=config.reminder_config.buy_reminder_days)
    return datetime.utcnow() + timedelta(days=config.reminder_config.rent_reminder_days)  # для аренды

