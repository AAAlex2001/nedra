from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import request

settings = get_settings()

app = FastAPI(
    title="Nedra API",
    version="0.1.0",
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
