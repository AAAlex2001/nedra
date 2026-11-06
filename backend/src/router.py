"""Маршруты API."""

from fastapi import APIRouter

from src.articles.admin.routers.articles import router as admin_articles_router
from src.articles.admin.routers.tags import router as admin_article_tags_router
from src.articles.admin.routers.uploads import router as admin_article_uploads_router
from src.articles.site.routers.articles import router as articles_router
from src.articles.site.routers.interactions import router as article_interactions_router
from src.articles.site.routers.tags import router as article_tags_router
from src.audit.admin.routers.audits import router as admin_audit_router
from src.audit.admin.routers.details import router as admin_audit_read_router
from src.audit.site.routers.conclusion import router as audit_conclusion_router
from src.audit.site.routers.remarks import router as audit_remarks_router
from src.audit.site.routers.routes import router as audit_router
from src.auth.admin.routers.expert_applications import (
    router as admin_application_router,
)
from src.auth.site.routers.accounts import router as auth_router
from src.auth.site.routers.expert_application import router as application_router
from src.billing.admin.routers.invoices import router as admin_billing_router
from src.billing.site.routers.act import router as acts_router
from src.billing.site.routers.invoices import router as billing_router
from src.commission.admin.routers.applications import router as admin_commission_router
from src.commission.site.routers.applications import router as commission_router
from src.expertise.admin.routers.details import router as admin_expertise_read_router
from src.expertise.admin.routers.expertises import router as admin_expertise_router
from src.expertise.site.routers.conclusion import router as expertise_conclusion_router
from src.expertise.site.routers.payments import router as expertise_payment_router
from src.expertise.site.routers.remarks import router as expertise_remarks_router
from src.expertise.site.routers.routes import router as expertise_router
from src.notifications.site.routers.notifications import router as notifications_router
from src.payments.site.routers.payments import router as payments_router
from src.payments.site.routers.webhook import router as payment_webhook_router
from src.requests.admin.routers.contact_requests import (
    router as admin_contact_requests_router,
)
from src.requests.site.routers.contact_requests import router as contact_requests_router
from src.tariffs.admin.routers.tariffs import router as admin_tariffs_router
from src.tariffs.site.routers.tariffs import router as tariffs_router
from src.users.admin.routers.customer import router as admin_customers_router
from src.users.admin.routers.experts import router as admin_experts_router
from src.users.site.routers.email_change import router as user_email_change_router
from src.users.site.routers.expert import router as experts_router
from src.users.site.routers.profile import router as users_router

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
router.include_router(admin_article_tags_router)
router.include_router(admin_article_uploads_router)
router.include_router(article_tags_router)
router.include_router(article_interactions_router)
router.include_router(user_email_change_router)
router.include_router(payment_webhook_router)
