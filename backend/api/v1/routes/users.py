from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.advertisement import AdvertisementDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.users,
    tags=["Users"],
)


@router.get('/{user_id}/advertisements/')
async def get_user_advertisements(
        user_id: int,
        repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> list[AdvertisementDTO]:
    advertisements = await repo.advertisements.get_user_advertisements(user_id=user_id)
    return advertisements

