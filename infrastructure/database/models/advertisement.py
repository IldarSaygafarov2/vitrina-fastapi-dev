import enum
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, created_at
from .mixins.id_int_pk import IntIdMixin


class PropertyType(str, enum.Enum):
    NEW = "Новостройка"
    OLD = "Вторичный фонд"


class PropertyTypeUz(str, enum.Enum):
    NEW = "Yangi bino"
    OLD = "Ikkilamchi fond"


class OperationType(str, enum.Enum):
    BUY = "Покупка"
    RENT = "Аренда"


class OperationTypeUz(str, enum.Enum):
    BUY = "Sotib olish"
    RENT = "Ijara"


class RepairType(str, enum.Enum):
    WITH = "С ремонтом"
    DESIGNED = "Дизайнерский ремонт"
    WITHOUT = "Без ремонта"
    ROUGH = "Черновая"
    PRE_FINISHED = "Предчистовая"


class RepairTypeUz(str, enum.Enum):
    WITH = "Ta’mirlangan"
    WITHOUT = "Ta'mirsiz"
    DESIGNED = "Dizaynerlik ta’mir"
    ROUGH = "Qora Suvoq"
    PRE_FINISHED = "Tugallanmagan ta’mir"


class Advertisement(Base, IntIdMixin):
    name: Mapped[str] = mapped_column(String, index=True)
    name_uz: Mapped[str] = mapped_column(String, nullable=True)

    unique_id: Mapped[str] = mapped_column(
        String(6), nullable=True
    )

    owner_phone_number: Mapped[str] = mapped_column(nullable=True)

    house_quadrature_from: Mapped[int] = mapped_column(default=0)
    house_quadrature_to: Mapped[int] = mapped_column(default=0)
    creation_year: Mapped[int] = mapped_column(default=0)

    property_type: Mapped["PropertyType"] = mapped_column(
        ENUM(PropertyType), default=PropertyType.NEW
    )
    property_type_uz: Mapped["PropertyTypeUz"] = mapped_column(
        ENUM(PropertyTypeUz),
        default=PropertyTypeUz.NEW,
        nullable=True,
    )

    operation_type: Mapped["OperationType"] = mapped_column(
        ENUM(OperationType), default=OperationType.RENT
    )
    operation_type_uz: Mapped["OperationTypeUz"] = mapped_column(
        ENUM(OperationTypeUz),
        default=OperationTypeUz.RENT,
        nullable=True,
    )

    repair_type: Mapped["RepairType"] = mapped_column(
        ENUM(RepairType), default=RepairType.WITH
    )
    repair_type_uz: Mapped["RepairTypeUz"] = mapped_column(
        ENUM(RepairTypeUz),
        default=RepairTypeUz.WITH,
        nullable=True,
    )

    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="SET NULL"),
        nullable=True,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    description: Mapped[str]
    description_uz: Mapped[str] = mapped_column(nullable=True)

    address: Mapped[str]
    address_uz: Mapped[str] = mapped_column(nullable=True)

    price: Mapped[int]
    updated_price: Mapped[int] = mapped_column(default=0, nullable=True)
    rooms_quantity: Mapped[int] = mapped_column(nullable=True)
    quadrature_from: Mapped[int] = mapped_column(nullable=True)
    quadrature_to: Mapped[int] = mapped_column(nullable=True)

    quadrature: Mapped[int] = mapped_column(nullable=True)

    floor_from: Mapped[int]
    floor_to: Mapped[int]
    is_moderated: Mapped[bool] = mapped_column(nullable=True)

    preview: Mapped[str] = mapped_column(nullable=True)
    for_base_channel: Mapped[bool] = mapped_column(nullable=True, default=False)
    reminder_time: Mapped[datetime] = mapped_column(nullable=True)
    is_reminded: Mapped[bool] = mapped_column(nullable=True)

    images: Mapped[list["AdvertisementImage"]] = relationship(
        back_populates="advertisement"
    )
    category = relationship("Category", back_populates="advertisement")
    district = relationship("District", back_populates="advertisement")
    user = relationship("User", back_populates="advertisement")
    queue = relationship("AdvertisementQueue", back_populates="advertisement")
    created_at: Mapped[created_at]


class AdvertisementImage(Base, IntIdMixin):
    url: Mapped[str]
    tg_image_hash: Mapped[str] = mapped_column(nullable=True)
    image_hash: Mapped[str] = mapped_column(String(16), nullable=True)

    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    advertisement: Mapped["Advertisement"] = relationship(back_populates="images")


class AdvertisementQueue(Base, IntIdMixin):
    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    advertisement: Mapped["Advertisement"] = relationship(back_populates="queue")
    time_to_send: Mapped[datetime] = mapped_column(nullable=True)
    is_sent: Mapped[bool] = mapped_column(default=False)