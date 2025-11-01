from aiogram import Router, types, F
from aiogram.filters import CommandStart

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.utils.helpers import download_file, download_advertisement_photo
from tgbot.utils.image_checker import is_duplicate
from pathlib import Path

_path = Path(__file__).parent

dev_router = Router()


@dev_router.message(CommandStart())
async def dev_start(message: types.Message, repo: RequestsRepo):
    await message.answer('send photo')


@dev_router.message(F.photo)
async def check_photo(message: types.Message, repo: RequestsRepo):
    photo_id = message.photo[-1].file_id

    location = await download_advertisement_photo(bot=message.bot, file_id=photo_id, folder=_path)

    duplicated = await is_duplicate(location, repo)
    for img_id, adv_id in sorted(duplicated, key=lambda x: x[-1]):
        advertisement = await repo.advertisements.get_advertisement_by_id(advertisement_id=adv_id)
        print(advertisement.created_at)