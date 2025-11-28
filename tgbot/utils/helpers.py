import shutil
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot
from aiogram.types import InputMediaPhoto

from backend.app.config import config
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.templates.advertisement_creation import realtor_advertisement_completed_text
from tgbot.templates.messages import (
    rent_channel_advertisement_message,
    buy_channel_advertisement_message,
)


def filter_digits(message: str) -> str:
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
        serialized.append(
            {
                "type": "photo",
                "media": m.media,
                "caption": getattr(m, "caption", None),
                "parse_mode": "HTML",
            }
        )
    return serialized


def deserialize_media_group(media_data: list[dict]) -> list[InputMediaPhoto]:
    return [InputMediaPhoto(**item) for item in media_data]


async def send_message_to_rent_topic(
    bot: Bot,
    price: int,
    operation_type: str,
    media_group: list[InputMediaPhoto],
) -> None:
    """Отправляем сообщение в супер группу фильтруя по цене."""

    topic_data = config.super_group.make_forum_topics_data(operation_type)
    prices = list(topic_data.items())

    # supergroups ids
    rent_supergroup_id = config.super_group.rent_supergroup_id
    buy_supergroup_id = config.super_group.buy_supergroup_id

    supergroup_id = (
        rent_supergroup_id if operation_type == "Аренда" else buy_supergroup_id
    )

    for thread_id, _price in prices:
        a, b = _price

        price_range = list(range(a, b))
        if price not in price_range:
            continue
        await bot.send_media_group(
            chat_id=supergroup_id, message_thread_id=thread_id, media=media_group
        )


def correct_advertisement_dict(data: dict):
    data["created_at"] = data["created_at"].strftime("%d.%m.%Y %H:%M:%S")
    data["category"] = data["category"]["name"]
    data["district"] = data["district"]["name"]
    data["user"] = data["user"]["fullname"] if data.get("user") else None
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
    """Получаем время для проверки актуальности по указанному типу операции"""
    if operation_type == "Покупка":
        return datetime.utcnow() + timedelta(
            minutes=config.reminder_config.buy_reminder_minutes
        )
    return datetime.utcnow() + timedelta(
        minutes=config.reminder_config.rent_reminder_minutes
    )  # для аренды


async def get_advertisement_photos(advertisement_id: int, repo: "RequestsRepo"):
    photos = await repo.advertisement_images.get_advertisement_images(
        advertisement_id=advertisement_id
    )
    return [item.tg_image_hash for item in photos]


async def collect_media_group_for_advertisement(
    advertisement, repo: RequestsRepo
) -> list[InputMediaPhoto]:
    """собираем медиа группу для отправки."""
    advertisement_photos = await get_advertisement_photos(advertisement.id, repo)
    advertisement_message = realtor_advertisement_completed_text(advertisement)
    media_group = get_media_group(advertisement_photos, advertisement_message)
    return media_group


def get_channel_name_and_message_by_operation_type(advertisement) -> tuple[str, str]:
    if advertisement.operation_type.value == "Аренда":
        channel_name = config.tg_bot.rent_channel_name
        advertisement_message = rent_channel_advertisement_message(advertisement)
    else:
        channel_name = config.tg_bot.buy_channel_name
        advertisement_message = buy_channel_advertisement_message(advertisement)

    return channel_name, advertisement_message


async def send_error_message_to_dev(bot: Bot, message: str, exception: Exception) -> None:
    await bot.send_message(
        chat_id=config.tg_bot.main_chat_id, text=f"ошибка {message}"
    )
    await bot.send_message(
        chat_id=config.tg_bot.main_chat_id, text=f"{exception}\n{exception.__class__.__name__}"
    )
