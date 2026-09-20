"""Окружение для тестов: настройки не должны зависеть от локального .env."""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-not-for-production-123456")
os.environ.setdefault("COMPANY_VAT_RATE", "0")
