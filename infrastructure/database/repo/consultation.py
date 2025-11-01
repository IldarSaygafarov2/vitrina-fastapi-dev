from .base import BaseRepo

from sqlalchemy import insert, select

from infrastructure.database.models import ConsultationRequest


class ConsultationRepo(BaseRepo):
    async def create(self, fullname: str, phone_number: str):
        stmt = (
            insert(ConsultationRequest)
            .values(fullname=fullname, phone_number=phone_number)
            .returning(ConsultationRequest)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_consultations(self):
        stmt = select(ConsultationRequest).order_by(ConsultationRequest.created_at)
        result = await self.session.execute(stmt)
        return result.scalars().all()
