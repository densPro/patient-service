"""Abstract patient repository interface (port)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.patient import Patient
from app.domain.enums.patient_status import PatientStatus


class IPatientRepository(ABC):
    """Port defining the contract for patient persistence.

    Concrete implementations live in the infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        """Retrieve a patient by their unique ID."""
        ...

    @abstractmethod
    async def get_by_mrn(self, mrn: str) -> Patient | None:
        """Retrieve a patient by their Medical Record Number."""
        ...

    @abstractmethod
    async def search(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        mrn: str | None = None,
        status: PatientStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Patient], int]:
        """Search patients with optional filters.

        Returns:
            A tuple of (matching patients, total count).
        """
        ...

    @abstractmethod
    async def add(self, patient: Patient) -> Patient:
        """Persist a new patient entity."""
        ...

    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        """Persist changes to an existing patient entity."""
        ...
