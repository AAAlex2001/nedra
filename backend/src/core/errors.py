"""Централизованная обработка доменных исключений FastAPI."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики доменных исключений приложения."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Возвращает 422 для доменных ошибок валидации."""

        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(LookupError)
    async def lookup_error_handler(request: Request, exc: LookupError) -> JSONResponse:
        """Возвращает 404 для не найденных сущностей."""

        return JSONResponse(status_code=404, content={"detail": str(exc)})
