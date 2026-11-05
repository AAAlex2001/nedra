"""Ответы на ошибки экспертизы."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.expertise.exceptions import (
    ExpertiseAccessError,
    ExpertiseDocumentNotFoundError,
    ExpertiseNotFoundError,
    ExpertiseStateError,
    InvalidExpertiseError,
)


async def expertise_not_found(
    request: Request,
    error: ExpertiseNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии заявки."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Экспертиза не найдена"},
    )


async def expertise_access_denied(
    request: Request,
    error: ExpertiseAccessError,
) -> JSONResponse:
    """Сообщить об отсутствии доступа."""

    return JSONResponse(
        status_code=403,
        content={"detail": str(error)},
    )


async def invalid_expertise_state(
    request: Request,
    error: ExpertiseStateError,
) -> JSONResponse:
    """Сообщить о недоступном действии."""

    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_expertise_data(
    request: Request,
    error: InvalidExpertiseError,
) -> JSONResponse:
    """Сообщить об ошибке в заявке."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


def register_expertise_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки экспертизы."""

    app.add_exception_handler(ExpertiseDocumentNotFoundError, expertise_document_not_found)
    app.add_exception_handler(ExpertiseNotFoundError, expertise_not_found)
    app.add_exception_handler(ExpertiseAccessError, expertise_access_denied)
    app.add_exception_handler(ExpertiseStateError, invalid_expertise_state)
    app.add_exception_handler(InvalidExpertiseError, invalid_expertise_data)


async def expertise_document_not_found(
    request: Request,
    error: ExpertiseDocumentNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии файла."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Документ не найден"},
    )
