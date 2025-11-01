from backend.api.v1 import router as api_v1_router
from backend.app.config import config
from fastapi import APIRouter


router = APIRouter(
    prefix=config.api_prefix.prefix
)
router.include_router(api_v1_router)
