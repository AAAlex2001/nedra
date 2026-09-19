"""Анонимный идентификатор посетителя для просмотров и реакций на статьи."""

from uuid import UUID, uuid4

from fastapi import Request, Response

from app.config import get_settings

VISITOR_COOKIE = "visitor_id"
VISITOR_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


def get_visitor_id(request: Request, response: Response) -> str:
    """Анонимный идентификатор посетителя из cookie.

    Просмотры и реакции не требуют входа, поэтому привязываются к UUID
    в cookie. Если cookie нет или она испорчена — выдаём новую и ставим
    её в ответ. Cookie живёт год и недоступна из JavaScript.
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


def is_uuid(value: str) -> bool:
    """Проверить, что строка — корректный UUID."""

    try:
        UUID(value)
    except ValueError:
        return False

    return True
