"""Маршруты экспертизы."""

from fastapi import APIRouter

from src.expertise.site.routers.billing import router as billing_router
from src.expertise.site.routers.contracts import router as contract_router
from src.expertise.site.routers.documents import router as documents_router
from src.expertise.site.routers.expertises import router as request_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(contract_router)
router.include_router(billing_router)
router.include_router(request_router)
