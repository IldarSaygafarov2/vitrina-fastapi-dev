from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.filters.advertisement import AdvertisementFilter
from backend.core.interfaces.advertisement import (
    AdvertisementDetailDTO,
    AdvertisementDTO,
    PaginatedAdvertisementDTO,
)
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.advertisements,
    tags=["Advertisements"],
)


@router.get("/")
async def get_advertisements(
    filters: Annotated[AdvertisementFilter, Query()],
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> PaginatedAdvertisementDTO:

    advertisements = await repo.advertisements.get_filtered_advertisements(filters)
    count = advertisements["total_count"]

    advertisements = [
        AdvertisementDTO.model_validate(obj, from_attributes=True)
        for obj in advertisements["data"]
    ]

    return PaginatedAdvertisementDTO(
        total=count,
        limit=filters.limit,
        offset=filters.offset,
        results=advertisements,
    )


@router.get("/{advertisement_id}")
async def get_advertisement(
    advertisement_id: int,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
) -> AdvertisementDetailDTO | dict:

    _advertisement = await repo.advertisements.get_advertisement_by_id(
        advertisement_id=advertisement_id
    )
    advertisement = AdvertisementDetailDTO.model_validate(
        _advertisement, from_attributes=True
    )

    related_objects = (
        await repo.advertisements.get_advertisements_by_category_id_and_operation_type(
            category_id=advertisement.category.id,
            operation_type=_advertisement.operation_type,
        )
    )

    advertisement.related_objects = related_objects

    advertisement.images = sorted(
        [i.model_dump() for i in advertisement.images],
        key=lambda l: l["id"],
    )

    if advertisement is None:
        return {"detail": "Advertisement not found"}

    return advertisement


@router.get("/unique/{unique_id}", response_model=AdvertisementDTO)
async def get_advertisement_by_unique_id(
    unique_id: str,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    advertisement = await repo.advertisements.get_advertisement_by_unique_id(
        unique_id=unique_id
    )
    if advertisement is None:
        return {"detail": "Advertisement not found"}
    return AdvertisementDTO.model_validate(advertisement, from_attributes=True)
