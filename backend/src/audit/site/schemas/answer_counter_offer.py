"""Ответ на встречное предложение."""

from pydantic import BaseModel


class AnswerAuditCounterOfferRequest(BaseModel):
    """Решение руководителя по цене заказчика."""

    accept: bool
