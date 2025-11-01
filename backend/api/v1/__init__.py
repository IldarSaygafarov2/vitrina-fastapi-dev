from fastapi import APIRouter

from backend.app.config import config

from .routes.advertisements import router as advertisements_router
from .routes.agents import router as agents_router
from .routes.categories import router as categories_router
from .routes.consultation import router as consultation_router
from .routes.districts import router as districts_router
from .routes.user_request import router as user_request_router
from .routes.users import router as users_router
from .routes.dev import dev_router


router = APIRouter(
    prefix=config.api_prefix.v1.prefix,
)


router.include_router(districts_router)
router.include_router(categories_router)
router.include_router(advertisements_router)
router.include_router(users_router)
router.include_router(user_request_router)
router.include_router(consultation_router)
router.include_router(agents_router)
router.include_router(dev_router)