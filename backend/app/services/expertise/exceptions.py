"""Ошибки бизнес-логики экспертизы. Роутеры переводят их в HTTP-коды."""


class InvalidExpertiseError(ValueError):
    """Заявка не проходит проверку по справочнику: объект, область, класс или категория."""


class ExpertiseNotFoundError(LookupError):
    """Экспертизы с таким идентификатором нет или у пользователя нет к ней доступа."""


class ExpertiseDocumentNotFoundError(LookupError):
    """Документа с таким идентификатором нет в этой экспертизе."""


class ExpertiseStateError(Exception):
    """Действие не подходит текущему статусу экспертизы: шаг уже пройден или ещё не наступил."""


class ExpertiseAccessError(Exception):
    """Действие доступно только участнику экспертизы с нужной ролью."""


class PriceMissingError(Exception):
    """Для пары «область × объект» не задан тариф, договор заключить нельзя."""
