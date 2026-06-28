"""Concrete specialty repository using async SQLAlchemy."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.specialty_repository import ISpecialtyRepository
from app.domain.entities.specialty import Specialty
from app.domain.enums.specialty_category import SpecialtyCategory
from app.infrastructure.database.models.specialty_model import SpecialtyModel


class SpecialtyRepository(ISpecialtyRepository):
    """SQLAlchemy implementation of ``ISpecialtyRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_by_id(self, specialty_id: uuid.UUID) -> Specialty | None:
        stmt = select(SpecialtyModel).where(SpecialtyModel.id == specialty_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Specialty | None:
        stmt = select(SpecialtyModel).where(SpecialtyModel.code == code.upper())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, *, active_only: bool = False) -> list[Specialty]:
        stmt = select(SpecialtyModel)
        if active_only:
            stmt = stmt.where(SpecialtyModel.is_active.is_(True))
        stmt = stmt.order_by(SpecialtyModel.category, SpecialtyModel.name)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def add(self, specialty: Specialty) -> Specialty:
        model = self._to_model(specialty)
        self._session.add(model)
        await self._session.flush()
        return specialty

    async def update(self, specialty: Specialty) -> Specialty:
        stmt = select(SpecialtyModel).where(SpecialtyModel.id == specialty.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Specialty {specialty.id} not found for update.")

        model.code = specialty.code
        model.name = specialty.name
        model.category = specialty.category.value
        model.description = specialty.description
        model.is_active = specialty.is_active
        model.updated_at = specialty.updated_at

        await self._session.flush()
        return specialty

    # ------------------------------------------------------------------
    # Mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: SpecialtyModel) -> Specialty:
        """Map ORM model → domain entity."""
        return Specialty(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            code=model.code,
            name=model.name,
            category=SpecialtyCategory(model.category),
            description=model.description,
            is_active=model.is_active,
        )

    @staticmethod
    def _to_model(specialty: Specialty) -> SpecialtyModel:
        """Map domain entity → ORM model."""
        return SpecialtyModel(
            id=specialty.id,
            code=specialty.code,
            name=specialty.name,
            category=specialty.category.value,
            description=specialty.description,
            is_active=specialty.is_active,
            created_at=specialty.created_at,
            updated_at=specialty.updated_at,
        )
