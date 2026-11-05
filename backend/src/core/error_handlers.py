"""Ошибки входных данных."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.file_exceptions import InvalidUploadError
from src.documents.company_requisites import CompanyRequisitesMissingError


async def missing_company_requisites(
    request: Request,
    error: CompanyRequisitesMissingError,
) -> JSONResponse:
    """Сообщить об отсутствии реквизитов."""

    return JSONResponse(
        status_code=503,
        content={"detail": "Реквизиты организации не настроены, обратитесь к администратору"},
    )


async def invalid_upload(
    request: Request,
    error: InvalidUploadError,
) -> JSONResponse:
    """Сообщить о недопустимом файле."""

    return JSONResponse(
        status_code=422,
        content={"detail": str(error)},
    )


async def invalid_request(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Сообщить о неверных полях запроса."""

    details = []

    for field_error in error.errors():
        details.append(
            {
                "loc": field_error["loc"],
                "msg": field_error["msg"],
                "type": field_error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={"detail": details},
    )


def register_core_error_handlers(*, app: FastAPI) -> None:
    """Подключить обработку ошибок запросов."""

    app.add_exception_handler(RequestValidationError, invalid_request)
    app.add_exception_handler(InvalidUploadError, invalid_upload)
    app.add_exception_handler(CompanyRequisitesMissingError, missing_company_requisites)
