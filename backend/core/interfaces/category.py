from typing import Optional
from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    name: str
    name_uz: Optional[str]
    slug: str


class CategoryCreateDTO(BaseModel):
    category_name: str
    category_name_uz: str


class CategoryShortDTO(BaseModel):
    id: int
    name: str