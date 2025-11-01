from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.config import config
from backend.app.dependencies import get_repo
from backend.core.interfaces.category import CategoryCreateDTO, CategoryDTO
from infrastructure.database.repo.requests import RequestsRepo

router = APIRouter(
    prefix=config.api_prefix.v1.categories,
    tags=["Categories"],
)


@router.get("/", response_model=list[CategoryDTO])
async def get_categories(
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    categories = await repo.categories.get_categories()
    return categories


@router.post("/create", response_model=CategoryDTO)
async def create_category(
    category_data: CategoryCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    new_category = await repo.categories.create_category(
        category_name=category_data.category_name,
        category_name_uz=category_data.category_name_uz,
    )
    return CategoryDTO.model_validate(new_category, from_attributes=True)


@router.get("/{category_slug}")
async def get_category_by_slug(
    category_slug: str,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    category = await repo.categories.get_category_by_slug(
        category_slug=category_slug,
    )
    if category is None:
        return {"detail": "not found"}
    return CategoryDTO.model_validate(category, from_attributes=True)


@router.delete("/{category_slug}")
async def delete_category(
    category_slug: str,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    await repo.categories.delete_category(category_slug=category_slug)
    return {"status": "ok"}


@router.put("/{category_slug}")
async def update_category(
    category_slug: str,
    category_data: CategoryCreateDTO,
    repo: Annotated[RequestsRepo, Depends(get_repo)],
):
    updated = await repo.categories.update_category(
        category_slug=category_slug,
        category_name=category_data.category_name,
    )
    return CategoryDTO.model_validate(updated, from_attributes=True)
