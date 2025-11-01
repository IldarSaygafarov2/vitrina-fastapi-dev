from datetime import datetime
from pydantic import BaseModel, Field
from infrastructure.database.models.user_request import ObjectType
from infrastructure.database.models.advertisement import OperationType


class UserRequestCreateDTO(BaseModel):
    first_name: str
    operation_type: OperationType
    object_type: ObjectType
    phone_number: str
    message: str


class UserRequestDTO(BaseModel):
    id: int
    first_name: str
    operation_type: OperationType
    object_type: ObjectType
    phone_number: str
    message: str
    created_at: datetime
