"""Command handler: partially update an existing doctor."""

from __future__ import annotations

import uuid

from app.application.commands.create_doctor import _to_response
from app.application.dtos.doctor_dtos import DoctorResponseDTO, DoctorUpdateDTO
from app.application.interfaces.unit_of_work import IUnitOfWork
from app.domain.exceptions import (
    DoctorNotFoundError,
    InvalidDoctorDataError,
    SpecialtyNotFoundError,
)
from app.domain.value_objects.address import Address
from app.domain.value_objects.contact_info import ContactInfo
from app.domain.value_objects.license_info import LicenseInfo


class UpdateDoctorCommand:
    """Partially updates an existing doctor record."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, doctor_id: uuid.UUID, dto: DoctorUpdateDTO
    ) -> DoctorResponseDTO:
        """Apply partial updates to a doctor.

        Raises:
            DoctorNotFoundError: If no doctor exists with the given ID.
            SpecialtyNotFoundError: If the referenced specialty_id does not exist.
            InvalidDoctorDataError: If the update violates domain rules.
        """
        async with self._uow:
            doctor = await self._uow.doctors.get_by_id(doctor_id)
            if doctor is None:
                raise DoctorNotFoundError(str(doctor_id))

            # Validate new specialty_id if provided
            if dto.specialty_id is not None:
                specialty = await self._uow.specialties.get_by_id(dto.specialty_id)
                if specialty is None:
                    raise SpecialtyNotFoundError(str(dto.specialty_id))
                doctor.specialty_id = dto.specialty_id

            try:
                if dto.first_name is not None:
                    if not dto.first_name.strip():
                        raise ValueError("First name cannot be empty.")
                    doctor.first_name = dto.first_name.strip()
                if dto.last_name is not None:
                    if not dto.last_name.strip():
                        raise ValueError("Last name cannot be empty.")
                    doctor.last_name = dto.last_name.strip()
                if dto.date_of_birth is not None:
                    doctor.date_of_birth = dto.date_of_birth
                if dto.gender is not None:
                    doctor.gender = dto.gender
                if dto.years_of_experience is not None:
                    doctor.years_of_experience = dto.years_of_experience
                if dto.bio is not None:
                    doctor.bio = dto.bio

                # Status transitions go through domain methods
                if dto.status is not None and dto.status != doctor.status:
                    from app.domain.enums.doctor_status import DoctorStatus
                    if dto.status == DoctorStatus.INACTIVE:
                        doctor.deactivate()
                    elif dto.status == DoctorStatus.ACTIVE:
                        doctor.reactivate()
                    elif dto.status == DoctorStatus.ON_LEAVE:
                        doctor.go_on_leave()
                    elif dto.status == DoctorStatus.RETIRED:
                        doctor.retire()

                # Value objects
                if dto.license_info is not None:
                    doctor.license_info = LicenseInfo(
                        license_number=dto.license_info.license_number,
                        issuing_body=dto.license_info.issuing_body,
                        issue_date=dto.license_info.issue_date,
                        expiration_date=dto.license_info.expiration_date,
                        state=dto.license_info.state,
                    )
                if dto.contact_info is not None:
                    doctor.contact_info = ContactInfo(
                        phone_number=dto.contact_info.phone_number or "",
                        email=dto.contact_info.email,
                    )
                if dto.address is not None:
                    doctor.address = Address(
                        street_line_1=dto.address.street_line_1 or "",
                        street_line_2=dto.address.street_line_2,
                        city=dto.address.city or "",
                        state=dto.address.state or "",
                        postal_code=dto.address.postal_code or "",
                        country=dto.address.country or "",
                    )

            except ValueError as exc:
                raise InvalidDoctorDataError(str(exc)) from exc

            doctor.touch()
            await self._uow.doctors.update(doctor)
            await self._uow.commit()

            return _to_response(doctor)
