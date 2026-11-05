"""Ошибки аудита."""


class AuditNotFoundError(Exception):
    """Аудит не найден."""


class AuditAccessError(Exception):
    """Нет доступа к аудиту."""


class AuditStateError(Exception):
    """Действие недоступно на текущем этапе."""


class InvalidAuditPriceError(Exception):
    """Некорректная стоимость аудита."""


class InvalidAuditApplicationError(Exception):
    """Неполные или некорректные данные заявки."""


class AuditDocumentNotFoundError(Exception):
    """Файл документа не найден."""
