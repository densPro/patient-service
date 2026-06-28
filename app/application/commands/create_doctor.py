"""Command handler: create a new doctor."""

from __future__ import annotations

import uuid

from app.application.dtos.doctor_dtos import (
    DoctorAddressDTO,
    DoctorContactInfoDTO,
    DoctorCreateDTO,
    DoctorResponseDTO,
    LicenseInfoDTO,
)
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.entities.doctor import Doctor
from app.domain.exceptions import (
    DuplicateDoctorError,
    InvalidDoctorDataError,
    SpecialtyNotFoundError,
)
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.license_info import LicenseInfo


def _generate_employee_id() -> str:
    """Generate a unique employee identifier.

    Format: ``EMP-<8-hex-chars>`` (e.g. ``EMP-3A9F12BC``).
    """
    return f"EMP-{uuid.uuid4().hex[:8].upper()}"


class CreateDoctorCommand:
    """Creates a new doctor aggregate and persists it."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, dto: DoctorCreateDTO) -> DoctorResponseDTO:
        """Validate, build, and persist a new doctor.

        Raises:
            SpecialtyNotFoundError: If the referenced specialty does not exist.
            DuplicateDoctorError: If the generated employee ID collides (unlikely).
            InvalidDoctorDataError: If domain validation fails.
        """
        employee_id = _generate_employee_id()

        async with self._uow:
            # Validate specialty exists
            specialty = await self._uow.specialties.get_by_id(dto.specialty_id)
            if specialty is None:
                raise SpecialtyNotFoundError(str(dto.specialty_id))

            # Check employee_id uniqueness (collision is extremely unlikely)
            existing = await self._uow.doctors.get_by_employee_id(employee_id)
            if existing is not None:
                raise DuplicateDoctorError(employee_id)

            # Map nested DTOs → value objects
            license_info = (
                LicenseInfo(
                    license_number=dto.license_info.license_number,
                    issuing_body=dto.license_info.issuing_body,
                    issue_date=dto.license_info.issue_date,
                    expiration_date=dto.license_info.expiration_date,
                    state=dto.license_info.state,
                )
                if dto.license_info
                else None
            )

            contact_info = (
                ContactInfo(
                    phone_number=dto.contact_info.phone_number or "",
                    email=dto.contact_info.email,
                )
                if dto.contact_info
                else None
            )

            address = (
                Address(
                    street_line_1=dto.address.street_line_1 or "",
                    street_line_2=dto.address.street_line_2,
                    city=dto.address.city or "",
                    state=dto.address.state or "",
                    postal_code=dto.address.postal_code or "",
                    country=dto.address.country or "",
                )
                if dto.address
                else None
            )

            try:
                doctor = Doctor.create(
                    employee_id=employee_id,
                    first_name=dto.first_name,
                    last_name=dto.last_name,
                    date_of_birth=dto.date_of_birth,
                    gender=dto.gender,
                    specialty_id=dto.specialty_id,
                    license_info=license_info,
                    contact_info=contact_info,
                    address=address,
                    years_of_experience=dto.years_of_experience,
                    bio=dto.bio,
                )
            except ValueError as exc:
                raise InvalidDoctorDataError(str(exc)) from exc

            await self._uow.doctors.add(doctor)
            await self._uow.commit()

            return _to_response(doctor)


def _to_response(doctor: Doctor) -> DoctorResponseDTO:
    """Map domain Doctor entity → DoctorResponseDTO."""
    license_dto = None
    if doctor.license_info:
        license_dto = LicenseInfoDTO(
            license_number=doctor.license_info.license_number,
            issuing_body=doctor.license_info.issuing_body,
            issue_date=doctor.license_info.issue_date,
            expiration_date=doctor.license_info.expiration_date,
            state=doctor.license_info.state,
        )

    contact_dto = None
    if doctor.contact_info:
        contact_dto = DoctorContactInfoDTO(
            phone_number=doctor.contact_info.phone_number,
            email=doctor.contact_info.email,
        )

    address_dto = None
    if doctor.address:
        address_dto = DoctorAddressDTO(
            street_line_1=doctor.address.street_line_1,
            street_line_2=doctor.address.street_line_2,
            city=doctor.address.city,
            state=doctor.address.state,
            postal_code=doctor.address.postal_code,
            country=doctor.address.country,
        )

    return DoctorResponseDTO(
        id=doctor.id,
        employee_id=doctor.employee_id,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        full_name=doctor.full_name,
        date_of_birth=doctor.date_of_birth,
        age=doctor.age,
        gender=doctor.gender,
        specialty_id=doctor.specialty_id,
        license_info=license_dto,
        contact_info=contact_dto,
        address=address_dto,
        years_of_experience=doctor.years_of_experience,
        bio=doctor.bio,
        status=doctor.status,
        created_at=doctor.created_at,
        updated_at=doctor.updated_at,
    )
