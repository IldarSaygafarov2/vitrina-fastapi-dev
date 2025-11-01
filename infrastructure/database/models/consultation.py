from sqlalchemy.orm import Mapped

from .base import Base, created_at
from .mixins.id_int_pk import IntIdMixin


class ConsultationRequest(Base, IntIdMixin):
    fullname: Mapped[str]
    phone_number: Mapped[str]
    created_at: Mapped[created_at]
