import asyncio
import os
from datetime import datetime

from sqlalchemy.ext.asyncio.session import AsyncSession

from config.loader import load_config
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool


async def delete(adv, repo):
    images = [img.url for img in adv.images]
    for image in images:
        print(image)
        try:
            os.remove(image)
        except Exception as e:
            print(e)
    await repo.advertisements.delete_advertisement(advertisement_id=adv.id)


async def clean_data(session: AsyncSession):
    repo = RequestsRepo(session)

    # Категория продажа - до 01.04.25
    # Категория аренда - до 01.06.25

    advertisements = await repo.advertisements.get_all_advertisements()
    for advertisement in advertisements:
        if advertisement.operation_type.value == 'Аренда' and advertisement.created_at.date() < datetime(2025, 4,
                                                                                                         1).date():
            await delete(advertisement, repo)
            print("АРЕНДА", advertisement.name, advertisement.created_at, )
        elif advertisement.operation_type.value == 'Покупка' and advertisement.created_at.date() < datetime(2025, 6,
                                                                                     1).date():
            await delete(advertisement, repo)
            print("Покупка", advertisement.name, advertisement.created_at, )


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await clean_data(session)


asyncio.run(main())
