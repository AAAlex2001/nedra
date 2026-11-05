"""Ошибки экспертизы."""


class ExpertiseNotFoundError(Exception):
    """Экспертиза не найдена."""


class ExpertiseAccessError(Exception):
    """Недостаточно прав для действия."""


class ExpertiseStateError(Exception):
    """Действие недоступно на этом этапе."""


class InvalidExpertiseError(Exception):
    """В заявке неверные данные."""


class ExpertiseDocumentNotFoundError(Exception):
    """Файл документа не найден."""
