import math

from fastapi import APIRouter, Depends
from backend.app.config import config
from backend.core.interfaces.advertisement import AdvertisementForReportDTO, PaginatedAdvertisementForReportDTO

from infrastructure.database.repo.requests import RequestsRepo

from backend.app.dependencies import get_repo
from typing import Annotated



dev_router = APIRouter(prefix=config.api_prefix.v1.dev, tags=['Dev Routes'])


@dev_router.get('/advertisements/', response_model=PaginatedAdvertisementForReportDTO)
async def get_all_advertisements(
        repo: Annotated[RequestsRepo, Depends(get_repo)],
        operation_type: str,
        page: int = 1,
        page_size: int = 20,

):
    # считаем общее количество
    total = await repo.advertisements.count_advertisements_by_operation_type(operation_type)

    # вычисляем смещение
    offset = (page - 1) * page_size

    # получаем данные
    advertisements = await repo.advertisements.get_advertisements_by_operation_type(
        operation_type=operation_type,
        limit=page_size,
        offset=offset,
    )

    advertisements = [
        AdvertisementForReportDTO.model_validate(obj, from_attributes=True)
        for obj in advertisements
    ]

    pages = math.ceil(total / page_size) if page_size else 1

    return PaginatedAdvertisementForReportDTO(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        advertisements=advertisements,
    )