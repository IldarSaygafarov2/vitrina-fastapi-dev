import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import clean_json, read_json
from infrastructure.database.models.advertisement import (
    Advertisement,
    AdvertisementImage,
)
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool


async def add_images(session: AsyncSession):
    repo = RequestsRepo(session)

    advertisements = await repo.advertisements.get_advertisements()
    images = read_json("external/test.json")

    for adv in advertisements:
        for i in images[adv.name]:
            await repo.advertisements.update_advertisement_preview(
                advertisement_id=adv.id,
                url=images[adv.name][0]["photo"],
            )
            await repo.advertisement_images.insert_advertisement_image(
                advertisement_id=adv.id, url=i["photo"], tg_image_hash=""
            )
        print("added photo to adv with name", adv.name)


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_images(session=session)


asyncio.run(main())
