import asyncio
import uuid

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import clean_json
from infrastructure.database.models.advertisement import (
    Advertisement,
)
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.utils.helpers import generate_code


async def add_advertisements(session: AsyncSession):
    repo = RequestsRepo(session)

    advertisements = await repo.advertisements.get_all_advertisements()

    for advertisement in advertisements:
        updated = await repo.advertisements.update_advertisement_unique_id(
            advertisement_id=advertisement.id,
            unique_id=generate_code(),
        )
        print(f"{updated.name} - {updated.unique_id}")

    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_advertisements(session=session)


asyncio.run(main())
