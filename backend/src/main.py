"""Точка входа FastAPI-приложения."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.config import get_settings
from src.core.errors import register_exception_handlers
from src.requests.router import router as requests_router

settings = get_settings()

app = FastAPI(
    title="Nedra API",
    version="0.2.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
Path(settings.private_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(requests_router, prefix="/api/v1")

@app.get("/api/health")
async def health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""

    return {"status": "ok"}
