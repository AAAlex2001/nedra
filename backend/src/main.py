"""Запуск нового API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.settings import Settings
from src.error_handlers import register_error_handlers
from src.router import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Открыть ресурсы приложения."""

    settings = app.state.settings
    settings.media_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    settings.private_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    engine = create_async_engine(settings.database_url)
    app.state.session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:
        yield
    finally:
        await engine.dispose()


async def health() -> dict[str, str]:
    """Проверить доступность API."""

    return {"status": "ok"}


def create_app(*, settings: Settings | None = None) -> FastAPI:
    """Создать приложение."""

    settings = settings or Settings()
    app = FastAPI(
        title="Nedra API",
        version="0.3.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        debug=settings.debug,
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app=app)
    app.include_router(router)
    app.add_api_route(
        "/api/health",
        health,
        methods=["GET"],
        tags=["service"],
    )
    app.mount(
        "/media",
        StaticFiles(
            directory=settings.media_dir,
            check_dir=False,
        ),
        name="media",
    )

    return app
