"""Command handler: soft-deactivate a specialty."""

from __future__ import annotations

import uuid

from app.application.dtos.specialty_dtos import SpecialtyResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.specialty import Specialty
from app.domain.exceptions import SpecialtyNotFoundError


class DeactivateSpecialtyCommand:
    """Soft-deactivates a specialty (sets is_active = False)."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, specialty_id: uuid.UUID) -> SpecialtyResponseDTO:
        """Deactivate the specified specialty.

        Raises:
            SpecialtyNotFoundError: If the specialty does not exist.
        """
        async with self._uow:
            specialty = await self._uow.specialties.get_by_id(specialty_id)
            if specialty is None:
                raise SpecialtyNotFoundError(str(specialty_id))

            specialty.deactivate()
            await self._uow.specialties.update(specialty)
            await self._uow.commit()

            return _to_response(specialty)


def _to_response(specialty: Specialty) -> SpecialtyResponseDTO:
    return SpecialtyResponseDTO(
        id=specialty.id,
        code=specialty.code,
        name=specialty.name,
        category=specialty.category,
        description=specialty.description,
        is_active=specialty.is_active,
        created_at=specialty.created_at,
        updated_at=specialty.updated_at,
    )
