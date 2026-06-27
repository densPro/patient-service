"""Command handler: soft-deactivate a doctor."""

from __future__ import annotations

import uuid

from app.application.commands.create_doctor import _to_response
from app.application.dtos.doctor_dtos import DoctorResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import DoctorNotFoundError


class DeactivateDoctorCommand:
    """Soft-deactivates a doctor (sets status = INACTIVE)."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, doctor_id: uuid.UUID) -> DoctorResponseDTO:
        """Deactivate the specified doctor.

        Raises:
            DoctorNotFoundError: If the doctor does not exist.
        """
        async with self._uow:
            doctor = await self._uow.doctors.get_by_id(doctor_id)
            if doctor is None:
                raise DoctorNotFoundError(str(doctor_id))

            doctor.deactivate()
            await self._uow.doctors.update(doctor)
            await self._uow.commit()

            return _to_response(doctor)
