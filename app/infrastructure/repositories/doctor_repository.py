"""Concrete doctor repository using async SQLAlchemy."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.doctor_repository import IDoctorRepository
from app.domain.entities.doctor import Doctor
from app.domain.enums.doctor_status import DoctorStatus
from app.domain.enums.gender import Gender
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.license_info import LicenseInfo
from app.infrastructure.database.models.doctor_model import DoctorModel


class DoctorRepository(IDoctorRepository):
    """SQLAlchemy implementation of ``IDoctorRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        stmt = select(DoctorModel).where(DoctorModel.id == doctor_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_employee_id(self, employee_id: str) -> Doctor | None:
        stmt = select(DoctorModel).where(DoctorModel.employee_id == employee_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search(
        self,
        *,
        specialty_id: uuid.UUID | None = None,
        status: DoctorStatus | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Doctor], int]:
        stmt = select(DoctorModel)
        count_stmt = select(func.count()).select_from(DoctorModel)

        # Apply filters
        if specialty_id is not None:
            condition = DoctorModel.specialty_id == specialty_id
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if status is not None:
            condition = DoctorModel.status == status.value
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if first_name:
            condition = DoctorModel.first_name.ilike(f"%{first_name}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if last_name:
            condition = DoctorModel.last_name.ilike(f"%{last_name}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        # Total count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginated results
        stmt = stmt.order_by(DoctorModel.last_name, DoctorModel.first_name)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def add(self, doctor: Doctor) -> Doctor:
        model = self._to_model(doctor)
        self._session.add(model)
        await self._session.flush()
        return doctor

    async def update(self, doctor: Doctor) -> Doctor:
        stmt = select(DoctorModel).where(DoctorModel.id == doctor.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Doctor {doctor.id} not found for update.")

        model.first_name = doctor.first_name
        model.last_name = doctor.last_name
        model.date_of_birth = doctor.date_of_birth
        model.gender = doctor.gender.value
        model.specialty_id = doctor.specialty_id
        model.license_info = (
            doctor.license_info.to_dict() if doctor.license_info else None
        )
        model.contact_info = (
            doctor.contact_info.to_dict() if doctor.contact_info else None
        )
        model.address = doctor.address.to_dict() if doctor.address else None
        model.years_of_experience = doctor.years_of_experience
        model.bio = doctor.bio
        model.status = doctor.status.value
        model.updated_at = doctor.updated_at

        await self._session.flush()
        return doctor

    # ------------------------------------------------------------------
    # Mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: DoctorModel) -> Doctor:
        """Map ORM model → domain entity."""
        license_info = (
            LicenseInfo.from_dict(model.license_info) if model.license_info else None
        )
        contact_info = (
            ContactInfo.from_dict(model.contact_info) if model.contact_info else None
        )
        address = Address.from_dict(model.address) if model.address else None

        return Doctor(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            employee_id=model.employee_id,
            first_name=model.first_name,
            last_name=model.last_name,
            date_of_birth=model.date_of_birth,
            gender=Gender(model.gender),
            specialty_id=model.specialty_id,
            license_info=license_info,
            contact_info=contact_info,
            address=address,
            years_of_experience=model.years_of_experience,
            bio=model.bio,
            status=DoctorStatus(model.status),
        )

    @staticmethod
    def _to_model(doctor: Doctor) -> DoctorModel:
        """Map domain entity → ORM model."""
        return DoctorModel(
            id=doctor.id,
            employee_id=doctor.employee_id,
            first_name=doctor.first_name,
            last_name=doctor.last_name,
            date_of_birth=doctor.date_of_birth,
            gender=doctor.gender.value,
            specialty_id=doctor.specialty_id,
            license_info=(
                doctor.license_info.to_dict() if doctor.license_info else None
            ),
            contact_info=(
                doctor.contact_info.to_dict() if doctor.contact_info else None
            ),
            address=doctor.address.to_dict() if doctor.address else None,
            years_of_experience=doctor.years_of_experience,
            bio=doctor.bio,
            status=doctor.status.value,
            created_at=doctor.created_at,
            updated_at=doctor.updated_at,
        )
