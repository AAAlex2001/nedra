"""Зависимости для роутеров: фабрики сервисов, идентификация посетителя, защита админки."""

import secrets
from uuid import UUID, uuid4

from fastapi import Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.services.articles import ArticleService
from app.services.request import RequestService

VISITOR_COOKIE = "visitor_id"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def get_request_service(
    session: AsyncSession = Depends(get_session),
) -> RequestService:
    """Сервис заявок с сессией текущего запроса."""

    return RequestService(session)


def get_article_service(
    session: AsyncSession = Depends(get_session),
) -> ArticleService:
    """Сервис статей с сессией текущего запроса."""

    return ArticleService(session)


def get_visitor_id(request: Request, response: Response) -> str:
    """Анонимный идентификатор посетителя из cookie.

    Пользователей на сайте нет, поэтому просмотры и реакции привязываются
    к UUID в cookie. Если cookie нет или она испорчена — выдаём новую
    и ставим её в ответ. Cookie живёт год и недоступна из JavaScript.
    """

    visitor_id = request.cookies.get(VISITOR_COOKIE)
    if visitor_id and is_uuid(visitor_id):
        return visitor_id

    visitor_id = str(uuid4())
    response.set_cookie(
        VISITOR_COOKIE,
        visitor_id,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=get_settings().cookie_secure,
        path="/",
    )

    return visitor_id


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    """Пропустить запрос только с верным заголовком X-Admin-Token.

    Токен знает только сервер Next.js и добавляет его к запросам из админки.
    В браузер он не попадает. Сравнение через compare_digest — за постоянное
    время, чтобы по скорости ответа нельзя было подобрать токен посимвольно.
    """

    expected = get_settings().admin_api_token

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Админ-доступ не настроен",
        )

    if not x_admin_token or not secrets.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет доступа",
        )


def is_uuid(value: str) -> bool:
    """Проверить, что строка — корректный UUID."""

    try:
        UUID(value)
    except ValueError:
        return False

    return True
