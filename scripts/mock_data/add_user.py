import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import read_json
from infrastructure.database.models import User
from infrastructure.database.setup import create_engine, create_session_pool


async def add_mock_user(session: AsyncSession):
    users_json = read_json("users_output.json")
    users = []
    for item in users_json:
        user = User(
            first_name=item["first_name"],
            lastname=item["lastname"],
            fullname=f'{item["first_name"]} {item["lastname"]}',
            phone_number=item["phone_number"],
            tg_username=item["tg_username"],
            role=item["role"],
            tg_chat_id=item["tg_chat_id"],
            added_by=item["added_by"],
        )
        users.append(user)

    session.add_all(users)
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_mock_user(session=session)


asyncio.run(main())
