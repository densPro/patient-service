"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.infrastructure.database.session import engine
from app.presentation.routers import health_router, patient_router
from app.presentation.routers import body_measurement_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown hooks."""
    # Startup — nothing special needed; engine is lazy
    yield
    # Shutdown — dispose the connection pool
    await engine.dispose()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=(
            "Patient management microservice for the Chirimoya healthcare platform. "
            "Provides CRUD operations and search capabilities for patient records."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # --- CORS ---
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

    return app


app = create_app()
