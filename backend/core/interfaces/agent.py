from typing import Optional
from pydantic import BaseModel

from backend.core.interfaces.advertisement import AdvertisementDTO


class AgentListDTO(BaseModel):
    id: int
    first_name: Optional[str]
    lastname: Optional[str]
    tg_username: Optional[str]
    phone_number: Optional[str]


class AgentDetailDTO(BaseModel):
    id: int
    first_name: Optional[str]
    lastname: Optional[str]
    tg_username: Optional[str]
    phone_number: Optional[str]
    user_photo: Optional[str]
    advertisements: list[Optional[AdvertisementDTO]]
