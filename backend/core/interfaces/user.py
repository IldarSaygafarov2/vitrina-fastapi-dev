from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    id: int
    first_name: Optional[str]
    lastname: Optional[str]
    tg_username: Optional[str]
    phone_number: Optional[str]


class UserAdvertisementObjectDTO(BaseModel):
    id: int
    fullname: Optional[str]
    first_name: Optional[str]
    lastname: Optional[str]
    tg_username: Optional[str]
    phone_number: Optional[str]
    profile_image: Optional[str]


class UserShortDTO(BaseModel):
    id: int
    fullname: Optional[str]


class UserCreateDTO(BaseModel):
    first_name: str
    lastname: str
    phone_number: str
    tg_username: str
    role: str
