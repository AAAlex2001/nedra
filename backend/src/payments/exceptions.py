"""Ошибки оплаты."""


class PaymentNotFoundError(Exception):
    """Платёж не найден."""


class PaymentGatewayError(Exception):
    """Платёжный сервис недоступен."""


class PaymentConfigurationError(Exception):
    """Оплата не настроена."""


class PaymentStateError(Exception):
    """Оплата недоступна на этом этапе."""
