"""HTTP-ответы на ошибки публикаций."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.articles.exceptions import (
    ArticleConflictError,
    ArticleNotFoundError,
    TagNotFoundError,
)


async def article_not_found(
    request: Request,
    error: ArticleNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии публикации."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Статья не найдена"},
    )


async def tag_not_found(
    request: Request,
    error: TagNotFoundError,
) -> JSONResponse:
    """Сообщить об отсутствии тега."""

    return JSONResponse(
        status_code=404,
        content={"detail": "Тег не найден"},
    )


async def address_conflict(
    request: Request,
    error: ArticleConflictError,
) -> JSONResponse:
    """Сообщить о занятом адресе."""

    return JSONResponse(
        status_code=409,
        content={"detail": "Такой адрес уже занят"},
    )


def register_article_error_handlers(*, app: FastAPI) -> None:
    """Подключить ошибки публикаций."""

    app.add_exception_handler(ArticleNotFoundError, article_not_found)
    app.add_exception_handler(TagNotFoundError, tag_not_found)
    app.add_exception_handler(ArticleConflictError, address_conflict)
