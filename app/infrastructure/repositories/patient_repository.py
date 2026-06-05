"""Concrete patient repository using async SQLAlchemy."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.patient_repository import IPatientRepository
from app.domain.entities.patient import Patient
from app.domain.enums.blood_type import BloodType
from app.domain.enums.gender import Gender
from app.domain.enums.marital_status import MaritalStatus
from app.domain.enums.patient_status import PatientStatus
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.emergency_contact import EmergencyContact
from app.domain.value_objects.insurance_info import InsuranceInfo
from app.infrastructure.database.models.patient_model import PatientModel


class PatientRepository(IPatientRepository):
    """SQLAlchemy implementation of ``IPatientRepository``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        stmt = select(PatientModel).where(PatientModel.id == patient_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_mrn(self, mrn: str) -> Patient | None:
        stmt = select(PatientModel).where(PatientModel.mrn == mrn)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search(
        self,
        *,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth: str | None = None,
        mrn: str | None = None,
        status: PatientStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Patient], int]:
        stmt = select(PatientModel)
        count_stmt = select(func.count()).select_from(PatientModel)

        # Apply filters
        if first_name:
            condition = PatientModel.first_name.ilike(f"%{first_name}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if last_name:
            condition = PatientModel.last_name.ilike(f"%{last_name}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if date_of_birth:
            try:
                dob = date.fromisoformat(date_of_birth)
                condition = PatientModel.date_of_birth == dob
                stmt = stmt.where(condition)
                count_stmt = count_stmt.where(condition)
            except ValueError:
                pass  # Ignore invalid date format — return all
        if mrn:
            condition = PatientModel.mrn.ilike(f"%{mrn}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if status:
            condition = PatientModel.status == status.value
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        # Total count
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        # Paginated results
        stmt = stmt.order_by(PatientModel.last_name, PatientModel.first_name)
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(m) for m in models], total

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    async def add(self, patient: Patient) -> Patient:
        model = self._to_model(patient)
        self._session.add(model)
        await self._session.flush()
        return patient

    async def update(self, patient: Patient) -> Patient:
        stmt = select(PatientModel).where(PatientModel.id == patient.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Patient {patient.id} not found for update.")

        # Apply entity state to model
        model.first_name = patient.first_name
        model.last_name = patient.last_name
        model.date_of_birth = patient.date_of_birth
        model.gender = patient.gender.value
        model.marital_status = patient.marital_status.value
        model.ssn_last_four = patient.ssn_last_four
        model.national_id = patient.national_id
        model.blood_type = patient.blood_type.value
        model.allergies = patient.allergies
        model.chronic_conditions = patient.chronic_conditions
        model.contact_info = patient.contact_info.to_dict() if patient.contact_info else None
        model.address = patient.address.to_dict() if patient.address else None
        model.emergency_contact = (
            patient.emergency_contact.to_dict() if patient.emergency_contact else None
        )
        model.insurance_info = (
            patient.insurance_info.to_dict() if patient.insurance_info else None
        )
        model.notes = patient.notes
        model.status = patient.status.value
        model.updated_at = patient.updated_at

        await self._session.flush()
        return patient

    # ------------------------------------------------------------------
    # Mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_entity(model: PatientModel) -> Patient:
        """Map ORM model → domain entity."""
        contact_info = (
            ContactInfo.from_dict(model.contact_info) if model.contact_info else None
        )
        address = Address.from_dict(model.address) if model.address else None
        emergency_contact = (
            EmergencyContact.from_dict(model.emergency_contact)
            if model.emergency_contact
            else None
        )
        insurance_info = (
            InsuranceInfo.from_dict(model.insurance_info)
            if model.insurance_info
            else None
        )

        return Patient(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            mrn=model.mrn,
            first_name=model.first_name,
            last_name=model.last_name,
            date_of_birth=model.date_of_birth,
            gender=Gender(model.gender),
            marital_status=MaritalStatus(model.marital_status),
            ssn_last_four=model.ssn_last_four,
            national_id=model.national_id,
            blood_type=BloodType(model.blood_type),
            allergies=model.allergies or [],
            chronic_conditions=model.chronic_conditions or [],
            contact_info=contact_info,
            address=address,
            emergency_contact=emergency_contact,
            insurance_info=insurance_info,
            notes=model.notes,
            status=PatientStatus(model.status),
        )

    @staticmethod
    def _to_model(patient: Patient) -> PatientModel:
        """Map domain entity → ORM model."""
        return PatientModel(
            id=patient.id,
            mrn=patient.mrn,
            first_name=patient.first_name,
            last_name=patient.last_name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender.value,
            marital_status=patient.marital_status.value,
            ssn_last_four=patient.ssn_last_four,
            national_id=patient.national_id,
            blood_type=patient.blood_type.value,
            allergies=patient.allergies,
            chronic_conditions=patient.chronic_conditions,
            contact_info=patient.contact_info.to_dict() if patient.contact_info else None,
            address=patient.address.to_dict() if patient.address else None,
            emergency_contact=(
                patient.emergency_contact.to_dict()
                if patient.emergency_contact
                else None
            ),
            insurance_info=(
                patient.insurance_info.to_dict() if patient.insurance_info else None
            ),
            notes=patient.notes,
            status=patient.status.value,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
        )
