"""Abstract body measurement repository interface (port)."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from app.domain.entities.body_measurement import BodyMeasurement


class IBodyMeasurementRepository(ABC):
    """Port defining the contract for body measurement persistence."""

    @abstractmethod
    async def get_latest_by_patient(self, patient_id: uuid.UUID) -> BodyMeasurement | None:
        """Retrieve the most recent measurement for a patient."""
        ...

    @abstractmethod
    async def list_by_patient(
        self,
        patient_id: uuid.UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BodyMeasurement], int]:
        """List all measurements for a patient, newest first.

        Returns:
            A tuple of (measurements, total_count).
        """
        ...

    @abstractmethod
    async def get_latest_for_patients(
        self, patient_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, BodyMeasurement]:
        """Retrieve the most recent measurement for a list of patients.

        Returns:
            A dictionary mapping patient_id to their latest BodyMeasurement.
        """
        ...

    @abstractmethod
    async def add(self, measurement: BodyMeasurement) -> BodyMeasurement:
        """Persist a new body measurement."""
        ...

