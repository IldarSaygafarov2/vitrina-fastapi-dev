from aiogram.filters import BaseFilter
from aiogram.types import Message

from backend.app.config import config


class IsDevFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == config.tg_bot.test_main_chat_id
