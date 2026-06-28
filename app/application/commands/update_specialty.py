"""Command handler: partially update an existing specialty."""

from __future__ import annotations

import uuid

from app.application.dtos.specialty_dtos import SpecialtyResponseDTO, SpecialtyUpdateDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.specialty import Specialty
from app.domain.exceptions import InvalidSpecialtyDataError, SpecialtyNotFoundError


class UpdateSpecialtyCommand:
    """Partially updates an existing specialty."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, specialty_id: uuid.UUID, dto: SpecialtyUpdateDTO
    ) -> SpecialtyResponseDTO:
        """Apply partial updates to a specialty.

        Raises:
            SpecialtyNotFoundError: If no specialty exists with the given ID.
            InvalidSpecialtyDataError: If the update violates domain rules.
        """
        async with self._uow:
            specialty = await self._uow.specialties.get_by_id(specialty_id)
            if specialty is None:
                raise SpecialtyNotFoundError(str(specialty_id))

            try:
                specialty.update_details(
                    name=dto.name,
                    category=dto.category,
                    description=dto.description,
                )
            except ValueError as exc:
                raise InvalidSpecialtyDataError(str(exc)) from exc

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
