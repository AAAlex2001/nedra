"""Идентификатор посетителя."""

from uuid import UUID, uuid4

from fastapi import Depends, Request, Response

from src.articles.options import VISITOR_COOKIE, VISITOR_COOKIE_MAX_AGE
from src.core.settings import Settings, get_settings


def get_visitor_id(
    *,
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
) -> str:
    """Прочитать или выдать cookie посетителя."""

    visitor_id = request.cookies.get(VISITOR_COOKIE)

    if visitor_id:
        try:
            return str(UUID(visitor_id))
        except ValueError:
            pass

    visitor_id = str(uuid4())
    response.set_cookie(
        VISITOR_COOKIE,
        visitor_id,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )

    return visitor_id
