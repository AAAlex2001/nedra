"""Маршруты аудита."""

from fastapi import APIRouter

from src.audit.site.routers.audits import router as request_router
from src.audit.site.routers.contracts import router as contract_router
from src.audit.site.routers.documents import router as documents_router
from src.audit.site.routers.payments import router as payment_router
from src.audit.site.routers.plans import router as plan_router
from src.audit.site.routers.price import router as price_router
from src.audit.site.routers.team import router as group_router

router = APIRouter()

router.include_router(documents_router)
router.include_router(price_router)
router.include_router(group_router)
router.include_router(plan_router)
router.include_router(contract_router)
router.include_router(payment_router)
router.include_router(request_router)
