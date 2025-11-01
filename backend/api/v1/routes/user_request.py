from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_google_sheet, get_repo
from backend.core.interfaces.user_request import UserRequestCreateDTO, UserRequestDTO
from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.googlesheets.main import GoogleSheet

router = APIRouter(
    prefix=config.api_prefix.v1.request,
    tags=["Users requests"],
)


@router.post("/add")
async def add_user_request(
    request_data: UserRequestCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
    google_sheet: Annotated[GoogleSheet, Depends(get_google_sheet)],
) -> UserRequestDTO:
    new_request = await repo.user_request.create(
        first_name=request_data.first_name,
        phone_number=request_data.phone_number,
        operation_type=request_data.operation_type,
        object_type=request_data.object_type,
        message=request_data.message,
    )
    reqs = []
    users_requests = await repo.user_request.get_users_requests()
    for req in users_requests:
        reqs.append(
            [
                req.first_name,
                req.operation_type.value,
                req.object_type.value,
                req.phone_number,
                req.message,
                req.created_at.strftime("%Y:%m:%d %H:%M:%S"),
            ]
        )

    google_sheet.update(worksheet_name="Заявки пользователей", lists=reqs)
    return UserRequestDTO.model_validate(new_request, from_attributes=True)
