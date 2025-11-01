from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.district import DistrictCreateDTO, DistrictDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.districts,
    tags=["Districts"],
)


@router.get("/", response_model=list[DistrictDTO])
async def get_districts(
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    districts = await repo.districts.get_districts()
    return districts


@router.post("/create", response_model=DistrictDTO)
async def create_district(
    district_data: DistrictCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    district = await repo.districts.create_district(
        district_name=district_data.district_name,
        district_name_uz=district_data.district_name_uz,
    )
    return DistrictDTO.model_validate(district, from_attributes=True)


@router.get("/{district_slug}")
async def get_district(
    district_slug: str,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    district = await repo.districts.get_district_by_slug(district_slug)
    if not district:
        return {"detail": "not found"}
    return DistrictDTO.model_validate(district, from_attributes=True)


@router.delete("/{district_slug}")
async def delete_district(
    district_slug: str,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    await repo.districts.delete_district(district_slug=district_slug)
    return {"status": "ok"}


@router.put("/{district_slug}", response_model=DistrictDTO)
async def update_district(
    district_slug: str,
    district_data: DistrictCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    updated = await repo.districts.update_district(
        district_slug=district_slug,
        distict_name=district_data.district_name,
    )
    return DistrictDTO.model_validate(updated, from_attributes=True)
