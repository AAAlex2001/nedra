"""Маршруты экспертизы."""

from fastapi import APIRouter

from src.expertise.site.billing_router import router as billing_router
from src.expertise.site.contract_router import router as contract_router
from src.expertise.site.documents_router import router as documents_router
from src.expertise.site.request_router import router as request_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(contract_router)
router.include_router(billing_router)
router.include_router(request_router)
