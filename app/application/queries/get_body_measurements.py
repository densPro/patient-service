"""Query handlers: retrieve body measurements for a patient."""

from __future__ import annotations

import uuid

from app.application.dtos.body_measurement_dtos import (
    BodyMeasurementResponseDTO,
    PaginatedMeasurementsResponseDTO,
)
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.body_measurement import BodyMeasurement
from app.domain.entities.patient import Patient
from app.domain.exceptions import PatientNotFoundError



def _to_dto(measurement: BodyMeasurement, patient: Patient) -> BodyMeasurementResponseDTO:
    """Map a BodyMeasurement entity → response DTO."""
    return BodyMeasurementResponseDTO(
        id=measurement.id,
        patient_id=measurement.patient_id,
        measured_at=measurement.measured_at,
        height_cm=measurement.height_cm,
        height_m=measurement.height_m,
        weight_kg=measurement.weight_kg,
        waist_cm=measurement.waist_cm,
        hip_cm=measurement.hip_cm,
        bmi=measurement.bmi,
        bmi_category=measurement.bmi_category,
        healthy_weight=measurement.healthy_weight,
        minimum_weight=measurement.minimum_weight,
        maximum_weight=measurement.maximum_weight,
        bmr_harris_benedict=measurement.calculate_bmr_harris_benedict(patient.age, patient.gender.value) if patient.age is not None else None,
        bmr_mifflin_st_jeor=measurement.calculate_bmr_mifflin_st_jeor(patient.age, patient.gender.value) if patient.age is not None else None,
        created_at=measurement.created_at,
    )




class GetBodyMeasurementsQuery:
    """Queries for body measurements belonging to a specific patient."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def latest(self, patient_id: uuid.UUID) -> BodyMeasurementResponseDTO:
        """Return the most recent measurement for a patient.

        Raises:
            PatientNotFoundError: If no patient with the given ID exists.
            PatientNotFoundError: If the patient has no measurements recorded.
        """
        async with self._uow:
            patient = await self._uow.patients.get_by_id(patient_id)
            if patient is None:
                raise PatientNotFoundError(str(patient_id))

            measurement = await self._uow.measurements.get_latest_by_patient(patient_id)
            if measurement is None:
                raise PatientNotFoundError(
                    f"No measurements found for patient {patient_id}."
                )
            return _to_dto(measurement, patient)

    async def list_all(
        self,
        patient_id: uuid.UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedMeasurementsResponseDTO:
        """Return paginated measurement history for a patient.

        Raises:
            PatientNotFoundError: If no patient with the given ID exists.
        """
        async with self._uow:
            patient = await self._uow.patients.get_by_id(patient_id)
            if patient is None:
                raise PatientNotFoundError(str(patient_id))

            measurements, total = await self._uow.measurements.list_by_patient(
                patient_id, limit=limit, offset=offset
            )

            return PaginatedMeasurementsResponseDTO(
                items=[_to_dto(m, patient) for m in measurements],
                total=total,
                limit=limit,
                offset=offset,
            )
