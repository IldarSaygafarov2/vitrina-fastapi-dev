import asyncio

from backend.app.config import config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from tgbot.utils.image_checker import get_image_hash_as_int, get_image_hash_hex


async def update_images_hash(session):
    repo = RequestsRepo(session)

    images = await repo.advertisement_images.get_all_images()
    for idx, image in enumerate(images, start=1):
        try:
            image_hash = get_image_hash_hex(image.url)
        except Exception as e:
            image_hash = ''
            print(e)
        updated = await repo.advertisement_images.update_image_hash(image_id=image.id, image_hash=image_hash)
        print(idx, updated.url, updated.image_hash)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await update_images_hash(session)


asyncio.run(main())
