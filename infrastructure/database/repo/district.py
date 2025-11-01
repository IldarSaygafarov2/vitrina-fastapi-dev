from sqlalchemy import delete, insert, select, update

from infrastructure.database.models import District
from infrastructure.utils.slugifier import generate_slug
from .base import BaseRepo


class DistrictRepo(BaseRepo):
    async def get_districts(self):
        stmt = select(District)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_district_by_id(self, district_id: int):
        stmt = select(District).where(District.id == district_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_district_by_slug(self, district_slug: str):
        stmt = select(District).where(District.slug == district_slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_district_id_by_name(self, district_name: str):
        stmt = select(District.id).where(District.name == district_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_district(self, district_name: str, district_name_uz: str):
        slug = generate_slug(district_name)
        stmt = (
            insert(District)
            .values(
                name=district_name,
                name_uz=district_name_uz,
                slug=slug,
            )
            .returning(District)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def update_district(
        self,
        district_slug: str,
        distict_name: str,
    ):
        slug = generate_slug(distict_name)
        stmt = (
            update(District)
            .values(
                name=distict_name,
                slug=slug,
            )
            .where(District.slug == district_slug)
            .returning(District)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_district(self, district_slug: int):
        stmt = delete(District).where(District.slug == district_slug)
        await self.session.execute(stmt)
        await self.session.commit()
