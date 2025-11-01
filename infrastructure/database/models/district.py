from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins.id_int_pk import IntIdMixin


class District(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    name_uz: Mapped[str] = mapped_column(nullable=True)

    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    advertisement = relationship("Advertisement", back_populates="district")
