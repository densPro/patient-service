"""Query handler: retrieve a single patient."""

from __future__ import annotations

import uuid

from app.application.commands.create_patient import _to_response
from app.application.dtos.patient_response import PatientResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import PatientNotFoundError


class GetPatientQuery:
    """Retrieves a patient by ID or MRN."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def by_id(self, patient_id: uuid.UUID) -> PatientResponseDTO:
        """Fetch a patient by their unique ID.

        Raises:
            PatientNotFoundError: If no patient exists with the given ID.
        """
        async with self._uow:
            patient = await self._uow.patients.get_by_id(patient_id)
            if patient is None:
                raise PatientNotFoundError(str(patient_id))
            patient.latest_measurement = await self._uow.measurements.get_latest_by_patient(
                patient_id
            )
            return _to_response(patient)

    async def by_mrn(self, mrn: str) -> PatientResponseDTO:
        """Fetch a patient by their Medical Record Number.

        Raises:
            PatientNotFoundError: If no patient exists with the given MRN.
        """
        async with self._uow:
            patient = await self._uow.patients.get_by_mrn(mrn)
            if patient is None:
                raise PatientNotFoundError(mrn)
            patient.latest_measurement = await self._uow.measurements.get_latest_by_patient(
                patient.id
            )
            return _to_response(patient)
