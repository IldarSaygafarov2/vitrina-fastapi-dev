from .base import BaseRepo
from sqlalchemy import (
    select,
    insert,
    update,
    delete,
)
from infrastructure.database.models import Category
from infrastructure.utils.slugifier import generate_slug


class CategoryRepo(BaseRepo):
    async def get_categories(self):
        stmt = select(Category)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int):
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_category_id_by_name(self, category_name: str):
        stmt = select(Category.id).where(Category.name == category_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_category_by_slug(self, category_slug: str):
        stmt = select(Category).where(Category.slug == category_slug)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_category(self, category_name: str, category_name_uz: str):
        slug = generate_slug(category_name)
        stmt = (
            insert(Category)
            .values(
                name=category_name,
                name_uz=category_name_uz,
                slug=slug,
            )
            .returning(Category)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def delete_category(self, category_slug: str):
        stmt = delete(Category).where(Category.slug == category_slug)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_category(
        self,
        category_slug: int,
        category_name: str,
    ):
        slug = generate_slug(category_name)
        stmt = (
            update(Category)
            .values(
                name=category_name,
                slug=slug,
            )
            .where(Category.slug == category_slug)
            .returning(Category)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
