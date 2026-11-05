"""Маршруты аудита."""

from fastapi import APIRouter

from src.audit.site.contract_router import router as contract_router
from src.audit.site.documents_router import router as documents_router
from src.audit.site.group_router import router as group_router
from src.audit.site.payment_router import router as payment_router
from src.audit.site.plan_router import router as plan_router
from src.audit.site.price_router import router as price_router
from src.audit.site.request_router import router as request_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(price_router)
router.include_router(group_router)
router.include_router(plan_router)
router.include_router(contract_router)
router.include_router(payment_router)
router.include_router(request_router)
