import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Category
from config.loader import load_config
from infrastructure.database.setup import create_engine, create_session_pool
from external.db_migrate import clean_json
from slugify import slugify


async def add_categories(session: AsyncSession):
    cleaned_categories = clean_json("external/categories.json", "id", "name_ru")

    categories = []

    for category in cleaned_categories:
        slug = slugify(category["name"])
        obj = Category(
            name=category["name"],
            slug=slug,
            name_uz=category["name_uz"],
        )
        categories.append(obj)
        print("added", category["name"])

    session.add_all(categories)
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_categories(session=session)


asyncio.run(main())
