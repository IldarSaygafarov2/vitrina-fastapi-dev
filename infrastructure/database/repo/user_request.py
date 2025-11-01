from sqlalchemy import insert, select

from infrastructure.database.models import UserRequest
from .base import BaseRepo


class UserRequestRepo(BaseRepo):
    async def create(
        self,
        first_name: str,
        operation_type: str,
        object_type: str,
        phone_number: str,
        message: str,
    ):
        stmt = (
            insert(UserRequest)
            .values(
                first_name=first_name,
                operation_type=operation_type,
                object_type=object_type,
                phone_number=phone_number,
                message=message,
            )
            .returning(UserRequest)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_users_requests(self):
        stmt = select(UserRequest).order_by(UserRequest.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()
