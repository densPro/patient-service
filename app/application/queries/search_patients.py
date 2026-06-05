"""Query handler: search patients with filters and pagination."""

from __future__ import annotations

from app.application.commands.create_patient import _to_response
from app.application.dtos.patient_response import PaginatedPatientsResponseDTO
from app.application.dtos.patient_search import PatientSearchDTO
from app.application.interfaces.unit_of_work import IUnitOfWork


class SearchPatientsQuery:
    """Searches patients with optional filters and pagination."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, dto: PatientSearchDTO
    ) -> PaginatedPatientsResponseDTO:
        """Run the search and return paginated results."""
        async with self._uow:
            patients, total = await self._uow.patients.search(
                first_name=dto.first_name,
                last_name=dto.last_name,
                date_of_birth=dto.date_of_birth,
                mrn=dto.mrn,
                status=dto.status,
                limit=dto.limit,
                offset=dto.offset,
            )

            if patients:
                patient_ids = [p.id for p in patients]
                latest_measurements = await self._uow.measurements.get_latest_for_patients(patient_ids)
                for p in patients:
                    p.latest_measurement = latest_measurements.get(p.id)

            return PaginatedPatientsResponseDTO(
                items=[_to_response(p) for p in patients],
                total=total,
                limit=dto.limit,
                offset=dto.offset,
            )

