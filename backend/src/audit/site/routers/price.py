"""Согласование цены."""

from fastapi import APIRouter, Depends

from src.audit.site.dependencies.price import (
    get_answer_audit_counter_offer_usecase,
    get_answer_audit_offer_usecase,
    get_propose_audit_price_usecase,
)
from src.audit.site.schemas.answer_audit_counter_offer import (
    AnswerAuditCounterOfferRequest,
    AnswerAuditCounterOfferResponse,
)
from src.audit.site.schemas.answer_audit_offer import (
    AnswerAuditOfferRequest,
    AnswerAuditOfferResponse,
)
from src.audit.site.schemas.propose_audit_price import (
    ProposeAuditPriceRequest,
    ProposeAuditPriceResponse,
)
from src.audit.site.usecases.answer_audit_counter_offer import (
    AnswerAuditCounterOfferUseCase,
)
from src.audit.site.usecases.answer_audit_offer import AnswerAuditOfferUseCase
from src.audit.site.usecases.propose_audit_price import ProposeAuditPriceUseCase
from src.auth.site.dependencies.authentication import require_customer, require_expert
from src.users.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


@router.post("/{audit_id}/offer")
async def propose_audit_price(
    *,
    audit_id: int,
    payload: ProposeAuditPriceRequest,
    user: User = Depends(require_expert),
    usecase: ProposeAuditPriceUseCase = Depends(get_propose_audit_price_usecase),
) -> ProposeAuditPriceResponse:
    """Предложить цену аудита."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        price=payload.price,
    )


@router.post("/{audit_id}/offer/answer")
async def answer_audit_offer(
    *,
    audit_id: int,
    payload: AnswerAuditOfferRequest,
    user: User = Depends(require_customer),
    usecase: AnswerAuditOfferUseCase = Depends(get_answer_audit_offer_usecase),
) -> AnswerAuditOfferResponse:
    """Ответить на цену аудитора."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        answer=payload.answer,
        price=payload.price,
    )


@router.post("/{audit_id}/counter/answer")
async def answer_audit_counter_offer(
    *,
    audit_id: int,
    payload: AnswerAuditCounterOfferRequest,
    user: User = Depends(require_expert),
    usecase: AnswerAuditCounterOfferUseCase = Depends(get_answer_audit_counter_offer_usecase),
) -> AnswerAuditCounterOfferResponse:
    """Ответить на встречную цену."""

    return await usecase.execute(
        user=user,
        audit_id=audit_id,
        accept=payload.accept,
    )
