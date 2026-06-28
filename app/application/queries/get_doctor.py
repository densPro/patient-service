"""Query handler: retrieve a single doctor."""

from __future__ import annotations

import uuid

from app.application.commands.create_doctor import _to_response
from app.application.dtos.doctor_dtos import DoctorResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import DoctorNotFoundError


class GetDoctorQuery:
    """Read-side handler for single-doctor lookups."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def by_id(self, doctor_id: uuid.UUID) -> DoctorResponseDTO:
        """Retrieve a doctor by UUID.

        Raises:
            DoctorNotFoundError: If not found.
        """
        async with self._uow:
            doctor = await self._uow.doctors.get_by_id(doctor_id)
            if doctor is None:
                raise DoctorNotFoundError(str(doctor_id))
            return _to_response(doctor)

    async def by_employee_id(self, employee_id: str) -> DoctorResponseDTO:
        """Retrieve a doctor by their employee ID.

        Raises:
            DoctorNotFoundError: If not found.
        """
        async with self._uow:
            doctor = await self._uow.doctors.get_by_employee_id(employee_id)
            if doctor is None:
                raise DoctorNotFoundError(employee_id)
            return _to_response(doctor)
