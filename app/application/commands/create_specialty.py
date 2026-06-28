"""Command handler: create a new specialty."""

from __future__ import annotations

from app.application.dtos.specialty_dtos import SpecialtyCreateDTO, SpecialtyResponseDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.specialty import Specialty
from app.domain.exceptions import DuplicateSpecialtyError, InvalidSpecialtyDataError


class CreateSpecialtyCommand:
    """Creates a new specialty and persists it."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: SpecialtyCreateDTO) -> SpecialtyResponseDTO:
        """Validate, build, and persist a new specialty.

        Raises:
            DuplicateSpecialtyError: If the code already exists.
            InvalidSpecialtyDataError: If domain validation fails.
        """
        async with self._uow:
            existing = await self._uow.specialties.get_by_code(dto.code.upper())
            if existing is not None:
                raise DuplicateSpecialtyError(dto.code)

            try:
                specialty = Specialty.create(
                    code=dto.code,
                    name=dto.name,
                    category=dto.category,
                    description=dto.description,
                )
            except ValueError as exc:
                raise InvalidSpecialtyDataError(str(exc)) from exc

            await self._uow.specialties.add(specialty)
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
