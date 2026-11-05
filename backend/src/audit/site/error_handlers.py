"""Ошибки работы с аудитом."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.audit.exceptions import (
    AuditAccessError,
    AuditDocumentNotFoundError,
    AuditNotFoundError,
    AuditStateError,
    InvalidAuditApplicationError,
    InvalidAuditPriceError,
)


async def audit_not_found(
    request: Request,
    error: AuditNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии аудита."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Аудит не найден"},
    )


async def audit_access_denied(
    request: Request,
    error: AuditAccessError,
) -> JSONResponse:
    """Сообщить об отсутствии доступа."""

    return JSONResponse(
        status_code=403,
        content={"detail": str(error)},
    )


async def invalid_audit_state(
    request: Request,
    error: AuditStateError,
) -> JSONResponse:
    """Сообщить о недоступном действии."""

    return JSONResponse(
        status_code=409,
        content={"detail": str(error)},
    )


async def invalid_audit_data(
    request: Request,
    error: Exception,
) -> JSONResponse:
    """Сообщить об ошибке в заявке."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


def register_audit_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки аудита."""

    app.add_exception_handler(AuditDocumentNotFoundError, audit_document_not_found)
    app.add_exception_handler(AuditNotFoundError, audit_not_found)
    app.add_exception_handler(AuditAccessError, audit_access_denied)
    app.add_exception_handler(AuditStateError, invalid_audit_state)
    app.add_exception_handler(InvalidAuditApplicationError, invalid_audit_data)
    app.add_exception_handler(InvalidAuditPriceError, invalid_audit_data)


async def audit_document_not_found(
    request: Request,
    error: AuditDocumentNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии файла."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Документ не найден"},
    )
