"""Abstract Doctor repository interface (port)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.doctor import Doctor
from app.domain.enums.doctor_status import DoctorStatus


class IDoctorRepository(ABC):
    """Port defining the contract for doctor persistence operations."""

    @abstractmethod
    async def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        """Retrieve a doctor by their UUID."""
        ...

    @abstractmethod
    async def get_by_employee_id(self, employee_id: str) -> Doctor | None:
        """Retrieve a doctor by their system-generated employee ID."""
        ...

    @abstractmethod
    async def search(
        self,
        *,
        specialty_id: uuid.UUID | None = None,
        status: DoctorStatus | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Doctor], int]:
        """Search doctors with optional filters.

        Returns a tuple of (list_of_doctors, total_count).
        """
        ...

    @abstractmethod
    async def add(self, doctor: Doctor) -> Doctor:
        """Persist a new doctor and return it."""
        ...

    @abstractmethod
    async def update(self, doctor: Doctor) -> Doctor:
        """Update an existing doctor and return it."""
        ...
