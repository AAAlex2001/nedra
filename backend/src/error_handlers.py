"""Обработка ошибок API."""

from fastapi import FastAPI

from src.articles.error_handlers import register_article_error_handlers
from src.audit.site.error_handlers import register_audit_error_handlers
from src.auth.admin.error_handlers import register_admin_auth_error_handlers
from src.auth.site.error_handlers import register_auth_error_handlers
from src.billing.error_handlers import register_billing_error_handlers
from src.commission.admin.error_handlers import register_admin_commission_error_handlers
from src.core.error_handlers import register_core_error_handlers
from src.expertise.site.error_handlers import register_expertise_error_handlers
from src.notifications.site.error_handlers import register_notification_error_handlers
from src.payments.site.error_handlers import register_payment_error_handlers
from src.requests.admin.error_handlers import (
    register_admin_contact_request_error_handlers,
)
from src.requests.site.error_handlers import register_contact_request_error_handlers
from src.tariffs.admin.error_handlers import register_admin_tariff_error_handlers
from src.users.admin.error_handlers import register_admin_user_error_handlers
from src.users.site.error_handlers import register_user_error_handlers


def register_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки модулей."""

    register_core_error_handlers(app=app)
    register_article_error_handlers(app=app)
    register_billing_error_handlers(app=app)
    register_audit_error_handlers(app=app)
    register_expertise_error_handlers(app=app)
    register_auth_error_handlers(app=app)
    register_admin_auth_error_handlers(app=app)
    register_user_error_handlers(app=app)
    register_admin_user_error_handlers(app=app)
    register_notification_error_handlers(app=app)
    register_payment_error_handlers(app=app)
    register_contact_request_error_handlers(app=app)
    register_admin_contact_request_error_handlers(app=app)
    register_admin_commission_error_handlers(app=app)
    register_admin_tariff_error_handlers(app=app)
