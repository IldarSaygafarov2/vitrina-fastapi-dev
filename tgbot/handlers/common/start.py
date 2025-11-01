from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tgbot.filters.common import CommonFilter

router = Router()
router.message.filter(CommonFilter())


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Добро пожаловать в бот Vitrina")
