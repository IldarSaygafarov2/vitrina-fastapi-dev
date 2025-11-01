import asyncio

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import clean_json
from infrastructure.database.models import District
from infrastructure.database.setup import create_engine, create_session_pool


async def add_categories(session: AsyncSession):
    cleaned_districts = clean_json("external/districts.json", "id", "name_ru")

    districts = []

    for category in cleaned_districts:
        slug = slugify(category["name"])
        obj = District(
            name=category["name"],
            slug=slug,
            name_uz=category["name_uz"],
        )
        districts.append(obj)
        print("added", category["name"])

    session.add_all(districts)
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_categories(session=session)


asyncio.run(main())
