import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from config.loader import load_config
from external.db_migrate import read_json
from infrastructure.database.models.advertisement import Advertisement
from infrastructure.database.setup import create_engine, create_session_pool
from datetime import datetime


async def add_advertisements(session: AsyncSession):
    advertisements = read_json("buy_6_output_clean.json")


    result = []

    for adv in advertisements:
        obj = Advertisement(
            name=adv['name'],
            house_quadrature_from=adv['house_quadrature_from'],
            house_quadrature_to=adv['house_quadrature_to'],
            creation_year=adv['creation_year'],
            property_type=adv['property_type'],
            repair_type=adv['repair_type'],
            description=adv['description'],
            address=adv['address'],
            price=adv['price'],
            quadrature_from=adv['quadrature_from'],
            quadrature_to=adv['quadrature_to'],
            floor_from=adv['floor_from'],
            floor_to=adv['floor_to'],
            id=adv['id'],
            operation_type=adv['operation_type'],
            district_id=adv['district_id'],
            category_id=adv['category_id'],
            user_id=adv['user_id'],
            name_uz=adv['name_uz'],
            description_uz=adv['description_uz'],
            address_uz=adv['address_uz'],
            property_type_uz=adv['property_type_uz'],
            operation_type_uz=adv['operation_type_uz'],
            repair_type_uz=adv['repair_type_uz'],
            preview=adv['preview'],
            is_moderated=adv['is_moderated'],
            created_at=datetime.strptime(adv['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z'),
            unique_id=adv['unique_id'],
            rooms_quantity=adv['rooms_quantity'],
            quadrature=adv['quadrature'],
            owner_phone_number=adv['owner_phone_number'],
            for_base_channel=adv['for_base_channel'],
        )
        result.append(obj)

    session.add_all(result)
    await session.commit()


async def main():
    config = load_config(".env")
    engine = create_engine(config.db)
    session_pool = create_session_pool(engine=engine)

    async with session_pool() as session:
        await add_advertisements(session=session)


asyncio.run(main())
