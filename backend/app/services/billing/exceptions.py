"""Ошибки биллинга. Роутеры переводят их в HTTP-коды."""


class InvalidCompanyError(ValueError):
    """Реквизиты организации не проходят проверку: ИНН или КПП неверной длины."""


class CompanyRequiredError(Exception):
    """Счёт нельзя выставить: в заявке нет реквизитов заказчика."""


class InvoiceNotFoundError(LookupError):
    """Счёта с таким идентификатором нет или он не принадлежит этому заказчику."""


class InvoiceAlreadyPaidError(Exception):
    """Счёт уже отмечен оплаченным, второй раз подтверждать нечего."""
