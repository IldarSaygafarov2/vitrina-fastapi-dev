from pydantic import BaseModel


class ConsultationCreateDTO(BaseModel):
    fullname: str
    phone_number: str


class ConsultationDTO(BaseModel):
    id: int
    fullname: str
    phone_number: str
