"""Command handler: record a new body measurement for a patient."""

from __future__ import annotations

import uuid

from app.application.dtos.body_measurement_dtos import (
    BodyMeasurementCreateDTO,
    BodyMeasurementResponseDTO,
)
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.body_measurement import BodyMeasurement
from app.domain.exceptions import InvalidPatientDataError, PatientNotFoundError


class AddBodyMeasurementCommand:
    """Validates, creates, and persists a body measurement for a patient."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, patient_id: uuid.UUID, dto: BodyMeasurementCreateDTO
    ) -> BodyMeasurementResponseDTO:
        """Record a new body measurement.

        Raises:
            PatientNotFoundError: If no patient exists with the given ID.
            InvalidPatientDataError: If the measurement data violates domain rules.
        """
        async with self._uow:
            # Verify patient exists
            patient = await self._uow.patients.get_by_id(patient_id)
            if patient is None:
                raise PatientNotFoundError(str(patient_id))

            try:
                measurement = BodyMeasurement.create(
                    patient_id=patient_id,
                    height_cm=dto.height_cm,
                    weight_kg=dto.weight_kg,
                    waist_cm=dto.waist_cm,
                    hip_cm=dto.hip_cm,
                    measured_at=dto.measured_at,
                )
            except ValueError as exc:
                raise InvalidPatientDataError(str(exc)) from exc

            await self._uow.measurements.add(measurement)
            await self._uow.commit()

            return BodyMeasurementResponseDTO(
                id=measurement.id,
                patient_id=measurement.patient_id,
                measured_at=measurement.measured_at,
                height_cm=measurement.height_cm,
                weight_kg=measurement.weight_kg,
                waist_cm=measurement.waist_cm,
                hip_cm=measurement.hip_cm,
                bmi=measurement.bmi,
                bmi_category=measurement.bmi_category,
                created_at=measurement.created_at,
            )
