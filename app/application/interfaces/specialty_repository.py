"""Abstract Specialty repository interface (port)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.specialty import Specialty


class ISpecialtyRepository(ABC):
    """Port defining the contract for specialty persistence operations."""

    @abstractmethod
    async def get_by_id(self, specialty_id: uuid.UUID) -> Specialty | None:
        """Retrieve a specialty by its UUID."""
        ...

    @abstractmethod
    async def get_by_code(self, code: str) -> Specialty | None:
        """Retrieve a specialty by its unique code."""
        ...

    @abstractmethod
    async def list_all(self, *, active_only: bool = False) -> list[Specialty]:
        """Return all specialties, optionally filtered to active only."""
        ...

    @abstractmethod
    async def add(self, specialty: Specialty) -> Specialty:
        """Persist a new specialty and return it."""
        ...

    @abstractmethod
    async def update(self, specialty: Specialty) -> Specialty:
        """Update an existing specialty and return it."""
        ...
