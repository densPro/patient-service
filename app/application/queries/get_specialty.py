"""Query handler: retrieve specialties."""

from __future__ import annotations

import uuid

from app.application.dtos.specialty_dtos import SpecialtyResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.specialty import Specialty
from app.domain.exceptions import SpecialtyNotFoundError


class GetSpecialtyQuery:
    """Read-side handler for specialty queries."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def by_id(self, specialty_id: uuid.UUID) -> SpecialtyResponseDTO:
        """Retrieve a specialty by UUID.

        Raises:
            SpecialtyNotFoundError: If not found.
        """
        async with self._uow:
            specialty = await self._uow.specialties.get_by_id(specialty_id)
            if specialty is None:
                raise SpecialtyNotFoundError(str(specialty_id))
            return _to_response(specialty)

    async def by_code(self, code: str) -> SpecialtyResponseDTO:
        """Retrieve a specialty by its unique code.

        Raises:
            SpecialtyNotFoundError: If not found.
        """
        async with self._uow:
            specialty = await self._uow.specialties.get_by_code(code.upper())
            if specialty is None:
                raise SpecialtyNotFoundError(code)
            return _to_response(specialty)

    async def list_all(self, *, active_only: bool = False) -> list[SpecialtyResponseDTO]:
        """Return all specialties, optionally filtered to active ones only."""
        async with self._uow:
            specialties = await self._uow.specialties.list_all(active_only=active_only)
            return [_to_response(s) for s in specialties]


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
