"""Query handler: search / list doctors with filters."""

from __future__ import annotations

from app.application.commands.create_doctor import _to_response
from app.application.dtos.doctor_dtos import (
    DoctorSearchDTO,
    PaginatedDoctorsResponseDTO,
)
from app.application.interfaces.unit_of_work import IUnitOfWork


class SearchDoctorsQuery:
    """Paginated doctor search with optional filters."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: DoctorSearchDTO) -> PaginatedDoctorsResponseDTO:
        """Return a paginated, filtered list of doctors."""
        async with self._uow:
            doctors, total = await self._uow.doctors.search(
                specialty_id=dto.specialty_id,
                status=dto.status,
                first_name=dto.first_name,
                last_name=dto.last_name,
                limit=dto.limit,
                offset=dto.offset,
            )
            return PaginatedDoctorsResponseDTO(
                items=[_to_response(d) for d in doctors],
                total=total,
                limit=dto.limit,
                offset=dto.offset,
            )
