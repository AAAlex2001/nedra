import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.expertise import get_apply_expertise_payment_usecase
from app.dependencies.payments import (
    get_create_payment_usecase,
    get_payment_repository,
    get_sync_payment_usecase,
)
from app.dependencies.users import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreateSchema, PaymentOutSchema, WebhookSchema
from app.services.expertise.usecases.apply_expertise_payment import ApplyExpertisePaymentUseCase
from app.services.payments.exceptions import PaymentGatewayError, PaymentNotFoundError
from app.services.payments.repo import PaymentRepository
from app.services.payments.usecases.create_payment import CreatePaymentUseCase
from app.services.payments.usecases.sync_payment_status import SyncPaymentStatusUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreateSchema,
    user: User = Depends(get_current_user),
    usecase: CreatePaymentUseCase = Depends(get_create_payment_usecase),
) -> PaymentOutSchema:
    """Создать платёж и получить ссылку на оплату."""

    try:
        payment = await usecase.execute(user, payload.amount, payload.description)
    except PaymentGatewayError as error:
        logger.exception("Не удалось создать платёж")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Платёжный сервис временно недоступен",
        ) from error

    return PaymentOutSchema.model_validate(payment)


@router.get("/{payment_id}")
async def get_payment(
    payment_id: int,
    user: User = Depends(get_current_user),
    payments: PaymentRepository = Depends(get_payment_repository),
) -> PaymentOutSchema:
    """Платёж текущего пользователя. Чужой платёж выглядит как несуществующий."""

    payment = await payments.get_for_user(payment_id, user.id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден",
        )

    return PaymentOutSchema.model_validate(payment)


@router.post("/{payment_id}/refresh")
async def refresh_payment(
    payment_id: int,
    user: User = Depends(get_current_user),
    payments: PaymentRepository = Depends(get_payment_repository),
    usecase: SyncPaymentStatusUseCase = Depends(get_sync_payment_usecase),
) -> PaymentOutSchema:
    """Проверить оплату у ЮKassa. Фронт зовёт после возврата со страницы оплаты."""

    payment = await payments.get_for_user(payment_id, user.id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден",
        )

    try:
        updated = await usecase.execute(payment.provider_payment_id)
    except PaymentGatewayError as error:
        logger.exception("Не удалось проверить платёж %s", payment_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Платёжный сервис временно недоступен",
        ) from error

    return PaymentOutSchema.model_validate(updated)


@router.post("/yookassa/webhook")
async def yookassa_webhook(
    payload: WebhookSchema,
    usecase: SyncPaymentStatusUseCase = Depends(get_sync_payment_usecase),
    apply_to_expertise: ApplyExpertisePaymentUseCase = Depends(get_apply_expertise_payment_usecase),
) -> dict[str, str]:
    """Уведомление от ЮKassa о смене статуса.

    Тело уведомления не считаем доказательством оплаты: берём из него только
    id и перепроверяем платёж через API. Отвечаем 200 даже на незнакомый id,
    иначе ЮKassa будет повторять уведомление сутки. Если платёж относится
    к экспертизе, она сдвигается на следующий шаг.
    """

    try:
        payment = await usecase.execute(payload.object.id)
        await apply_to_expertise.execute(payment)
    except PaymentNotFoundError:
        logger.warning("Уведомление о неизвестном платеже %s", payload.object.id)
    except PaymentGatewayError as error:
        logger.exception("Не удалось перепроверить платёж %s", payload.object.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Платёжный сервис временно недоступен",
        ) from error

    return {"status": "ok"}
