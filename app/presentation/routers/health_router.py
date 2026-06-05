"""Health and readiness probe endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import text

from app.infrastructure.database.session import engine

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Returns 200 if the service is alive.",
)
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "patient-service"}


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Returns 200 if the service can connect to the database.",
)
async def readiness() -> dict[str, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return {"status": "not_ready", "database": "disconnected"}
