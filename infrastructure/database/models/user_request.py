import enum

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.advertisement import OperationType

from .base import Base, created_at
from .mixins.id_int_pk import IntIdMixin


class ObjectType(str, enum.Enum):
    FLAT = "Квартиры"
    COMMERCIAL = "Коммерческая"
    NEW_BUILDING = "Новостройки"
    HOUSE = "Дома"


class UserRequest(Base, IntIdMixin):
    first_name: Mapped[str]
    operation_type: Mapped["OperationType"] = mapped_column(
        ENUM(OperationType),
        default=OperationType.RENT,
        nullable=True,
    )
    object_type: Mapped["ObjectType"] = mapped_column(
        ENUM(ObjectType),
        default=ObjectType.FLAT,
        nullable=True,
    )
    phone_number: Mapped[str]
    message: Mapped[str]

    created_at: Mapped[created_at]
