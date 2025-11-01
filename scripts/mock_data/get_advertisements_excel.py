import asyncio
import pprint

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from infrastructure.database.models.advertisement import Advertisement
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool


async def get_advertisements(session: AsyncSession):
    repo = RequestsRepo(session)

    ads = await repo.advertisements.get_all_advertisements()

    data = []

    for ad in ads:
        category = await repo.categories.get_category_by_id(category_id=ad.category_id)
        data.append((ad.unique_id, ad.name, category.name))

    array = pd.DataFrame(data, columns=["unique_id", "name", "category"])
    array.to_excel("external/advertisements.xlsx", index=False)


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await get_advertisements(session)


asyncio.run(main())
