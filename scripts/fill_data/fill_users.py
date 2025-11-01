import asyncio

from external.db_migrate import read_json
from infrastructure.database.repo.requests import RequestsRepo

from config.loader import load_config
from infrastructure.database.setup import create_engine, create_session_pool


config = load_config('.env')


async def fill_users(session):
    repo = RequestsRepo(session)

    users_json = read_json("users_output.json")

    for user in users_json:
        await repo.users._create_user(
            id=user['id'],
            profile_image=user['profile_image'],
            profile_image_hash=user['profile_image_hash'],
            first_name=user['first_name'],
            lastname=user['lastname'],
            added_by=user['added_by'],
            role=user['role'],
            tg_username=user['tg_username'],
            phone_number=user['phone_number'],
        )
        print(user)


async def main():
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        await fill_users(session)


asyncio.run(main())