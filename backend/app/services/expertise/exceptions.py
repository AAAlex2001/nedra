"""Ошибки бизнес-логики экспертизы. Роутеры переводят их в HTTP-коды."""


class InvalidExpertiseError(ValueError):
    """Заявка не проходит проверку по справочнику: объект, область, класс или категория."""


class ExpertiseNotFoundError(LookupError):
    """Экспертизы с таким идентификатором нет или у пользователя нет к ней доступа."""


class ExpertiseDocumentNotFoundError(LookupError):
    """Документа с таким идентификатором нет в этой экспертизе."""
