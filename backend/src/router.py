"""Маршруты API."""

from fastapi import APIRouter

from src.articles.admin.router import router as admin_articles_router
from src.articles.site.router import router as articles_router
from src.audit.admin.read_router import router as admin_audit_read_router
from src.audit.admin.router import router as admin_audit_router
from src.audit.site.conclusion_router import router as audit_conclusion_router
from src.audit.site.remarks_router import router as audit_remarks_router
from src.audit.site.router import router as audit_router
from src.auth.admin.router import router as admin_application_router
from src.auth.site.expert_application_router import router as application_router
from src.auth.site.router import router as auth_router
from src.billing.admin.router import router as admin_billing_router
from src.billing.site.act_router import router as acts_router
from src.billing.site.router import router as billing_router
from src.commission.admin.router import router as admin_commission_router
from src.commission.site.router import router as commission_router
from src.expertise.admin.read_router import router as admin_expertise_read_router
from src.expertise.admin.router import router as admin_expertise_router
from src.expertise.site.conclusion_router import router as expertise_conclusion_router
from src.expertise.site.payment_router import router as expertise_payment_router
from src.expertise.site.remarks_router import router as expertise_remarks_router
from src.expertise.site.router import router as expertise_router
from src.notifications.site.router import router as notifications_router
from src.payments.site.router import router as payments_router
from src.requests.admin.router import router as admin_contact_requests_router
from src.requests.site.router import router as contact_requests_router
from src.tariffs.admin.router import router as admin_tariffs_router
from src.tariffs.site.router import router as tariffs_router
from src.users.admin.customer_router import router as admin_customers_router
from src.users.admin.router import router as admin_experts_router
from src.users.site.expert_router import router as experts_router
from src.users.site.router import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(articles_router)
router.include_router(admin_articles_router)
router.include_router(expertise_router)
router.include_router(audit_router)
router.include_router(acts_router)
router.include_router(billing_router)
router.include_router(admin_billing_router)
router.include_router(admin_audit_router)
router.include_router(admin_audit_read_router)
router.include_router(admin_expertise_read_router)
router.include_router(admin_expertise_router)
router.include_router(audit_conclusion_router)
router.include_router(audit_remarks_router)
router.include_router(expertise_conclusion_router)
router.include_router(expertise_payment_router)
router.include_router(expertise_remarks_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(application_router)
router.include_router(admin_application_router)
router.include_router(payments_router)
router.include_router(notifications_router)
router.include_router(experts_router)
router.include_router(admin_experts_router)
router.include_router(admin_customers_router)
router.include_router(contact_requests_router)
router.include_router(admin_contact_requests_router)
router.include_router(commission_router)
router.include_router(admin_commission_router)
router.include_router(tariffs_router)
router.include_router(admin_tariffs_router)
