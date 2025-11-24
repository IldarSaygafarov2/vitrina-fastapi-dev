from datetime import datetime

from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from backend.core.filters.advertisement import AdvertisementFilter
from infrastructure.database.models import Advertisement, AdvertisementImage, AdvertisementQueue
from .base import BaseRepo


class AdvertisementRepo(BaseRepo):
    async def get_advertisements_by_month(self, month: int, operation_type: str):
        query = (
            select(Advertisement)
            .filter(func.extract("month", Advertisement.created_at) == month)
            .where(Advertisement.operation_type == operation_type)
            .options(
                selectinload(Advertisement.user),
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
            )
            .where(Advertisement.is_moderated == True)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_advertisement(
            self,
            category: int,
            district: int,
            title: str,
            title_uz: str,
            description: str,
            description_uz: str,
            address: str,
            address_uz: str,
            creation_year: int,
            price: int,
            rooms_quantity: int,
            quadrature: int,
            floor_from: int,
            floor_to: int,
            house_quadrature_from: int,
            house_quadrature_to: int,
            user: int,
            preview: str,
            operation_type,
            property_type,
            repair_type,
            operation_type_uz,
            property_type_uz,
            repair_type_uz,
            unique_id,
            owner_phone_number: str,
            reminder_time: datetime,
            is_reminded: bool = False,
    ):
        stmt = (
            insert(Advertisement)
            .values(
                unique_id=unique_id,
                preview=preview,
                operation_type=operation_type,
                category_id=category,
                district_id=district,
                name=title,
                name_uz=title_uz,
                description=description,
                description_uz=description_uz,
                address=address,
                address_uz=address_uz,
                property_type=property_type,
                creation_year=creation_year,
                price=price,
                rooms_quantity=rooms_quantity,
                quadrature=quadrature,
                floor_from=floor_from,
                floor_to=floor_to,
                house_quadrature_from=house_quadrature_from,
                house_quadrature_to=house_quadrature_to,
                user_id=user,
                repair_type=repair_type,
                operation_type_uz=operation_type_uz,
                property_type_uz=property_type_uz,
                repair_type_uz=repair_type_uz,
                owner_phone_number=owner_phone_number,
                reminder_time=reminder_time,
                is_reminded=is_reminded,
            )
            .options(
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
            )
            .returning(Advertisement)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_advertisement_is_reminded(self, advertisement_id: int):
        stmt = (
            update(Advertisement)
            .where(Advertisement.id == advertisement_id)
            .values(is_reminded=True)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_all_not_reminded_advertisements(self):
        stmt = (
            select(Advertisement.id, Advertisement.user_id, Advertisement.reminder_time)
            .where(Advertisement.is_reminded == False)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_advertisement_reminder_time(self, advertisement_id: int, reminder_time: datetime):
        stmt = (
            update(Advertisement)
            .where(Advertisement.id == advertisement_id)
            .values(reminder_time=reminder_time)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_advertisement_by_unique_id(self, unique_id: str):
        query = (
            select(Advertisement)
            .where(Advertisement.unique_id == unique_id)
            .options(
                selectinload(Advertisement.user),
                selectinload(Advertisement.images),
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_advertisements(self, limit: int = 15, offset: int = 0):
        stmt = (
            select(Advertisement)
            .options(selectinload(Advertisement.images))
            .limit(limit)
            .offset(offset)
            .filter_by(is_moderated=True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_filtered_advertisements(self, _filter: AdvertisementFilter):
        # Создаем базовый запрос для фильтрации
        query = select(Advertisement).filter(Advertisement.is_moderated == True)

        if _filter.rooms:
            rooms = [int(i) for i in _filter.rooms.split(",")]
            query = query.filter(Advertisement.rooms_quantity.in_(rooms))
        if _filter.operation_type:
            query = query.filter(Advertisement.operation_type == _filter.operation_type)
        if _filter.property_type:
            query = query.filter(Advertisement.property_type == _filter.property_type)
        if _filter.repair_type:
            query = query.filter(Advertisement.repair_type == _filter.repair_type)
        if _filter.floor_from:
            query = query.filter(Advertisement.floor_from >= _filter.floor_from)
        if _filter.floor_to:
            query = query.filter(Advertisement.floor_to <= _filter.floor_to)
        if _filter.house_quadrature_from:
            query = query.filter(
                Advertisement.house_quadrature_from >= _filter.house_quadrature_from
            )
        if _filter.house_quadrature_to:
            query = query.filter(
                Advertisement.house_quadrature_to <= _filter.house_quadrature_to
            )
        if _filter.price_from:
            query = query.filter(Advertisement.price >= _filter.price_from)
        if _filter.price_to:
            query = query.filter(Advertisement.price <= _filter.price_to)
        if _filter.quadrature_from:
            query = query.filter(Advertisement.quadrature >= _filter.quadrature_from)
        if _filter.quadrature_to:
            query = query.filter(Advertisement.quadrature <= _filter.quadrature_to)
        if _filter.category_id:
            query = query.filter(Advertisement.category_id == _filter.category_id)
        if _filter.district_id:
            query = query.filter(Advertisement.district_id == _filter.district_id)

        # Подсчитываем общее количество отфильтрованных записей (без пагинации)
        count_query = query.with_only_columns(func.count().label("total_count"))

        # Выполняем запрос для подсчета количества
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar()

        # Пагинация (основной запрос)
        query = query.order_by(
            desc(Advertisement.created_at)
        )  # Сортировка уже после подсчета
        query = query.offset(_filter.offset).limit(_filter.limit)
        result = await self.session.execute(query)

        # Возвращаем результат: данные и общее количество
        return {"data": result.scalars().all(), "total_count": total_count}

    async def get_advertisement_by_id(self, advertisement_id: int):
        stmt = (
            select(Advertisement)
            .options(
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
                selectinload(Advertisement.user),
                selectinload(Advertisement.images),
            )
            .where(Advertisement.id == advertisement_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_advertisement_by_title(self, title: str):
        stmt = select(Advertisement).where(Advertisement.name == title)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_total_advertisements(self):
        stmt = select(func.count(Advertisement.id)).where(
            Advertisement.is_moderated == True
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_user_advertisements(self, user_id: int):
        stmt = (
            select(Advertisement)
            .options(
                selectinload(Advertisement.images),
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
            )
            .where(Advertisement.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_advertisement_preview(self, advertisement_id: int, url: str):
        stmt = (
            update(Advertisement)
            .values(preview=url)
            .where(Advertisement.id == advertisement_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_advertisement(self, advertisement_id: int, **fields):
        stmt = (
            update(Advertisement)
            .values(**fields)
            .where(Advertisement.id == advertisement_id)
            .options(
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
                selectinload(Advertisement.user),
                selectinload(Advertisement.images),
            )
            .returning(Advertisement)
        )
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated.scalar_one()

    async def delete_advertisement(self, advertisement_id: int):
        stmt = delete(Advertisement).where(Advertisement.id == advertisement_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_all_advertisements(self):
        stmt = select(Advertisement).options(selectinload(Advertisement.images))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_moderated_advertisements(self, operation_type: str):
        stmt = (
            select(Advertisement)
            .where(Advertisement.is_moderated == True)
            .where(Advertisement.operation_type == operation_type)
            .options(
                selectinload(Advertisement.user),
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
                selectinload(Advertisement.images),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_advertisements_by_operation_type(self, operation_type: str) -> int:
        stmt = (
            select(func.count())
            .where(Advertisement.operation_type == operation_type)
            .where(Advertisement.is_moderated == True)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_advertisement_unique_id(
            self, advertisement_id: int, unique_id: str
    ):
        stmt = (
            update(Advertisement)
            .values(unique_id=unique_id)
            .where(Advertisement.id == advertisement_id)
            .returning(Advertisement)
        )
        updated = await self.session.execute(stmt)
        await self.session.commit()
        return updated.scalar_one()

    async def get_all_unique_ids(self):
        stmt = select(Advertisement.unique_id).distinct()
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_advertisements_by_category_id_and_operation_type(
            self, category_id: int, operation_type: str
    ):
        stmt = (
            select(Advertisement)
            .where(Advertisement.category_id == category_id)
            .where(Advertisement.operation_type == operation_type)
            .where(Advertisement.is_moderated == True)
            .limit(12)
            .options(selectinload(Advertisement.images))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_advertisements_by_operation_type(
            self, operation_type: str, limit: int = 20, offset: int = 0
    ):
        stmt = (
            select(Advertisement)
            .options(
                selectinload(Advertisement.user),
                selectinload(Advertisement.category),
                selectinload(Advertisement.district),
            )
            .where(Advertisement.operation_type == operation_type)
            .where(Advertisement.is_moderated == True)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class AdvertisementImageRepo(BaseRepo):
    async def insert_advertisement_image(
            self, advertisement_id: int, url: str, tg_image_hash: str, image_hash: str
    ):
        stmt = insert(AdvertisementImage).values(
            advertisement_id=advertisement_id,
            url=url,
            tg_image_hash=tg_image_hash,
            image_hash=image_hash,
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_image_by_id(self, image_id: int):
        stmt = select(AdvertisementImage).where(AdvertisementImage.id == image_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_image(self, image_id: int, url: str, tg_image_hash: str):
        stmt = (
            update(AdvertisementImage)
            .values(url=url, tg_image_hash=tg_image_hash)
            .where(AdvertisementImage.id == image_id)
            .returning(AdvertisementImage)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_advertisement_images(self, advertisement_id: int):
        query = select(AdvertisementImage).where(
            AdvertisementImage.advertisement_id == advertisement_id
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_images(self):
        query = select(AdvertisementImage).where(AdvertisementImage.image_hash == None)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_image_hash(self, image_id: int, image_hash: str):
        query = (
            update(AdvertisementImage)
            .values(image_hash=image_hash)
            .where(AdvertisementImage.id == image_id)
            .returning(AdvertisementImage)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()

    async def get_all_hashes(self):
        query = select(AdvertisementImage).where(AdvertisementImage.image_hash != None)
        result = await self.session.execute(query)
        return result.scalars().all()


class AdvertisementQueueRepo(BaseRepo):
    async def add_advertisement_to_queue(self, advertisement_id: int, time_to_send: datetime | None = None):
        stmt = (
            insert(AdvertisementQueue)
            .values(advertisement_id=advertisement_id, time_to_send=time_to_send)
            .returning(AdvertisementQueue)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_advertisement_queue(self, advertisement_id: int):
        stmt = (
            update(AdvertisementQueue)
            .values(is_sent=True)
            .where(AdvertisementQueue.advertisement_id == advertisement_id)
            .returning(AdvertisementQueue)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_all_not_sent_advertisements(self):
        stmt = (
            select(AdvertisementQueue)
            .where(AdvertisementQueue.is_sent == False)
            .order_by(AdvertisementQueue.time_to_send)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

