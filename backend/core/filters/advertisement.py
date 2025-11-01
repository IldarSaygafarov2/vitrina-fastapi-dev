import enum
from typing import Optional

from pydantic import BaseModel, Field


class AdvertisementOperationType(str, enum.Enum):
    buy = "BUY"
    rent = "RENT"


class AdvertisementPropertyType(str, enum.Enum):
    new = "NEW"
    old = "OLD"


class AdvertisementRepairType(str, enum.Enum):
    WITH = "WITH"
    WITHOUT = "WITHOUT"
    DESIGNED = "DESIGNED"
    ROUGH = "ROUGH"
    PRE_FINISHED = "PRE_FINISHED"


class AdvertisementFilter(BaseModel):
    operation_type: Optional[AdvertisementOperationType] = Field(None)
    property_type: Optional[AdvertisementPropertyType] = Field(None)
    repair_type: AdvertisementRepairType = Field(None)
    floor_from: Optional[int] = Field(None)
    floor_to: Optional[int] = Field(None)
    house_quadrature_from: Optional[int] = Field(None)
    house_quadrature_to: Optional[int] = Field(None)
    price_from: Optional[int] = Field(None)
    price_to: Optional[int] = Field(None)
    quadrature_from: Optional[int] = Field(None)
    quadrature_to: Optional[int] = Field(None)
    rooms: Optional[str] = Field(None)
    category_id: Optional[int] = Field(None)
    district_id: Optional[int] = Field(None)

    limit: Optional[int] = Field(15)
    offset: Optional[int] = Field(0)
