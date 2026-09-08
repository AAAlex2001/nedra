from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import admin_articles, articles, request

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


@app.get("/api/health", tags=["service"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(request.router, prefix="/api/v1")
app.include_router(articles.router, prefix="/api/v1")
app.include_router(admin_articles.router, prefix="/api/v1")

Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")
