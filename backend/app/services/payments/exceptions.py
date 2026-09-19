"""Ошибки бизнес-логики платежей. Роутеры переводят их в HTTP-коды."""


class PaymentNotFoundError(LookupError):
    """Платежа с таким идентификатором нет."""


class PaymentGatewayError(Exception):
    """ЮKassa недоступна или ответила ошибкой."""
