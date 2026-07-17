"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.infrastructure.database.session import engine
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.presentation.routers import health_router, patient_router
from app.presentation.routers import body_measurement_router
from app.presentation.routers import specialty_router, doctor_router

# Initialize logging as early as possible so every subsequent import
# (including database engine creation) can emit structured log lines.
setup_logging(level=settings.log_level, fmt=settings.log_format)

_log = get_logger("chirimoya.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    _log.info(
        "Starting up %s",
        settings.app_name,
        extra={
            "log_level":  settings.log_level,
            "log_format": settings.log_format,
            "debug":      settings.debug,
        },
    )
    yield
    # Shutdown — dispose the connection pool
    _log.info("Shutting down %s — disposing connection pool", settings.app_name)
    await engine.dispose()
    _log.info("Shutdown complete")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description=(
            "Patient Management microservice for the Chirimoya healthcare platform. "
            "Provides CRUD and search for patients, doctors, and medical specialties."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # --- Middleware (order matters: outermost = first to see the request) ---
    # RequestLoggingMiddleware must wrap everything so it captures the full
    # round-trip duration including CORS header injection.
    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    app.include_router(health_router.router)
    app.include_router(patient_router.router)
    app.include_router(body_measurement_router.router)
    app.include_router(specialty_router.router)
    app.include_router(doctor_router.router)

    _log.debug("Application factory complete — %d routes registered", len(app.routes))
    return app


app = create_app()
